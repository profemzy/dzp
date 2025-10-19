import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.agent import TerraformAgent
from src.core.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Custom JSON encoder to handle datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Custom JSON Response class that handles datetime objects
class DateTimeJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            cls=CustomJSONEncoder,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

# Pydantic models
class TerraformVariable(BaseModel):
    name: str
    value: str
    description: Optional[str] = None
    sensitive: bool = False
    type: Optional[str] = None

class TerraformCommandRequest(BaseModel):
    command: str = Field(..., description="Terraform command to execute (e.g., 'plan', 'apply', 'destroy')")
    variables: Optional[List[TerraformVariable]] = Field(None, description="Terraform variables")
    working_directory: Optional[str] = Field(None, description="Working directory for Terraform")
    auto_approve: bool = Field(False, description="Auto-approve destructive operations")

class TerraformCommandResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    exit_code: int
    execution_time: float

class AgentStatus(BaseModel):
    running: bool
    api_configured: bool
    session_duration: Optional[int] = None
    conversation_count: Optional[int] = None

class TokenUsage(BaseModel):
    total_tokens: int
    input_tokens: int
    output_tokens: int
    requests_count: int

class HealthResponse(BaseModel):
    status: str
    version: str
    agent_status: Optional[AgentStatus] = None

# FastAPI app
app = FastAPI(
    title="Terraform Agent API",
    description="API for interacting with Terraform through an AI agent",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME", "admin")
BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD", "password")

# Global agent instance
agent: Optional[TerraformAgent] = None

# Startup event to initialize agent
@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    global agent
    try:
        logger.info("Initializing Terraform Agent...")
        config = Config()
        agent = TerraformAgent(config)
        logger.info("✅ Terraform Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent on startup: {e}")
        # Don't fail startup, allow manual initialization

# Dependency to get the agent
async def get_agent() -> TerraformAgent:
    global agent
    if agent is None:
        # Try to auto-initialize if not already done
        try:
            config = Config()
            agent = TerraformAgent(config)
            logger.info("Agent auto-initialized on first request")
        except Exception as e:
            logger.error(f"Auto-initialization failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent not initialized. Call /initialize first."
            )
    return agent

# Helper function to create JSON responses with datetime support
def create_datetime_json_response(content: dict, status_code: int = 200) -> Response:
    """Create a JSON response that can handle datetime objects"""
    return DateTimeJSONResponse(
        content=content,
        status_code=status_code
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    error_response = {
        "error": "Internal server error",
        "error_code": "INTERNAL_ERROR",
        "details": {"message": str(exc)},
        "timestamp": datetime.now()
    }
    
    return create_datetime_json_response(error_response, status_code=500)

# Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    return {"message": "Terraform Agent API", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        agent_status_data = None
        if agent is not None:
            try:
                status_data = agent.get_enhanced_status()
                # Extract the nested agent_status and ensure all required fields
                agent_data = status_data.get('agent_status', {})

                # Calculate session duration in seconds
                session_duration = None
                if agent_data.get('session_duration'):
                    session_duration = int(agent.get_session_duration().total_seconds())

                agent_status_data = {
                    "running": agent_data.get('running', False),
                    "api_configured": True,
                    "session_duration": session_duration,
                    "conversation_count": agent_data.get('conversation_count', 0)
                }
            except Exception as e:
                logger.error(f"Error getting agent status: {e}")
                agent_status_data = {
                    "running": False,
                    "api_configured": False,
                    "session_duration": None,
                    "conversation_count": None
                }

        return {
            "status": "healthy",
            "version": "1.0.0",
            "agent_status": agent_status_data
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )

@app.post("/initialize")
async def initialize_agent():
    """Initialize the Terraform agent"""
    global agent
    try:
        if agent is not None:
            return {"message": "Agent already initialized"}
        
        # Initialize configuration
        config = Config()

        # Create agent
        agent = TerraformAgent(config)
        
        return {"message": "Agent initialized successfully"}
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize agent: {str(e)}"
        )

@app.post("/terraform/execute", response_model=TerraformCommandResponse)
async def execute_terraform_command(
    request: TerraformCommandRequest,
    agent: TerraformAgent = Depends(get_agent)
):
    """Execute a Terraform command"""
    try:
        import time
        start_time = time.time()

        # Build command string
        command = f"terraform {request.command}"

        # Execute command through agent
        output = await agent.process_command_async(command)

        execution_time = time.time() - start_time

        # Determine success based on output
        success = "✅" in output or "Successful" in output
        error = None if success else "Command failed"
        exit_code = 0 if success else 1

        return TerraformCommandResponse(
            success=success,
            output=output,
            error=error,
            exit_code=exit_code,
            execution_time=execution_time
        )
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Command execution failed: {str(e)}"
        )

@app.get("/agent/status")
async def get_agent_status(agent: TerraformAgent = Depends(get_agent)):
    """Get the current status of the agent"""
    try:
        status_data = agent.get_enhanced_status()

        # Extract the nested agent_status and ensure all required fields
        agent_data = status_data.get('agent_status', {})

        # Calculate session duration in seconds
        session_duration = None
        if agent_data.get('session_duration'):
            session_duration = int(agent.get_session_duration().total_seconds())

        # Return status with all available information
        return {
            "running": agent_data.get('running', False),
            "api_configured": True,
            "session_duration": session_duration,
            "conversation_count": agent_data.get('conversation_count', 0),
            "ai_processor": status_data.get('ai_processor', {}),
            "deepagents_available": status_data.get('deepagents_available', False),
            "model_config": status_data.get('model_config', {})
        }
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")

        # Return error response with datetime support
        error_response = {
            "error": "Failed to get agent status",
            "error_code": "AGENT_STATUS_ERROR",
            "details": {"message": str(e)},
            "timestamp": datetime.now()
        }

        return create_datetime_json_response(error_response, status_code=500)

@app.get("/agent/tokens")
async def get_token_usage(agent: TerraformAgent = Depends(get_agent)):
    """Get token usage statistics"""
    try:
        # Check if the AI processor supports token usage tracking
        if hasattr(agent.ai_processor, 'get_token_usage_stats'):
            stats = agent.ai_processor.get_token_usage_stats()
            return stats
        else:
            # Return empty stats if not available
            return {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "requests_count": 0
            }
    except Exception as e:
        logger.error(f"Error getting token usage: {e}")
        return {
            "total_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "requests_count": 0
        }

# Chat endpoint
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@app.post("/chat")
async def chat(request: ChatRequest, agent_inst: TerraformAgent = Depends(get_agent)):
    """Send a chat message to the agent"""
    try:
        # Process the command asynchronously
        response = await agent_inst.process_command_async(request.message)

        return {
            "success": True,
            "response": response,
            "session_id": request.session_id or "default",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
