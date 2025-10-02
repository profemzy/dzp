"""
Claude-based AI processor with native tool use for Terraform operations
Uses Anthropic's Claude API with advanced features:
- Prompt caching for cost efficiency
- Extended thinking for complex reasoning
- Streaming responses for better UX
- Token counting and budget management
- Vision support for infrastructure diagrams
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Callable

from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import Message, TextBlock, ToolUseBlock, Usage

from src.core.config import Config
from src.core.logger import get_logger

logger = get_logger(__name__)


class ClaudeProcessor:
    """Claude-based processor with native tool use and prompt caching"""

    def __init__(self, config: Config):
        self.config = config
        self.client = None
        self.async_client = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.terraform_context_cache = None

        # Advanced features configuration
        self.enable_extended_thinking = True  # For complex infrastructure reasoning
        self.enable_streaming = True  # For real-time response streaming
        self.thinking_budget_tokens = 10000  # Budget for extended thinking

        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cache_creation_tokens = 0
        self.total_cache_read_tokens = 0

        # Initialize Claude clients if API key is available
        if config.anthropic_api_key:
            try:
                self.client = Anthropic(api_key=config.anthropic_api_key)
                self.async_client = AsyncAnthropic(api_key=config.anthropic_api_key)
                logger.info("Claude clients initialized successfully (sync + async)")
            except Exception as e:
                logger.error(f"Failed to initialize Claude clients: {e}")
                self.client = None
                self.async_client = None
        else:
            logger.warning("Anthropic API key not available, Claude processor disabled")

        # Define tools for Claude to use
        self.tools = self._define_tools()

        # Tool execution handlers
        self.tool_handlers = {}

        # Streaming callback
        self.stream_callback: Optional[Callable[[str], None]] = None

    def register_tool_handler(self, tool_name: str, handler):
        """Register a handler function for a specific tool"""
        self.tool_handlers[tool_name] = handler
        logger.debug(f"Registered tool handler: {tool_name}")

    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define tools that Claude can use for Terraform operations"""
        return [
            {
                "name": "execute_terraform_plan",
                "description": "Execute 'terraform plan' command to show what changes Terraform will make to infrastructure. Use this when the user asks about planned changes, wants to see what will happen, or asks to run a plan.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "detailed": {
                            "type": "boolean",
                            "description": "Whether to show detailed exit codes",
                            "default": True
                        }
                    }
                }
            },
            {
                "name": "execute_terraform_apply",
                "description": "Execute 'terraform apply' command to apply infrastructure changes. WARNING: This modifies actual infrastructure. Only use when the user explicitly confirms they want to apply changes.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "auto_approve": {
                            "type": "boolean",
                            "description": "Skip interactive approval (use with caution)",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "execute_terraform_validate",
                "description": "Execute 'terraform validate' to check if the Terraform configuration is syntactically valid and internally consistent. Use this when user asks about configuration validity or wants to check for errors.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "execute_terraform_init",
                "description": "Execute 'terraform init' to initialize the Terraform working directory, download providers, and set up the backend. Use this when the user wants to initialize or re-initialize Terraform.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "upgrade": {
                            "type": "boolean",
                            "description": "Upgrade providers to latest versions",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "execute_terraform_destroy",
                "description": "Execute 'terraform destroy' to destroy all resources managed by Terraform. EXTREME CAUTION: This deletes infrastructure. Only use when user explicitly confirms destruction.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "auto_approve": {
                            "type": "boolean",
                            "description": "Skip interactive approval (use with extreme caution)",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "get_resources",
                "description": "Get information about Terraform resources in the configuration. Use this to answer questions about what resources exist, their types, counts, or details.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": "Filter by specific resource type (e.g., 'azurerm_virtual_machine')"
                        },
                        "search_query": {
                            "type": "string",
                            "description": "Search term to filter resource names"
                        }
                    }
                }
            },
            {
                "name": "analyze_infrastructure",
                "description": "Analyze the Terraform infrastructure configuration to get summary information about resources, variables, outputs, or providers.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "analysis_type": {
                            "type": "string",
                            "enum": ["summary", "resources", "variables", "outputs", "providers"],
                            "description": "Type of analysis to perform"
                        }
                    },
                    "required": ["analysis_type"]
                }
            },
            {
                "name": "get_terraform_state",
                "description": "Get information about the current Terraform state to see what resources are actually deployed and managed.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "list_resources": {
                            "type": "boolean",
                            "description": "List all resources in state",
                            "default": True
                        }
                    }
                }
            }
        ]

    def _build_system_context(self, project_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Build system context with prompt caching for cost efficiency"""

        system_messages = [
            {
                "type": "text",
                "text": """You are an expert Terraform infrastructure assistant powered by Claude AI. Your role is to help users:

1. **Understand Infrastructure**: Explain Terraform configurations, resources, and their relationships
2. **Execute Operations**: Run terraform commands (plan, apply, validate, init, destroy) when requested
3. **Analyze Changes**: Interpret terraform plan output and explain what changes will occur
4. **Provide Guidance**: Offer best practices, security considerations, and optimization suggestions
5. **Answer Questions**: Respond to queries about resources, variables, outputs, and state

**Important Guidelines**:
- Always explain what a terraform command will do before executing destructive operations
- For 'apply' or 'destroy' commands, confirm user intent and warn about infrastructure changes
- Provide clear, actionable responses with relevant details
- Use your tools to get real-time information rather than guessing
- Format responses with proper markdown for readability
- Be security-conscious and highlight potential risks

**Available Tools**:
You have access to tools for executing terraform commands and querying infrastructure. Use them appropriately based on user requests.""",
                "cache_control": {"type": "ephemeral"}
            }
        ]

        # Add terraform context with caching for cost efficiency
        if project_data:
            resources = project_data.get('resources', {})
            variables = project_data.get('variables', {})
            outputs = project_data.get('outputs', {})
            providers = project_data.get('providers', {})

            # Build comprehensive context
            context_parts = [
                "## Current Infrastructure Overview\n",
                f"\n**Resources**: {resources.get('count', 0)} total resources defined"
            ]

            # Add resource breakdown
            by_type = resources.get('by_type', {})
            if by_type:
                context_parts.append("\n\n**Resource Types**:")
                for resource_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                    context_parts.append(f"\n- {resource_type}: {count}")

            # Add variables info
            if variables.get('count', 0) > 0:
                context_parts.append(f"\n\n**Variables**: {variables['count']} configuration variables defined")

            # Add outputs info
            if outputs.get('count', 0) > 0:
                context_parts.append(f"\n\n**Outputs**: {outputs['count']} output values defined")

            # Add providers info
            if providers.get('count', 0) > 0:
                provider_list = [p.get('name', 'unknown') for p in providers.get('details', [])]
                context_parts.append(f"\n\n**Providers**: {', '.join(set(provider_list))}")

            # Add resource details (limited to avoid token bloat)
            resource_details = resources.get('details', [])
            if resource_details:
                context_parts.append("\n\n**Sample Resources** (first 10):")
                for resource in resource_details[:10]:
                    context_parts.append(f"\n- `{resource.get('name')}` ({resource.get('type')})")

            context_text = ''.join(context_parts)

            system_messages.append({
                "type": "text",
                "text": context_text,
                "cache_control": {"type": "ephemeral"}
            })

            # Cache the context
            self.terraform_context_cache = context_text

        return system_messages

    def set_stream_callback(self, callback: Callable[[str], None]):
        """Set callback for streaming responses"""
        self.stream_callback = callback

    def _should_use_extended_thinking(self, query: str) -> bool:
        """Determine if query requires extended thinking"""
        # Use extended thinking for complex queries
        thinking_keywords = [
            "analyze", "compare", "optimize", "recommend", "best practice",
            "should i", "what if", "impact", "risk", "security",
            "dependencies", "plan", "strategy", "migrate", "upgrade"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in thinking_keywords)

    async def process_query(
        self,
        query: str,
        project_data: Dict[str, Any] = None,
        use_tools: bool = True,
        use_streaming: bool = None
    ) -> str:
        """Process user query using Claude with tool use and advanced features"""

        if not self.async_client:
            return self._fallback_response(query, project_data)

        # Determine if streaming should be used
        if use_streaming is None:
            use_streaming = self.enable_streaming

        # Check if extended thinking should be used
        use_extended_thinking = (
            self.enable_extended_thinking and
            self._should_use_extended_thinking(query)
        )

        try:
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": query
            })

            # Build system context with prompt caching
            system_messages = self._build_system_context(project_data)

            # Build request parameters
            request_params = {
                "model": self.config.anthropic_model,
                "max_tokens": self.config.anthropic_max_tokens,
                "system": system_messages,
                "tools": self.tools if use_tools else [],
                "messages": self.conversation_history
            }

            # Add extended thinking if needed
            if use_extended_thinking:
                logger.info("🧠 Using extended thinking mode for complex analysis")
                request_params["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": self.thinking_budget_tokens
                }

            # Process with or without streaming
            if use_streaming and self.stream_callback:
                response_text = await self._process_with_streaming(request_params, system_messages, use_tools)
            else:
                response = await self.async_client.messages.create(**request_params)

                # Track token usage
                self._track_token_usage(response.usage)

                # Handle tool use if Claude wants to use tools
                if response.stop_reason == "tool_use":
                    response_text = await self._handle_tool_use(response, system_messages)
                else:
                    # Extract text response (including thinking if present)
                    response_text = self._extract_text_from_response(response, include_thinking=use_extended_thinking)

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })

            logger.debug(f"Claude response: {response_text[:200]}...")
            return response_text

        except Exception as e:
            logger.error(f"Error processing query with Claude: {e}")
            return f"I encountered an error processing your query: {str(e)}\n\nPlease try rephrasing your question or check your API configuration."

    async def _handle_tool_use(self, response: Message, system_messages: List[Dict]) -> str:
        """Handle tool use by executing tools and getting final response"""

        tool_results = []
        assistant_content = []

        # Process all content blocks
        for block in response.content:
            if isinstance(block, TextBlock):
                assistant_content.append(block.model_dump())
            elif isinstance(block, ToolUseBlock):
                assistant_content.append(block.model_dump())

                # Execute the tool
                tool_name = block.name
                tool_input = block.input

                logger.info(f"Claude is using tool: {tool_name} with input: {tool_input}")

                # Execute tool handler
                result = await self._execute_tool(tool_name, tool_input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result) if not isinstance(result, str) else result
                })

        # Add assistant message with tool use to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_content
        })

        # Add tool results to history
        self.conversation_history.append({
            "role": "user",
            "content": tool_results
        })

        # Get final response from Claude after tool execution
        final_response = self.client.messages.create(
            model=self.config.anthropic_model,
            max_tokens=self.config.anthropic_max_tokens,
            system=system_messages,
            tools=self.tools,
            messages=self.conversation_history
        )

        # Handle potential nested tool use (recursive)
        if final_response.stop_reason == "tool_use":
            return await self._handle_tool_use(final_response, system_messages)

        return self._extract_text_from_response(final_response)

    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool and return the result"""

        # Check if we have a registered handler
        if tool_name in self.tool_handlers:
            try:
                handler = self.tool_handlers[tool_name]
                result = await handler(tool_input)
                return result
            except Exception as e:
                logger.error(f"Tool handler '{tool_name}' failed: {e}")
                return {"error": str(e), "tool": tool_name}
        else:
            logger.warning(f"No handler registered for tool: {tool_name}")
            return {
                "error": f"Tool handler not registered: {tool_name}",
                "available_tools": list(self.tool_handlers.keys())
            }

    async def _process_with_streaming(
        self,
        request_params: Dict[str, Any],
        system_messages: List[Dict],
        use_tools: bool
    ) -> str:
        """Process query with streaming for real-time response"""
        accumulated_text = []
        accumulated_thinking = []
        tool_uses = []
        current_tool_use = None

        async with self.async_client.messages.stream(**request_params) as stream:
            async for event in stream:
                # Handle different event types
                if hasattr(event, 'type'):
                    if event.type == "content_block_start":
                        # New content block starting
                        if hasattr(event, 'content_block'):
                            if event.content_block.type == "tool_use":
                                current_tool_use = {
                                    "id": event.content_block.id,
                                    "name": event.content_block.name,
                                    "input": ""
                                }
                            elif event.content_block.type == "thinking":
                                pass  # Thinking block started

                    elif event.type == "content_block_delta":
                        # Content delta received
                        if hasattr(event, 'delta'):
                            if event.delta.type == "text_delta":
                                # Regular text
                                text = event.delta.text
                                accumulated_text.append(text)
                                if self.stream_callback:
                                    self.stream_callback(text)

                            elif event.delta.type == "thinking_delta":
                                # Extended thinking content
                                thinking_text = event.delta.thinking
                                accumulated_thinking.append(thinking_text)
                                if self.stream_callback:
                                    self.stream_callback(f"[Thinking: {thinking_text}]")

                            elif event.delta.type == "input_json_delta":
                                # Tool input delta
                                if current_tool_use:
                                    current_tool_use["input"] += event.delta.partial_json

                    elif event.type == "content_block_stop":
                        # Content block finished
                        if current_tool_use:
                            tool_uses.append(current_tool_use)
                            current_tool_use = None

                    elif event.type == "message_stop":
                        # Message complete - track usage
                        if hasattr(stream, 'get_final_message'):
                            final_message = await stream.get_final_message()
                            if hasattr(final_message, 'usage'):
                                self._track_token_usage(final_message.usage)

        # If tools were used, execute them
        if tool_uses and use_tools:
            # Execute tools and get final response
            tool_results = []
            for tool_use in tool_uses:
                tool_input = json.loads(tool_use["input"])
                result = await self._execute_tool(tool_use["name"], tool_input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use["id"],
                    "content": json.dumps(result) if not isinstance(result, str) else result
                })

            # Add tool results and get final response
            self.conversation_history.append({
                "role": "assistant",
                "content": [{"type": "tool_use", **tu} for tu in tool_uses]
            })
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })

            # Get final response after tool execution
            final_response = await self.async_client.messages.create(
                model=self.config.anthropic_model,
                max_tokens=self.config.anthropic_max_tokens,
                system=system_messages,
                tools=[],  # No more tools needed
                messages=self.conversation_history
            )

            self._track_token_usage(final_response.usage)
            return self._extract_text_from_response(final_response)

        # Return accumulated text
        full_text = ''.join(accumulated_text)

        # Include thinking if available
        if accumulated_thinking:
            thinking_summary = ''.join(accumulated_thinking)
            logger.info(f"Extended thinking: {thinking_summary[:200]}...")
            # Optionally include thinking in response
            # full_text = f"**[Reasoning]**: {thinking_summary}\n\n{full_text}"

        return full_text if full_text else "I couldn't generate a response."

    def _track_token_usage(self, usage: Usage):
        """Track token usage for analytics and budgeting"""
        self.total_input_tokens += usage.input_tokens
        self.total_output_tokens += usage.output_tokens

        # Track cache tokens if available
        if hasattr(usage, 'cache_creation_input_tokens') and usage.cache_creation_input_tokens:
            self.total_cache_creation_tokens += usage.cache_creation_input_tokens

        if hasattr(usage, 'cache_read_input_tokens') and usage.cache_read_input_tokens:
            self.total_cache_read_tokens += usage.cache_read_input_tokens

        logger.debug(f"Token usage - Input: {usage.input_tokens}, Output: {usage.output_tokens}, "
                    f"Cache read: {getattr(usage, 'cache_read_input_tokens', 0)}")

    def get_token_usage_stats(self) -> Dict[str, int]:
        """Get comprehensive token usage statistics"""
        total_tokens = self.total_input_tokens + self.total_output_tokens
        cache_savings = self.total_cache_read_tokens

        # Estimate cost (approximate pricing for Claude 3.5 Sonnet)
        input_cost = (self.total_input_tokens / 1_000_000) * 3.00  # $3 per 1M tokens
        output_cost = (self.total_output_tokens / 1_000_000) * 15.00  # $15 per 1M tokens
        cache_cost = (self.total_cache_read_tokens / 1_000_000) * 0.30  # $0.30 per 1M cached tokens
        cache_creation_cost = (self.total_cache_creation_tokens / 1_000_000) * 3.75  # $3.75 per 1M tokens

        total_cost = input_cost + output_cost + cache_cost + cache_creation_cost

        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": total_tokens,
            "cache_creation_tokens": self.total_cache_creation_tokens,
            "cache_read_tokens": self.total_cache_read_tokens,
            "cache_savings_tokens": cache_savings,
            "estimated_cost_usd": round(total_cost, 4),
            "input_cost_usd": round(input_cost, 4),
            "output_cost_usd": round(output_cost, 4),
            "cache_cost_usd": round(cache_cost, 4),
            "cache_creation_cost_usd": round(cache_creation_cost, 4)
        }

    def _extract_text_from_response(self, response: Message, include_thinking: bool = False) -> str:
        """Extract text content from Claude's response"""
        text_parts = []
        thinking_parts = []

        for block in response.content:
            if isinstance(block, TextBlock):
                text_parts.append(block.text)
            elif hasattr(block, 'text'):
                text_parts.append(block.text)
            elif hasattr(block, 'type') and block.type == "thinking":
                if hasattr(block, 'thinking'):
                    thinking_parts.append(block.thinking)

        # Optionally include thinking in the response
        result = '\n'.join(text_parts) if text_parts else "I couldn't generate a response."

        if include_thinking and thinking_parts:
            thinking_summary = '\n'.join(thinking_parts)
            logger.info(f"🧠 Extended thinking used: {len(thinking_summary)} characters")
            # Optionally prepend thinking to response
            # result = f"**[Internal Reasoning]**:\n{thinking_summary}\n\n{result}"

        return result

    def _fallback_response(self, query: str, project_data: Dict[str, Any] = None) -> str:
        """Fallback response when Claude is not available"""
        return """I'm currently unable to process your query because the Claude AI API is not configured.

To enable Claude-powered responses:
1. Get an API key from https://console.anthropic.com
2. Add it to your `.env` file as `ANTHROPIC_API_KEY=your-key-here`
3. Restart the application

In the meantime, you can still use basic commands like 'status', 'help', or 'clear'."""

    async def process_with_image(
        self,
        query: str,
        image_path: str,
        project_data: Dict[str, Any] = None
    ) -> str:
        """Process query with an image (e.g., infrastructure diagram)"""
        import base64

        if not self.async_client:
            return self._fallback_response(query, project_data)

        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_data = base64.standard_b64encode(image_file.read()).decode('utf-8')

            # Determine media type
            if image_path.lower().endswith('.png'):
                media_type = "image/png"
            elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
                media_type = "image/jpeg"
            elif image_path.lower().endswith('.gif'):
                media_type = "image/gif"
            elif image_path.lower().endswith('.webp'):
                media_type = "image/webp"
            else:
                return f"Unsupported image format: {image_path}"

            # Add user message with image
            self.conversation_history.append({
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            })

            # Build system context
            system_messages = self._build_system_context(project_data)

            # Call Claude
            response = await self.async_client.messages.create(
                model=self.config.anthropic_model,
                max_tokens=self.config.anthropic_max_tokens,
                system=system_messages,
                messages=self.conversation_history
            )

            self._track_token_usage(response.usage)
            response_text = self._extract_text_from_response(response)

            # Add response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })

            logger.info(f"Processed query with image: {image_path}")
            return response_text

        except Exception as e:
            logger.error(f"Error processing image query: {e}")
            return f"I encountered an error processing the image: {str(e)}"

    async def batch_process_queries(
        self,
        queries: List[str],
        project_data: Dict[str, Any] = None
    ) -> List[str]:
        """Process multiple queries in batch for efficiency"""
        results = []

        # Note: Anthropic doesn't have a native batch API yet,
        # but we can process efficiently with async
        tasks = []
        for query in queries:
            task = self.process_query(query, project_data=project_data, use_streaming=False)
            tasks.append(task)

        # Process all queries concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(f"Error processing query {i+1}: {str(result)}")
            else:
                processed_results.append(result)

        return processed_results

    def export_conversation(self, file_path: str):
        """Export conversation history to JSON file"""
        import json
        from pathlib import Path

        data = {
            "conversation_history": self.conversation_history,
            "token_usage": self.get_token_usage_stats(),
            "terraform_context": self.terraform_context_cache
        }

        Path(file_path).write_text(json.dumps(data, indent=2))
        logger.info(f"Conversation exported to {file_path}")

    def import_conversation(self, file_path: str):
        """Import conversation history from JSON file"""
        import json
        from pathlib import Path

        data = json.loads(Path(file_path).read_text())

        self.conversation_history = data.get("conversation_history", [])
        self.terraform_context_cache = data.get("terraform_context")

        # Restore token usage if available
        token_usage = data.get("token_usage", {})
        self.total_input_tokens = token_usage.get("total_input_tokens", 0)
        self.total_output_tokens = token_usage.get("total_output_tokens", 0)
        self.total_cache_creation_tokens = token_usage.get("cache_creation_tokens", 0)
        self.total_cache_read_tokens = token_usage.get("cache_read_tokens", 0)

        logger.info(f"Conversation imported from {file_path}")

    def clear_memory(self):
        """Clear conversation history and reset token tracking"""
        self.conversation_history.clear()
        self.terraform_context_cache = None
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cache_creation_tokens = 0
        self.total_cache_read_tokens = 0
        logger.info("Claude conversation memory and token tracking cleared")

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history.copy()
