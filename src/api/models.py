"""
Pydantic models for API request/response schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Represents a chat message"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message to process")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation continuity")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the request")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: str = Field(..., description="Assistant's response")
    session_id: str = Field(..., description="Session identifier")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Response metadata")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")


class SessionInfo(BaseModel):
    """Session information model"""
    session_id: str = Field(..., description="Session identifier")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: datetime = Field(..., description="Last activity time")
    message_count: int = Field(..., description="Number of messages in session")
    status: str = Field(..., description="Session status")


class ProjectOverview(BaseModel):
    """Project overview model"""
    resources: Dict[str, Any] = Field(..., description="Resources information")
    variables: Dict[str, Any] = Field(..., description="Variables information")
    outputs: Dict[str, Any] = Field(..., description="Outputs information")
    providers: Dict[str, Any] = Field(..., description="Providers information")
    terraform_configured: bool = Field(..., description="Whether Terraform is configured")


class AgentStatus(BaseModel):
    """Agent status model"""
    running: bool = Field(..., description="Whether agent is running")
    session_duration: str = Field(..., description="Session duration")
    conversation_count: int = Field(..., description="Number of conversations")
    ai_processor: Dict[str, Any] = Field(..., description="AI processor information")
    deepagents_available: bool = Field(..., description="Whether DeepAgents is available")
    workflows_available: int = Field(..., description="Number of available workflows")
    hil_status: Dict[str, Any] = Field(..., description="Human-in-the-loop status")
    model_configuration: Dict[str, Any] = Field(default_factory=dict, description="Model configuration")


class TerraformCommandRequest(BaseModel):
    """Request model for Terraform command execution"""
    command: str = Field(..., description="Terraform command to execute")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Command parameters")
    auto_approve: bool = Field(False, description="Whether to auto-approve destructive operations")


class TerraformCommandResponse(BaseModel):
    """Response model for Terraform command execution"""
    success: bool = Field(..., description="Whether command succeeded")
    output: str = Field(..., description="Command output")
    error: Optional[str] = Field(None, description="Error message if failed")
    duration: float = Field(..., description="Command execution duration")
    summary: Optional[Dict[str, Any]] = Field(None, description="Command summary (for plan, etc.)")


class WorkflowRequest(BaseModel):
    """Request model for workflow execution"""
    workflow_name: str = Field(..., description="Name of workflow to execute")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Workflow parameters")


class WorkflowResponse(BaseModel):
    """Response model for workflow execution"""
    success: bool = Field(..., description="Whether workflow succeeded")
    workflow_name: str = Field(..., description="Workflow name")
    result: Optional[Dict[str, Any]] = Field(None, description="Workflow result")
    error: Optional[str] = Field(None, description="Error message if failed")
    plan: Optional[Dict[str, Any]] = Field(None, description="Workflow execution plan")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    uptime: float = Field(..., description="Service uptime in seconds")
    dependencies: Dict[str, bool] = Field(..., description="Dependency status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")


class TokenUsageResponse(BaseModel):
    """Token usage statistics response"""
    total_input_tokens: int = Field(..., description="Total input tokens used")
    total_output_tokens: int = Field(..., description="Total output tokens used")
    total_tokens: int = Field(..., description="Total tokens used")
    cache_creation_tokens: int = Field(..., description="Cache creation tokens")
    cache_read_tokens: int = Field(..., description="Cache read tokens")
    cache_savings_tokens: int = Field(..., description="Cache savings tokens")
    estimated_cost_usd: float = Field(..., description="Estimated cost in USD")
    input_cost_usd: float = Field(..., description="Input cost in USD")
    output_cost_usd: float = Field(..., description="Output cost in USD")
    cache_cost_usd: float = Field(..., description="Cache cost in USD")
    cache_creation_cost_usd: float = Field(..., description="Cache creation cost in USD")


class ConversationHistory(BaseModel):
    """Conversation history model"""
    session_id: str = Field(..., description="Session identifier")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: datetime = Field(..., description="Last activity time")
