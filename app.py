import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agents import ArticleWorkflow

# Page configuration
st.set_page_config(
    page_title="AI Article Backlinking Generator",
    page_icon="📝",
    layout="wide"
)

# Minimalist CSS
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    /* Main container */
    .main {
        padding: 2rem;
        background: #f8f9fa;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header */
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0;
    }
    
    .main-header p {
        font-size: 1rem;
        color: #7f8c8d;
        margin-top: 0.5rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.2rem;
        font-weight: 500;
        color: #2c3e50;
        padding: 0.75rem 0;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 2px solid #3498db;
    }
    
    /* Button */
    .stButton>button {
        width: 100%;
        background: #3498db;
        color: white;
        padding: 0.75rem 2rem;
        font-size: 16px;
        font-weight: 500;
        border-radius: 8px;
        border: none;
        transition: background 0.2s ease;
    }
    
    .stButton>button:hover {
        background: #2980b9;
    }
    
    /* Input styling */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stNumberInput>div>div>input {
        border-radius: 6px;
        border: 1px solid #ddd;
        padding: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 1px #3498db;
    }
    
    /* Processing box */
    .processing-box {
        background: #fff;
        border: 2px solid #3498db;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
    
    .processing-box h3 {
        color: #2c3e50;
        margin: 0 0 1rem 0;
    }
    
    .processing-box p {
        color: #7f8c8d;
        margin: 0;
    }
    
    /* Success box */
    .success-box {
        background: #2ecc71;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Warning box */
    .warning-box {
        background: #e74c3c;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e0e0e0;
        margin: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #3498db;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #7f8c8d;
        margin-top: 0.5rem;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Progress bar */
    .stProgress>div>div>div>div {
        background: #3498db;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <h1>AI Article Backlinking Generator</h1>
        <p>Automate content creation with AI-powered SEO optimization</p>
    </div>
""", unsafe_allow_html=True)

# Check for API key with beautiful styling
if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
    st.markdown("""
        <div class="warning-box">
            <h3>⚠️ OpenAI API Key Not Configured</h3>
            <p>Please set your OpenAI API key in the `.env` file:</p>
            <ol>
                <li>Open the `.env` file in the project directory</li>
                <li>Replace `your_openai_api_key_here` with your actual API key</li>
                <li>Get your API key from: <a href="https://platform.openai.com/api-keys" style="color: white; text-decoration: underline;">https://platform.openai.com/api-keys</a></li>
                <li>Save the file and refresh this page</li>
            </ol>
            <p><strong>Example:</strong><br>
            <code>OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx</code></p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown("---")

# Initialize session state
if 'generated_article' not in st.session_state:
    st.session_state.generated_article = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Create two columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="section-header">📝 Content Input</div>', unsafe_allow_html=True)
    
    # Keyword Input
    st.markdown("**Primary Keyword**")
    primary_keyword = st.text_input(
        "",
        placeholder="e.g., digital marketing strategies",
        key="primary_kw"
    )
    
    # LSI Keywords
    st.markdown("**LSI Keywords**")
    num_lsi = st.number_input("Number of LSI keywords", min_value=1, max_value=10, value=3)
    lsi_keywords = []
    for i in range(num_lsi):
        lsi = st.text_input(f"LSI Keyword {i+1}", key=f"lsi_{i}", placeholder=f"e.g., SEO optimization")
        if lsi:
            lsi_keywords.append(lsi)
    
    # Main Article Content
    st.markdown("**Main Article Content**")
    main_article_content = st.text_area(
        "",
        height=200,
        placeholder="Paste your article content here...",
        key="main_content"
    )
    
    # Main Article Link
    st.markdown("**Main Article Link**")
    main_article_link = st.text_input(
        "",
        placeholder="https://example.com/main-article",
        key="main_link"
    )
    
    # Related Links
    st.markdown("**Related Links**")
    num_links = st.number_input("Number of related links", min_value=0, max_value=10, value=2)
    related_links = []
    for i in range(num_links):
        link = st.text_input(f"Link {i+1}", key=f"link_{i}", placeholder="https://example.com/related")
        if link:
            related_links.append(link)

with col2:
    st.markdown('<div class="section-header">⚙️ Generation Settings</div>', unsafe_allow_html=True)
    
    # Target metrics
    st.markdown("**Keyword Density Range (%)**")
    col_a, col_b = st.columns(2)
    with col_a:
        keyword_density_min = st.number_input("Min", 0.0, 5.0, 1.5, 0.1, key="kw_min")
    with col_b:
        keyword_density_max = st.number_input("Max", 0.0, 5.0, 3.0, 0.1, key="kw_max")
    
    st.markdown("**LSI Density Range (%)**")
    col_c, col_d = st.columns(2)
    with col_c:
        lsi_density_min = st.number_input("Min", 0.0, 10.0, 4.0, 0.5, key="lsi_min")
    with col_d:
        lsi_density_max = st.number_input("Max", 0.0, 10.0, 6.0, 0.5, key="lsi_max")
    
    st.markdown("**Readability**")
    max_words_per_line = st.slider("Max words per sentence", 5, 20, 13, 1)
    
    st.markdown("**Article Length**")
    target_word_count = st.number_input("Target word count", min_value=300, max_value=5000, value=1000, step=100)
    
    st.markdown("**Debug**")
    debug_mode = st.checkbox("Enable debug mode", value=False)
    
    st.markdown("---")
    
    # Generate button
    generate_button = st.button("🚀 Generate Article", disabled=st.session_state.processing)

# Processing and Results
if generate_button:
    # Validation
    errors = []
    if not primary_keyword:
        errors.append("Primary keyword is required")
    if not lsi_keywords:
        errors.append("At least one LSI keyword is required")
    if not main_article_content:
        errors.append("Main article content is required")
    if not main_article_link:
        errors.append("Main article link is required")
    
    if errors:
        st.error("Please fix the following errors:")
        for error in errors:
            st.write(f"- {error}")
    else:
        st.session_state.processing = True
        
        # Simple processing message
        st.markdown("""
            <div class="processing-box">
                <h3>🤖 AI Crew is Working...</h3>
                <p>Please wait approximately 3-5 minutes while our AI agents optimize your article.</p>
                <p style="margin-top: 1rem; font-size: 0.875rem;">The agents are paraphrasing, adding keywords, and optimizing readability.</p>
            </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        
        try:
            # Initialize workflow
            workflow = ArticleWorkflow()
            
            # Prepare input data
            input_data = {
                'primary_keyword': primary_keyword,
                'lsi_keywords': lsi_keywords,
                'main_article_content': main_article_content,
                'main_article_link': main_article_link,
                'related_links': related_links,
                'keyword_density_range': (keyword_density_min, keyword_density_max),
                'lsi_density_range': (lsi_density_min, lsi_density_max),
                'max_words_per_line': max_words_per_line,
                'target_word_count': target_word_count,
                'debug_mode': debug_mode
            }
            
            # Simple progress callback
            def update_progress(step, progress, agent_log):
                progress_bar.progress(progress)
            
            # Run the workflow
            result = workflow.run(input_data, progress_callback=update_progress)
            
            st.session_state.generated_article = result
            st.session_state.processing = False
            
            # Clear progress
            progress_bar.empty()
            
            st.markdown("""
                <div class="success-box">
                    <strong>✅ Article Generated Successfully!</strong>
                </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.session_state.processing = False
            st.error(f"❌ An error occurred: {str(e)}")
            st.exception(e)

# Display results
if st.session_state.generated_article:
    st.markdown("---")
    st.markdown('<div class="section-header">Generated Article</div>', unsafe_allow_html=True)
    
    result = st.session_state.generated_article
    
    # Beautiful metrics cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{result.get('word_count', 'N/A')}</div>
                <div class="metric-label">Word Count</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{result.get('keyword_density', 0):.2f}%</div>
                <div class="metric-label">Keyword Density</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{result.get('lsi_density', 0):.2f}%</div>
                <div class="metric-label">LSI Density</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{result.get('avg_words_per_sentence', 0):.1f}</div>
                <div class="metric-label">Avg Words/Sentence</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📝 Final Article", "📊 Analysis", "🔍 Details"])
    
    with tab1:
        st.markdown("### Final Optimized Article")
        st.text_area("", value=result.get('final_article', ''), height=500, key="final_output")
        
        # Download button
        st.download_button(
            label="📥 Download Article",
            data=result.get('final_article', ''),
            file_name=f"article_{primary_keyword.replace(' ', '_')}.txt",
            mime="text/plain"
        )
    
    with tab2:
        st.markdown("### Keyword Analysis")
        if 'keyword_analysis' in result:
            st.json(result['keyword_analysis'])
        
        st.markdown("### LSI Analysis")
        if 'lsi_analysis' in result:
            st.json(result['lsi_analysis'])
        
        st.markdown("### Readability Metrics")
        if 'readability_metrics' in result:
            st.json(result['readability_metrics'])
    
    with tab3:
        st.markdown("### Links Embedded")
        st.write(f"- **Main Article Link**: {main_article_link}")
        if related_links:
            st.write("- **Related Links**:")
            for link in related_links:
                st.write(f"  - {link}")
        
        st.markdown("### Agent Activity Logs")
        if 'agent_logs' in result:
            st.text_area("Complete Agent Logs", value=result['agent_logs'], height=400)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #7f8c8d; padding: 1rem;">
        <p>Powered by CrewAI & Streamlit | v1.0</p>
    </div>
""", unsafe_allow_html=True)

