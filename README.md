# 🔗 Backlink Article Generator

AI-powered tool that generates SEO-optimized articles by analyzing your content + competitor articles, with natural backlinks and brand mentions.

## Features

- **Content Synthesis**: Mix your article (60-70%) with 3 competitor articles (30-40%)
- **Multi-Agent Validation**: 5 AI agents ensure quality (Title, Backlink, Readability, Brand Mentions)
- **Natural Backlinks**: Embed your article link with keyword anchor text
- **Brand Integration**: Add "Labellerr AI" mentions naturally (4-5 times)
- **Web Scraping**: Optional automatic content extraction from URLs
- **Multiple AI Providers**: Gemini 2.0 Flash (recommended), OpenAI, Groq

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Get API Key:**
   - **Gemini** (Recommended): https://aistudio.google.com/app/apikey
   - **OpenAI**: https://platform.openai.com/api-keys
   - **Groq**: https://console.groq.com/keys

3. **Run the app:**
```bash
streamlit run app.py
```

4. **In the UI:**
   - Enter your API key
   - Add primary keyword & secondary keywords
   - Paste your original article (URL + content)
   - Add 3 competitor articles (URL + content)
   - Click "Generate Backlinked Article"

## Input Requirements

- **Primary Keyword**: Your target SEO keyword
- **Secondary Keywords**: Related terms (comma-separated)
- **Original Article**: Your article to backlink (URL + full content)
- **Competitor Articles**: 3 articles (URLs + full content)
- **Settings**: Word count, brand mention count

## Output

- **Generated Article**: New comprehensive article (1000+ words)
- **Validation Reports**: What each agent checked/fixed
- **Metrics**: Word count, sentences, backlink status, brand mentions
- **Download**: Save as TXT file

## AI Agents

1. **Content Synthesizer**: Creates new article from 4 sources
2. **Title Validator**: Ensures primary keyword in title
3. **Backlink Validator**: Checks link embedding with proper anchor
4. **Readability Validator**: Ensures sentences under 13-14 words
5. **Brand Mention Validator**: Verifies Labellerr AI mentions (4-5x)

## Requirements

```
streamlit>=1.28.0
crewai>=0.28.0
python-dotenv>=1.0.0
google-generativeai>=0.3.0
beautifulsoup4>=4.12.0
requests>=2.31.0
groq>=0.4.1
```

## Article Requirements

Generated articles will:
- Include primary keyword in title
- Be 1000+ words (configurable)
- Use active voice
- Keep sentences under 13-14 words
- Be written for US audiences
- Embed your backlink naturally
- Mention "Labellerr AI" 4-5 times

## Tips

✅ **DO:**
- Use complete competitor articles (500+ words)
- Choose highly relevant competitors
- Review generated content before publishing

❌ **DON'T:**
- Use very short content (<300 words)
- Mix unrelated topics
- Publish without fact-checking

## Troubleshooting

**"API key not found"** → Enter API key in UI

**"At least one competitor required"** → Add content to competitor sections

**Generation too slow** → Use Gemini 2.0 Flash Lite (fastest model, 30 RPM)

## License

Open-source and available for personal and commercial use.

---

**Ready to generate better content with natural backlinks!** 🚀
