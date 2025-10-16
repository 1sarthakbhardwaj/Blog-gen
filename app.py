import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agents import BacklinkArticleWorkflow
from scraper import scrape_article

# Page configuration
st.set_page_config(
    page_title="Backlink Article Generator",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern CSS Styling
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main container */
    .main {
        padding: 1.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header */
    .main-header {
        text-align: center;
        padding: 1.5rem 1rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        color: white;
    }
    
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }
    
    .main-header p {
        font-size: 1rem;
        margin-top: 0.5rem;
        opacity: 0.9;
        color: white;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.6rem 0;
        margin: 1rem 0 0.8rem 0;
        border-bottom: 2px solid #667eea;
        color: #2d3748;
    }
    
    /* Competitor section */
    .competitor-section {
        background: #f7fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 2rem;
        font-size: 16px;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
        margin-top: 1rem;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Info boxes */
    .info-box {
        background: #e6fffa;
        border-left: 4px solid #38b2ac;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff5f5;
        border-left: 4px solid #f56565;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #f0fff4;
        border-left: 4px solid #48bb78;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #718096;
        font-weight: 500;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Progress bar */
    .stProgress>div>div>div>div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        padding: 10px 20px;
    }
    
    /* Text areas */
    .stTextArea textarea {
        border-radius: 6px;
        border: 2px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 1px #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <h1>🔗 Backlink Article Generator</h1>
        <p>Generate SEO-optimized articles from your content + competitor analysis</p>
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_article' not in st.session_state:
    st.session_state.generated_article = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

# API Configuration Section
st.markdown('<div class="section-header">🔑 API Configuration</div>', unsafe_allow_html=True)

col_api1, col_api2 = st.columns([1, 2])

with col_api1:
    provider = st.radio(
        "Choose AI Provider:",
        ["Google Gemini (Recommended)", "OpenAI", "Groq"],
        horizontal=False,
        help="Gemini 2.0 Flash is optimized for this workflow"
    )

with col_api2:
    # API Key input based on provider
    if provider == "Google Gemini (Recommended)":
        api_key = st.text_input(
            "Google API Key",
            type="password",
            placeholder="AIza...",
            help="Get your API key from https://aistudio.google.com/app/apikey"
        )
        
        # Model selection for Gemini
        gemini_model = st.selectbox(
            "Gemini Model",
            [
                "gemini/gemini-2.0-flash-exp (Recommended - Latest & Fastest)",
                "gemini/gemini-1.5-pro (Most Capable)",
                "gemini/gemini-1.5-flash (Fast & Efficient)"
            ],
            help="Gemini 2.0 Flash Experimental is recommended for best results"
        )
        selected_model = gemini_model.split(" (")[0]
        
    elif provider == "OpenAI":
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-proj-...",
            help="Get your API key from https://platform.openai.com/api-keys"
        )
        
        openai_model = st.selectbox(
            "OpenAI Model",
            [
                "openai/gpt-4o",
                "openai/gpt-4o-mini",
                "openai/gpt-4-turbo"
            ]
        )
        selected_model = openai_model
        
    else:  # Groq
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Get your API key from https://console.groq.com/keys"
        )
        
        groq_model = st.selectbox(
            "Groq Model",
            [
                "groq/llama-3.3-70b-versatile",
                "groq/llama-3.1-8b-instant",
                "groq/mixtral-8x7b-32768"
            ]
        )
        selected_model = groq_model

# Check if API key is provided
if not api_key:
    st.markdown("""
        <div class="warning-box">
            <h3>⚠️ API Key Required</h3>
            <p>Please enter your API key to use the Backlink Article Generator.</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# Store in session state
st.session_state.api_key = api_key
st.session_state.selected_model = selected_model
st.session_state.provider = provider

st.markdown("---")

# Main Input Section
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown('<div class="section-header">📝 Content Inputs</div>', unsafe_allow_html=True)
    
    # Keywords
    st.markdown("**Primary Keyword** *")
    primary_keyword = st.text_input(
        "",
        placeholder="e.g., human pose estimation",
        key="primary_kw",
        help="This keyword will be used in the title and as backlink anchor text"
    )
    
    st.markdown("**Secondary Keywords** (comma-separated)")
    secondary_keywords_input = st.text_area(
        "",
        placeholder="e.g., pose detection, body keypoints, OpenPose alternatives",
        height=80,
        key="secondary_kw",
        help="Related keywords to naturally include in the article"
    )
    secondary_keywords = [kw.strip() for kw in secondary_keywords_input.split(',') if kw.strip()]
    
    st.markdown("---")
    
    # Original Article
    st.markdown("**Original Article (Your Content)** *")
    original_article_url = st.text_input(
        "Article URL",
        placeholder="https://www.labellerr.com/blog/your-article",
        key="original_url",
        help="This link will be embedded in the new article"
    )
    
    original_article_content = st.text_area(
        "Article Content",
        placeholder="Paste your original article content here...",
        height=250,
        key="original_content",
        help="Your article that will be used as the primary source (60-70% weight)"
    )
    
    st.markdown("---")
    
    # Competitor Articles
    st.markdown('<div class="section-header">🎯 Competitor Articles</div>', unsafe_allow_html=True)
    
    # Optional: Auto-scrape toggle (disabled for now)
    enable_scraping = st.checkbox(
        "🔬 Enable automatic content scraping (Experimental)",
        value=False,
        help="Automatically extract content from competitor URLs"
    )
    
    competitor_articles = []
    
    for i in range(1, 4):
        st.markdown(f'<div class="competitor-section"><strong>Competitor {i}</strong></div>', unsafe_allow_html=True)
        
        comp_url = st.text_input(
            f"URL {i}",
            placeholder=f"https://competitor{i}.com/article",
            key=f"comp_url_{i}"
        )
        
        if enable_scraping and comp_url:
            if st.button(f"📥 Scrape Content {i}", key=f"scrape_btn_{i}"):
                with st.spinner(f"Scraping competitor {i}..."):
                    result = scrape_article(comp_url)
                    if result['error']:
                        st.error(f"Error: {result['error']}")
                        st.session_state[f'comp_content_{i}'] = ""
                    else:
                        st.session_state[f'comp_content_{i}'] = result['content']
                        st.success(f"✅ Scraped {len(result['content'])} characters")
        
        comp_content = st.text_area(
            f"Content {i}",
            placeholder=f"Paste competitor {i} article content...",
            height=150,
            key=f"comp_content_{i}",
            value=st.session_state.get(f'comp_content_{i}', '')
        )
        
        competitor_articles.append({'url': comp_url, 'content': comp_content})

with col2:
    st.markdown('<div class="section-header">⚙️ Generation Settings</div>', unsafe_allow_html=True)
    
    target_word_count = st.number_input(
        "Target Word Count",
        min_value=800,
        max_value=5000,
        value=1200,
        step=100,
        help="Minimum word count for the generated article"
    )
    
    labellerr_link = st.text_input(
        "Labellerr AI Link",
        value="https://labellerr.com",
        help="Link to use for Labellerr AI mentions"
    )
    
    labellerr_mention_count = st.slider(
        "Labellerr AI Mentions",
        min_value=3,
        max_value=6,
        value=4,
        help="How many times to naturally mention Labellerr AI"
    )
    
    st.markdown("---")
    
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown(f"""
    **Selected Configuration:**
    - **Model**: {selected_model}
    - **Provider**: {provider}
    - **Target Length**: {target_word_count} words
    - **Brand Mentions**: {labellerr_mention_count}x
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Generate button
    generate_button = st.button(
        "🚀 Generate Backlinked Article",
        disabled=st.session_state.processing,
        type="primary"
    )

# Processing Logic
if generate_button:
    # Validation
    errors = []
    if not primary_keyword:
        errors.append("Primary keyword is required")
    if not original_article_url:
        errors.append("Original article URL is required")
    if not original_article_content:
        errors.append("Original article content is required")
    if not any(comp['content'] for comp in competitor_articles):
        errors.append("At least one competitor article content is required")
    
    if errors:
        st.error("**Please fix the following errors:**")
        for error in errors:
            st.write(f"❌ {error}")
    else:
        st.session_state.processing = True
        
        # Processing UI
        st.markdown("""
            <div class="info-box">
                <h3>🤖 AI Agents Working...</h3>
                <p>The multi-agent workflow is analyzing content and generating your article.</p>
                <p style="margin-top: 0.5rem; font-size: 0.875rem;">
                    <strong>Process:</strong> Content Synthesis → Title Validation → Backlink Validation → 
                    Word Count Check → Readability Optimization → Brand Integration
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize workflow
            workflow = BacklinkArticleWorkflow(
                api_key=st.session_state.api_key,
                model=st.session_state.selected_model,
                provider=st.session_state.provider
            )
            
            # Prepare input data
            input_data = {
                'primary_keyword': primary_keyword,
                'secondary_keywords': secondary_keywords,
                'original_article_url': original_article_url,
                'original_article_content': original_article_content,
                'competitor_articles': competitor_articles,
                'target_word_count': target_word_count,
                'labellerr_link': labellerr_link,
                'labellerr_mention_count': labellerr_mention_count
            }
            
            # Progress callback
            def update_progress(step, progress, log):
                progress_bar.progress(progress / 100)
                status_text.markdown(f"**{step}**\n\n{log}")
            
            # Run the workflow
            result = workflow.run(input_data, progress_callback=update_progress)
            
            st.session_state.generated_article = result
            st.session_state.processing = False
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
            st.markdown("""
                <div class="success-box">
                    <strong>✅ Article Generated Successfully!</strong>
                    <p>Your SEO-optimized article with backlinks is ready.</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Auto-scroll to results
            st.rerun()
            
        except Exception as e:
            st.session_state.processing = False
            st.error(f"❌ An error occurred: {str(e)}")
            if "api" in str(e).lower() or "key" in str(e).lower():
                st.info("💡 Tip: Check your API key and ensure you have sufficient credits")

# Display Results
if st.session_state.generated_article:
    st.markdown("---")
    st.markdown('<div class="section-header">📊 Results</div>', unsafe_allow_html=True)
    
    result = st.session_state.generated_article
    
    # Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{result.get('word_count', 0)}</div>
                <div class="metric-label">Words</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{result.get('sentence_count', 0)}</div>
                <div class="metric-label">Sentences</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{result.get('avg_words_per_sentence', 0):.1f}</div>
                <div class="metric-label">Avg Words/Sentence</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        backlink_color = "#48bb78" if result.get('backlink_status') == "Present" else "#f56565"
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {backlink_color};">
                    {"✓" if result.get('backlink_status') == "Present" else "✗"}
                </div>
                <div class="metric-label">Backlink</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs for Results
    tab1, tab2 = st.tabs(["📝 Final Article", "📊 Validation Summary"])
    
    with tab1:
        st.markdown("### Generated Article")
        
        # Display the article
        article_display = st.text_area(
            "",
            value=result.get('final_article', ''),
            height=600,
            key="final_article_display"
        )
        
        # Download button
        col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 2])
        with col_dl1:
            st.download_button(
                label="📥 Download as TXT",
                data=result.get('final_article', ''),
                file_name=f"article_{primary_keyword.replace(' ', '_')}.txt",
                mime="text/plain"
            )
        
        with col_dl2:
            # Copy to clipboard helper
            st.markdown("""
                <div style="padding: 0.5rem; background: #f7fafc; border-radius: 6px; text-align: center;">
                    <small>Select all (Ctrl/Cmd+A) and copy (Ctrl/Cmd+C)</small>
                </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Validation Summary")
        
        # Display validation summary
        if 'validation_summary' in result:
            st.text_area(
                "",
                value=result['validation_summary'],
                height=400,
                key="validation_display"
            )

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #718096; padding: 1rem;">
        <p><strong>Backlink Article Generator</strong> | Powered by CrewAI & Gemini 2.0 Flash | v2.0</p>
        <p style="font-size: 0.875rem;">Generate SEO-optimized content with natural backlinks and competitor analysis</p>
    </div>
""", unsafe_allow_html=True)
