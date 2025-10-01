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
