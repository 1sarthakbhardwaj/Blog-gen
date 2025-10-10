# 📝 AI Article Backlinking Generator

A powerful Streamlit application powered by CrewAI that automates the creation of SEO-optimized articles with natural backlinking, keyword optimization, and enhanced readability.

## 🌟 Features

- **Intelligent Article Generation**: Creates unique articles similar to your reference content
- **Natural Backlink Integration**: Seamlessly embeds your main article link and related links
- **Keyword Optimization**: Maintains optimal keyword density (1.5% - 3%)
- **LSI Keyword Integration**: Adds semantic keywords at 4-6% density
- **Readability Enhancement**: Ensures sentences are concise (max 13 words) for Hemingway test
- **Real-time Metrics**: Tracks word count, keyword density, and readability scores
- **Multi-Agent Workflow**: Uses specialized AI agents for each optimization task

## 🤖 AI Agents

The application uses 4 specialized CrewAI agents:

1. **Content Writer & Backlinking Specialist**: Generates the initial article with naturally embedded backlinks
2. **SEO Keyword Optimization Specialist**: Optimizes primary keyword density
3. **LSI Keyword Integration Expert**: Integrates semantic keywords for topical authority
4. **Readability & Clarity Specialist**: Enhances readability with concise sentences

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (or other LLM provider)

### Quick Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the setup script:
```bash
python setup.py
```
   The setup script will guide you through creating the `.env` file and verifying dependencies.

### Manual Setup

Alternatively, you can set up manually:

1. Create a `.env` file in the project root:
```bash
touch .env
```

2. Open `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

3. Get your API key from: https://platform.openai.com/api-keys

## 💻 Usage

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser (usually automatically opens to `http://localhost:8501`)

3. Fill in the input form:
   - **Primary Keyword**: Your main business unit keyword
   - **LSI Keywords**: Add related semantic keywords
   - **Main Article Content**: Paste reference content for style/structure
   - **Main Article Link**: The primary link to backlink
   - **Related Links**: Additional links to embed naturally

4. Configure generation settings:
   - Keyword density range (default: 1.5% - 3%)
   - LSI density range (default: 4% - 6%)
   - Max words per sentence (default: 13)
   - Target word count

5. Click "🚀 Generate Article" and wait for the AI agents to work

6. Review the generated article with metrics and download if satisfied

## 📊 Output Metrics

The app provides comprehensive metrics:

- **Word Count**: Total words in the article
- **Keyword Density**: Percentage of primary keyword usage
- **LSI Density**: Percentage of LSI keyword usage
- **Avg Words/Sentence**: Average sentence length for readability
- **Detailed Analysis**: Per-keyword occurrence and density
- **Readability Metrics**: Sentence statistics for Hemingway test

## 🔧 Configuration

### Using Different LLM Models

By default, the app uses OpenAI's GPT-4o-mini. To change the model, edit `agents.py`:

```python
self.llm = LLM(
    model="openai/gpt-4",  # or "openai/gpt-3.5-turbo", etc.
    temperature=0.7
)
```

### For Other LLM Providers

CrewAI supports multiple providers. You can use Anthropic Claude, Google Gemini, or others:

```python
# Anthropic Claude
self.llm = LLM(
    model="anthropic/claude-3-opus-20240229",
    temperature=0.7
)

# Google Gemini
self.llm = LLM(
    model="gemini/gemini-pro",
    temperature=0.7
)

# Ollama (local)
self.llm = LLM(
    model="ollama/llama2",
    temperature=0.7
)
```

## 📝 Workflow Process

1. **Article Generation**: Creates base article with embedded backlinks
2. **Keyword Optimization**: Adjusts primary keyword density to target range
3. **LSI Integration**: Adds semantic keywords throughout the content
4. **Readability Enhancement**: Shortens sentences and improves clarity

All steps are performed sequentially by specialized AI agents.

## 🎯 Best Practices

- **Reference Content**: Provide high-quality reference content for best results
- **Keyword Selection**: Choose relevant, specific keywords
- **LSI Keywords**: Use semantically related terms, not just synonyms
- **Link Relevance**: Ensure backlinks are contextually relevant
- **Review Output**: Always review and edit the generated content before publishing

## 🐛 Troubleshooting

### API Key Errors
- Ensure your `.env` file contains a valid `OPENAI_API_KEY`
- Check that the key has sufficient credits

### Generation Errors
- Verify all required fields are filled
- Check your internet connection
- Ensure the API service is available

### Performance Issues
- Longer articles take more time to generate
- Complex optimizations may require multiple iterations
- Consider using faster models like GPT-3.5-turbo for testing

## 📄 License

This project is open-source and available for personal and commercial use.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 💡 Tips

- Start with shorter articles (500-1000 words) for faster results
- Use the analysis tab to understand keyword distribution
- Adjust density ranges based on your SEO strategy
- Test generated content with actual Hemingway Editor for validation

## 📞 Support

For issues or questions, please check the troubleshooting section or review the code comments for detailed implementation notes.

---

**Happy Content Creating! 🚀**

# Blog-gen
