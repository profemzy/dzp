"""
OpenAI Compatible processor for Terraform operations
Simplified processor that works with OpenAI Compatible endpoints
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from src.core.config import Config
from src.core.logger import get_logger

logger = get_logger(__name__)


class OpenAIProcessor:
    """OpenAI Compatible processor for Terraform operations"""

    def __init__(self, config: Config):
        self.config = config
        self.model = None
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Initialize the model
        self._initialize_model()
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def _initialize_model(self):
        """Initialize OpenAI Compatible model"""
        try:
            self.model = self._create_openai_model()
            logger.info(f"OpenAI Compatible model initialized: {self.config.openai_compatible_model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI Compatible model: {e}")
            raise

    def _create_openai_model(self) -> ChatOpenAI:
        """Create OpenAI Compatible model"""
        api_key = self.config.openai_compatible_api_key or "not-required"
        
        return ChatOpenAI(
            model=self.config.openai_compatible_model,
            api_key=api_key,
            base_url=self.config.openai_compatible_base_url,
            max_tokens=self.config.openai_compatible_max_tokens,
            temperature=0.1,
        )

    def register_tool_handler(self, tool_name: str, handler: callable):
        """Register a tool handler (for compatibility with existing code)"""
        # Store tool handlers for potential future use
        if not hasattr(self, 'tool_handlers'):
            self.tool_handlers = {}
        
        self.tool_handlers[tool_name] = handler
        logger.info(f"Registered tool handler: {tool_name}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    async def _invoke_model_with_retry(self, messages: List) -> Any:
        """Invoke model with retry logic for transient failures"""
        return await self.model.ainvoke(messages)

    async def process_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user request using OpenAI Compatible model
        
        Args:
            request: The user's request
            context: Additional context (files, previous results, etc.)
            
        Returns:
            Response dictionary with messages
        """
        try:
            # Validate input
            if not request or not request.strip():
                raise ValueError("Request cannot be empty")
            
            # Build conversation messages
            messages = self._build_messages(request, context)
            
            # Get response from model with retry
            response = await self._invoke_model_with_retry(messages)
            
            # Update token usage
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                self.total_input_tokens += usage.get('input_tokens', 0)
                self.total_output_tokens += usage.get('output_tokens', 0)
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": request})
            self.conversation_history.append({"role": "assistant", "content": response.content})
            
            return {
                "messages": [response],
                "usage": {
                    "input_tokens": self.total_input_tokens,
                    "output_tokens": self.total_output_tokens,
                    "total_tokens": self.total_input_tokens + self.total_output_tokens
                }
            }
            
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {
                "messages": [AIMessage(content=f"Validation Error: {str(e)}")],
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            return {
                "messages": [AIMessage(content=f"Error: {str(e)}")],
                "error": str(e)
            }

    async def process_query(self, query: str, project_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a query (for compatibility with existing code)
        
        Args:
            query: The user's query
            project_data: Optional project context data
            
        Returns:
            Processed response as string
        """
        try:
            result = await self.process_request(query, project_data)
            
            # Extract the response content from the result
            if isinstance(result, dict) and "messages" in result:
                messages = result["messages"]
                if messages and len(messages) > 0:
                    last_message = messages[-1]
                    if hasattr(last_message, 'content'):
                        return last_message.content
                    elif isinstance(last_message, dict) and "content" in last_message:
                        return last_message["content"]
            
            # Fallback: return string representation
            return str(result)
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error processing query: {str(e)}"

    def _build_messages(self, request: str, context: Optional[Dict[str, Any]] = None) -> List:
        """Build message list for the model"""
        messages = []
        
        # System prompt
        system_prompt = self._get_system_prompt()
        messages.append(SystemMessage(content=system_prompt))
        
        # Add context if provided
        if context:
            context_prompt = self._build_context_prompt(context)
            messages.append(SystemMessage(content=context_prompt))
        
        # User request
        messages.append(HumanMessage(content=request))
        
        return messages

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the model"""
        return """You are an expert Terraform infrastructure assistant. Your role is to help users:

1. **Understand Infrastructure**: Explain Terraform configurations, resources, and their relationships
2. **Execute Operations**: Run terraform commands (plan, apply, validate, init, destroy) when requested
3. **Analyze Changes**: Interpret terraform plan output and explain what changes will occur
4. **Provide Guidance**: Offer best practices, security considerations, and optimization suggestions
5. **Answer Questions**: Respond to queries about resources, variables, outputs, and state

**Important Guidelines**:
- Always explain what a terraform command will do before executing destructive operations
- For 'apply' or 'destroy' commands, confirm user intent and warn about infrastructure changes
- Provide clear, actionable responses with relevant details
- Format responses with proper markdown for readability
- Be security-conscious and highlight potential risks

**Current Context**:
You are working with the Terraform configuration in the project directory.
You have access to analyze .tf files and provide infrastructure insights.
"""

    def _build_context_prompt(self, project_data: Dict[str, Any]) -> str:
        """Build context prompt from project data"""
        if not project_data:
            return ""
        
        context_parts = ["## Current Infrastructure Overview\n"]
        
        # Add resource information
        resources = project_data.get("resources", {})
        if resources:
            context_parts.append(f"**Resources**: {resources.get('count', 0)} total resources defined")
            
            # Add resource breakdown
            by_type = resources.get("by_type", {})
            if by_type:
                context_parts.append("\n**Resource Types**:")
                for resource_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                    context_parts.append(f"- {resource_type}: {count}")
        
        # Add variables
        variables = project_data.get("variables", {})
        if variables:
            context_parts.append(f"\n**Variables**: {variables.get('count', 0)} configuration variables")
        
        # Add outputs
        outputs = project_data.get("outputs", {})
        if outputs:
            context_parts.append(f"\n**Outputs**: {outputs.get('count', 0)} output values")
        
        return "\n".join(context_parts)

    def clear_memory(self):
        """Clear processor memory"""
        self.conversation_history.clear()
        logger.info("Processor memory cleared")

    def get_token_usage_stats(self) -> Dict[str, Any]:
        """Get token usage statistics"""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
        }

    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to the OpenAI Compatible endpoint"""
        try:
            # Simple test message
            test_messages = [
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content="Hello! This is a connection test. Please respond with 'Connection successful.'")
            ]
            
            response = await self.model.ainvoke(test_messages)
            
            return {
                "success": True,
                "provider": "OpenAI Compatible",
                "model": self.config.openai_compatible_model,
                "response": response.content[:100] + "..." if len(response.content) > 100 else response.content
            }
            
        except Exception as e:
            return {
                "success": False,
                "provider": "OpenAI Compatible",
                "error": str(e)
            }
