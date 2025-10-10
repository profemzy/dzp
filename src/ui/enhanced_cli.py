"""
Enhanced CLI UI components for Terraform AI Agent
"""

import time
from datetime import datetime
from typing import Any, Dict, List

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from src.core.logger import get_logger

logger = get_logger(__name__)


class EnhancedCLI:
    """Enhanced CLI UI components following single responsibility principle"""

    def __init__(self):
        self.console = Console()
        self.colors = {
            "primary": "#00D4AA",
            "secondary": "#FF6B6B",
            "accent": "#4ECDC4",
            "warning": "#FFD93D",
            "info": "#6C63FF",
            "success": "#95E77E",
            "text": "#E8E8E8",
            "muted": "#A0A0A0",
        }
        self.history = InMemoryHistory()
        self.session = None
        self._setup_prompt_session()

    def _setup_prompt_session(self):
        """Setup prompt_toolkit session with history and key bindings"""
        # Define command completion suggestions
        self.command_completer = WordCompleter(
            [
                "help",
                "clear",
                "status",
                "tokens",
                "usage",
                "exit",
                "quit",
                "show all resources",
                "run terraform plan",
                "validate configuration",
                "how many resources",
                "what virtual machines",
                "analyze security",
                "export",
                "import",
            ],
            ignore_case=True,
        )

        # Key bindings
        kb = KeyBindings()

        @kb.add(Keys.ControlC)
        def _(event):
            event.app.exit()

        # Style for prompt
        style = Style.from_dict(
            {
                "prompt": "#00D4AA bold",
            }
        )

        self.session = PromptSession(
            history=self.history,
            completer=self.command_completer,
            key_bindings=kb,
            style=style,
            wrap_lines=True,
        )

    def show_welcome(self):
        """Show enhanced welcome screen"""
        welcome_text = """
[bold #00D4AA]🤖 DZP IAC Agent[/bold #00D4AA]

[dim]Intelligent infrastructure automation powered by Claude AI[/dim]

[bold]What I can do:[/bold]
• 💬 Answer questions about your infrastructure in plain English
• 🔍 Analyze Terraform configurations and resources
• ⚙️  Execute terraform commands (plan, apply, validate, etc.)
• 🧠 Provide recommendations with deep reasoning
• 💰 Track token usage and costs

[bold]Quick Commands:[/bold]
Type [#4ECDC4]help[/#4ECDC4] to see all available commands
Type [#4ECDC4]tokens[/#4ECDC4] to view usage and costs
Type [#4ECDC4]exit[/#4ECDC4] to quit

[dim]💡 Just ask me anything about your Terraform infrastructure![/dim]
        """

        panel = Panel(
            Text.from_markup(welcome_text),
            title="🚀 Welcome",
            title_align="center",
            border_style="#00D4AA",
            padding=(1, 2),
        )

        self.console.print(panel)
        self.console.print()

    def show_project_overview(self, project_data: Dict[str, Any], agent_status: Dict[str, Any] = None):
        """Show enhanced project information"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
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
                    "Infrastructure resources defined",
                )
                table.add_row(
                    "⚙️  Variables",
                    f"[bold]{variables.get('count', 0)}[/bold]",
                    "Configuration variables",
                )
                table.add_row(
                    "📤 Outputs",
                    f"[bold]{outputs.get('count', 0)}[/bold]",
                    "Output values",
                )
                table.add_row(
                    "🔌 Providers",
                    f"[bold]{providers.get('count', 0)}[/bold]",
                    "Cloud providers",
                )

                panel = Panel(
                    table,
                    title="📋 Project Overview",
                    title_align="left",
                    border_style="#00D4AA",
                    padding=(1, 2),
                )

                self.console.print(panel)

                # Show AI configuration status if available
                if agent_status:
                    self.show_ai_status(agent_status)

                # Show resource breakdown if available
                if resources.get("by_type"):
                    self.show_resource_breakdown(resources["by_type"])

            except Exception as e:
                self.console.print(
                    f"[#FF6B6B]❌ Failed to load project info: {e}[/#FF6B6B]"
                )

    def show_resource_breakdown(self, by_type: Dict[str, int]):
        """Show resource breakdown table"""
        table = Table(title="🏗️  Resources by Type", box=box.ROUNDED, show_header=True)
        table.add_column("Resource Type", style="#00D4AA", width=30)
        table.add_column("Count", justify="right", style="#FFFFFF", width=10)
        table.add_column("Progress", width=20)

        total_resources = sum(by_type.values())

        for resource_type, count in sorted(
            by_type.items(), key=lambda x: x[1], reverse=True
        ):
            # Clean up resource type names
            clean_name = resource_type.replace("azurerm_", "").replace("_", " ").title()

            # Create progress bar
            percentage = (count / total_resources) * 100 if total_resources > 0 else 0
            progress_bar = "█" * int(percentage / 10) + "░" * (
                10 - int(percentage / 10)
            )
            progress_color = "#00D4AA" if percentage > 20 else "#FFD93D"

            table.add_row(
                clean_name,
                f"[bold]{count}[/bold]",
                f"[{progress_color}]{progress_bar}[/{progress_color}] {percentage:.1f}%",
            )

        self.console.print(table)
        self.console.print()

    def show_ai_status(self, agent_status: Dict[str, Any]):
        """Show AI configuration and processor status"""
        model_config = agent_status.get("model_config", {})
        processor_info = agent_status.get("ai_processor", {})
        
        # Create AI status table
        table = Table(
            title="🧠 AI Configuration",
            box=box.ROUNDED,
            show_header=True,
            title_style="#6C63FF"
        )
        table.add_column("Configuration", style="#00D4AA", width=25)
        table.add_column("Value", style="#FFFFFF", width=30)
        table.add_column("Status", width=15)

        # Provider information
        provider = model_config.get("provider", "Unknown")
        model = model_config.get("model", "Unknown")
        api_configured = model_config.get("api_configured", False)
        
        # Provider status color
        provider_color = "#95E77E" if api_configured else "#FF6B6B"
        provider_status = "✅ Connected" if api_configured else "❌ Not Configured"
        
        table.add_row(
            "🤖 AI Provider",
            f"[bold]{provider}[/bold]",
            f"[{provider_color}]{provider_status}[/{provider_color}]"
        )
        
        # Model information
        table.add_row(
            "🧠 Model",
            model,
            "[#95E77E]Active[/#95E77E]"
        )
        
        # Available processors
        available_processors = processor_info.get("available_processors", [])
        processor_names = [proc["name"] for proc in available_processors]
        active_processor = agent_status.get("deepagents_available", False)
        
        processor_status = "✅ DeepAgents" if active_processor else "✅ Claude Native"
        processor_color = "#00D4AA" if active_processor else "#4ECDC4"
        
        table.add_row(
            "⚙️  Processors",
            f"{', '.join(processor_names)}",
            f"[{processor_color}]{processor_status}[/{processor_color}]"
        )
        
        # DeepAgents status
        deepagents_available = agent_status.get("deepagents_available", False)
        workflows_count = agent_status.get("workflows_available", 0)
        
        if deepagents_available:
            da_status = f"✅ {workflows_count} workflows"
            da_color = "#95E77E"
        else:
            da_status = "⚠️ Disabled"
            da_color = "#FFD93D"
        
        table.add_row(
            "🔀 DeepAgents",
            "Multi-agent orchestration",
            f"[{da_color}]{da_status}[/{da_color}]"
        )
        
        # Human-in-the-Loop status
        hil_enabled = agent_status.get("hil_status", {}).get("enabled", False)
        
        if hil_enabled:
            hil_status = "✅ Enabled"
            hil_color = "#95E77E"
        else:
            hil_status = "⚠️ Disabled"
            hil_color = "#FFD93D"
        
        table.add_row(
            "👤 Human-in-the-Loop",
            "Approval workflows",
            f"[{hil_color}]{hil_status}[/{hil_color}]"
        )

        self.console.print(table)
        self.console.print()

    def show_command_processing(self, command: str):
        """Show command being processed"""
        panel = Panel(
            f"[dim]Processing command...[/dim]\n\n[bold #00D4AA]{command}[/bold #00D4AA]",
            title="🔍 Command",
            border_style="#4ECDC4",
            padding=(1, 2),
        )
        self.console.print(panel)

    def show_ai_response(self, response: str):
        """Display AI response in a beautiful panel"""
        # Use Markdown for AI responses as they may contain markdown formatting
        panel = Panel(
            Markdown(response),
            title="🤖 AI Response",
            border_style="#00D4AA",
            padding=(1, 2),
        )
        self.console.print(panel)
        self.console.print()

    def show_error(self, error: str):
        """Display error message"""
        panel = Panel(
            f"[#FF6B6B]Error: {error}[/#FF6B6B]",
            title="❌ Error",
            border_style="#FF6B6B",
            padding=(1, 2),
        )
        self.console.print(panel)
        self.console.print()

    def show_help(self):
        """Show enhanced help"""
        help_text = """
[bold #00D4AA]📚 DZP IAC Agent - Help Guide[/bold #00D4AA]

[bold]💬 Ask Questions (Natural Language):[/bold]
• [#4ECDC4]How many resources are defined?[/#4ECDC4]
• [#4ECDC4]Show all virtual machines[/#4ECDC4]
• [#4ECDC4]What is the resource group name?[/#4ECDC4]
• [#4ECDC4]Analyze the security of this infrastructure[/#4ECDC4]
• [#4ECDC4]Should I migrate to Kubernetes?[/#4ECDC4]

[bold]⚙️  Execute Terraform Commands:[/bold]
• [#4ECDC4]run terraform plan[/#4ECDC4]
• [#4ECDC4]validate configuration[/#4ECDC4]
• [#4ECDC4]show terraform state[/#4ECDC4]
• [#4ECDC4]terraform init[/#4ECDC4]

[bold]🛠️  Utility Commands:[/bold]
• [#6C63FF]help[/#6C63FF] - Show this help message
• [#6C63FF]tokens[/#6C63FF] or [#6C63FF]usage[/#6C63FF] - View token usage and costs
• [#6C63FF]status[/#6C63FF] - Show session information
• [#6C63FF]clear[/#6C63FF] - Clear the screen
• [#6C63FF]export <filename>[/#6C63FF] - Export conversation history
• [#6C63FF]import <filename>[/#6C63FF] - Import conversation history
• [#FF6B6B]exit[/#FF6B6B] or [#FF6B6B]quit[/#FF6B6B] - Exit the agent

[bold]💡 Tips:[/bold]
• Use ↑/↓ arrows to navigate command history
• Press Tab for command autocomplete
• Ask follow-up questions naturally ([#95E77E]"what are they?"[/#95E77E], [#95E77E]"tell me more"[/#95E77E])
• Complex questions trigger extended thinking mode automatically 🧠
        """

        panel = Panel(
            Text.from_markup(help_text),
            title="📖 Help",
            title_align="center",
            border_style="#00D4AA",
            padding=(1, 2),
        )

        self.console.print(panel)
        self.console.print()

    def show_status(
        self, session_duration: datetime, conversation_history: List[Dict[str, str]]
    ):
        """Show session status"""
        status_text = f"""
[bold #00D4AA]📊 Session Status[/bold #00D4AA]

[dim]Session Duration:[/dim] [bold]{session_duration.total_seconds():.0f} seconds[/bold]
[dim]Commands Processed:[/dim] [bold]{len(conversation_history) // 2}[/bold]
[dim]Conversation History:[/dim] [bold]{len(conversation_history)} messages[/bold]

[dim]AI Engine:[/dim] [#4ECDC4]Claude AI (Native Tool Use)[/#4ECDC4]
[dim]Model:[/dim] [#95E77E]Claude 3.5 Sonnet[/#95E77E]
[dim]Memory:[/dim] [#6C63FF]Conversation Context Active[/#6C63FF]
        """

        panel = Panel(
            Text.from_markup(status_text),
            title="📈 Status",
            border_style="#4ECDC4",
            padding=(1, 2),
        )

        self.console.print(panel)
        self.console.print()

    def show_goodbye(
        self, session_duration: datetime, conversation_history: List[Dict[str, str]]
    ):
        """Show enhanced goodbye message"""
        goodbye_text = f"""
[bold #00D4AA]👋 Thank you for using DZP IAC Agent![/bold #00D4AA]

[dim]Session Summary:[/dim]
• Session Duration: {session_duration.total_seconds():.0f} seconds
• Commands Processed: {len(conversation_history) // 2}

[dim]See you next time! 🚀[/dim]
        """

        panel = Panel(
            Text.from_markup(goodbye_text),
            title="Goodbye",
            title_align="center",
            border_style="#00D4AA",
            padding=(1, 2),
        )

        self.console.print(panel)

    def show_initial_help(self):
        """Show initial help panel"""
        help_panel = Panel(
            Text.from_markup(
                "[dim]Ask me anything about your Terraform infrastructure, or type[/dim] [#4ECDC4]help[/#4ECDC4] [dim]for examples[/dim]"
            ),
            border_style="#4ECDC4",
            padding=(1, 2),
        )
        self.console.print(help_panel)

    async def get_command_input(self) -> str:
        """Get command input from user with history"""
        try:
            # Clean, professional prompt
            command = await self.session.prompt_async([("class:prompt", "\n> ")])

            command = command.strip()

            # Add to history
            if command and command not in ["exit", "quit"]:
                self.history.append_string(command)

            return command

        except (KeyboardInterrupt, EOFError):
            return "exit"

    def show_knowledge_base_progress(self, description: str):
        """Show knowledge base initialization progress"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task(description, total=None)
            time.sleep(1)

    def clear_screen(self):
        """Clear the console screen"""
        self.console.clear()
