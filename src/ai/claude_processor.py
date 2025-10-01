"""
Claude-based AI processor with native tool use for Terraform operations
Uses Anthropic's Claude API with prompt caching for cost efficiency
"""

import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from anthropic.types import Message, TextBlock, ToolUseBlock

from src.core.config import Config
from src.core.logger import get_logger

logger = get_logger(__name__)


class ClaudeProcessor:
    """Claude-based processor with native tool use and prompt caching"""

    def __init__(self, config: Config):
        self.config = config
        self.client = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.terraform_context_cache = None

        # Initialize Claude client if API key is available
        if config.anthropic_api_key:
            try:
                self.client = Anthropic(api_key=config.anthropic_api_key)
                logger.info("Claude client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
                self.client = None
        else:
            logger.warning("Anthropic API key not available, Claude processor disabled")

        # Define tools for Claude to use
        self.tools = self._define_tools()

        # Tool execution handlers
        self.tool_handlers = {}

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

    async def process_query(
        self,
        query: str,
        project_data: Dict[str, Any] = None,
        use_tools: bool = True
    ) -> str:
        """Process user query using Claude with tool use"""

        if not self.client:
            return self._fallback_response(query, project_data)

        try:
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": query
            })

            # Build system context with prompt caching
            system_messages = self._build_system_context(project_data)

            # Call Claude with tools
            response = self.client.messages.create(
                model=self.config.anthropic_model,
                max_tokens=self.config.anthropic_max_tokens,
                system=system_messages,
                tools=self.tools if use_tools else [],
                messages=self.conversation_history
            )

            # Handle tool use if Claude wants to use tools
            if response.stop_reason == "tool_use":
                response_text = await self._handle_tool_use(response, system_messages)
            else:
                # Extract text response
                response_text = self._extract_text_from_response(response)

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

    def _extract_text_from_response(self, response: Message) -> str:
        """Extract text content from Claude's response"""
        text_parts = []

        for block in response.content:
            if isinstance(block, TextBlock):
                text_parts.append(block.text)
            elif hasattr(block, 'text'):
                text_parts.append(block.text)

        return '\n'.join(text_parts) if text_parts else "I couldn't generate a response."

    def _fallback_response(self, query: str, project_data: Dict[str, Any] = None) -> str:
        """Fallback response when Claude is not available"""
        return """I'm currently unable to process your query because the Claude AI API is not configured.

To enable Claude-powered responses:
1. Get an API key from https://console.anthropic.com
2. Add it to your `.env` file as `ANTHROPIC_API_KEY=your-key-here`
3. Restart the application

In the meantime, you can still use basic commands like 'status', 'help', or 'clear'."""

    def clear_memory(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        self.terraform_context_cache = None
        logger.info("Claude conversation memory cleared")

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history.copy()
