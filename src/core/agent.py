"""
Core Terraform AI Agent business logic
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.core.config import Config
from src.core.task_engine import TaskEngine, Task, TaskStatus
from src.core.logger import get_logger
from src.ai.langchain_processor import LangChainProcessor

logger = get_logger(__name__)


class TerraformAgent:
    """Core Terraform AI Agent following single responsibility principle"""
    
    def __init__(self, config: Config):
        self.config = config
        self.task_engine = TaskEngine(config)
        self.langchain_processor = LangChainProcessor(config)
        self.running = True
        self.conversation_history = []
        self.session_start = datetime.now()
        
        # Setup task engine callbacks
        self.task_engine.add_task_callback(self._on_task_update)
        
        # Setup RAG knowledge base
        self._setup_knowledge_base()
    
    def _setup_knowledge_base(self):
        """Setup RAG knowledge base with Terraform files"""
        try:
            terraform_files = []
            project_root = Path(self.config.project_root)
            
            # Find all Terraform files
            for tf_file in project_root.rglob("*.tf"):
                terraform_files.append(str(tf_file))
            
            if terraform_files:
                self.langchain_processor.create_knowledge_base(terraform_files)
                logger.info(f"Knowledge base created with {len(terraform_files)} Terraform files")
            else:
                logger.warning("No Terraform files found")
                
        except Exception as e:
            logger.error(f"Failed to create knowledge base: {e}")
    
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
    
    def _detect_terraform_command(self, command: str) -> Optional[str]:
        """Detect if command is a terraform operation"""
        command_lower = command.lower()
        
        # Terraform command patterns
        terraform_commands = {
            'terraform init': 'init',
            'terraform plan': 'plan',
            'terraform apply': 'apply',
            'terraform destroy': 'destroy',
            'terraform validate': 'validate',
            'terraform show': 'show',
            'terraform output': 'output',
            'terraform state list': 'state_list',
            'run terraform plan': 'plan',
            'run terraform apply': 'apply',
            'run terraform destroy': 'destroy',
            'run terraform init': 'init',
            'validate configuration': 'validate',
            'validate terraform': 'validate',
            'show terraform plan': 'show',
            'show terraform state': 'state_list',
            'list terraform state': 'state_list',
            'terraform state': 'state_list'
        }
        
        for pattern, action in terraform_commands.items():
            if pattern in command_lower:
                return action
        
        return None
    
    async def _execute_terraform_command(self, command: str, action: str) -> str:
        """Execute a terraform command and return formatted response"""
        try:
            # Execute the appropriate terraform command
            if action == 'init':
                result = await self.task_engine.execute_terraform_init()
            elif action == 'plan':
                result = await self.task_engine.execute_terraform_plan()
            elif action == 'apply':
                result = await self.task_engine.execute_terraform_apply()
            elif action == 'destroy':
                result = await self.task_engine.execute_terraform_destroy()
            elif action == 'validate':
                result = await self.task_engine.execute_terraform_validate()
            elif action == 'show':
                result = await self.task_engine.execute_terraform_show()
            elif action == 'output':
                result = await self.task_engine.execute_terraform_output()
            elif action == 'state_list':
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
        if result['success']:
            response = f"✅ **Terraform {action.replace('_', ' ').title()} Successful**\n\n"
            
            if action == 'plan':
                response += self._format_plan_result(result)
            elif action == 'apply':
                response += self._format_apply_result(result)
            elif action == 'destroy':
                response += self._format_destroy_result(result)
            elif action == 'init':
                response += self._format_init_result(result)
            elif action == 'validate':
                response += self._format_validate_result(result)
            elif action == 'show':
                response += self._format_show_result(result)
            elif action == 'output':
                response += self._format_output_result(result)
            elif action == 'state_list':
                response += self._format_state_list_result(result)
            else:
                response += self._format_generic_result(result)
            
            if result.get('duration'):
                response += f"\n\n**⏱️ Duration:** {result['duration']:.2f} seconds"
            
        else:
            response = f"❌ **Terraform {action.replace('_', ' ').title()} Failed**\n\n"
            
            if result.get('error'):
                error_msg = result['error']
                # Extract meaningful error message
                if isinstance(error_msg, str):
                    lines = error_msg.split('\n')
                    for line in lines:
                        if 'Error:' in line or 'error:' in line or line.strip():
                            response += f"**Error:** {line.strip()}\n"
                            break
                else:
                    response += f"**Error:** {str(error_msg)}\n"
            
            # Show only relevant error output, not the full dump
            if result.get('output') and isinstance(result['output'], str):
                output = result['output']
                # Extract key error information
                error_lines = []
                for line in output.split('\n'):
                    if any(keyword in line.lower() for keyword in ['error:', 'failed', 'invalid', 'missing']):
                        if len(error_lines) < 3:  # Limit error lines
                            error_lines.append(line.strip())
                
                if error_lines:
                    response += f"\n**Details:**\n"
                    for line in error_lines:
                        response += f"• {line}\n"
        
        return response
    
    def _format_plan_result(self, result: Dict[str, Any]) -> str:
        """Format terraform plan result with intelligent summary"""
        response = ""
        
        if result.get('summary'):
            summary = result['summary']
            response += f"**📋 Plan Summary:**\n"
            response += f"• ➕ Resources to add: {summary.get('add', 0)}\n"
            response += f"• 🔄 Resources to change: {summary.get('change', 0)}\n"
            response += f"• 🗑️  Resources to destroy: {summary.get('destroy', 0)}\n\n"
        
        # Analyze the plan output for meaningful insights
        output = result.get('output', '')
        if isinstance(output, str):
            # Provide intelligent interpretation
            if summary := result.get('summary', {}):
                if summary.get('add', 0) == 0 and summary.get('change', 0) == 0 and summary.get('destroy', 0) == 0:
                    response += "🎉 **Good news!** Your infrastructure is already up-to-date. No changes are needed.\n\n"
                else:
                    total_changes = summary.get('add', 0) + summary.get('change', 0) + summary.get('destroy', 0)
                    response += f"📊 **Analysis:** {total_changes} change{'s' if total_changes != 1 else ''} detected.\n\n"
                    
                    if summary.get('add', 0) > 0:
                        response += f"🆕 **New Resources:** {summary.get('add', 0)} resources will be created.\n"
                    if summary.get('change', 0) > 0:
                        response += f"🔄 **Updates:** {summary.get('change', 0)} resources will be modified.\n"
                    if summary.get('destroy', 0) > 0:
                        response += f"🗑️  **Removals:** {summary.get('destroy', 0)} resources will be destroyed.\n"
                    
                    response += "\n💡 **Next Steps:** Review the changes and run 'terraform apply' when ready.\n\n"
            
            # Extract key information without showing raw output
            if 'Refreshing state' in output:
                response += "🔄 **State Status:** Infrastructure state refreshed successfully.\n"
            
            if 'No changes' in output:
                response += "✅ **Status:** Infrastructure matches configuration.\n"
        
        return response
    
    def _format_apply_result(self, result: Dict[str, Any]) -> str:
        """Format terraform apply result"""
        response = "**🚀 Apply Summary:**\n"
        
        output = result.get('output', '')
        if isinstance(output, str):
            # Extract key apply information
            if 'Apply complete!' in output:
                response += "✅ **Status:** Infrastructure successfully updated.\n"
            
            # Count applied resources
            lines = output.split('\n')
            applied_count = 0
            for line in lines:
                if ':' in line and ('created' in line or 'modified' in line):
                    applied_count += 1
            
            if applied_count > 0:
                response += f"📦 **Resources Applied:** {applied_count} resources updated.\n"
            else:
                response += "📦 **Resources Applied:** No changes were needed.\n"
        
        response += "\n🎯 **Result:** Your infrastructure is now synchronized with the configuration.\n"
        return response + "\n"
    
    def _format_destroy_result(self, result: Dict[str, Any]) -> str:
        """Format terraform destroy result"""
        response = "**💥 Destroy Summary:**\n"
        
        output = result.get('output', '')
        if isinstance(output, str):
            if 'Destroy complete!' in output:
                response += "✅ **Status:** Infrastructure successfully destroyed.\n"
                response += "⚠️  **Warning:** All managed resources have been removed.\n"
            else:
                response += "🔄 **Status:** Infrastructure destruction process.\n"
        
        response += "\n🔒 **Security Note:** Double-check that all resources have been properly cleaned up.\n"
        return response + "\n"
    
    def _format_init_result(self, result: Dict[str, Any]) -> str:
        """Format terraform init result"""
        response = "**🔧 Initialization Summary:**\n"
        
        output = result.get('output', '')
        if isinstance(output, str):
            if 'Terraform has been successfully initialized!' in output:
                response += "✅ **Status:** Terraform workspace initialized successfully.\n"
            
            # Check for provider installations
            if 'Installing' in output and 'provider' in output:
                response += "📦 **Providers:** Required providers installed.\n"
            
            if 'Backend' in output and 'configured' in output:
                response += "💾 **Backend:** Remote storage configured.\n"
        
        response += "\n🚀 **Ready:** You can now run terraform plan and apply commands.\n"
        return response + "\n"
    
    def _format_validate_result(self, result: Dict[str, Any]) -> str:
        """Format terraform validate result"""
        response = "**✅ Validation Summary:**\n"
        response += "🔍 **Status:** Configuration syntax is valid.\n"
        response += "📋 **Result:** No configuration errors found.\n\n"
        response += "💡 **Good to go:** Your terraform files are ready for deployment.\n"
        return response + "\n"
    
    def _format_show_result(self, result: Dict[str, Any]) -> str:
        """Format terraform show result"""
        response = "**📊 Current State Summary:**\n"
        
        output = result.get('output', '')
        if isinstance(output, str):
            # Count resources in state
            resource_count = output.count('resource "')
            if resource_count > 0:
                response += f"📦 **Resources in State:** {resource_count} resources managed.\n"
            else:
                response += "📦 **Resources in State:** No resources currently managed.\n"
        
        response += "\n🔍 **Info:** This shows the current infrastructure state.\n"
        return response + "\n"
    
    def _format_output_result(self, result: Dict[str, Any]) -> str:
        """Format terraform output result"""
        response = "**📤 Output Values:**\n"
        
        output = result.get('output', '')
        if isinstance(output, str):
            # Parse output values
            lines = output.split('\n')
            for line in lines:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.split('=', 1)
                    response += f"• **{key.strip()}:** {value.strip()}\n"
        
        if not output or '=' not in output:
            response += "📭 **No output values** are currently defined.\n"
        
        return response + "\n"
    
    def _format_state_list_result(self, result: Dict[str, Any]) -> str:
        """Format terraform state list result"""
        response = "**📋 State Resources:**\n"
        
        output = result.get('output', '')
        if isinstance(output, str):
            # Count resources by type
            lines = output.split('\n')
            resource_count = len([line for line in lines if line.strip()])
            
            if resource_count > 0:
                response += f"📦 **Total Resources:** {resource_count} resources in state.\n"
                
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
        
        if result.get('duration'):
            response += f"⏱️ **Duration:** {result['duration']:.2f} seconds\n"
        
        return response + "\n"
    
    async def process_command_async(self, command: str) -> str:
        """Process a command asynchronously and return the response"""
        if not command.strip():
            return ""
        
        command_lower = command.lower()
        
        # Handle system commands
        if command_lower in ['exit', 'quit', 'q']:
            self.running = False
            return "exit"
        
        if command_lower in ['help', 'h']:
            return "help"
        
        if command_lower in ['clear', 'cls']:
            return "clear"
        
        if command_lower == 'status':
            return "status"
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": command})
        
        try:
            # Check if this is a terraform command
            terraform_action = self._detect_terraform_command(command)
            if terraform_action:
                # Execute terraform command asynchronously
                response = await self._execute_terraform_command(command, terraform_action)
            else:
                # Use LangChain for processing with project data
                project_data = self.get_project_data()
                response = self.langchain_processor.process_query(command, project_data=project_data)
            
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def process_command(self, command: str) -> str:
        """Process a command and return the response (synchronous wrapper)"""
        if not command.strip():
            return ""
        
        command_lower = command.lower()
        
        # Handle system commands
        if command_lower in ['exit', 'quit', 'q']:
            self.running = False
            return "exit"
        
        if command_lower in ['help', 'h']:
            return "help"
        
        if command_lower in ['clear', 'cls']:
            return "clear"
        
        if command_lower == 'status':
            return "status"
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": command})
        
        try:
            # Check if this is a terraform command
            terraform_action = self._detect_terraform_command(command)
            if terraform_action:
                # For terraform commands, we need to run in async context
                # This is a fallback for non-async usage
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is already running, create a new one
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, self._execute_terraform_command(command, terraform_action))
                            response = future.result()
                    else:
                        response = loop.run_until_complete(self._execute_terraform_command(command, terraform_action))
                except:
                    # Final fallback - try to create new loop
                    response = asyncio.run(self._execute_terraform_command(command, terraform_action))
            else:
                # Use LangChain for processing with project data
                project_data = self.get_project_data()
                response = self.langchain_processor.process_query(command, project_data=project_data)
            
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def is_running(self) -> bool:
        """Check if agent is still running"""
        return self.running
    
    def stop(self):
        """Stop the agent"""
        self.running = False
    
    def get_session_duration(self) -> datetime:
        """Get session duration"""
        return datetime.now() - self.session_start
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        self.langchain_processor.clear_memory()
