"""
Configuration management for Terraform AI Agent
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """Application configuration"""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_base_url: Optional[str] = Field(None, env="OPENAI_BASE_URL")
    openai_model: str = Field("gpt-3.5-turbo", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(2000, env="OPENAI_MAX_TOKENS")
    
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
    
    def __init__(self, **data):
        # Explicitly read environment variables
        env_data = {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "openai_base_url": os.getenv("OPENAI_BASE_URL"),
            "openai_model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            "openai_max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
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
                timeout=10
            )
            if result.returncode == 0:
                # Extract version from output
                for line in result.stdout.split('\n'):
                    if 'Terraform v' in line:
                        return line.split('Terraform v')[1].strip()
            return None
        except Exception:
            return None
    
    def get_project_config(self) -> Dict[str, Any]:
        """Get project-specific configuration"""
        config_file = Path(self.project_root) / ".tf-agent.yml"
        if config_file.exists():
            import yaml
            with open(config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def is_terraform_project(self) -> bool:
        """Check if current directory is a Terraform project"""
        terraform_files = [
            ".terraform",
            "*.tf",
            "*.tfvars",
            "terraform.tfstate"
        ]
        
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
