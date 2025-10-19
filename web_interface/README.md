# 🌐 DZP IAC Agent Web Interface

A complete web application example demonstrating how to integrate with the DZP IAC Agent REST API.

## 🚀 Quick Start

### Prerequisites

1. **DZP IAC Agent installed**:
   ```bash
   pip install -e .
   ```

2. **Environment configured**:
   ```bash
   cp .env.example .env
   # Edit .env with your AI provider settings
   ```

3. **Terraform project** (optional but recommended):
   ```bash
   # Create a test directory with Terraform files
   mkdir test-terraform
   cd test-terraform
   # Add your .tf files here
   ```

### Running the Web App

#### Option 1: Using the installed script
```bash
dzp-web --host 0.0.0.0 --port 8080
```

#### Option 2: Running directly
```bash
cd examples/web_app
python server.py --host 0.0.0.0 --port 8080
```

#### Option 3: Development mode with auto-reload
```bash
dzp-web --reload --port 8080
```

### Access the Interface

Once running, open your browser to:

- **Web Interface**: http://localhost:8080
- **API Documentation**: http://localhost:8080/api/docs
- **API Health Check**: http://localhost:8080/api/health

## 🎯 Features

### Chat Interface
- **Natural Language Conversations**: Ask questions about your infrastructure in plain English
- **Session Management**: Persistent conversation history across page refreshes
- **Real-time Responses**: See typing indicators and get immediate feedback
- **Metadata Display**: View which AI model and processor handled your request

### Agent Status Dashboard
- **Live Status Monitoring**: See if the agent is running and healthy
- **Model Information**: Display current AI model and provider
- **DeepAgents Status**: Check if multi-agent orchestration is available
- **Conversation Statistics**: Track number of conversations

### Terraform Operations
- **Safe Command Execution**: Run plan, validate, apply, and init commands
- **Real-time Results**: See command output and execution time
- **Plan Summaries**: Visual breakdown of add/change/destroy counts
- **Error Handling**: Clear error messages for failed operations

### Token Usage Tracking
- **Cost Monitoring**: Track token usage and estimated costs
- **Cache Efficiency**: Monitor cache savings and optimization
- **Real-time Updates**: Usage statistics refresh every 30 seconds

## 🏗️ Architecture

### Frontend (Vanilla JavaScript)
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, professional interface with smooth animations
- **Real-time Updates**: Automatic status and usage refreshes
- **Error Handling**: Graceful error display and recovery

### Backend Integration
- **FastAPI Server**: Serves both the web app and API
- **CORS Support**: Proper cross-origin request handling
- **Session Management**: Server-side session persistence
- **Health Monitoring**: Built-in health checks and dependency status

### API Communication
- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Responses**: Structured data with metadata
- **Error Handling**: Comprehensive error responses with details
- **Async Operations**: Non-blocking request processing

## 📱 Usage Examples

### Chat Interactions

Try these example prompts:

```
What resources are defined in my Terraform configuration?
```

```
Analyze the security of my infrastructure
```

```
Run terraform plan and show me what will change
```

```
How many virtual machines are currently deployed?
```

```
Validate my Terraform configuration for syntax errors
```

### Terraform Operations

1. **Validate Configuration**: Click "Validate" to check syntax
2. **Plan Changes**: Click "Plan" to see what will change
3. **Apply Changes**: Click "Apply" after reviewing the plan
4. **Initialize**: Click "Init" to set up the Terraform workspace

### Status Monitoring

- **Agent Health**: Green = healthy, Red = unhealthy
- **Model Info**: Shows current AI model in use
- **DeepAgents**: Shows if multi-agent features are available
- **Token Usage**: Monitors API costs and efficiency

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# AI Configuration
AI_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_BASE_URL=http://localhost:11434/v1
OPENAI_COMPATIBLE_MODEL=llama3.1

# Terraform Configuration
TERRAFORM_DIR=/path/to/your/terraform/files
TERRAFORM_PATH=terraform

# API Configuration
LOG_LEVEL=info
```

### Customization

#### Styling
Edit the CSS in `index.html` to customize colors, fonts, and layout:

```css
/* Change primary color */
:root {
    --primary-color: #00D4AA;
    --secondary-color: #667eea;
}
```

#### API Endpoints
Modify the JavaScript to use different API endpoints:

```javascript
// Change API base URL
const API_BASE_URL = 'http://your-api-server:8000/api';
```

## 🚀 Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install the package
COPY . .
RUN pip install -e .

# Expose port
EXPOSE 8080

# Run the web app
CMD ["dzp-web", "--host", "0.0.0.0", "--port", "8080"]
```

Build and run:

```bash
docker build -t dzp-web-app .
docker run -p 8080:8080 -v /path/to/terraform:/app/terraform dzp-web-app
```

### Production Considerations

1. **Authentication**: Add API key or JWT authentication
2. **HTTPS**: Use SSL/TLS certificates
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **CORS**: Configure appropriate origins for your domain
5. **Logging**: Set up centralized logging
6. **Monitoring**: Add health checks and metrics

## 🔍 Troubleshooting

### Common Issues

#### Agent Not Starting
```bash
# Check environment variables
cat .env

# Test AI connection
curl http://localhost:8080/api/health
```

#### Terraform Commands Fail
```bash
# Check Terraform installation
terraform version

# Verify working directory
ls -la $TERRAFORM_DIR

# Check file permissions
chmod -R 755 /path/to/terraform/files
```

#### Web Interface Not Loading
```bash
# Check if server is running
curl http://localhost:8080

# Check logs for errors
dzp-web --log-level debug
```

#### API Errors
```bash
# Test API directly
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Check API documentation
open http://localhost:8080/api/docs
```

### Debug Mode

Run with debug logging:

```bash
dzp-web --log-level debug --reload
```

## 🎨 Customization Guide

### Adding New Features

#### New Terraform Commands
1. Add the command to the API in `src/api/app.py`
2. Add a button in `index.html`
3. Implement the JavaScript function

```javascript
async function runCustomCommand() {
    const response = await fetch('/api/terraform/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: 'custom' })
    });
    // Handle response
}
```

#### New API Endpoints
1. Add the endpoint in `src/api/app.py`
2. Add the model in `src/api/models.py`
3. Call it from JavaScript

```python
@app.get("/api/custom")
async def custom_endpoint():
    return {"data": "custom response"}
```

### Theming

Modify the CSS variables in `index.html`:

```css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-secondary;
    --background-gradient: linear-gradient(...);
}
```

## 📚 API Reference

### Key Endpoints Used

- `POST /api/chat` - Send chat messages
- `GET /api/agent/status` - Get agent status
- `GET /api/agent/tokens` - Get token usage
- `POST /api/terraform/execute` - Run Terraform commands
- `GET /api/health` - Health check

### Response Formats

All responses follow the documented API format. See `docs/API_DOCUMENTATION.md` for complete details.

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd dzp

# Install in development mode
pip install -e ".[dev]"

# Run web app in development
dzp-web --reload --log-level debug
```

### Making Changes

1. **Frontend**: Edit `index.html` and `server.py`
2. **API**: Edit files in `src/api/`
3. **Styling**: Modify CSS in `index.html`
4. **Testing**: Test with different Terraform projects

## 📄 License

This example is part of the DZP IAC Agent project. See the main project license for details.

---

**DZP IAC Agent Web Interface** - Modern web interface for intelligent infrastructure automation
