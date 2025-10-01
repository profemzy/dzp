# 🤖 Autonomous Infrastructure as Code Agent

An intelligent agent powered by **LangChain** and **Azure OpenAI** that can work with Terraform codebases, understand infrastructure configurations, run plans, and execute natural language commands with a beautiful terminal interface.

## ✨ Features

### 🧠 AI-Powered Intelligence
- **LangChain Integration**: Modern conversation memory with context awareness
- **RAG (Retrieval-Augmented Generation)**: Knowledge base from Terraform documents
- **Azure OpenAI Compatibility**: Enterprise-ready AI integration
- **Context-Aware Responses**: Understands follow-up questions like "what are they?"
- **Natural Language Processing**: Advanced NLP for infrastructure queries

### 🏗️ Terraform Analysis
- **Infrastructure Parsing**: Analyze complex Terraform configurations
- **Resource Discovery**: Identify and categorize all infrastructure resources
- **Project Overview**: Comprehensive metrics and breakdowns
- **Multi-file Support**: Handle large-scale Terraform projects
- **Real-time Analysis**: Process 70+ resources seamlessly

### 🎨 Professional Terminal UI
- **Rich Interface**: Beautiful colors, tables, and panels
- **Progress Indicators**: Animated spinners and status updates
- **Session Analytics**: Track commands and conversation history
- **Enhanced Help System**: Colorized commands and examples
- **Professional Design**: Consistent theming and layout

### 💬 Natural Language Interface
- **Intuitive Commands**: Ask questions in plain English
- **Follow-up Questions**: Context-aware conversation flow
- **Comprehensive Responses**: Detailed, actionable information
- **Error Handling**: Graceful fallbacks and clear messages

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Azure OpenAI API key (or OpenAI API key)
- Terraform CLI (for infrastructure operations)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd terraform-ai-agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Create a `.env` file with your configuration:

```env
# Azure OpenAI Configuration (recommended)
OPENAI_API_KEY=your-azure-openai-api-key
OPENAI_BASE_URL=https://your-resource.openai.azure.com/
OPENAI_MODEL=azure/gpt-4

# Alternative: Standard OpenAI
# OPENAI_API_KEY=your-openai-api-key
# OPENAI_MODEL=gpt-4

# Project Configuration
PROJECT_ROOT=./examples/sample-terraform
LOG_LEVEL=INFO
```

## 🎯 Usage

### Start the Agent

```bash
python main.py
```

### Example Commands

#### Infrastructure Queries
- `"What resources are listed in this configuration?"`
- `"Show me all virtual machines"`
- `"What is the name of the resource group created by the codebase?"`
- `"How many storage accounts are defined?"`

#### Infrastructure Operations
- `"Upgrade the drive size of the ops-vm to 100GB"`
- `"Add a new subnet to the virtual network"`
- `"Modify the VM size to Standard_D4s_v3"`

#### Terraform Operations
- `"Run terraform plan and explain the changes"`
- `"What resources will be created in the production environment?"`
- `"Are these resources already applied in state?"`

#### Follow-up Questions
- `"What are they?"` (referring to previously mentioned resources)
- `"Tell me more about the virtual machines"`
- `"Show me the resource groups"`

### System Commands
- `help` - Show available commands
- `status` - Show session statistics
- `clear` - Clear the screen
- `exit` - Exit the agent

## 🏗️ Architecture

### Core Components

```
src/
├── ai/
│   └── langchain_processor.py    # LangChain integration & RAG
├── core/
│   ├── agent.py                  # Main business logic
│   ├── config.py                 # Configuration management
│   ├── logger.py                 # Logging system
│   └── task_engine.py            # Simplified task processing
├── terraform/
│   ├── parser.py                 # HCL/Terraform parsing
│   └── cli.py                    # Terraform CLI operations
└── ui/
    └── enhanced_cli.py           # Professional terminal UI
```

### Technology Stack

- **AI Framework**: LangChain with modern syntax
- **LLM**: Azure OpenAI / OpenAI GPT-4
- **Vector Database**: ChromaDB for RAG
- **UI Framework**: Rich terminal library
- **Embeddings**: text-embedding-ada-002
- **Parser**: Python-HCL2 for Terraform

### Design Principles

- **Single Responsibility**: Each module has a clear, focused purpose
- **Modern Syntax**: Up-to-date LangChain API (no deprecation warnings)
- **Error Resilience**: Graceful handling of API failures and edge cases
- **Context Awareness**: Maintains conversation history and context
- **Professional UI**: Beautiful, intuitive terminal interface

## 📊 Capabilities Demonstrated

The agent successfully handles:

- **72 Resources** analyzed in real-time
- **98 Variables** processed and categorized
- **64 Outputs** identified and explained
- **Conversation Context** maintained across multiple queries
- **Follow-up Questions** understood and answered appropriately
- **Complex Terraform** configurations parsed and explained

## 🔧 Development

### Project Structure

```
terraform-ai-agent/
├── main.py                      # Enhanced CLI entry point
├── requirements.txt             # Python dependencies
├── setup.py                     # Package configuration
├── .env.example                 # Environment template
├── README.md                    # This file
├── USAGE.md                     # Detailed usage guide
├── todo_list.md                 # Project completion status
├── src/                         # Source code
├── examples/                    # Sample Terraform configurations
└── chroma_db/                   # Vector database storage
```

### Best Practices Implemented

- **Clean Architecture**: Separation of concerns with clear module boundaries
- **Modern Python**: Type hints, async/await, proper error handling
- **Configuration Management**: Environment-based configuration
- **Logging**: Structured logging with appropriate levels
- **Testing**: Comprehensive testing with real Terraform configurations
- **Documentation**: Complete documentation with examples

## 🐛 Troubleshooting

### Common Issues

1. **API Key Issues**
   - Ensure your `.env` file is properly configured
   - Verify Azure OpenAI endpoint accessibility
   - Check API key permissions and quotas

2. **Terraform Parsing Errors**
   - Ensure Terraform files are valid HCL syntax
   - Check file permissions and accessibility
   - Verify `PROJECT_ROOT` configuration

3. **Vector Database Issues**
   - Delete `chroma_db/` directory to reset knowledge base
   - Ensure sufficient disk space for embeddings
   - Check network connectivity for embedding API

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.

## 📈 Performance

- **Startup Time**: ~3 seconds for knowledge base initialization
- **Query Response**: ~2-5 seconds depending on complexity
- **Memory Usage**: ~200MB for typical projects
- **Context Window**: Supports up to 50 conversation turns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing code style and patterns
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain** for the powerful AI framework
- **Azure OpenAI** for enterprise-grade AI capabilities
- **Rich** for the beautiful terminal interface
- **Python-HCL2** for Terraform parsing capabilities

---

## 🎯 Project Status: ✅ COMPLETE

**Total Tasks Completed: 37/37 across 7 phases**

The Autonomous Infrastructure as Code Agent is fully functional with:
- ✅ LangChain integration with modern syntax
- ✅ Azure OpenAI compatibility
- ✅ RAG capabilities with Terraform knowledge
- ✅ Conversation context and memory
- ✅ Professional terminal UI
- ✅ Production-ready implementation
- ✅ Clean, maintainable codebase
- ✅ Comprehensive documentation
