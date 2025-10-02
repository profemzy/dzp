#!/usr/bin/env python3
"""
Main entry point for Terraform AI Agent
Follows single responsibility principle with separated concerns
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config import Config
from src.core.agent import TerraformAgent
from src.ui.enhanced_cli import EnhancedCLI
from src.core.logger import get_logger

logger = get_logger(__name__)


class TerraformAgentApp:
    """Main application class coordinating UI and business logic"""
    
    def __init__(self):
        self.config = Config()
        self.agent = TerraformAgent(self.config)
        self.cli = EnhancedCLI()
    
    async def run(self):
        """Run the main application"""
        # Initialize UI
        self.cli.clear_screen()
        self.cli.show_welcome()
        
        # Show project information
        project_data = self.agent.get_project_data()
        self.cli.show_project_overview(project_data)
        
        # Show initial help
        self.cli.show_initial_help()
        
        # Main command loop
        while self.agent.is_running():
            try:
                # Get user input (now async)
                command = await self.cli.get_command_input()

                # Process command asynchronously
                response = await self.agent.process_command_async(command)
                
                # Handle response
                await self._handle_response(response)
                
            except KeyboardInterrupt:
                await self._handle_shutdown()
                break
            except EOFError:
                await self._handle_shutdown()
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                self.cli.show_error(f"Unexpected error: {e}")
    
    async def _handle_response(self, response: str):
        """Handle different types of responses"""
        if response == "exit":
            await self._handle_shutdown()
        elif response == "help":
            self.cli.show_help()
        elif response == "clear":
            self.cli.clear_screen()
        elif response == "status":
            session_duration = self.agent.get_session_duration()
            conversation_history = self.agent.get_conversation_history()
            self.cli.show_status(session_duration, conversation_history)
        elif response == "tokens":
            await self._handle_token_usage()
        elif response.startswith("export"):
            await self._handle_export(response)
        elif response.startswith("import"):
            await self._handle_import(response)
        elif response.startswith("Error"):
            self.cli.show_error(response)
        elif response:
            # Show command processing
            last_command = self.agent.get_conversation_history()[-1]["content"]
            self.cli.show_command_processing(last_command)

            # Show typing indicator and response
            with self.cli.console.status("[bold #00D4AA]🤖 Thinking...[/bold #00D4AA]"):
                await asyncio.sleep(0.1)  # Brief pause for UX

            self.cli.show_ai_response(response)

    async def _handle_token_usage(self):
        """Handle token usage display"""
        if hasattr(self.agent.ai_processor, 'get_token_usage_stats'):
            stats = self.agent.ai_processor.get_token_usage_stats()

            from rich.table import Table
            from rich.panel import Panel
            from rich import box

            table = Table(title="💰 Token Usage & Cost Analysis", box=box.ROUNDED, show_header=True)
            table.add_column("Metric", style="#00D4AA", width=30)
            table.add_column("Value", justify="right", style="#FFFFFF", width=20)

            table.add_row("Total Input Tokens", f"{stats['total_input_tokens']:,}")
            table.add_row("Total Output Tokens", f"{stats['total_output_tokens']:,}")
            table.add_row("Total Tokens", f"{stats['total_tokens']:,}")
            table.add_row("", "")  # Spacer
            table.add_row("Cache Creation Tokens", f"{stats['cache_creation_tokens']:,}", style="#FFD93D")
            table.add_row("Cache Read Tokens", f"{stats['cache_read_tokens']:,}", style="#95E77E")
            table.add_row("Cache Savings", f"{stats['cache_savings_tokens']:,}", style="#95E77E bold")
            table.add_row("", "")  # Spacer
            table.add_row("Estimated Total Cost", f"${stats['estimated_cost_usd']:.4f}", style="#FF6B6B bold")
            table.add_row("  ├─ Input Cost", f"${stats['input_cost_usd']:.4f}")
            table.add_row("  ├─ Output Cost", f"${stats['output_cost_usd']:.4f}")
            table.add_row("  ├─ Cache Read Cost", f"${stats['cache_cost_usd']:.4f}")
            table.add_row("  └─ Cache Creation Cost", f"${stats['cache_creation_cost_usd']:.4f}")

            self.cli.console.print(table)
            self.cli.console.print()
        else:
            self.cli.show_error("Token usage tracking not available for current AI provider")

    async def _handle_export(self, command: str):
        """Handle conversation export"""
        parts = command.split(maxsplit=1)
        file_path = parts[1] if len(parts) > 1 else "conversation_export.json"

        try:
            self.agent.ai_processor.export_conversation(file_path)
            self.cli.console.print(f"[#95E77E]✅ Conversation exported to: {file_path}[/#95E77E]")
        except Exception as e:
            self.cli.show_error(f"Failed to export conversation: {str(e)}")

    async def _handle_import(self, command: str):
        """Handle conversation import"""
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            self.cli.show_error("Usage: import <file_path>")
            return

        file_path = parts[1]

        try:
            self.agent.ai_processor.import_conversation(file_path)
            self.cli.console.print(f"[#95E77E]✅ Conversation imported from: {file_path}[/#95E77E]")
        except Exception as e:
            self.cli.show_error(f"Failed to import conversation: {str(e)}")
    
    async def _handle_shutdown(self):
        """Handle application shutdown"""
        session_duration = self.agent.get_session_duration()
        conversation_history = self.agent.get_conversation_history()
        self.cli.show_goodbye(session_duration, conversation_history)
        self.agent.stop()


async def main():
    """Main function"""
    try:
        app = TerraformAgentApp()
        await app.run()
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        # Try to get the running event loop
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop is running, use asyncio.run()
        asyncio.run(main())
    else:
        # Event loop is already running, schedule the coroutine
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.run(main())
