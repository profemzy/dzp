# 🤖 DZP IAC Agent

An intelligent Infrastructure as Code agent powered by **OpenAI-compatible models** and **DeepAgents multi-agent orchestration** for Terraform automation. Features production-ready reliability, comprehensive security, and intelligent workflow coordination.

## ✨ Features

### 🤖 AI & Multi-Agent Orchestration
- **OpenAI-Compatible**: Works with OpenAI, Ollama, LocalAI, LM Studio, and any OpenAI-compatible endpoint
- **DeepAgents Integration**: Multi-agent orchestration with 4 specialized sub-agents
  - **Security Auditor**: Security analysis and compliance checking (CIS, NIST, SOC2, GDPR)
  - **Cost Optimizer**: Cost optimization and resource sizing recommendations
  - **Deployment Validator**: Deployment validation and testing
  - **Migration Planner**: Infrastructure migration planning and execution
- **Intelligent Workflow Coordination**: Pre-built workflow templates for common IaC tasks
- **Human-in-the-Loop**: Critical operations require human approval (configurable)
- **Context-Aware**: Maintains conversation memory and understands follow-ups
- **Natural Language Processing**: Handles questions in plain English

### 🏗️ Terraform Operations
- **Infrastructure Analysis**: Parse and analyze complex Terraform configurations
- **Resource Discovery**: Identify and categorize all infrastructure resources
- **Terraform Execution**: Run plan, apply, validate, init, destroy with async operations
- **State Management**: Query and analyze Terraform state
- **Multi-file Support**: Handle large-scale Terraform projects
- **Real-time Execution**: Async operations with progress tracking

### 🎨 Professional Terminal UI
- **Rich Interface**: Beautiful colors, tables, and panels powered by Rich library
- **Progress Indicators**: Animated spinners and real-time status updates
- **Session Management**: Export/import conversations
- **Enhanced Help**: Colorized commands and examples
- **Interactive Prompts**: Smart command completion and history

### 🔒 Production-Ready Features
- **🔐 Security**: Input sanitization, command injection prevention
- **🔄 Retry Logic**: Automatic retry with exponential backoff
- **📊 Monitoring**: Operation logging, performance metrics
- **✅ Validation**: Configuration validation, input validation, type safety
- **🛡️ Error Handling**: Comprehensive error handling with graceful degradation
- **💾 Session Management**: Export/import conversations for audit trails

## ⚡ TL;DR - Quick Setup

```bash
# 1. Clone and navigate
git clone <repository-url>
cd dzp

# 2. Install dependencies and package
uv sync --dev
uv pip install -e .

# 3. Make globally available
echo 'export PATH="'$(pwd)'/.venv/bin:$PATH"' >> ~/.zshrc  # or ~/.bashrc
source ~/.zshrc

# 4. Configure
cp .env.example .env
# Edit .env with your API keys

# 5. Run from anywhere!
dzp
```

## 🚀 Installation Guide

### Prerequisites

- **Python 3.11+** - Required for modern async features
- **Terraform CLI** - Install from https://terraform.io/downloads
- **uv package manager** (recommended) - Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **API Key** - One of:
  - OpenAI API key from https://platform.openai.com/api-keys
  - OR local endpoint (Ollama, LocalAI, LM Studio) - No API key needed

### Step-by-Step Installation

**1. Clone the repository**
```bash
git clone <repository-url>
cd dzp
```

**2. Install dependencies**

Using uv (recommended):
```bash
uv sync --dev
```

Or using make:
```bash
make setup-dev  # One-time setup with all dependencies
```

Or using pip:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

**3. Install as global command**

After installing dependencies, install the package in editable mode:
```bash
uv pip install -e .
```

This creates three executable commands: `dzp`, `tf-agent`, and `dzp-agent`.

**4. Make `dzp` globally available** (choose one option):

**Option A: Add to PATH (Recommended)**
```bash
# For zsh users (macOS default)
echo 'export PATH="'$(pwd)'/.venv/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# For bash users
echo 'export PATH="'$(pwd)'/.venv/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Option B: Create system-wide symlink**
```bash
sudo ln -sf $(pwd)/.venv/bin/dzp /usr/local/bin/dzp
```

**Option C: Activate virtual environment**
```bash
source .venv/bin/activate
# Now dzp, tf-agent, and dzp-agent are available
```

**5. Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Configuration

Create a `.env` file with your configuration. Here's a comprehensive example:

```env
# ===========================================
# AI Configuration
# ===========================================
# Supported providers: openai, openai_compatible
AI_PROVIDER=openai_compatible

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MAX_TOKENS=4096

# OpenAI Compatible Endpoints (Ollama, LocalAI, LM Studio, etc.)
# API key may not be required for local endpoints
OPENAI_COMPATIBLE_API_KEY=
OPENAI_COMPATIBLE_MODEL=llama3.1
OPENAI_COMPATIBLE_BASE_URL=http://localhost:11434/v1
OPENAI_COMPATIBLE_MAX_TOKENS=4096

# ===========================================
# DeepAgents Configuration
# ===========================================
# Enable multi-agent orchestration for complex workflows
USE_DEEPAGENTS=false
# Require human approval for critical operations (apply, destroy)
HUMAN_IN_THE_LOOP=true

# ===========================================
# Terraform Configuration
# ===========================================
TERRAFORM_PATH=terraform
TERRAFORM_WORKSPACE=default
# Absolute path to your Terraform infrastructure directory
TERRAFORM_DIR=/absolute/path/to/terraform/files

# ===========================================
# Application Configuration
# ===========================================
LOG_LEVEL=INFO
LOG_FILE=
MAX_FILE_SIZE=10485760  # 10MB

# ===========================================
# UI Configuration
# ===========================================
UI_THEME=dark
AUTO_REFRESH=true
REFRESH_INTERVAL=30
```

## 🎯 Usage

### Starting the Agent

**Using the global command:**
```bash
dzp
```

That's it! Just run `dzp` from anywhere on your system.

**Alternative commands:**
```bash
tf-agent   # Alternative command name
dzp-agent  # Alternative command name
```

**Other ways to run:**

```bash
# With uv
uv run main.py

# With Makefile
make run

# With Python directly
python main.py
```

### Available Console Commands

The package provides three executable commands after installation:

| Command | Description |
|---------|-------------|
| `dzp` | **Main entry point** - Recommended command to run the agent |
| `tf-agent` | Alternative command name for Terraform Agent |
| `dzp-agent` | Alternative command name for DZP IAC Agent |

All three commands launch the same application. Use whichever you prefer!

### Example Conversations

#### Infrastructure Queries
```
> How many resources are in this configuration?
> What virtual machines are defined?
> Show me all storage accounts
> Analyze the security of this infrastructure
```

#### Terraform Operations
```
> Run terraform plan
> Validate the configuration
> Show terraform state
> Are these resources deployed?
> Initialize terraform
```

#### 🧠 Intelligent Follow-up Conversations
```bash
# Start with a terraform operation
> terraform plan
✅ Terraform Plan Successful - 10 resources to add

# Ask follow-up questions - the agent understands context!
> What resources will be created?
🏗️ Resources to be Created: Resource Groups, VMs, Networks, Storage...

> Tell me more about the virtual machine
💻 Linux VM: Ubuntu 22.04 LTS, Standard_B1s size, with SSH access

> How much will this cost per month?
💰 Estimated cost: ~$45-65/month based on selected resources

> Are the security rules appropriate?
🔒 Security Analysis: NSG allows SSH (port 22), HTTP (80), HTTPS (443)
```

#### Advanced Queries with DeepAgents
```
> Should I migrate from VMs to Kubernetes?
> Analyze the security implications of this setup
> What's the best way to optimize costs?
> Compare these two infrastructure approaches
> Plan a migration from AWS to Azure
```

#### Utility Commands
```
> status          # Show session statistics
> export my_session.json   # Export conversation
> import my_session.json   # Import conversation
> help            # Show all commands
> clear           # Clear screen
> exit            # Exit agent
```

## 🏗️ Architecture

### Technology Stack

- **AI Models**: OpenAI, Ollama, LocalAI, LM Studio, or any OpenAI-compatible endpoint
- **Multi-Agent**: DeepAgents for orchestration with specialized sub-agents
- **Function Calling**: LangChain tool integration for structured interactions
- **UI**: Rich terminal library for beautiful CLI experience
- **Parser**: Python-HCL2 for Terraform configuration parsing
- **Async**: AsyncIO for concurrent operations and real-time updates

### Core Components

```
dzp/
├── main.py                      # Application entry point
├── src/
│   ├── ai/
│   │   ├── model_factory.py     # AI model factory (OpenAI/Compatible)
│   │   ├── enhanced_processor.py # Enhanced AI processor
│   │   ├── openai_processor.py  # OpenAI compatible processor
│   │   └── deepagents_processor.py # DeepAgents multi-agent orchestration
│   ├── core/
│   │   ├── agent.py             # Main business logic & tool handlers
│   │   ├── config.py            # Configuration management
│   │   ├── logger.py            # Logging system
│   │   ├── task_engine.py       # Task execution engine
│   │   ├── workflows.py         # Workflow templates
│   │   └── human_in_the_loop.py # Human approval system
│   ├── terraform/
│   │   ├── parser.py            # HCL/Terraform parsing
│   │   └── cli.py               # Terraform CLI operations
│   └── ui/
│       └── enhanced_cli.py      # Professional terminal UI
└── docs/
    ├── CHEATSHEET.md            # Quick reference guide
    └── CODE_EXPLANATION.md      # Code architecture documentation
```

### AI Tools (8 Total)

The agent provides 8 specialized tools for Terraform operations:

1. **execute_terraform_plan** - Execute terraform plan to preview changes
2. **execute_terraform_apply** - Apply infrastructure changes
3. **execute_terraform_validate** - Validate Terraform configuration
4. **execute_terraform_init** - Initialize Terraform working directory
5. **execute_terraform_destroy** - Destroy managed infrastructure
6. **get_resources** - Query and analyze resource information
7. **analyze_infrastructure** - Deep analysis of infrastructure configuration
8. **get_terraform_state** - Check current deployment state

### DeepAgents Sub-Agents (4 Specialized Agents)

When `USE_DEEPAGENTS=true`, you get access to specialized sub-agents:

1. **Security Auditor**
   - Security vulnerability analysis
   - Compliance checking (CIS, NIST, SOC2, GDPR)
   - Network security review
   - IAM and access control analysis
   - Encryption and data protection review

2. **Cost Optimizer**
   - Resource sizing recommendations
   - Cost estimation and forecasting
   - Unused resource identification
   - Reserved instances and spot instance suggestions
   - Multi-cloud cost comparison

3. **Deployment Validator**
   - Pre-deployment validation
   - Post-deployment testing
   - Health check configuration
   - Rollback strategy planning
   - Integration testing

4. **Migration Planner**
   - Migration strategy development
   - Risk assessment and mitigation
   - Dependency mapping
   - Phased migration planning
   - Cross-cloud migration support

## 📚 Documentation

- **[CHEATSHEET.md](docs/CHEATSHEET.md)** - 🎯 Quick reference with example prompts and queries
- **[CODE_EXPLANATION.md](docs/CODE_EXPLANATION.md)** - 🏗️ Architecture and code organization

## 🔧 Development

### Development Commands

The project includes a Makefile for common development tasks:

```bash
# Show all available commands
make help

# Install dependencies
make install

# Install development dependencies
make dev

# Run the application
make run

# Run tests
make test

# Run linting (ruff + mypy)
make lint

# Format code (black + ruff)
make format

# Clean cache and build artifacts
make clean

# One-time development setup
make setup-dev
```

### Best Practices

- **Clean Architecture**: Separation of concerns with modular design
- **Modern Python**: Type hints, async/await, Pydantic validation
- **Error Handling**: Comprehensive error handling with graceful fallbacks
- **Logging**: Structured logging with configurable levels
- **Tool Safety**: Destructive operations require confirmation
- **Testable**: Modular design enables easy unit testing

## 🐛 Troubleshooting

### Command Not Found: `dzp`
If you get "command not found: dzp" after installation:

1. **Verify installation:**
   ```bash
   ls -la .venv/bin/dzp
   ```

2. **Check if PATH is updated:**
   ```bash
   echo $PATH | grep dzp
   ```

3. **Reload your shell configuration:**
   ```bash
   source ~/.zshrc  # or source ~/.bashrc
   ```

4. **Or open a new terminal window** - The PATH is loaded automatically in new terminals

5. **Alternative:** Run directly with full path:
   ```bash
   /path/to/dzp/.venv/bin/dzp
   ```

### API Key Issues
- Ensure `.env` file has valid `OPENAI_API_KEY` (if using OpenAI)
- For local endpoints (Ollama, LocalAI), API key is usually not required
- Check provider-specific documentation for API key requirements
- Verify API key has proper permissions and is not expired

### Terraform Not Found
- Install Terraform CLI: https://terraform.io/downloads
- Set `TERRAFORM_PATH` in `.env` if not in system PATH
- Verify installation: `terraform version`
- Ensure Terraform binary is executable

### Configuration Issues
- Set correct `TERRAFORM_DIR` in `.env` to point to your Terraform files
- Must be an absolute path to directory containing `.tf` files
- Example: `TERRAFORM_DIR=/Users/username/projects/terraform`
- Ensure directory exists and contains valid Terraform configuration

### Installation Issues
If `uv pip install -e .` fails:
- Ensure you're in the project directory
- Try: `uv sync --dev` first
- Check Python version: `python --version` (must be 3.11+)
- Reinstall uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- On macOS, ensure Xcode Command Line Tools are installed: `xcode-select --install`

### DeepAgents Not Working
If DeepAgents features aren't working:
- Verify `USE_DEEPAGENTS=true` in `.env`
- Check that `deepagents>=0.0.11` is installed: `pip show deepagents`
- Review logs for initialization errors
- Ensure AI model supports function calling (required for DeepAgents)

## 📈 Performance

- **Startup Time**: ~1-2 seconds
- **Query Response**: 1-3 seconds for standard queries
- **Terraform Plan**: 3-5 seconds (depends on infrastructure size)
- **DeepAgents**: 5-15 seconds for complex multi-agent workflows
- **Async Operations**: Non-blocking with real-time progress updates

## 🌟 Key Advantages

### vs Traditional IaC Tools

| Feature | DZP IAC Agent | Traditional CLI |
|---------|---------------|-----------------|
| **Interface** | Natural language | Command syntax |
| **Learning Curve** | Minimal | Steep |
| **Multi-Agent** | ✅ Built-in | ❌ Not available |
| **Security Analysis** | ✅ Automated | ⚠️ Manual review |
| **Cost Optimization** | ✅ AI-powered | ⚠️ Manual analysis |
| **Context Awareness** | ✅ Conversation memory | ❌ Stateless |
| **Human-in-Loop** | ✅ Configurable | ⚠️ Manual gates |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow existing code style and conventions
4. Add tests for new functionality
5. Run linting and tests: `make lint && make test`
6. Submit a pull request with clear description

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **OpenAI** for GPT models and API
- **DeepAgents** for multi-agent orchestration framework
- **HashiCorp** for Terraform
- **Rich** for beautiful terminal UI
- **LangChain** for AI framework and tool integration

---

## 🎯 Project Status: ✅ PRODUCTION READY

This is a complete, production-ready Infrastructure as Code automation agent with:
- ✅ OpenAI-compatible AI integration
- ✅ Multi-agent orchestration with DeepAgents
- ✅ 8 specialized Terraform tools
- ✅ 4 expert sub-agents for IaC workflows
- ✅ Human-in-the-loop safety controls
- ✅ Professional terminal UI
- ✅ Clean, maintainable codebase
- ✅ Comprehensive documentation
- ✅ Global command installation

**DZP IAC Agent** - Built with AI for intelligent infrastructure automation.
