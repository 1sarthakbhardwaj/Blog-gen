from crewai import Agent, Task, Crew, Process, LLM
import re
from typing import Dict, List, Tuple, Callable, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ArticleWorkflow:
    """
    Main workflow class for article generation with backlinking optimization
    """
    
    def __init__(self, api_key=None, model=None, provider=None):
        # Use provided API key and model, or fall back to environment variables
        if api_key and model:
            self.api_key = api_key
            self.model = model
            self.provider = provider
            
            # Set the API key as environment variable based on provider
            if "openai" in model.lower():
                os.environ["OPENAI_API_KEY"] = api_key
            elif "groq" in model.lower():
                os.environ["GROQ_API_KEY"] = api_key
        else:
            # Fallback to environment variables
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError(
                    "API key not found. Please provide API key in the UI or set OPENAI_API_KEY in your .env file."
                )
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.model = "openai/gpt-4o-mini"
            self.provider = "OpenAI"
        
        # Initialize LLM using CrewAI's LLM class with API key
        self.llm = LLM(
            model=self.model,
            temperature=0.7,
            api_key=self.api_key
        )
        
        # Initialize agents
        self.article_writer = self._create_article_writer()
        self.keyword_optimizer = self._create_keyword_optimizer()
        self.lsi_optimizer = self._create_lsi_optimizer()
        self.readability_enhancer = self._create_readability_enhancer()
    
    def _create_article_writer(self) -> Agent:
        """Agent responsible for paraphrasing the article with backlinks"""
        return Agent(
            role='Content Paraphrasing & Backlinking Specialist',
            goal='Paraphrase existing articles while naturally incorporating backlinks and maintaining the original structure',
            backstory="""You are an expert content rewriter with years of experience in paraphrasing 
            and SEO content. You excel at taking existing content and rewriting it in a fresh way while 
            maintaining the same meaning, structure, and flow. You seamlessly integrate backlinks in a 
            natural, reader-friendly way without disrupting the content. You preserve the original 
            article's organization, headings, and key points while giving it new words.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_keyword_optimizer(self) -> Agent:
        """Agent responsible for optimizing keyword density"""
        return Agent(
            role='SEO Keyword Optimization Specialist',
            goal='Ensure optimal keyword density (1.5%-3%) throughout the article while maintaining natural flow',
            backstory="""You are an SEO expert specializing in keyword optimization. You have 
            a keen eye for keyword placement and density, ensuring that target keywords appear 
            at the right frequency without over-optimization or keyword stuffing. You understand 
            the balance between SEO requirements and natural language.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_lsi_optimizer(self) -> Agent:
        """Agent responsible for optimizing LSI keyword density"""
        return Agent(
            role='LSI Keyword Integration Expert',
            goal='Integrate LSI keywords at 4-6% density to improve semantic relevance and topical authority',
            backstory="""You are a semantic SEO specialist who understands the importance of 
            Latent Semantic Indexing (LSI) keywords. You excel at naturally weaving related 
            terms and concepts into content to create comprehensive, semantically rich articles 
            that search engines recognize as authoritative.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_readability_enhancer(self) -> Agent:
        """Agent responsible for improving readability"""
        return Agent(
            role='Readability & Clarity Specialist',
            goal='Enhance article readability by ensuring sentences are concise (max 13 words) and easy to understand',
            backstory="""You are a writing coach and editor who specializes in readability 
            optimization. You have mastered the Hemingway writing style - clear, concise, and 
            powerful. You can transform complex sentences into simple, digestible chunks that 
            readers love and that score well on readability tests.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def run(self, input_data: Dict, progress_callback: Optional[Callable] = None) -> Dict:
        """
        Run the complete article generation and optimization workflow
        
        Args:
            input_data: Dictionary containing all input parameters
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Dictionary containing the final article and metrics
        """
        processing_log = []
        
        # Task 1: Paraphrase article with backlinks
        if progress_callback:
            progress_callback("Step 1/4: Paraphrasing article with backlinks...", 25, "Starting article paraphrasing...")
        
        article_generation_task = Task(
            description=f"""
            PARAPHRASE the following article while keeping the EXACT SAME STRUCTURE, flow, and meaning.
            
            ORIGINAL ARTICLE TO PARAPHRASE:
            {input_data['main_article_content']}
            
            REQUIREMENTS:
            1. **DO NOT change the overall structure** - keep the same sections, paragraphs, and flow
            2. **REWORD every sentence** - use different words but maintain the exact same meaning
            3. **Keep the same length** - approximately {input_data['target_word_count']} words
            4. **Naturally embed this main link**: {input_data['main_article_link']}
               - Find a relevant spot in the paraphrased content
               - Use natural anchor text (e.g., "learn more about [topic]", "as discussed in [topic]")
            5. **Include these related links naturally**: {', '.join(input_data['related_links']) if input_data['related_links'] else 'None'}
               - Spread them throughout the article in contextually relevant places
            6. **The primary keyword is**: {input_data['primary_keyword']}
               - Keep it where it naturally appears, don't force it
            
            IMPORTANT: This is a PARAPHRASING task, not a rewriting task. The content structure 
            must remain identical - only the wording should change. If the original has 5 paragraphs, 
            your output should have 5 paragraphs with similar topics.
            
            Return ONLY the paraphrased article content with embedded links.
            """,
            agent=self.article_writer,
            expected_output="A paraphrased article with naturally embedded backlinks"
        )
        
        # Task 2: Optimize keyword density
        keyword_optimization_task = Task(
            description=f"""
            You MUST optimize the article to achieve keyword density between 
            {input_data['keyword_density_range'][0]}% and {input_data['keyword_density_range'][1]}%.
            
            PRIMARY KEYWORD: '{input_data['primary_keyword']}'
            
            STEP 1: Count total words in the article
            STEP 2: Calculate how many times the keyword should appear:
            - For a 1000 word article at 2% density = 20 occurrences
            - Formula: (total_words * target_density) / 100
            
            STEP 3: Strategically add the keyword by:
            - Replacing generic phrases with the keyword
            - Adding it naturally in topic-relevant sentences
            - Using it in transitional phrases
            - Including it in conclusions and introductions
            
            EXAMPLE INSERTIONS:
            - "This is where [PRIMARY_KEYWORD] becomes important..."
            - "Understanding [PRIMARY_KEYWORD] helps..."
            - "When implementing [PRIMARY_KEYWORD]..."
            - "The benefits of [PRIMARY_KEYWORD] include..."
            
            REQUIREMENTS:
            - DO NOT change the overall structure
            - Insert keyword naturally, not forced
            - Maintain readability and flow
            - Keep all backlinks intact
            - MUST achieve target density range
            
            Return the article with the keyword properly distributed throughout.
            """,
            agent=self.keyword_optimizer,
            expected_output="Article with optimized keyword density in target range",
            context=[article_generation_task]
        )
        
        # Task 3: Optimize LSI keywords
        lsi_optimization_task = Task(
            description=f"""
            You MUST integrate LSI keywords to achieve {input_data['lsi_density_range'][0]}% to 
            {input_data['lsi_density_range'][1]}% density.
            
            LSI KEYWORDS: {', '.join(input_data['lsi_keywords'])}
            
            STEP 1: Calculate required occurrences for EACH LSI keyword
            - For 1000 words at 5% total LSI density = 50 total LSI keyword occurrences
            - Distribute evenly across all LSI keywords
            
            STEP 2: Add LSI keywords naturally by:
            - Using them in supporting sentences
            - Integrating them in examples
            - Adding them in explanatory phrases
            - Including them in topic elaborations
            
            EXAMPLE INSERTIONS:
            - "This relates to [LSI_KEYWORD]..."
            - "Consider [LSI_KEYWORD] as well..."
            - "Another aspect involves [LSI_KEYWORD]..."
            - "In terms of [LSI_KEYWORD]..."
            
            REQUIREMENTS:
            - Distribute LSI keywords evenly throughout article
            - Keep natural flow and readability
            - Maintain all backlinks and primary keyword
            - DO NOT change structure
            - MUST hit target density range
            
            Return the article with LSI keywords properly integrated.
            """,
            agent=self.lsi_optimizer,
            expected_output="Article with LSI keywords achieving target density",
            context=[keyword_optimization_task]
        )
        
        # Task 4: Enhance readability
        readability_enhancement_task = Task(
            description=f"""
            Improve the article's readability by ensuring sentences are concise and clear.
            
            Requirements:
            - Maximum {input_data['max_words_per_line']} words per sentence
            - Use simple, clear language
            - Break down complex sentences into shorter ones
            - Maintain active voice where possible
            - Ensure smooth transitions between sentences
            - DO NOT change the overall structure or meaning
            - Preserve all backlinks, keywords, and LSI keywords
            
            The final article should score well on Hemingway readability test.
            
            Return the final, polished article.
            """,
            agent=self.readability_enhancer,
            expected_output="Final article with optimized readability",
            context=[lsi_optimization_task]
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.article_writer,
                self.keyword_optimizer,
                self.lsi_optimizer,
                self.readability_enhancer
            ],
            tasks=[
                article_generation_task,
                keyword_optimization_task,
                lsi_optimization_task,
                readability_enhancement_task
            ],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            # Update progress
            if progress_callback:
                progress_callback("Step 2/4: Optimizing keyword density...", 50, "Starting keyword optimization...")
            
            # Debug mode check
            if input_data.get('debug_mode', False):
                print("DEBUG: Starting CrewAI workflow...")
                print(f"DEBUG: Primary keyword: {input_data['primary_keyword']}")
                print(f"DEBUG: LSI keywords: {input_data['lsi_keywords']}")
                print(f"DEBUG: Article length: {len(input_data['main_article_content'])} characters")
            
            # Execute the workflow
            result = crew.kickoff()
            
            if input_data.get('debug_mode', False):
                print("DEBUG: CrewAI workflow completed successfully")
                print(f"DEBUG: Result type: {type(result)}")
                print(f"DEBUG: Result length: {len(str(result))} characters")
            
            # Update progress
            if progress_callback:
                progress_callback("Step 3/4: Integrating LSI keywords...", 75, "LSI keyword integration completed...")
            
            # Extract final article from result
            final_article = str(result)
            
            # Update progress
            if progress_callback:
                progress_callback("Step 4/4: Finalizing article...", 90, "Finalizing article...")
            
            # Calculate metrics
            metrics = self._calculate_metrics(
                final_article,
                input_data['primary_keyword'],
                input_data['lsi_keywords']
            )
            
            # Create a simple log
            simple_log = f"""
Agent Workflow Completed Successfully!

Step 1: Article Paraphrasing - ✅ Completed
- Paraphrased original content while maintaining structure
- Added backlinks naturally

Step 2: Keyword Optimization - ✅ Completed  
- Optimized keyword density to {metrics['keyword_density']:.2f}%
- Target range: {input_data['keyword_density_range'][0]}% - {input_data['keyword_density_range'][1]}%

Step 3: LSI Integration - ✅ Completed
- Added LSI keywords with {metrics['lsi_density']:.2f}% density
- Target range: {input_data['lsi_density_range'][0]}% - {input_data['lsi_density_range'][1]}%

Step 4: Readability Enhancement - ✅ Completed
- Average words per sentence: {metrics['avg_words_per_sentence']:.1f}
- Target: max {input_data['max_words_per_line']} words per sentence

Final Article Stats:
- Word Count: {metrics['word_count']}
- Keyword Density: {metrics['keyword_density']:.2f}%
- LSI Density: {metrics['lsi_density']:.2f}%
- Readability: {metrics['avg_words_per_sentence']:.1f} words/sentence
"""
            
            if progress_callback:
                progress_callback("✅ Complete! Article generated successfully.", 100, simple_log)
            
            # Return comprehensive result
            return {
                'final_article': final_article,
                'word_count': metrics['word_count'],
                'keyword_density': metrics['keyword_density'],
                'lsi_density': metrics['lsi_density'],
                'avg_words_per_sentence': metrics['avg_words_per_sentence'],
                'keyword_analysis': metrics['keyword_analysis'],
                'lsi_analysis': metrics['lsi_analysis'],
                'readability_metrics': metrics['readability_metrics'],
                'processing_log': processing_log,
                'agent_logs': simple_log
            }
            
        except Exception as e:
            error_msg = f"Error during workflow execution: {str(e)}"
            if progress_callback:
                progress_callback("❌ Error occurred", 0, error_msg)
            raise e
    
    def _calculate_metrics(self, article: str, primary_keyword: str, lsi_keywords: List[str]) -> Dict:
        """Calculate various metrics for the article"""
        
        # Word count
        words = article.split()
        word_count = len(words)
        
        # Keyword density
        keyword_count = article.lower().count(primary_keyword.lower())
        keyword_density = (keyword_count / word_count) * 100 if word_count > 0 else 0
        
        # LSI keyword density
        lsi_count = sum(article.lower().count(lsi.lower()) for lsi in lsi_keywords)
        lsi_density = (lsi_count / word_count) * 100 if word_count > 0 else 0
        
        # Sentence analysis
        sentences = re.split(r'[.!?]+', article)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        sentence_word_counts = [len(s.split()) for s in sentences]
        avg_words_per_sentence = sum(sentence_word_counts) / len(sentence_word_counts) if sentence_word_counts else 0
        
        # Detailed keyword analysis
        keyword_analysis = {
            'primary_keyword': primary_keyword,
            'occurrences': keyword_count,
            'density_percentage': round(keyword_density, 2)
        }
        
        # Detailed LSI analysis
        lsi_analysis = {}
        for lsi in lsi_keywords:
            count = article.lower().count(lsi.lower())
            density = (count / word_count) * 100 if word_count > 0 else 0
            lsi_analysis[lsi] = {
                'occurrences': count,
                'density_percentage': round(density, 2)
            }
        
        # Readability metrics
        readability_metrics = {
            'total_sentences': len(sentences),
            'avg_words_per_sentence': round(avg_words_per_sentence, 2),
            'longest_sentence_words': max(sentence_word_counts) if sentence_word_counts else 0,
            'shortest_sentence_words': min(sentence_word_counts) if sentence_word_counts else 0
        }
        
        return {
            'word_count': word_count,
            'keyword_density': round(keyword_density, 2),
            'lsi_density': round(lsi_density, 2),
            'avg_words_per_sentence': round(avg_words_per_sentence, 2),
            'keyword_analysis': keyword_analysis,
            'lsi_analysis': lsi_analysis,
            'readability_metrics': readability_metrics
        }

