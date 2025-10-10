# 🚀 DZP IAC Agent - Code Architecture

Complete code architecture explanation for the DZP IAC Agent with OpenAI-compatible models and DeepAgents multi-agent orchestration.

## 📋 Table of Contents

1. [Application Overview](#application-overview)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [AI Integration Layer](#ai-integration-layer)
5. [Terraform Integration](#terraform-integration)
6. [Security & Production Features](#security--production-features)
7. [Configuration Management](#configuration-management)

---

## Application Overview

### What is DZP IAC Agent?

DZP IAC Agent is an intelligent Terraform Infrastructure as Code assistant that:
- Uses **natural language** to interact with Terraform
- Supports **OpenAI-compatible models** (OpenAI, Ollama, LocalAI, kimi, etc.)
- Leverages **DeepAgents** for complex multi-agent workflows
- Provides **Human-in-the-Loop** approval for critical operations
- Executes Terraform commands safely with input validation

### Technology Stack

- **Python 3.11+**: Modern async/await support
- **LangChain**: AI model orchestration
- **DeepAgents**: Multi-agent coordination
- **Rich**: Beautiful terminal UI
- **Pydantic**: Configuration validation
- **Tenacity**: Retry logic for reliability

---

## Project Structure

```
dzp/
├── main.py                          # Application entry point
├── pyproject.toml                   # Dependencies and project config
├── .env                             # Environment configuration (not in git)
├── .env.example                     # Environment template
├── src/
│   ├── ai/                          # AI Integration Layer
│   │   ├── openai_processor.py      # OpenAI-compatible processor
│   │   ├── deepagents_processor.py  # DeepAgents multi-agent orchestration
│   │   ├── enhanced_processor.py    # Unified processor interface
│   │   └── model_factory.py         # Model creation factory
│   ├── core/                        # Core Business Logic
│   │   ├── agent.py                 # Main agent orchestration
│   │   ├── config.py                # Configuration management
│   │   ├── logger.py                # Centralized logging
│   │   ├── workflows.py             # Pre-built workflow templates
│   │   ├── human_in_the_loop.py     # Approval system
│   │   └── task_engine.py           # Task execution engine
│   ├── terraform/                   # Terraform Integration
│   │   ├── cli.py                   # Terraform CLI wrapper
│   │   └── parser.py                # Terraform file parser
│   └── ui/                          # User Interface
│       └── enhanced_cli.py          # Terminal UI
└── docs/                            # Documentation
    ├── CHEATSHEET.md                # Quick reference
    └── CODE_EXPLANATION.md          # This file
```

---

## Core Components

### 1. Configuration Management (`src/core/config.py`)

**Purpose**: Central configuration with validation

**Key Features**:
- Environment variable loading with `.env` file
- **Pydantic validation** for type safety
- Field validators for AI provider, log level, Terraform path
- Sensible defaults for all settings

**Example**:
```python
class Config(BaseModel):
    # AI Provider Configuration
    ai_provider: str = Field("openai_compatible", env="AI_PROVIDER")
    
    @field_validator("ai_provider")
    @classmethod
    def validate_ai_provider(cls, v: str) -> str:
        valid_providers = ["openai", "openai_compatible"]
        if v.lower() not in valid_providers:
            logger.warning(f"Invalid provider. Defaulting to 'openai_compatible'")
            return "openai_compatible"
        return v.lower()
```

**Production Features**:
- ✅ Input validation prevents invalid configurations
- ✅ Warnings for missing Terraform CLI
- ✅ Type safety with Pydantic

### 2. Main Agent (`src/core/agent.py`)

**Purpose**: Orchestrates all operations and tool execution

**Key Responsibilities**:
- Registers Terraform tools for AI to use
- Manages conversation flow
- Coordinates between AI processor and Terraform CLI
- Executes workflows

**Tool Registration**:
```python
def _register_tools(self):
    # Create tools that AI can call
    tools = [
        self._create_terraform_plan_tool(),
        self._create_terraform_apply_tool(),
        self._create_terraform_validate_tool(),
        # ... more tools
    ]
```

**Production Features**:
- ✅ Async/await for non-blocking operations
- ✅ Comprehensive error handling
- ✅ Tool result formatting

### 3. Logging System (`src/core/logger.py`)

**Purpose**: Centralized, configurable logging

**Key Features**:
- File and console logging
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Structured log format with timestamps
- Module-specific loggers

**Usage**:
```python
from src.core.logger import get_logger

logger = get_logger(__name__)
logger.info("Operation completed successfully")
logger.error("Failed to process request", exc_info=True)
```

---

## AI Integration Layer

### 1. OpenAI Processor (`src/ai/openai_processor.py`)

**Purpose**: Interface to OpenAI-compatible models

**Key Features**:
- **Retry Logic**: Exponential backoff for transient failures (using tenacity)
- **Token Tracking**: Monitors input/output tokens for cost management
- **Input Validation**: Prevents empty or invalid requests
- **Conversation History**: Maintains context across requests

**Retry Implementation**:
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    reraise=True
)
async def _invoke_model_with_retry(self, messages: List) -> Any:
    return await self.model.ainvoke(messages)
```

**Production Features**:
- ✅ Automatic retry on network failures
- ✅ Request validation
- ✅ Comprehensive error handling with stack traces
- ✅ Token usage monitoring

### 2. DeepAgents Processor (`src/ai/deepagents_processor.py`)

**Purpose**: Multi-agent orchestration for complex workflows

**Sub-Agents**:
1. **security-auditor**: Security analysis and compliance
2. **cost-optimizer**: Cost optimization and resource sizing
3. **deployment-validator**: Deployment validation and testing
4. **migration-planner**: Infrastructure migration planning

**Configuration**:
```python
agent = create_deep_agent(
    tools=self.terraform_tools,
    instructions=instructions,
    model=self.model,
    subagents=self.subagents,
    tool_configs=tool_configs,
    recursion_limit=50,  # Increased from default 25
)
```

**Production Features**:
- ✅ Specialized sub-agents for different tasks
- ✅ Increased recursion limit for complex workflows
- ✅ Human-in-the-loop approval for critical tools
- ✅ Coordinated multi-step operations

### 3. Enhanced Processor (`src/ai/enhanced_processor.py`)

**Purpose**: Unified interface that switches between processors

**Key Responsibilities**:
- Initializes both OpenAI and DeepAgents processors
- Routes requests based on configuration
- Provides consistent API regardless of backend

**Request Routing**:
```python
async def process_request(self, request, context=None):
    # Choose the appropriate processor
    if self.config.use_deepagents and self.deepagents_processor:
        return await self.deepagents_processor.process_request(request, context)
    elif self.openai_processor:
        return await self.openai_processor.process_request(request, context)
```

### 4. Model Factory (`src/ai/model_factory.py`)

**Purpose**: Creates appropriate AI model instances

**Supported Providers**:
- OpenAI (gpt-4o, gpt-4-turbo, etc.)
- OpenAI Compatible (Ollama, LocalAI, LM Studio, kimi, etc.)

**Factory Pattern**:
```python
@staticmethod
def create_model(config: Config) -> BaseLanguageModel:
    provider = config.ai_provider.lower()
    
    if provider == "openai":
        return ModelFactory._create_openai_model(config)
    elif provider == "openai_compatible":
        return ModelFactory._create_openai_compatible_model(config)
```

---

## Terraform Integration

### 1. Terraform CLI Wrapper (`src/terraform/cli.py`)

**Purpose**: Safe interface to Terraform CLI

**Security Features**:
- **Input Sanitization**: Removes dangerous characters (; & | ` $ etc.)
- **Working Directory Validation**: Ensures directory exists and is valid
- **Path Resolution**: Converts to absolute paths to prevent traversal attacks

**Input Sanitization**:
```python
def _sanitize_input(self, value: str) -> str:
    """Sanitize user input to prevent command injection"""
    dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "<", ">", "\n", "\r"]
    sanitized = value
    for char in dangerous_chars:
        if char in sanitized:
            logger.warning(f"Removing dangerous character '{char}' from input")
            sanitized = sanitized.replace(char, "")
    return sanitized
```

**Async Command Execution**:
```python
async def _run_command(
    self,
    command: List[str],
    timeout: int = 300
) -> TerraformResult:
    # Create subprocess
    process = await asyncio.create_subprocess_exec(
        *full_command,
        cwd=self.working_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Wait with timeout
    stdout, stderr = await asyncio.wait_for(
        process.communicate(), 
        timeout=timeout
    )
```

**Production Features**:
- ✅ Command injection prevention
- ✅ Timeout protection
- ✅ Proper error handling
- ✅ Return code interpretation

### 2. Terraform Parser (`src/terraform/parser.py`)

**Purpose**: Parse and analyze Terraform configuration files

**Capabilities**:
- Parse `.tf` files using python-hcl2
- Extract resources, variables, outputs, providers
- Count and categorize resources
- Provide configuration summaries

---

## Security & Production Features

### Security Measures

1. **Input Validation**
   - Configuration validation with Pydantic
   - Request validation (non-empty, proper format)
   - Terraform input sanitization

2. **Command Injection Prevention**
   - Dangerous character filtering
   - Path validation and resolution
   - No shell=True in subprocess calls

3. **Error Handling**
   - Try-catch blocks on all critical operations
   - Detailed error logging with stack traces
   - Graceful degradation

4. **Human-in-the-Loop**
   - Critical operations require approval
   - Risk assessment for operations
   - Approval history tracking

### Reliability Features

1. **Retry Logic**
   - Exponential backoff for transient failures
   - Configurable retry attempts
   - Connection and timeout error handling

2. **Logging**
   - Centralized logging system
   - Configurable log levels
   - File and console output

3. **Token Tracking**
   - Input/output token monitoring
   - Cost estimation
   - Usage statistics

4. **Configuration Validation**
   - Field validators
   - Type checking
   - Sensible defaults

---

## Configuration Management

### Environment Variables

**AI Configuration**:
```bash
AI_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_BASE_URL=http://localhost:11434/v1
OPENAI_COMPATIBLE_MODEL=kimi-k2:1t-cloud
OPENAI_COMPATIBLE_MAX_TOKENS=4096
```

**DeepAgents Configuration**:
```bash
USE_DEEPAGENTS=true
HUMAN_IN_THE_LOOP=true
```

**Terraform Configuration**:
```bash
TERRAFORM_PATH=terraform
TERRAFORM_WORKSPACE=default
TERRAFORM_DIR=/absolute/path/to/terraform/files
```

**Application Configuration**:
```bash
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760
UI_THEME=dark
```

### Configuration Validation Flow

1. Load `.env` file with dotenv
2. Parse with Pydantic BaseModel
3. Run field validators
4. Set defaults for missing values
5. Log warnings for invalid values
6. Initialize application with validated config

---

## Key Programming Patterns

### 1. Factory Pattern
Used in `model_factory.py` to create different AI model instances

### 2. Dependency Injection
Configuration and logger injected into classes for testability

### 3. Async/Await
Non-blocking operations for better performance

### 4. Retry Pattern
Automatic retry with exponential backoff for reliability

### 5. Validator Pattern
Pydantic validators for configuration validation

### 6. Strategy Pattern
Different processors (OpenAI, DeepAgents) with same interface

---

## Data Flow

### Simple Query Flow

```
User Input → Enhanced Processor → OpenAI Processor 
  → Model API → Response → Format → Display
```

### Complex Query with DeepAgents

```
User Input → Enhanced Processor → DeepAgents Processor
  → Main Agent → Sub-Agent Selection → Tool Execution
  → Sub-Agent Analysis → Result Aggregation → Response
```

### Terraform Operation Flow

```
User Request → Agent → Tool Selection → Terraform CLI
  → Execute Command → Parse Output → Format Response
  → Display to User
```

---

## Error Handling Strategy

### Levels of Error Handling

1. **Validation Layer**: Catch invalid inputs early
2. **Processor Layer**: Handle AI API errors with retry
3. **CLI Layer**: Handle Terraform execution errors
4. **UI Layer**: Display user-friendly error messages

### Error Recovery

- **Transient Errors**: Automatic retry with backoff
- **Configuration Errors**: Log warning, use defaults
- **Critical Errors**: Log with stack trace, inform user
- **Timeout Errors**: Terminate process, return timeout error

---

## Testing Approach

### Integration Testing

The project includes `test_integration.py` that validates:
- Configuration loading
- Model factory creation
- Processor initialization
- Workflow templates
- Human-in-the-loop system

### Manual Testing

```bash
# Test configuration
uv run python test_integration.py

# Test main application
uv run python main.py
```

---

## Performance Considerations

### Optimization Techniques

1. **Async Operations**: Non-blocking I/O
2. **Token Limits**: Configurable max tokens
3. **Caching**: Conversation history for context
4. **Lazy Loading**: Components initialized on demand

### Scalability

- Stateless processors (can be scaled horizontally)
- Configurable timeouts
- Resource limits (max file size)
- Token usage monitoring

---

## Future Enhancements

Potential areas for improvement:

1. **Caching Layer**: Cache Terraform plan results
2. **Metrics Collection**: Prometheus/Grafana integration
3. **Web Interface**: REST API + web UI
4. **Multi-tenancy**: Support multiple projects
5. **State Management**: Better state file handling
6. **Testing**: Comprehensive unit and integration tests

---

## Learning Resources

### Python Concepts Used

- **Async/Await**: Modern Python concurrency
- **Type Hints**: Static typing with Python
- **Pydantic**: Data validation library
- **Decorators**: @retry, @field_validator, @tool
- **Context Managers**: with statements for resources

### Design Patterns

- Factory Pattern (model_factory.py)
- Strategy Pattern (multiple processors)
- Dependency Injection (config, logger)
- Retry Pattern (with tenacity)

### External Libraries

- **LangChain**: LLM application framework
- **DeepAgents**: Multi-agent orchestration
- **Rich**: Terminal UI library
- **Tenacity**: Retry library
- **Pydantic**: Data validation

---

**DZP IAC Agent** - Production-ready Terraform automation with OpenAI-compatible models and DeepAgents
