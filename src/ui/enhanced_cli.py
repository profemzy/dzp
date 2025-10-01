"""
Enhanced CLI UI components for Terraform AI Agent
"""

import time
from datetime import datetime
from typing import Dict, List, Any

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table

from src.core.logger import get_logger

logger = get_logger(__name__)


class EnhancedCLI:
    """Enhanced CLI UI components following single responsibility principle"""
    
    def __init__(self):
        self.console = Console()
        self.colors = {
            'primary': '#00D4AA',
            'secondary': '#FF6B6B',
            'accent': '#4ECDC4',
            'warning': '#FFD93D',
            'info': '#6C63FF',
            'success': '#95E77E',
            'text': '#E8E8E8',
            'muted': '#A0A0A0'
        }
    
    def show_welcome(self):
        """Show enhanced welcome screen"""
        welcome_text = """
[bold #00D4AA]🤖 Terraform AI Agent - Enhanced CLI Mode[/bold #00D4AA]

[dim]Your intelligent infrastructure companion powered by LangChain & Azure OpenAI[/dim]

[bold]✨ Features:[/bold]
• 🧠 [link=https://python.langchain.com]LangChain[/link] integration with conversation memory
• 🔍 RAG (Retrieval-Augmented Generation) capabilities  
• 🎯 Context-aware responses
• 🏗️ Terraform infrastructure analysis
• 💬 Natural language interface
• 🎨 Beautiful terminal UI
        """
        
        panel = Panel(
            Markdown(welcome_text),
            title="🚀 Welcome",
            title_align="center",
            border_style="#00D4AA",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_project_overview(self, project_data: Dict[str, Any]):
        """Show enhanced project information"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("📊 Analyzing infrastructure...", total=None)
            
            try:
                progress.update(task, description="✅ Analysis complete")
                time.sleep(0.5)
                
                # Create beautiful project overview
                resources = project_data.get("resources", {})
                variables = project_data.get("variables", {})
                outputs = project_data.get("outputs", {})
                providers = project_data.get("providers", {})
                
                # Create metrics table
                table = Table(show_header=False, box=box.ROUNDED, expand=True)
                table.add_column("Metric", style="#00D4AA", width=20)
                table.add_column("Value", style="#FFFFFF", width=15)
                table.add_column("Description", style="#A0A0A0", width=40)
                
                table.add_row(
                    "📦 Resources",
                    f"[bold]{resources.get('count', 0)}[/bold]",
                    "Infrastructure resources defined"
                )
                table.add_row(
                    "⚙️  Variables", 
                    f"[bold]{variables.get('count', 0)}[/bold]",
                    "Configuration variables"
                )
                table.add_row(
                    "📤 Outputs",
                    f"[bold]{outputs.get('count', 0)}[/bold]", 
                    "Output values"
                )
                table.add_row(
                    "🔌 Providers",
                    f"[bold]{providers.get('count', 0)}[/bold]",
                    "Cloud providers"
                )
                
                panel = Panel(
                    table,
                    title="📋 Project Overview",
                    title_align="left",
                    border_style="#00D4AA",
                    padding=(1, 2)
                )
                
                self.console.print(panel)
                
                # Show resource breakdown if available
                if resources.get("by_type"):
                    self.show_resource_breakdown(resources["by_type"])
                
            except Exception as e:
                self.console.print(f"[#FF6B6B]❌ Failed to load project info: {e}[/#FF6B6B]")
    
    def show_resource_breakdown(self, by_type: Dict[str, int]):
        """Show resource breakdown table"""
        table = Table(title="🏗️  Resources by Type", box=box.ROUNDED, show_header=True)
        table.add_column("Resource Type", style="#00D4AA", width=30)
        table.add_column("Count", justify="right", style="#FFFFFF", width=10)
        table.add_column("Progress", width=20)
        
        total_resources = sum(by_type.values())
        
        for resource_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            # Clean up resource type names
            clean_name = resource_type.replace("azurerm_", "").replace("_", " ").title()
            
            # Create progress bar
            percentage = (count / total_resources) * 100 if total_resources > 0 else 0
            progress_bar = "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10))
            progress_color = "#00D4AA" if percentage > 20 else "#FFD93D"
            
            table.add_row(
                clean_name,
                f"[bold]{count}[/bold]",
                f"[{progress_color}]{progress_bar}[/{progress_color}] {percentage:.1f}%"
            )
        
        self.console.print(table)
        self.console.print()
    
    def show_command_processing(self, command: str):
        """Show command being processed"""
        panel = Panel(
            f"[dim]Processing command...[/dim]\n\n[bold #00D4AA]{command}[/bold #00D4AA]",
            title="🔍 Command",
            border_style="#4ECDC4",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def show_ai_response(self, response: str):
        """Display AI response in a beautiful panel"""
        panel = Panel(
            Markdown(response),
            title="🤖 AI Response",
            border_style="#00D4AA",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()
    
    def show_error(self, error: str):
        """Display error message"""
        panel = Panel(
            f"[#FF6B6B]Error: {error}[/#FF6B6B]",
            title="❌ Error",
            border_style="#FF6B6B",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()
    
    def show_help(self):
        """Show enhanced help"""
        help_text = """
[bold #00D4AA]🤖 Terraform AI Agent Help[/bold #00D4AA]

[dim]Natural Language Commands:[/dim]
• [#4ECDC4]show all virtual machines[/#4ECDC4] - List all VM instances
• [ #4ECDC4]what is the name of the resource group[/#4ECDC4] - Get resource group info
• [ #4ECDC4]run terraform plan[/#4ECDC4] - Execute terraform plan
• [ #4ECDC4]validate configuration[/#4ECDC4] - Check terraform syntax
• [ #4ECDC4]show all resources[/#4ECDC4] - List all resources
• [ #4ECDC4]upgrade the drive size of the ops-vm[/#4ECDC4] - Modify resources

[dim]System Commands:[/dim]
• [ #6C63FF]help, h[/#6C63FF] - Show this help
• [ #6C63FF]clear, cls[/#6C63FF] - Clear screen
• [ #6C63FF]status[/#6C63FF] - Show session status
• [ #FF6B6B]exit, quit, q[/#FF6B6B] - Exit the agent

[dim]💡 Tip:[/dim] You can ask follow-up questions like [bold]what are they?[/bold] or [bold]tell me more[/bold]
        """
        
        panel = Panel(
            Markdown(help_text),
            title="📚 Help",
            title_align="center",
            border_style="#00D4AA",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_status(self, session_duration: datetime, conversation_history: List[Dict[str, str]]):
        """Show session status"""
        status_text = f"""
[bold #00D4AA]📊 Session Status[/bold #00D4AA]

[dim]Session Duration:[/dim] [bold]{session_duration.total_seconds():.0f} seconds[/bold]
[dim]Commands Processed:[/dim] [bold]{len(conversation_history) // 2}[/bold]
[dim]Conversation History:[/dim] [bold]{len(conversation_history)} messages[/bold]

[dim]AI Engine:[/dim] [ #4ECDC4]LangChain + Azure OpenAI[/#4ECDC4]
[dim]Knowledge Base:[/dim] [ #95E77E]RAG Enabled[/#95E77E]
[dim]Memory:[/dim] [ #6C63FF]Conversation Context Active[/#6C63FF]
        """
        
        panel = Panel(
            Markdown(status_text),
            title="📈 Status",
            border_style="#4ECDC4",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def show_goodbye(self, session_duration: datetime, conversation_history: List[Dict[str, str]]):
        """Show enhanced goodbye message"""
        goodbye_text = f"""
[bold #00D4AA]👋 Thank you for using Terraform AI Agent![/bold #00D4AA]

[dim]Session Summary:[/dim]
• Session Duration: {session_duration.total_seconds():.0f} seconds
• Commands Processed: {len(conversation_history) // 2}

[dim]See you next time! 🚀[/dim]
        """
        
        panel = Panel(
            Markdown(goodbye_text),
            title="Goodbye",
            title_align="center",
            border_style="#00D4AA",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def show_initial_help(self):
        """Show initial help panel"""
        help_panel = Panel(
            "[dim]Type your commands in natural language or 'help' for available commands[/dim]",
            border_style="#4ECDC4",
            padding=(1, 2)
        )
        self.console.print(help_panel)
    
    def get_command_input(self) -> str:
        """Get command input from user"""
        try:
            command = Prompt.ask(
                "\n[bold #00D4AA]🔍 Enter your command[/bold #00D4AA]",
                default="help",
                show_default=False
            )
            return command.strip()
        except (KeyboardInterrupt, EOFError):
            return "exit"
    
    def show_knowledge_base_progress(self, description: str):
        """Show knowledge base initialization progress"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task(description, total=None)
            time.sleep(1)
    
    def clear_screen(self):
        """Clear the console screen"""
        self.console.clear()
