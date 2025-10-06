"""
Core Terraform AI Agent business logic
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.ai.claude_processor import ClaudeProcessor
from src.core.config import Config
from src.core.logger import get_logger
from src.core.task_engine import Task, TaskEngine, TaskStatus

logger = get_logger(__name__)


class TerraformAgent:
    """Core Terraform AI Agent following single responsibility principle"""

    def __init__(self, config: Config):
        self.config = config
        self.task_engine = TaskEngine(config)

        # Initialize Claude AI processor with native tool use
        logger.info("Initializing Claude processor with native tool use")
        self.ai_processor = ClaudeProcessor(config)
        self._setup_claude_tools()

        self.running = True
        self.conversation_history = []
        self.session_start = datetime.now()

        # Context tracking for intelligent follow-ups
        self.last_command = None
        self.last_result = None
        self.last_plan_summary = None

        # Setup task engine callbacks
        self.task_engine.add_task_callback(self._on_task_update)

        # MCP initialization flag
        self.mcp_initialized = False

    async def initialize_async(self):
        """Async initialization for MCP and other async components"""
        if not self.mcp_initialized:
            try:
                await self.ai_processor.initialize_mcp()
                self.mcp_initialized = True
                logger.info("Agent async initialization complete")
            except Exception as e:
                logger.warning(f"MCP initialization failed (will continue without MCP): {e}")

    def _setup_claude_tools(self):
        """Setup tool handlers for Claude processor"""
        # Register all tool handlers
        self.ai_processor.register_tool_handler(
            "execute_terraform_plan", self._handle_terraform_plan_tool
        )
        self.ai_processor.register_tool_handler(
            "execute_terraform_apply", self._handle_terraform_apply_tool
        )
        self.ai_processor.register_tool_handler(
            "execute_terraform_validate", self._handle_terraform_validate_tool
        )
        self.ai_processor.register_tool_handler(
            "execute_terraform_init", self._handle_terraform_init_tool
        )
        self.ai_processor.register_tool_handler(
            "execute_terraform_destroy", self._handle_terraform_destroy_tool
        )
        self.ai_processor.register_tool_handler(
            "get_resources", self._handle_get_resources_tool
        )
        self.ai_processor.register_tool_handler(
            "analyze_infrastructure", self._handle_analyze_infrastructure_tool
        )
        self.ai_processor.register_tool_handler(
            "get_terraform_state", self._handle_get_state_tool
        )

        logger.info("Claude tool handlers registered successfully")

    # Tool handlers for Claude
    async def _handle_terraform_plan_tool(
        self, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle terraform plan tool execution"""
        detailed = tool_input.get("detailed", True)
        result = await self.task_engine.execute_terraform_plan(detailed=detailed)
        return result

    async def _handle_terraform_apply_tool(
        self, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle terraform apply tool execution"""
        auto_approve = tool_input.get("auto_approve", False)
        result = await self.task_engine.execute_terraform_apply(
            auto_approve=auto_approve
        )
        return result

    async def _handle_terraform_validate_tool(
        self, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle terraform validate tool execution"""
        result = await self.task_engine.execute_terraform_validate()
        return result

    async def _handle_terraform_init_tool(
        self, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle terraform init tool execution"""
        result = await self.task_engine.execute_terraform_init()
        return result

    async def _handle_terraform_destroy_tool(
        self, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle terraform destroy tool execution"""
        auto_approve = tool_input.get("auto_approve", False)
        result = await self.task_engine.execute_terraform_destroy(
            auto_approve=auto_approve
        )
        return result

    async def _handle_get_resources_tool(
        self, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get resources tool execution"""
        resource_type = tool_input.get("resource_type")
        search_query = tool_input.get("search_query")

        project_data = self.get_project_data()
        resources = project_data.get("resources", {})

        # Filter resources if criteria provided
        if resource_type or search_query:
            details = resources.get("details", [])
            filtered = []

            for resource in details:
                if (
                    resource_type
                    and resource_type.lower() not in resource.get("type", "").lower()
                ):
                    continue
                if (
                    search_query
                    and search_query.lower() not in resource.get("name", "").lower()
                ):
                    continue
                filtered.append(resource)

            return {"count": len(filtered), "resources": filtered}

        return resources

    async def _handle_analyze_infrastructure_tool(
        self, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle infrastructure analysis tool execution"""
        analysis_type = tool_input.get("analysis_type", "summary")

        project_data = self.get_project_data()

        if analysis_type == "summary":
            return {
                "resources": project_data.get("resources", {}).get("count", 0),
                "variables": project_data.get("variables", {}).get("count", 0),
                "outputs": project_data.get("outputs", {}).get("count", 0),
                "providers": project_data.get("providers", {}).get("count", 0),
            }
        elif analysis_type == "resources":
            return project_data.get("resources", {})
        elif analysis_type == "variables":
            return project_data.get("variables", {})
        elif analysis_type == "outputs":
            return project_data.get("outputs", {})
        elif analysis_type == "providers":
            return project_data.get("providers", {})
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}

    async def _handle_get_state_tool(
        self, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get terraform state tool execution"""
        list_resources = tool_input.get("list_resources", True)

        if list_resources:
            result = await self.task_engine.execute_terraform_state_list()
            return result
        else:
            return {"message": "State information requested but list_resources=False"}

    def _on_task_update(self, task: Task):
        """Handle task updates"""
        if task.status == TaskStatus.COMPLETED:
            logger.info(f"Task completed: {task.intent.original_query}")
        elif task.status == TaskStatus.FAILED:
            logger.error(f"Task failed: {task.error}")
        elif task.status == TaskStatus.RUNNING:
            logger.info(f"Running: {task.intent.original_query}")

    def get_project_data(self) -> Dict[str, Any]:
        """Get project data from task engine"""
        return self.task_engine.get_project_data()

    def _build_context_aware_prompt(self, command: str) -> str:
        """Build a context-aware prompt for Claude that includes conversation history"""

        # Build context from recent interactions
        context_parts = []

        if self.last_command and self.last_result:
            context_parts.append(f"Previous Command: {self.last_command}")
            context_parts.append(f"Previous Result: {self._format_context_for_claude()}")

            if self.last_plan_summary:
                context_parts.append(f"Plan Summary: {self.last_plan_summary}")

        if self.conversation_history:
            # Get last few conversation exchanges for context
            recent_history = self.conversation_history[-4:]  # Last 2 exchanges
            if recent_history:
                context_parts.append("\nRecent Conversation:")
                for msg in recent_history:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    context_parts.append(f"{role}: {msg['content'][:100]}...")

        context_str = "\n".join(context_parts) if context_parts else "No previous context"

        # Build the full prompt
        full_prompt = f"""
Context:
{context_str}

Current Question: "{command}"

Instructions:
- If this question is related to the previous terraform plan or operations, use that context to provide a specific answer
- If it's a follow-up question about infrastructure, reference the specific resources mentioned
- If there's no relevant context, answer based on the current terraform configuration
- Always be helpful and specific about terraform infrastructure
- If the user is asking about resources that will be created/modified, provide details from the most recent plan if available
"""

        return full_prompt

    def _format_context_for_claude(self) -> str:
        """Format last result for Claude context"""
        if not self.last_result:
            return "No previous result"

        if self.last_command in ["terraform plan", "run terraform plan"]:
            summary = self.last_result.get("summary", {})
            if summary:
                return f"Terraform plan shows {summary.get('add', 0)} resources to add, {summary.get('change', 0)} to change, {summary.get('destroy', 0)} to destroy"
            else:
                return "Terraform plan was executed"

        action = self.last_result.get("action", self.last_command)
        success = self.last_result.get("success", False)
        return f"Last action: {action}, Success: {success}"

    def _detect_simple_system_command(self, command: str) -> Optional[str]:
        """Detect only simple system commands that don't need LLM"""
        command_lower = command.lower().strip()

        # Only handle very basic system commands here
        if command_lower in ["help", "h"]:
            return "help"
        if command_lower == "status":
            return "status"
        if command_lower in ["clear", "cls"]:
            return "clear"
        if command_lower in ["tokens", "usage"]:
            return "tokens"

        return None  # Everything else goes to LLM with context

    def _detect_terraform_command(self, command: str) -> Optional[str]:
        """Detect if command is a terraform operation"""
        command_lower = command.lower()

        # Terraform command patterns
        terraform_commands = {
            "terraform init": "init",
            "terraform plan": "plan",
            "terraform apply": "apply",
            "terraform destroy": "destroy",
            "terraform validate": "validate",
            "terraform show": "show",
            "terraform output": "output",
            "terraform state list": "state_list",
            "run terraform plan": "plan",
            "run terraform apply": "apply",
            "run terraform destroy": "destroy",
            "run terraform init": "init",
            "validate configuration": "validate",
            "validate terraform": "validate",
            "show terraform plan": "show",
            "show terraform state": "state_list",
            "list terraform state": "state_list",
            "terraform state": "state_list",
        }

        for pattern, action in terraform_commands.items():
            if pattern in command_lower:
                return action

        return None

    async def _execute_terraform_command(self, command: str, action: str) -> str:
        """Execute a terraform command and return formatted response"""
        try:
            # Execute the appropriate terraform command
            if action == "init":
                result = await self.task_engine.execute_terraform_init()
            elif action == "plan":
                result = await self.task_engine.execute_terraform_plan()
            elif action == "apply":
                result = await self.task_engine.execute_terraform_apply()
            elif action == "destroy":
                result = await self.task_engine.execute_terraform_destroy()
            elif action == "validate":
                result = await self.task_engine.execute_terraform_validate()
            elif action == "show":
                result = await self.task_engine.execute_terraform_show()
            elif action == "output":
                result = await self.task_engine.execute_terraform_output()
            elif action == "state_list":
                result = await self.task_engine.execute_terraform_state_list()
            else:
                return f"Unknown terraform command: {action}"

            # Format the response
            return self._format_terraform_result(result, action)

        except Exception as e:
            logger.error(f"Error executing terraform command: {e}")
            return f"Error executing terraform command: {str(e)}"

    def _format_terraform_result(self, result: Dict[str, Any], action: str) -> str:
        """Format terraform execution result for user display"""
        if result["success"]:
            response = (
                f"✅ **Terraform {action.replace('_', ' ').title()} Successful**\n\n"
            )

            if action == "plan":
                response += self._format_plan_result(result)
            elif action == "apply":
                response += self._format_apply_result(result)
            elif action == "destroy":
                response += self._format_destroy_result(result)
            elif action == "init":
                response += self._format_init_result(result)
            elif action == "validate":
                response += self._format_validate_result(result)
            elif action == "show":
                response += self._format_show_result(result)
            elif action == "output":
                response += self._format_output_result(result)
            elif action == "state_list":
                response += self._format_state_list_result(result)
            else:
                response += self._format_generic_result(result)

            if result.get("duration"):
                response += f"\n\n**⏱️ Duration:** {result['duration']:.2f} seconds"

        else:
            response = f"❌ **Terraform {action.replace('_', ' ').title()} Failed**\n\n"

            if result.get("error"):
                error_msg = result["error"]
                # Extract meaningful error message
                if isinstance(error_msg, str):
                    lines = error_msg.split("\n")
                    for line in lines:
                        if "Error:" in line or "error:" in line or line.strip():
                            response += f"**Error:** {line.strip()}\n"
                            break
                else:
                    response += f"**Error:** {str(error_msg)}\n"

            # Show only relevant error output, not the full dump
            if result.get("output") and isinstance(result["output"], str):
                output = result["output"]
                # Extract key error information
                error_lines = []
                for line in output.split("\n"):
                    if any(
                        keyword in line.lower()
                        for keyword in ["error:", "failed", "invalid", "missing"]
                    ):
                        if len(error_lines) < 3:  # Limit error lines
                            error_lines.append(line.strip())

                if error_lines:
                    response += "\n**Details:**\n"
                    for line in error_lines:
                        response += f"• {line}\n"

        return response

    def _format_plan_result(self, result: Dict[str, Any]) -> str:
        """Format terraform plan result with intelligent summary"""
        response = ""

        if result.get("summary"):
            summary = result["summary"]
            response += "**📋 Plan Summary:**\n"
            response += f"• ➕ Resources to add: {summary.get('add', 0)}\n"
            response += f"• 🔄 Resources to change: {summary.get('change', 0)}\n"
            response += f"• 🗑️  Resources to destroy: {summary.get('destroy', 0)}\n\n"

        # Analyze the plan output for meaningful insights
        output = result.get("output", "")
        if isinstance(output, str):
            # Provide intelligent interpretation
            if summary := result.get("summary", {}):
                if (
                    summary.get("add", 0) == 0
                    and summary.get("change", 0) == 0
                    and summary.get("destroy", 0) == 0
                ):
                    response += "🎉 **Good news!** Your infrastructure is already up-to-date. No changes are needed.\n\n"
                else:
                    total_changes = (
                        summary.get("add", 0)
                        + summary.get("change", 0)
                        + summary.get("destroy", 0)
                    )
                    response += f"📊 **Analysis:** {total_changes} change{'s' if total_changes != 1 else ''} detected.\n\n"

                    if summary.get("add", 0) > 0:
                        response += f"🆕 **New Resources:** {summary.get('add', 0)} resources will be created.\n"
                    if summary.get("change", 0) > 0:
                        response += f"🔄 **Updates:** {summary.get('change', 0)} resources will be modified.\n"
                    if summary.get("destroy", 0) > 0:
                        response += f"🗑️  **Removals:** {summary.get('destroy', 0)} resources will be destroyed.\n"

                    response += "\n💡 **Next Steps:** Review the changes and run 'terraform apply' when ready.\n\n"

            # Extract key information without showing raw output
            if "Refreshing state" in output:
                response += "🔄 **State Status:** Infrastructure state refreshed successfully.\n"

            if "No changes" in output:
                response += "✅ **Status:** Infrastructure matches configuration.\n"

        return response

    def _format_apply_result(self, result: Dict[str, Any]) -> str:
        """Format terraform apply result"""
        response = "**🚀 Apply Summary:**\n"

        output = result.get("output", "")
        if isinstance(output, str):
            # Extract key apply information
            if "Apply complete!" in output:
                response += "✅ **Status:** Infrastructure successfully updated.\n"

            # Count applied resources
            lines = output.split("\n")
            applied_count = 0
            for line in lines:
                if ":" in line and ("created" in line or "modified" in line):
                    applied_count += 1

            if applied_count > 0:
                response += (
                    f"📦 **Resources Applied:** {applied_count} resources updated.\n"
                )
            else:
                response += "📦 **Resources Applied:** No changes were needed.\n"

        response += "\n🎯 **Result:** Your infrastructure is now synchronized with the configuration.\n"
        return response + "\n"

    def _format_destroy_result(self, result: Dict[str, Any]) -> str:
        """Format terraform destroy result"""
        response = "**💥 Destroy Summary:**\n"

        output = result.get("output", "")
        if isinstance(output, str):
            if "Destroy complete!" in output:
                response += "✅ **Status:** Infrastructure successfully destroyed.\n"
                response += "⚠️  **Warning:** All managed resources have been removed.\n"
            else:
                response += "🔄 **Status:** Infrastructure destruction process.\n"

        response += "\n🔒 **Security Note:** Double-check that all resources have been properly cleaned up.\n"
        return response + "\n"

    def _format_init_result(self, result: Dict[str, Any]) -> str:
        """Format terraform init result"""
        response = "**🔧 Initialization Summary:**\n"

        output = result.get("output", "")
        if isinstance(output, str):
            if "Terraform has been successfully initialized!" in output:
                response += (
                    "✅ **Status:** Terraform workspace initialized successfully.\n"
                )

            # Check for provider installations
            if "Installing" in output and "provider" in output:
                response += "📦 **Providers:** Required providers installed.\n"

            if "Backend" in output and "configured" in output:
                response += "💾 **Backend:** Remote storage configured.\n"

        response += (
            "\n🚀 **Ready:** You can now run terraform plan and apply commands.\n"
        )
        return response + "\n"

    def _format_validate_result(self, result: Dict[str, Any]) -> str:
        """Format terraform validate result"""
        response = "**✅ Validation Summary:**\n"
        response += "🔍 **Status:** Configuration syntax is valid.\n"
        response += "📋 **Result:** No configuration errors found.\n\n"
        response += (
            "💡 **Good to go:** Your terraform files are ready for deployment.\n"
        )
        return response + "\n"

    def _format_show_result(self, result: Dict[str, Any]) -> str:
        """Format terraform show result"""
        response = "**📊 Current State Summary:**\n"

        output = result.get("output", "")
        if isinstance(output, str):
            # Count resources in state
            resource_count = output.count('resource "')
            if resource_count > 0:
                response += (
                    f"📦 **Resources in State:** {resource_count} resources managed.\n"
                )
            else:
                response += (
                    "📦 **Resources in State:** No resources currently managed.\n"
                )

        response += "\n🔍 **Info:** This shows the current infrastructure state.\n"
        return response + "\n"

    def _format_output_result(self, result: Dict[str, Any]) -> str:
        """Format terraform output result"""
        response = "**📤 Output Values:**\n"

        output = result.get("output", "")
        if isinstance(output, str):
            # Parse output values
            lines = output.split("\n")
            for line in lines:
                if "=" in line and not line.strip().startswith("#"):
                    key, value = line.split("=", 1)
                    response += f"• **{key.strip()}:** {value.strip()}\n"

        if not output or "=" not in output:
            response += "📭 **No output values** are currently defined.\n"

        return response + "\n"

    def _format_state_list_result(self, result: Dict[str, Any]) -> str:
        """Format terraform state list result"""
        response = "**📋 State Resources:**\n"

        output = result.get("output", "")
        if isinstance(output, str):
            # Count resources by type
            lines = output.split("\n")
            resource_count = len([line for line in lines if line.strip()])

            if resource_count > 0:
                response += (
                    f"📦 **Total Resources:** {resource_count} resources in state.\n"
                )

                # Show first few as examples
                examples = [line.strip() for line in lines[:5] if line.strip()]
                if examples:
                    response += "\n**Sample Resources:**\n"
                    for example in examples:
                        response += f"• {example}\n"

                if resource_count > 5:
                    response += f"\n... and {resource_count - 5} more resources.\n"
            else:
                response += "📭 **No resources** found in state.\n"

        return response + "\n"

    def _format_generic_result(self, result: Dict[str, Any]) -> str:
        """Format generic terraform result"""
        response = "**📋 Operation Summary:**\n"
        response += "✅ **Status:** Command completed successfully.\n"

        if result.get("duration"):
            response += f"⏱️ **Duration:** {result['duration']:.2f} seconds\n"

        return response + "\n"

    async def process_command_async(self, command: str) -> str:
        """Process a command asynchronously and return the response"""
        if not command.strip():
            return ""

        command_lower = command.lower()

        # Handle system commands
        if command_lower in ["exit", "quit", "q"]:
            self.running = False
            return "exit"

        # Check for simple system commands
        system_cmd = self._detect_simple_system_command(command)
        if system_cmd:
            return system_cmd

        if command_lower.startswith("export"):
            return command

        if command_lower.startswith("import"):
            return command

        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": command})

        try:
            # Check if this is a terraform command
            terraform_action = self._detect_terraform_command(command)
            if terraform_action:
                # Execute terraform command asynchronously
                response = await self._execute_terraform_command(
                    command, terraform_action
                )
                # Update context tracking
                self.last_command = command
                self.last_result = self._extract_result_from_response(response, terraform_action)
                if terraform_action == "plan":
                    self.last_plan_summary = self.last_result.get("summary") if self.last_result else None
            else:
                # Use context-aware LLM processing for ALL non-terraform commands
                context_prompt = self._build_context_aware_prompt(command)
                response = await self.ai_processor.process_query(
                    context_prompt,
                    project_data=self.get_project_data()
                )

            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})

            return response

        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            logger.error(error_msg)
            return error_msg

    # Removed sync process_command method as app uses async version

    def is_running(self) -> bool:
        """Check if agent is still running"""
        return self.running

    def stop(self):
        """Stop the agent"""
        self.running = False

    def _extract_result_from_response(self, response: str, action: str) -> Optional[Dict[str, Any]]:
        """Extract structured result from formatted response"""
        try:
            # This is a simplified extraction - in a real implementation,
            # we'd want to store the raw result from the task engine
            result = {
                "action": f"terraform_{action}",
                "success": "✅" in response or "Successful" in response,
                "summary": {}
            }

            # Extract summary for plan commands
            if action == "plan" and "Plan Summary:" in response:
                # Simple extraction of plan summary
                import re
                add_match = re.search(r"Resources to add: (\d+)", response)
                change_match = re.search(r"Resources to change: (\d+)", response)
                destroy_match = re.search(r"Resources to destroy: (\d+)", response)

                if add_match or change_match or destroy_match:
                    result["summary"] = {
                        "add": int(add_match.group(1)) if add_match else 0,
                        "change": int(change_match.group(1)) if change_match else 0,
                        "destroy": int(destroy_match.group(1)) if destroy_match else 0
                    }

            return result
        except Exception as e:
            logger.error(f"Error extracting result from response: {e}")
            return None

    def get_session_duration(self) -> datetime:
        """Get session duration"""
        return datetime.now() - self.session_start

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()

    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        self.ai_processor.clear_memory()
        # Also clear context tracking
        self.last_command = None
        self.last_result = None
        self.last_plan_summary = None
