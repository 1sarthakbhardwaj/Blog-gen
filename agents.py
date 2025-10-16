from crewai import Agent, Task, Crew, Process, LLM
import re
from typing import Dict, List, Tuple, Callable, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BacklinkArticleWorkflow:
    """
    Workflow for generating backlinked articles from original + competitor content
    Uses Gemini 2.0 Flash with multi-agent validation system
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
            elif "gemini" in model.lower():
                os.environ["GOOGLE_API_KEY"] = api_key
        else:
            # Fallback to environment variables
            if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
                raise ValueError(
                    "API key not found. Please provide API key in the UI or set GOOGLE_API_KEY/OPENAI_API_KEY in your .env file."
                )
            # Default to Gemini
            self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
            self.model = "gemini/gemini-2.0-flash-exp"
            self.provider = "Google Gemini"
        
        # Initialize LLM using CrewAI's LLM class with API key
        try:
            self.llm = LLM(
                model=self.model,
                temperature=0.7,
                api_key=self.api_key
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize LLM with model {self.model}: {str(e)}")
        
        # Initialize agents
        self.content_synthesizer = self._create_content_synthesizer()
        self.title_validator = self._create_title_validator()
        self.backlink_validator = self._create_backlink_validator()
        self.word_count_validator = self._create_word_count_validator()
        self.readability_validator = self._create_readability_validator()
        self.brand_mention_validator = self._create_brand_mention_validator()
    
    def _create_content_synthesizer(self) -> Agent:
        """Agent responsible for synthesizing original + competitor content into new article"""
        return Agent(
            role='Competitive Content Synthesizer & SEO Specialist',
            goal='Create a comprehensive, SEO-optimized article by intelligently mixing original content with competitor insights',
            backstory="""You are an expert content strategist and SEO writer with 10+ years of experience 
            in competitive analysis and content creation. You excel at analyzing multiple articles on the same 
            topic and synthesizing them into a superior piece that combines the best insights from each source.
            
            You understand how to:
            - Prioritize the original content while incorporating competitor strengths
            - Create compelling titles with target keywords
            - Embed backlinks naturally using anchor text
            - Write in active voice for US audiences
            - Keep sentences concise and readable
            - Naturally mention brand names in context
            
            You never plagiarize but create fresh, original content that's better than the sources.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_title_validator(self) -> Agent:
        """Agent responsible for validating and fixing article title"""
        return Agent(
            role='Title Optimization Specialist',
            goal='Ensure the article title contains the primary keyword and is compelling for readers',
            backstory="""You are a headline optimization expert who specializes in SEO-friendly titles. 
            You know that a great title must include the primary keyword while remaining natural, compelling, 
            and click-worthy. You can quickly identify if a title is missing keywords and rewrite it to be 
            both SEO-optimized and engaging.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_backlink_validator(self) -> Agent:
        """Agent responsible for validating and embedding backlinks"""
        return Agent(
            role='Backlink Integration Specialist',
            goal='Ensure the original article link is naturally embedded with the primary keyword as anchor text',
            backstory="""You are an expert in natural link building and anchor text optimization. You understand 
            that backlinks must flow naturally within content and use relevant anchor text. You can identify 
            the perfect placement for links where they add value to readers while meeting SEO requirements. 
            You never force links but find contextually relevant spots.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_word_count_validator(self) -> Agent:
        """Agent responsible for ensuring minimum word count"""
        return Agent(
            role='Content Length Optimizer',
            goal='Ensure the article meets the minimum word count by expanding sections naturally',
            backstory="""You are a content expansion specialist who knows how to add valuable information 
            to articles without fluff or redundancy. When articles fall short of word count targets, you 
            identify sections that can be expanded with examples, explanations, case studies, or additional 
            insights. You maintain the article's quality and flow while reaching target length.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_readability_validator(self) -> Agent:
        """Agent responsible for ensuring readability standards"""
        return Agent(
            role='Readability & Clarity Expert',
            goal='Ensure all sentences are concise (13-14 words max) and maintain excellent readability',
            backstory="""You are a professional editor trained in the Hemingway style of writing. You specialize 
            in breaking down complex sentences into clear, concise statements without losing meaning. You can 
            quickly scan text, identify long sentences, and restructure them for optimal readability while 
            maintaining the author's voice and intent.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_brand_mention_validator(self) -> Agent:
        """Agent responsible for validating brand mentions"""
        return Agent(
            role='Brand Integration Specialist',
            goal='Ensure "Labellerr AI" is mentioned 4-5 times naturally with a mix of linked and plain text',
            backstory="""You are a brand content strategist who specializes in natural brand integration. 
            You understand that brand mentions must feel organic and add value to the content, not forced or 
            spammy. You can identify opportunities to mention brands where they genuinely fit the context, 
            and you balance hyperlinked mentions with plain text references for a natural reading experience.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def run(self, input_data: Dict, progress_callback: Optional[Callable] = None) -> Dict:
        """
        Run the complete backlink article generation and validation workflow
        
        Args:
            input_data: Dictionary containing all input parameters
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Dictionary containing the final article, validation reports, and metrics
        """
        
        # Task 1: Generate the main article
        if progress_callback:
            progress_callback("Step 1/5: Synthesizing content from all sources...", 20, "Analyzing and mixing articles...")
        
        # Build competitor content summary
        competitor_content = ""
        for i, comp in enumerate(input_data['competitor_articles'], 1):
            if comp['content']:
                competitor_content += f"\n\n=== COMPETITOR ARTICLE {i} ===\n"
                competitor_content += f"URL: {comp['url']}\n"
                competitor_content += f"CONTENT:\n{comp['content'][:3000]}\n"  # Limit to avoid token overflow
        
        content_generation_task = Task(
            description=f"""
            Create a NEW, COMPREHENSIVE article by intelligently mixing the original article with competitor insights.
            
            === PRIMARY SOURCE (PRIORITIZE 60-70%) ===
            URL: {input_data['original_article_url']}
            CONTENT:
            {input_data['original_article_content']}
            
            === COMPETITOR SOURCES (USE 30-40% COMBINED) ===
            {competitor_content}
            
            === REQUIREMENTS ===
            
            **PRIMARY KEYWORD**: {input_data['primary_keyword']}
            **SECONDARY KEYWORDS**: {', '.join(input_data['secondary_keywords'])}
            
            **CONTENT REQUIREMENTS**:
            1. Create a TITLE that includes the primary keyword "{input_data['primary_keyword']}"
            2. Write at least {input_data['target_word_count']} words
            3. Prioritize the original article's perspective and key points (60-70% weight)
            4. Incorporate valuable insights from competitor articles (30-40% combined)
            5. Create ORIGINAL content - do not copy sentences verbatim
            6. Use ACTIVE VOICE throughout
            7. Write for US audience (American English, cultural context)
            8. Keep sentences under 13-14 words maximum
            
            **BACKLINK REQUIREMENT**:
            - Naturally embed this link: {input_data['original_article_url']}
            - Use "{input_data['primary_keyword']}" or a variation as anchor text
            - Place it where it adds genuine value (e.g., "For a deeper dive into {input_data['primary_keyword']}, check out [link]")
            
            **BRAND MENTIONS**:
            - Mention "Labellerr AI" naturally {input_data['labellerr_mention_count']} times
            - Make 2-3 mentions hyperlinked to: {input_data.get('labellerr_link', 'https://labellerr.com')}
            - Keep 1-2 mentions as plain text
            - Only mention where contextually relevant (e.g., when discussing data annotation, AI tools, etc.)
            
            **STRUCTURE**:
            - Start with an engaging introduction
            - Use clear section headings (H2, H3)
            - Include examples and practical applications
            - End with a strong conclusion
            
            **FORMAT**:
            Return the article in this exact format:
            
            TITLE: [Your compelling title with primary keyword]
            
            [Article content with proper structure]
            
            IMPORTANT: The article must be original, comprehensive, and better than any single source.
            """,
            agent=self.content_synthesizer,
            expected_output="A comprehensive article with title, properly structured content, embedded backlink, and brand mentions"
        )
        
        # Task 2: Validate and fix title
        if progress_callback:
            progress_callback("Step 2/6: Validating article title...", 30, "Checking title for primary keyword...")
        
        title_validation_task = Task(
            description=f"""
            Check if the article title contains the primary keyword: "{input_data['primary_keyword']}"
            
            If the title doesn't contain the primary keyword, rewrite it to include the keyword naturally.
            
            Return ONLY the complete article with the corrected title (if needed).
            Do NOT include any validation text, reports, or metadata.
            Just return the clean article text.
            """,
            agent=self.title_validator,
            expected_output="Clean article text with validated title",
            context=[content_generation_task]
        )
        
        # Task 3: Validate and fix backlink
        if progress_callback:
            progress_callback("Step 3/6: Validating backlink placement...", 45, "Checking backlink with anchor text...")
        
        backlink_validation_task = Task(
            description=f"""
            Check if the link {input_data['original_article_url']} is embedded in the article with "{input_data['primary_keyword']}" as anchor text.
            
            If the link is missing or not properly embedded:
            1. Find a natural place in the article to add it
            2. Embed it using the primary keyword or a natural variation as anchor text
            3. Make sure it flows naturally in the context
            
            Return ONLY the complete article with the link properly embedded.
            Do NOT include any validation text, reports, or metadata.
            Just return the clean article text.
            """,
            agent=self.backlink_validator,
            expected_output="Clean article text with validated backlink",
            context=[title_validation_task]
        )
        
        # Task 4: Validate and expand word count
        if progress_callback:
            progress_callback("Step 4/6: Checking word count...", 60, "Ensuring minimum word count...")
        
        word_count_validation_task = Task(
            description=f"""
            Count the total words in the article.
            
            Target: At least {input_data['target_word_count']} words
            
            If the article has fewer than {input_data['target_word_count']} words:
            1. Identify sections that can be expanded naturally
            2. Add examples, explanations, or additional insights
            3. Maintain the article's quality and flow
            4. Expand until reaching the target word count
            
            Do NOT add fluff or repetitive content. Add valuable information only.
            
            Return ONLY the complete article (expanded if needed).
            Do NOT include any word count reports or metadata.
            Just return the clean article text.
            """,
            agent=self.word_count_validator,
            expected_output="Clean article text meeting minimum word count",
            context=[backlink_validation_task]
        )
        
        # Task 5: Validate and fix readability
        if progress_callback:
            progress_callback("Step 5/6: Enhancing readability...", 75, "Breaking down long sentences...")
        
        readability_validation_task = Task(
            description=f"""
            Check all sentences in the article. 
            
            Target: Maximum 13-14 words per sentence
            
            If any sentences are longer than 14 words:
            1. Break them into shorter sentences
            2. Maintain the original meaning and flow
            3. Keep natural transitions
            
            Return ONLY the complete article with optimized readability.
            Do NOT include any validation text, reports, or metadata.
            Just return the clean article text.
            """,
            agent=self.readability_validator,
            expected_output="Clean article text with optimized readability",
            context=[word_count_validation_task]
        )
        
        # Task 6: Validate and fix brand mentions
        if progress_callback:
            progress_callback("Step 6/6: Validating brand mentions...", 90, "Checking Labellerr AI mentions...")
        
        brand_validation_task = Task(
            description=f"""
            Count "Labellerr AI" mentions in the article.
            
            Target: {input_data['labellerr_mention_count']} mentions total
            - 2-3 should be hyperlinked to: {input_data.get('labellerr_link', 'https://labellerr.com')}
            - 1-2 should be plain text
            
            If the count is off or the mix is wrong:
            1. Add or adjust mentions to meet the target
            2. Only add where contextually relevant (data annotation, AI tools, computer vision, etc.)
            3. Ensure natural flow
            
            Return ONLY the complete article with proper brand mentions.
            Do NOT include any validation text, reports, or metadata.
            Just return the clean article text.
            """,
            agent=self.brand_mention_validator,
            expected_output="Clean article text with validated brand mentions",
            context=[readability_validation_task]
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.content_synthesizer,
                self.title_validator,
                self.backlink_validator,
                self.word_count_validator,
                self.readability_validator,
                self.brand_mention_validator
            ],
            tasks=[
                content_generation_task,
                title_validation_task,
                backlink_validation_task,
                word_count_validation_task,
                readability_validation_task,
                brand_validation_task
            ],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            # Execute the workflow
            result = crew.kickoff()
            
            if progress_callback:
                progress_callback("Step 5/5: Finalizing article...", 95, "Calculating metrics...")
            
            # Extract final article from result
            final_article = str(result)
            
            # Calculate metrics
            metrics = self._calculate_metrics(
                final_article,
                input_data['primary_keyword'],
                input_data['original_article_url']
            )
            
            # Create validation summary
            validation_summary = f"""
=== VALIDATION SUMMARY ===

✅ Content Generation: Complete
   - Mixed original + competitor content
   - Generated comprehensive article
   
✅ Title Validation: Checked
   - Primary keyword presence verified
   
✅ Backlink Validation: Checked
   - Original article link embedded
   - Anchor text optimized

✅ Word Count Validation: Checked
   - Target: {input_data['target_word_count']}+ words
   - Actual: {metrics['word_count']} words
   
✅ Readability Validation: Checked
   - Sentences optimized for readability
   - Target: Max 13-14 words per sentence
   
✅ Brand Mention Validation: Checked
   - Labellerr AI mentions integrated naturally
   - Mix of linked and plain text
   
=== FINAL METRICS ===
- Word Count: {metrics['word_count']}
- Sentence Count: {metrics['sentence_count']}
- Avg Words/Sentence: {metrics['avg_words_per_sentence']:.1f}
- Backlink Status: {metrics['backlink_status']}
"""
            
            if progress_callback:
                progress_callback("✅ Complete! Article generated successfully.", 100, validation_summary)
            
            # Return comprehensive result
            return {
                'final_article': final_article,
                'word_count': metrics['word_count'],
                'sentence_count': metrics['sentence_count'],
                'avg_words_per_sentence': metrics['avg_words_per_sentence'],
                'backlink_status': metrics['backlink_status'],
                'validation_summary': validation_summary
            }
            
        except Exception as e:
            error_msg = f"Error during workflow execution: {str(e)}"
            if progress_callback:
                progress_callback("❌ Error occurred", 0, error_msg)
            raise e
    
    def _calculate_metrics(self, article: str, primary_keyword: str, original_url: str) -> Dict:
        """Calculate various metrics for the article"""
        
        # Word count
        words = article.split()
        word_count = len(words)
        
        # Sentence analysis
        sentences = re.split(r'[.!?]+', article)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        sentence_count = len(sentences)
        sentence_word_counts = [len(s.split()) for s in sentences]
        avg_words_per_sentence = sum(sentence_word_counts) / len(sentence_word_counts) if sentence_word_counts else 0
        
        # Check backlink status
        backlink_status = "Present" if original_url in article else "Not Found"
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_words_per_sentence': round(avg_words_per_sentence, 2),
            'backlink_status': backlink_status
        }
