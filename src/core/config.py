"""
Configuration management for Terraform AI Agent
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, List

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

from src.core.logger import get_logger

# Load environment variables from .env file
load_dotenv()

logger = get_logger(__name__)


class Config(BaseModel):
    """Application configuration with validation"""

    # AI Provider Configuration
    ai_provider: str = Field("openai_compatible", env="AI_PROVIDER")

    # Claude/Anthropic Configuration (deprecated)
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field("claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(4096, env="ANTHROPIC_MAX_TOKENS")

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o", env="OPENAI_MODEL")
    openai_base_url: str = Field("https://api.openai.com/v1", env="OPENAI_BASE_URL")
    openai_max_tokens: int = Field(4096, env="OPENAI_MAX_TOKENS")

    # OpenAI Compatible Configuration
    openai_compatible_api_key: Optional[str] = Field(None, env="OPENAI_COMPATIBLE_API_KEY")
    openai_compatible_model: str = Field("llama3.1", env="OPENAI_COMPATIBLE_MODEL")
    openai_compatible_base_url: str = Field("http://localhost:11434/v1", env="OPENAI_COMPATIBLE_BASE_URL")
    openai_compatible_max_tokens: int = Field(4096, env="OPENAI_COMPATIBLE_MAX_TOKENS")

    # DeepAgents Configuration
    use_deepagents: bool = Field(False, env="USE_DEEPAGENTS")
    human_in_the_loop: bool = Field(True, env="HUMAN_IN_THE_LOOP")

    # Terraform Configuration
    terraform_path: str = Field("terraform", env="TERRAFORM_PATH")
    terraform_workspace: str = Field("default", env="TERRAFORM_WORKSPACE")

    # Application Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(None, env="LOG_FILE")
    max_file_size: int = Field(10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB

    # UI Configuration
    ui_theme: str = Field("dark", env="UI_THEME")
    auto_refresh: bool = Field(True, env="AUTO_REFRESH")
    refresh_interval: int = Field(30, env="REFRESH_INTERVAL")

    # Project Configuration
    project_root: Optional[str] = Field(None, env="PROJECT_ROOT")
    terraform_dir: str = Field(".", env="TERRAFORM_DIR")

    class Config:
        env_file_encoding = "utf-8"
    
    @field_validator("ai_provider")
    @classmethod
    def validate_ai_provider(cls, v: str) -> str:
        """Validate AI provider selection"""
        valid_providers = ["openai", "openai_compatible"]
        if v.lower() not in valid_providers:
            logger.warning(f"Invalid AI provider '{v}'. Valid options: {valid_providers}. Defaulting to 'openai_compatible'")
            return "openai_compatible"
        return v.lower()
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            logger.warning(f"Invalid log level '{v}'. Defaulting to 'INFO'")
            return "INFO"
        return v.upper()
    
    @field_validator("terraform_path")
    @classmethod
    def validate_terraform_path(cls, v: str) -> str:
        """Validate Terraform CLI path"""
        if not shutil.which(v):
            logger.warning(f"Terraform CLI not found at '{v}'. Please ensure Terraform is installed.")
        return v

    def __init__(self, **data):
        # Explicitly read environment variables
        env_data = {
            "ai_provider": os.getenv("AI_PROVIDER", "openai_compatible"),
            "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
            "anthropic_model": os.getenv(
                "ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"
            ),
            "anthropic_max_tokens": int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096")),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o"),
            "openai_base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "openai_max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "4096")),
            "openai_compatible_api_key": os.getenv("OPENAI_COMPATIBLE_API_KEY"),
            "openai_compatible_model": os.getenv("OPENAI_COMPATIBLE_MODEL", "llama3.1"),
            "openai_compatible_base_url": os.getenv("OPENAI_COMPATIBLE_BASE_URL", "http://localhost:11434/v1"),
            "openai_compatible_max_tokens": int(os.getenv("OPENAI_COMPATIBLE_MAX_TOKENS", "4096")),
            "use_deepagents": os.getenv("USE_DEEPAGENTS", "false").lower() == "true",
            "human_in_the_loop": os.getenv("HUMAN_IN_THE_LOOP", "true").lower() == "true",
            "terraform_path": os.getenv("TERRAFORM_PATH", "terraform"),
            "terraform_workspace": os.getenv("TERRAFORM_WORKSPACE", "default"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "log_file": os.getenv("LOG_FILE"),
            "max_file_size": int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            "ui_theme": os.getenv("UI_THEME", "dark"),
            "auto_refresh": os.getenv("AUTO_REFRESH", "true").lower() == "true",
            "refresh_interval": int(os.getenv("REFRESH_INTERVAL", "30")),
            "project_root": os.getenv("PROJECT_ROOT"),
            "terraform_dir": os.getenv("TERRAFORM_DIR", "."),
        }

        # Merge with provided data
        merged_data = {**env_data, **data}
        super().__init__(**merged_data)

        # Set project root if not specified
        if not self.project_root:
            self.project_root = str(Path.cwd())

        # IMPORTANT: Use terraform_dir directly from .env without modification
        # The .env file should contain the absolute path to the terraform directory
        terraform_dir_from_env = os.getenv("TERRAFORM_DIR")
        if terraform_dir_from_env and terraform_dir_from_env != ".":
            # Use the exact path from .env file
            self.terraform_dir = terraform_dir_from_env
        else:
            # Fallback to current directory if not specified
            self.terraform_dir = str(Path.cwd())

    def check_terraform(self) -> bool:
        """Check if Terraform CLI is available"""
        return shutil.which(self.terraform_path) is not None

    def get_terraform_version(self) -> Optional[str]:
        """Get Terraform version"""
        try:
            import subprocess

            result = subprocess.run(
                [self.terraform_path, "version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                # Extract version from output
                for line in result.stdout.split("\n"):
                    if "Terraform v" in line:
                        return line.split("Terraform v")[1].strip()
            return None
        except Exception:
            return None

    def get_project_config(self) -> Dict[str, Any]:
        """Get project-specific configuration"""
        config_file = Path(self.project_root) / ".tf-agent.yml"
        if config_file.exists():
            import yaml

            with open(config_file) as f:
                return yaml.safe_load(f) or {}
        return {}

    def is_terraform_project(self) -> bool:
        """Check if current directory is a Terraform project"""
        terraform_files = [".terraform", "*.tf", "*.tfvars", "terraform.tfstate"]

        terraform_path = Path(self.terraform_dir)
        for pattern in terraform_files:
            if list(terraform_path.glob(pattern)):
                return True
        return False

    def get_terraform_files(self) -> list:
        """Get all Terraform files in the project"""
        terraform_path = Path(self.terraform_dir)
        tf_files = []

        # Find all .tf files
        for tf_file in terraform_path.rglob("*.tf"):
            if tf_file.is_file():
                tf_files.append(str(tf_file))

        # Find .tfvars files
        for tfvars_file in terraform_path.rglob("*.tfvars"):
            if tfvars_file.is_file():
                tf_files.append(str(tfvars_file))

        return sorted(tf_files)
