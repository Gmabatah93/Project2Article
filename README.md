# Project-to-Article Generator

A Streamlit application that transforms code projects into engaging technical articles using AI-powered analysis.

## 🎯 Overview

This application allows developers to upload their project archives and automatically generate well-structured technical articles. Perfect for:
- **Indie Developers** who want to showcase their work
- **Bootcamp Graduates** building portfolio pieces  
- **Content Creators** generating tutorials at scale

## ✨ Features

### ✅ Complete Features (Milestones 1-4)
- ✅ File upload support (ZIP, TAR.GZ, max 20MB)
- ✅ Project analysis with file tree generation
- ✅ Configurable analysis depth (Overview/Detailed)
- ✅ Article tone selection (Explanatory/Conversational/Marketing)
- ✅ **Real LLM Integration**: OpenAI GPT-4, Anthropic Claude, Google Gemini
- ✅ **API Key Management**: Secure input fields with environment variable support
- ✅ **LangGraph Workflow**: Complete article generation pipeline
- ✅ **Graceful Fallback**: Mock clients for testing without API keys
- ✅ **Production Ready**: Error handling, logging, and comprehensive testing
- ✅ Modern, responsive UI with real-time feedback

### 🚀 Ready for Production
- 🤖 **Real AI-powered article generation**
- 📊 **Multiple LLM provider support**
- 🎨 **Automatic code snippet formatting**
- 📈 **Performance metrics and logging**
- 🛡️ **Security and privacy protection**

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd project_to_article_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional)
   ```bash
   # Create .env file
   touch .env
   
   # Add your API keys for real LLM integration
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   GOOGLE_API_KEY=your_google_key_here
   ```
   
   **Note**: API keys are optional. The app will use mock clients for testing if no keys are provided.

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 📖 Usage

### Step 1: Prepare Your Project
- Zip your project folder
- Ensure it's under 20MB
- Include a README file for better analysis

### Step 2: Upload and Configure
- Upload your project archive
- Choose analysis depth:
  - **Overview**: README & top-level files only
  - **Detailed**: Full source code analysis
- Select article tone and LLM provider
- Configure meta settings

### Step 3: Generate Article
- Click "Generate Article"
- Wait for processing (≤60 seconds)
- Review and download your article

## 🏗️ Architecture

```
project_to_article_app/
├── app.py               # Streamlit UI
├── graph/               # LangGraph DAG
│   ├── __init__.py
│   └── nodes.py         # Workflow nodes (M2+)
├── services/
│   ├── __init__.py
│   ├── llm_factory.py   # LLM provider abstraction (M4+)
│   └── parser.py        # File extraction & analysis
├── prompts/             # Prompt templates (M2+)
│   ├── planner_prompt.txt
│   └── section_prompt.txt
├── requirements.txt
└── README.md
```

## 🎯 Success Metrics

- **≥80%** of generated articles rated 4/5 or higher by users
- **≤60 seconds** Time-to-Article for projects ≤5MB
- **≥30%** returning user rate after 30 days

## 🔧 Development

### Project Structure
- **M0**: Project kickoff & tech spike ✅
- **M1**: File upload & parsing working ✅
- **M2**: LangGraph article pipeline (Overview) ✅
- **M3**: Depth = Detailed + tone control ✅
- **M4**: Real LLM integration & API management ✅
- **M5**: Production ready with comprehensive testing ✅
- **M6**: Ready for deployment and scaling 🚀

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
flake8 .
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create a GitHub issue
- **Documentation**: Check the PRD.md file
- **Questions**: Open a discussion

## 🧪 Testing

### Test Real LLM Integration
```bash
python test_real_llm.py
```

### Test Complete Workflow
```bash
python debug_workflow.py
```

### Visualize Workflow
```bash
python visualize_workflow.py
```

---

**🎉 Project Status: Production Ready!**

All milestones completed. The Project-to-Article Generator is now fully functional with real LLM integration, comprehensive testing, and production-ready features. 