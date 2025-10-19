# 🚀 DZP IAC Agent API Documentation

Complete REST API documentation for the DZP Infrastructure as Code Agent.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [Endpoints](#endpoints)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Web App Integration](#web-app-integration)

---

## Overview

The DZP IAC Agent API provides a RESTful interface to interact with the Terraform AI agent. It enables building web applications and other integrations that can:

- Chat with the AI agent using natural language
- Execute Terraform commands
- Manage conversation sessions
- Monitor agent status and token usage
- Execute complex workflows

### Key Features

- **Session Management**: Persistent conversation sessions with history
- **Real-time Processing**: Async request handling with streaming support
- **Comprehensive Error Handling**: Structured error responses
- **Health Monitoring**: Built-in health checks and dependency status
- **Terraform Integration**: Safe execution of Terraform operations
- **Workflow Orchestration**: Execute complex multi-step workflows

---

## Authentication

Currently, the API does not implement authentication. For production use, you should add:

- API Key authentication
- JWT tokens
- OAuth2 integration
- Rate limiting per user

### Security Headers

The API includes CORS middleware for cross-origin requests. Configure appropriately for your environment.

---

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com/api
```

All endpoints are relative to the base URL.

---

## Endpoints

### Health Check

#### GET /health

Check the health status of the API and its dependencies.

**Response:**
```json
{
  "status": "healthy|unhealthy",
  "version": "1.0.0",
  "uptime": 123.45,
  "dependencies": {
    "agent": true,
    "session_manager": true,
    "config": true,
    "ai_connection": true,
    "terraform": true
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

**Status Codes:**
- `200 OK` - Health check completed
- `503 Service Unavailable` - Critical dependencies unavailable

---

### Chat Endpoints

#### POST /chat

Send a message to the AI agent and get a response.

**Request Body:**
```json
{
  "message": "What resources are defined in my Terraform configuration?",
  "session_id": "optional-session-id",
  "context": {
    "additional": "context-data"
  }
}
```

**Response:**
```json
{
  "message": "I found 8 resources defined in your configuration...",
  "session_id": "session-uuid",
  "conversation_id": "conv-uuid",
  "metadata": {
    "model_info": {
      "provider": "openai_compatible",
      "model": "llama3.1"
    },
    "processor_info": {
      "active_processor": "openai",
      "use_deepagents": false
    }
  },
  "processing_time": 2.34
}
```

**Status Codes:**
- `200 OK` - Message processed successfully
- `400 Bad Request` - Invalid request format
- `500 Internal Server Error` - Processing failed

#### GET /sessions/{session_id}

Get information about a specific session.

**Response:**
```json
{
  "session_id": "session-uuid",
  "created_at": "2024-01-01T12:00:00",
  "last_activity": "2024-01-01T12:30:00",
  "message_count": 10,
  "status": "active"
}
```

#### GET /sessions/{session_id}/history

Get the complete conversation history for a session.

**Response:**
```json
{
  "session_id": "session-uuid",
  "messages": [
    {
      "role": "user",
      "content": "What resources are defined?",
      "timestamp": "2024-01-01T12:00:00"
    },
    {
      "role": "assistant",
      "content": "I found 8 resources...",
      "timestamp": "2024-01-01T12:00:05"
    }
  ],
  "created_at": "2024-01-01T12:00:00",
  "last_activity": "2024-01-01T12:30:00"
}
```

#### GET /sessions

List all active sessions.

**Response:**
```json
[
  {
    "session_id": "session-uuid-1",
    "created_at": "2024-01-01T12:00:00",
    "last_activity": "2024-01-01T12:30:00",
    "message_count": 10,
    "status": "active"
  }
]
```

#### DELETE /sessions/{session_id}

Delete a session and its history.

**Response:**
```json
{
  "message": "Session deleted successfully"
}
```

---

### Project and Agent Endpoints

#### GET /project/overview

Get an overview of the Terraform project.

**Response:**
```json
{
  "resources": {
    "count": 8,
    "by_type": {
      "azurerm_virtual_machine": 2,
      "azurerm_resource_group": 1
    },
    "details": [...]
  },
  "variables": {
    "count": 5,
    "details": [...]
  },
  "outputs": {
    "count": 2,
    "details": [...]
  },
  "providers": {
    "count": 1,
    "details": [...]
  },
  "terraform_configured": true
}
```

#### GET /agent/status

Get detailed agent status and configuration.

**Response:**
```json
{
  "running": true,
  "session_duration": "0:30:45",
  "conversation_count": 15,
  "ai_processor": {
    "ai_provider": "openai_compatible",
    "use_deepagents": true,
    "available_processors": [...]
  },
  "deepagents_available": true,
  "workflows_available": 4,
  "hil_status": {
    "enabled": true,
    "pending_approvals": 0
  },
  "model_config": {
    "provider": "openai_compatible",
    "model": "llama3.1",
    "api_configured": true
  }
}
```

#### GET /agent/tokens

Get token usage statistics and cost information.

**Response:**
```json
{
  "total_input_tokens": 1500,
  "total_output_tokens": 800,
  "total_tokens": 2300,
  "cache_creation_tokens": 100,
  "cache_read_tokens": 50,
  "cache_savings_tokens": 25,
  "estimated_cost_usd": 0.0234,
  "input_cost_usd": 0.0150,
  "output_cost_usd": 0.0080,
  "cache_cost_usd": 0.0004,
  "cache_creation_cost_usd": 0.0002
}
```

---

### Terraform Command Endpoints

#### POST /terraform/execute

Execute a Terraform command safely.

**Request Body:**
```json
{
  "command": "plan",
  "parameters": {
    "detailed": true
  },
  "auto_approve": false
}
```

**Response:**
```json
{
  "success": true,
  "output": "Terraform plan output...",
  "error": null,
  "duration": 3.45,
  "summary": {
    "add": 2,
    "change": 1,
    "destroy": 0
  }
}
```

**Supported Commands:**
- `plan` - Run terraform plan
- `apply` - Run terraform apply
- `destroy` - Run terraform destroy
- `validate` - Run terraform validate
- `init` - Run terraform init
- `state list` - List resources in state

---

### Workflow Endpoints

#### GET /workflows

List available workflow templates.

**Response:**
```json
{
  "workflows": {
    "security_audit": {
      "name": "Security Audit",
      "description": "Comprehensive security analysis",
      "type": "security"
    },
    "cost_optimization": {
      "name": "Cost Optimization",
      "description": "Optimize infrastructure costs",
      "type": "cost"
    }
  }
}
```

#### POST /workflows/execute

Execute a complex workflow using DeepAgents.

**Request Body:**
```json
{
  "workflow_name": "security_audit",
  "parameters": {
    "compliance_standards": ["CIS", "SOC2"],
    "resource_types": ["virtual_machine", "storage_account"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "workflow_name": "security_audit",
  "result": {
    "findings": [...],
    "recommendations": [...],
    "risk_score": 7.5
  },
  "error": null,
  "plan": {
    "template": {...},
    "execution_steps": [...]
  }
}
```

---

### Maintenance Endpoints

#### POST /maintenance/cleanup

Clean up expired sessions (runs in background).

**Response:**
```json
{
  "message": "Session cleanup started"
}
```

---

## Error Handling

All endpoints return structured error responses:

```json
{
  "error": "Error description",
  "error_code": "ERROR_CODE",
  "details": {
    "additional": "error-details"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### Common Error Codes

- `SESSION_NOT_FOUND` - Session ID not found
- `PROCESSING_ERROR` - Failed to process request
- `UNSUPPORTED_COMMAND` - Terraform command not supported
- `TOKEN_TRACKING_UNAVAILABLE` - Token tracking not available
- `INTERNAL_ERROR` - Internal server error

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `501 Not Implemented` - Feature not available
- `503 Service Unavailable` - Service temporarily unavailable

---

## Rate Limiting

Currently not implemented, but recommended for production:

```python
# Example rate limiting configuration
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, ...):
    ...
```

---

## Web App Integration

### Frontend Integration Example

Here's how to integrate the API with a React/Vue.js frontend:

#### 1. Chat Component

```javascript
// React Example
import React, { useState, useEffect } from 'react';

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Initialize session
  useEffect(() => {
    setSessionId(generateUUID());
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          session_id: sessionId
        })
      });

      const data = await response.json();
      
      const assistantMessage = { 
        role: 'assistant', 
        content: data.message,
        metadata: data.metadata
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
      setInput('');
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="content">{msg.content}</div>
            {msg.metadata && (
              <div className="metadata">
                <small>Model: {msg.metadata.model_info?.model}</small>
              </div>
            )}
          </div>
        ))}
        {isLoading && <div className="typing-indicator">AI is thinking...</div>}
      </div>
      
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about your infrastructure..."
          disabled={isLoading}
        />
        <button onClick={sendMessage} disabled={isLoading}>
          Send
        </button>
      </div>
    </div>
  );
}
```

#### 2. Status Dashboard

```javascript
function StatusDashboard() {
  const [status, setStatus] = useState(null);
  const [tokens, setTokens] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statusRes, tokensRes] = await Promise.all([
          fetch('/agent/status'),
          fetch('/agent/tokens')
        ]);
        
        setStatus(await statusRes.json());
        setTokens(await tokensRes.json());
      } catch (error) {
        console.error('Error fetching status:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard">
      <h2>Agent Status</h2>
      {status && (
        <div className="status-grid">
          <div className="status-item">
            <label>Status:</label>
            <span className={status.running ? 'healthy' : 'unhealthy'}>
              {status.running ? 'Running' : 'Stopped'}
            </span>
          </div>
          <div className="status-item">
            <label>Model:</label>
            <span>{status.model_config?.model}</span>
          </div>
          <div className="status-item">
            <label>DeepAgents:</label>
            <span className={status.deepagents_available ? 'enabled' : 'disabled'}>
              {status.deepagents_available ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        </div>
      )}
      
      {tokens && (
        <div className="token-usage">
          <h3>Token Usage</h3>
          <div className="usage-stats">
            <div>Total Tokens: {tokens.total_tokens.toLocaleString()}</div>
            <div>Estimated Cost: ${tokens.estimated_cost_usd.toFixed(4)}</div>
            <div>Cache Savings: {tokens.cache_savings_tokens.toLocaleString()}</div>
          </div>
        </div>
      )}
    </div>
  );
}
```

#### 3. Terraform Operations

```javascript
function TerraformPanel() {
  const [planResult, setPlanResult] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  const runTerraformCommand = async (command, autoApprove = false) => {
    setIsRunning(true);
    
    try {
      const response = await fetch('/terraform/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          command,
          auto_approve: autoApprove
        })
      });

      const result = await response.json();
      setPlanResult(result);
    } catch (error) {
      console.error('Error executing command:', error);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="terraform-panel">
      <h3>Terraform Operations</h3>
      
      <div className="command-buttons">
        <button 
          onClick={() => runTerraformCommand('plan')}
          disabled={isRunning}
        >
          {isRunning ? 'Running...' : 'Plan'}
        </button>
        
        <button 
          onClick={() => runTerraformCommand('apply')}
          disabled={isRunning || !planResult?.success}
          className="danger"
        >
          Apply
        </button>
        
        <button 
          onClick={() => runTerraformCommand('validate')}
          disabled={isRunning}
        >
          Validate
        </button>
      </div>

      {planResult && (
        <div className="result-panel">
          <h4>Result</h4>
          <div className={`status ${planResult.success ? 'success' : 'error'}`}>
            {planResult.success ? '✅ Success' : '❌ Failed'}
          </div>
          
          {planResult.summary && (
            <div className="summary">
              <div>Add: {planResult.summary.add}</div>
              <div>Change: {planResult.summary.change}</div>
              <div>Destroy: {planResult.summary.destroy}</div>
            </div>
          )}
          
          <pre className="output">
            {planResult.output}
          </pre>
        </div>
      )}
    </div>
  );
}
```

### WebSocket Support (Future Enhancement)

For real-time streaming responses, you can extend the API with WebSocket support:

```python
# Add to FastAPI app
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            # Process with streaming
            async for chunk in process_message_streaming(data, session_id):
                await websocket.send_text(chunk)
                
    except WebSocketDisconnect:
        # Handle disconnection
        pass
```

---

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_LOG_LEVEL=info

# AI Configuration
AI_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_BASE_URL=http://localhost:11434/v1
OPENAI_COMPATIBLE_MODEL=llama3.1

# Terraform Configuration
TERRAFORM_DIR=/path/to/terraform/files
TERRAFORM_PATH=terraform

# Security
CORS_ORIGINS=http://localhost:3000,https://yourapp.com
```

---

## Testing

### API Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Send chat message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What resources are defined?",
    "session_id": "test-session"
  }'

# Get agent status
curl http://localhost:8000/agent/status

# Execute Terraform plan
curl -X POST http://localhost:8000/terraform/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "plan",
    "auto_approve": false
  }'
```

### Automated Testing

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_chat_endpoint():
    response = client.post("/chat", json={
        "message": "Hello, what can you do?"
    })
    assert response.status_code == 200
    assert "message" in response.json()
    assert "session_id" in response.json()

def test_terraform_execute():
    response = client.post("/terraform/execute", json={
        "command": "validate"
    })
    assert response.status_code == 200
    assert "success" in response.json()
```

---

## Security Considerations

1. **Input Validation**: All inputs are validated using Pydantic models
2. **Command Injection**: Terraform commands are sanitized and parameterized
3. **CORS Configuration**: Configure appropriate origins for production
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Authentication**: Add API key or JWT authentication
6. **HTTPS**: Use HTTPS in production
7. **Logging**: Comprehensive logging for security monitoring

---

## Performance Optimization

1. **Async Operations**: All operations are async for better concurrency
2. **Session Caching**: In-memory session management with cleanup
3. **Connection Pooling**: Reuse AI model connections
4. **Background Tasks**: Cleanup operations run in background
5. **Response Compression**: Enable gzip compression for large responses

---

**DZP IAC Agent API** - Production-ready REST API for intelligent infrastructure automation
