"""
Enhanced AI processor that uses OpenAI Compatible endpoints and DeepAgents
"""

import asyncio
from typing import Any, Dict, List, Optional

from src.ai.openai_processor import OpenAIProcessor
from src.ai.deepagents_processor import DeepAgentsProcessor
from src.ai.model_factory import ModelFactory
from src.core.config import Config
from src.core.logger import get_logger

logger = get_logger(__name__)


class EnhancedAIProcessor:
    """Enhanced AI processor supporting multiple backends and providers"""

    def __init__(self, config: Config):
        self.config = config
        self.openai_processor = None
        self.deepagents_processor = None
        
        # Initialize processors based on configuration
        self._initialize_processors()

    def _initialize_processors(self):
        """Initialize appropriate processors based on configuration"""
        
        # Initialize OpenAI Compatible processor
        try:
            if self.config.ai_provider in ["openai", "openai_compatible"]:
                if self.config.ai_provider == "openai" and self.config.openai_api_key:
                    self.openai_processor = OpenAIProcessor(self.config)
                    logger.info("OpenAI processor initialized")
                elif self.config.ai_provider == "openai_compatible":
                    self.openai_processor = OpenAIProcessor(self.config)
                    logger.info("OpenAI Compatible processor initialized")
                else:
                    logger.warning("OpenAI processor not initialized (missing API key)")
            else:
                logger.warning(f"Unsupported AI provider: {self.config.ai_provider}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI processor: {e}")

        # Initialize DeepAgents processor if enabled
        if self.config.use_deepagents:
            try:
                # We'll create this later when we have access to terraform tools
                logger.info("DeepAgents processor will be initialized when terraform tools are available")
            except Exception as e:
                logger.warning(f"Failed to initialize DeepAgents processor: {e}")

    def initialize_deepagents(self, terraform_tools: List[Any]):
        """Initialize DeepAgents processor with terraform tools"""
        if self.config.use_deepagents:
            try:
                self.deepagents_processor = DeepAgentsProcessor(self.config, terraform_tools)
                logger.info("DeepAgents processor initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DeepAgents processor: {e}")
                self.deepagents_processor = None

    def get_active_processor(self) -> Optional[str]:
        """Get the name of the active processor"""
        if self.config.use_deepagents and self.deepagents_processor:
            return "deepagents"
        elif self.openai_processor:
            return "openai"
        else:
            return None

    def get_processor_info(self) -> Dict[str, Any]:
        """Get information about available processors"""
        info = {
            "ai_provider": self.config.ai_provider,
            "use_deepagents": self.config.use_deepagents,
            "model_info": ModelFactory.get_model_info(self.config),
            "available_processors": [],
        }

        if self.openai_processor:
            info["available_processors"].append({
                "name": "openai",
                "type": "OpenAI Compatible",
                "features": ["Tool calling", "Streaming", "Multiple model support"]
            })

        if self.deepagents_processor:
            info["available_processors"].append({
                "name": "deepagents",
                "type": "Multi-Agent Orchestration",
                "features": ["Todo planning", "Sub-agents", "Human-in-the-loop", "Virtual file system"]
            })
            info.update(self.deepagents_processor.get_agent_info())

        return info

    async def process_request(
        self, 
        request: str, 
        context: Optional[Dict[str, Any]] = None,
        stream_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Process a request using the appropriate processor
        
        Args:
            request: The user's request
            context: Additional context (files, previous results, etc.)
            stream_callback: Callback for streaming responses (OpenAI-compatible models)
            
        Returns:
            Processor response
        """
        
        # Choose the appropriate processor
        if self.config.use_deepagents and self.deepagents_processor:
            logger.info("Using DeepAgents processor for request")
            return await self.deepagents_processor.process_request(request, context)
        
        elif self.openai_processor:
            logger.info("Using OpenAI Compatible processor for request")
            # Use OpenAI processor 
            return await self.openai_processor.process_request(request, context)
        
        else:
            error_msg = "No AI processor available. Check configuration."
            logger.error(error_msg)
            return {
                "error": error_msg,
                "messages": [{"role": "assistant", "content": error_msg}]
            }

    def set_stream_callback(self, callback: callable):
        """
        Set streaming callback for processors that support it

        Args:
            callback: Function to call with each streamed chunk
        """
        if self.openai_processor and hasattr(self.openai_processor, 'set_stream_callback'):
            self.openai_processor.set_stream_callback(callback)
            logger.info("Stream callback set on OpenAI processor")

    def supports_streaming(self) -> bool:
        """Check if the current processor supports streaming"""
        return self.openai_processor is not None

    def supports_deepagents(self) -> bool:
        """Check if DeepAgents is available and configured"""
        return self.config.use_deepagents and self.deepagents_processor is not None

    def switch_processor(self, use_deepagents: Optional[bool] = None) -> bool:
        """
        Switch between processors
        
        Args:
            use_deepagents: Force use of DeepAgents (None = use config default)
            
        Returns:
            True if switch was successful
        """
        
        target_deepagents = use_deepagents if use_deepagents is not None else self.config.use_deepagents
        
        if target_deepagents and not self.deepagents_processor:
            logger.error("Cannot switch to DeepAgents: processor not initialized")
            return False
        
        if not target_deepagents and not self.openai_processor:
            logger.error("Cannot switch to OpenAI: processor not initialized")
            return False
        
        logger.info(f"Switching to {'DeepAgents' if target_deepagents else 'OpenAI'} processor")
        # Note: We're not actually changing the processor here, just logging
        # The actual switching happens at process_request time based on config
        
        return True

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration"""
        return ModelFactory.get_model_info(self.config)

    def register_tool_handler(self, tool_name: str, handler: callable):
        """
        Register a tool handler for compatibility with existing DZP code
        
        Args:
            tool_name: Name of the tool
            handler: Handler function for the tool
        """
        # Store tool handlers for potential future use
        if not hasattr(self, 'tool_handlers'):
            self.tool_handlers = {}
        
        self.tool_handlers[tool_name] = handler
        logger.info(f"Registered tool handler: {tool_name}")

    async def process_query(self, query: str, project_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a query using the appropriate processor (for compatibility)
        
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

    def clear_memory(self):
        """Clear processor memory (for compatibility)"""
        if self.openai_processor and hasattr(self.openai_processor, 'clear_memory'):
            self.openai_processor.clear_memory()
        
        logger.info("Processor memory cleared")

    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to the configured AI provider"""
        try:
            model = ModelFactory.create_model(self.config)
            
            # Simple test message
            test_messages = [{"role": "user", "content": "Hello! This is a connection test."}]
            
            if hasattr(model, 'ainvoke'):
                response = await model.ainvoke(test_messages)
            else:
                response = model.invoke(test_messages)
            
            return {
                "success": True,
                "provider": self.config.ai_provider,
                "model": getattr(self.config, f"{self.config.ai_provider}_model", "unknown"),
                "response": str(response)[:100] + "..." if len(str(response)) > 100 else str(response)
            }
            
        except Exception as e:
            return {
                "success": False,
                "provider": self.config.ai_provider,
                "error": str(e)
            }
