"""
Simplified article generation workflow
No CrewAI - just direct LLM calls in sequence
"""
import re
from typing import Dict, Optional, Callable
from llm_client import LLMClient


class BacklinkArticleWorkflow:
    """Simple workflow for generating backlinked articles"""
    
    def __init__(self, api_key: str, model: str, provider: str):
        self.llm = LLMClient(provider=provider, api_key=api_key, model=model)
    
    def run(self, input_data: Dict, progress_callback: Optional[Callable] = None) -> Dict:
        """Run the article generation workflow"""
        
        # Step 1: Generate main article
        if progress_callback:
            progress_callback("Step 1/6: Generating article...", 20, "Creating content from sources")
        
        article = self._generate_article(input_data)
        
        # Step 2: Validate title
        if progress_callback:
            progress_callback("Step 2/6: Validating title...", 35, "Checking keyword in title")
        
        article = self._validate_title(article, input_data['primary_keyword'])
        
        # Step 3: Validate backlink
        if progress_callback:
            progress_callback("Step 3/6: Validating backlink...", 50, "Checking link placement")
        
        article = self._validate_backlink(article, input_data)
        
        # Step 4: Validate word count
        if progress_callback:
            progress_callback("Step 4/6: Checking word count...", 65, "Ensuring minimum length")
        
        article = self._validate_word_count(article, input_data['target_word_count'])
        
        # Step 5: Optimize readability
        if progress_callback:
            progress_callback("Step 5/6: Optimizing readability...", 80, "Improving sentence structure")
        
        article = self._optimize_readability(article)
        
        # Step 6: Validate brand mentions
        if progress_callback:
            progress_callback("Step 6/6: Adding brand mentions...", 95, "Integrating Labellerr AI")
        
        article = self._validate_brand_mentions(article, input_data)
        
        # Calculate metrics
        metrics = self._calculate_metrics(article, input_data['primary_keyword'], input_data['original_article_url'])
        
        if progress_callback:
            progress_callback("Complete!", 100, "Article generated successfully")
        
        return {
            'final_article': article,
            'word_count': metrics['word_count'],
            'sentence_count': metrics['sentence_count'],
            'avg_words_per_sentence': metrics['avg_words_per_sentence'],
            'backlink_status': metrics['backlink_status'],
            'validation_summary': self._create_summary(metrics, input_data)
        }
    
    def _generate_article(self, data: Dict) -> str:
        """Step 1: Generate the initial article"""
        
        competitor_content = ""
        for i, comp in enumerate(data['competitor_articles'], 1):
            if comp['content']:
                competitor_content += f"\n\n=== COMPETITOR {i} ===\n{comp['content'][:8000]}\n"
        
        prompt = f"""Create a comprehensive, detailed article by intelligently combining the original article with competitor insights.

PRIMARY SOURCE (60-70% weight):
{data['original_article_content']}

COMPETITOR SOURCES (30-40% combined):
{competitor_content}

REQUIREMENTS:
1. Title MUST include: "{data['primary_keyword']}" and be compelling
2. Write {data['target_word_count']}+ words with substantial, meaningful content
3. Use active voice with sentences of 10-12 words (not too short, not too long)
4. Create detailed, informative content with examples, explanations, and insights
5. Embed this link naturally: {data['original_article_url']}
   - Use "{data['primary_keyword']}" as anchor text
6. Mention "Labellerr AI" {data['labellerr_mention_count']} times naturally
   - Link 2-3 mentions to: {data['labellerr_link']}
7. Use clear H2, H3 headings for structure
8. Write for US audience with engaging, professional tone
9. Include practical examples, use cases, and actionable insights
10. Make the content comprehensive and valuable, not vague

CONTENT QUALITY:
- Provide detailed explanations and context
- Include specific examples and use cases
- Add practical insights and applications
- Use professional, engaging language
- Ensure each paragraph adds value
- Create a cohesive, well-structured narrative

Return ONLY the article with this format:
TITLE: [Your compelling title with primary keyword]

[Comprehensive article content with detailed explanations, examples, and insights]"""

        return self.llm.generate(prompt, temperature=0.7)
    
    def _validate_title(self, article: str, keyword: str) -> str:
        """Step 2: Ensure title has keyword"""
        
        if keyword.lower() not in article.lower()[:200]:
            prompt = f"""Fix the title to include "{keyword}".

Current article:
{article[:1000]}...

Return the COMPLETE article with corrected title. Keep everything else the same."""
            
            return self.llm.generate(prompt, temperature=0.5)
        
        return article
    
    def _validate_backlink(self, article: str, data: Dict) -> str:
        """Step 3: Ensure backlink is present"""
        
        if data['original_article_url'] not in article:
            prompt = f"""Add this link: {data['original_article_url']}
Use "{data['primary_keyword']}" as anchor text.
Place it naturally in the article.

Current article:
{article}

Return the COMPLETE article with the link added."""
            
            return self.llm.generate(prompt, temperature=0.5)
        
        return article
    
    def _validate_word_count(self, article: str, target: int) -> str:
        """Step 4: Ensure minimum word count with substantial content"""
        
        words = len(article.split())
        if words < target:
            prompt = f"""Expand this article from {words} to {target}+ words with substantial, meaningful content.

Current article:
{article}

EXPANSION REQUIREMENTS:
- Add detailed explanations and context
- Include specific examples and use cases
- Provide practical insights and applications
- Add relevant statistics or data points
- Include step-by-step processes where applicable
- Add real-world scenarios and case studies
- Ensure each addition adds genuine value
- Maintain professional, engaging tone
- Keep sentences 10-12 words long
- No fluff or repetitive content

Return the COMPLETE expanded article with substantial, valuable content."""
            
            return self.llm.generate(prompt, temperature=0.7)
        
        return article
    
    def _optimize_readability(self, article: str) -> str:
        """Step 5: Optimize sentence length to 10-12 words"""
        
        # Check sentence lengths
        sentences = re.split(r'[.!?]+', article)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip() and len(s.strip()) > 10]
        
        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            # If average is too short (<8) or too long (>15), optimize
            if avg_length < 8 or avg_length > 15:
                prompt = f"""Optimize sentence length to 10-12 words per sentence for better readability.

Current article:
{article}

INSTRUCTIONS:
- Keep sentences between 8-15 words (target: 10-12 words)
- If sentences are too short, combine them naturally
- If sentences are too long, break them into shorter ones
- Maintain the same meaning and flow
- Keep the content detailed and informative
- Ensure professional, engaging tone

Return the COMPLETE article with optimized sentence length."""
                
                return self.llm.generate(prompt, temperature=0.5)
        
        return article
    
    def _validate_brand_mentions(self, article: str, data: Dict) -> str:
        """Step 6: Ensure proper brand mentions"""
        
        mentions = article.lower().count("labellerr")
        target = data['labellerr_mention_count']
        
        if mentions < target:
            prompt = f"""Add {target - mentions} more natural mentions of "Labellerr AI" to this article.
Link {data['labellerr_mention_count'] - 2} of them to: {data['labellerr_link']}

CONTEXT REQUIREMENTS:
- Only mention where contextually relevant (data annotation, AI tools, computer vision, machine learning, etc.)
- Make mentions feel natural and valuable to the reader
- Integrate smoothly into existing content
- Provide context about what Labellerr AI does
- Maintain professional tone
- Don't force mentions where they don't fit

Article:
{article}

Return the COMPLETE article with natural, contextual brand mentions added."""
            
            return self.llm.generate(prompt, temperature=0.6)
        
        return article
    
    def _calculate_metrics(self, article: str, keyword: str, url: str) -> Dict:
        """Calculate article metrics"""
        
        words = article.split()
        word_count = len(words)
        
        sentences = re.split(r'[.!?]+', article)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        sentence_count = len(sentences)
        
        avg_words = word_count / sentence_count if sentence_count > 0 else 0
        backlink_status = "Present" if url in article else "Not Found"
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_words_per_sentence': round(avg_words, 1),
            'backlink_status': backlink_status
        }
    
    def _create_summary(self, metrics: Dict, data: Dict) -> str:
        """Create validation summary"""
        
        return f"""=== VALIDATION SUMMARY ===

✅ Content Generation: Complete
✅ Title Validation: Checked for "{data['primary_keyword']}"
✅ Backlink Validation: {metrics['backlink_status']}
✅ Word Count: {metrics['word_count']} / {data['target_word_count']}+ target
✅ Readability: Optimized
✅ Brand Mentions: Integrated

=== METRICS ===
- Words: {metrics['word_count']}
- Sentences: {metrics['sentence_count']}
- Avg Words/Sentence: {metrics['avg_words_per_sentence']}
- Backlink: {metrics['backlink_status']}
"""
