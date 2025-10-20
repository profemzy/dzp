"""
Terraform CLI integration module
"""

import asyncio
import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.logger import get_logger

logger = get_logger(__name__)


class TerraformCommand(Enum):
    """Terraform commands"""

    INIT = "init"
    PLAN = "plan"
    APPLY = "apply"
    DESTROY = "destroy"
    VALIDATE = "validate"
    SHOW = "show"
    STATE_LIST = "state list"
    STATE_SHOW = "state show"
    OUTPUT = "output"
    IMPORT = "import"
    WORKSPACE_NEW = "workspace new"
    WORKSPACE_SELECT = "workspace select"
    WORKSPACE_LIST = "workspace list"
    WORKSPACE_SHOW = "workspace show"


@dataclass
class TerraformResult:
    """Result of a Terraform command execution"""

    success: bool
    return_code: int
    stdout: str
    stderr: str
    command: str
    duration: float


class TerraformCLI:
    """Interface to Terraform CLI with security validations"""

    def __init__(self, terraform_path: str = "terraform", working_dir: str = "."):
        self.terraform_path = terraform_path
        self.working_dir = Path(working_dir).resolve()  # Resolve to absolute path
        self._version_cache: Optional[str] = None
        self._validate_working_dir()
    
    def _validate_working_dir(self) -> None:
        """Validate that the working directory is safe"""
        if not self.working_dir.exists():
            logger.warning(f"Working directory does not exist: {self.working_dir}")
        elif not self.working_dir.is_dir():
            raise ValueError(f"Working directory is not a directory: {self.working_dir}")
    
    def _sanitize_input(self, value: str) -> str:
        """Sanitize user input to prevent command injection"""
        # Remove potentially dangerous characters
        dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "<", ">", "\n", "\r"]
        sanitized = value
        for char in dangerous_chars:
            if char in sanitized:
                logger.warning(f"Removing dangerous character '{char}' from input")
                sanitized = sanitized.replace(char, "")
        return sanitized

    async def _run_command(
        self,
        command: List[str],
        capture_output: bool = True,
        timeout: int = 300,
        input_text: Optional[str] = None,
    ) -> TerraformResult:
        """Run a Terraform command asynchronously"""
        import time

        start_time = time.time()

        full_command = [self.terraform_path] + command

        try:
            logger.debug(
                f"Running command: {' '.join(full_command)} in {self.working_dir}"
            )

            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *full_command,
                cwd=self.working_dir,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None,
                stdin=asyncio.subprocess.PIPE if input_text else None,
            )

            # Handle input if provided
            if input_text:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=input_text.encode()), timeout=timeout
                )
            else:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )

            # Decode outputs
            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""

            return_code = await process.wait()
            duration = time.time() - start_time

            # Check if this is a terraform plan command with detailed_exitcode
            is_plan_with_detailed_exitcode = (
                "-detailed-exitcode" in full_command and
                "plan" in full_command
            )

            # For terraform plan with detailed_exitcode, exit codes 0 and 2 are both success
            if is_plan_with_detailed_exitcode:
                success = return_code in [0, 2]
            else:
                success = return_code == 0

            terraform_result = TerraformResult(
                success=success,
                return_code=return_code,
                stdout=stdout_str,
                stderr=stderr_str,
                command=" ".join(full_command),
                duration=duration,
            )

            if terraform_result.success:
                logger.debug(f"Command completed successfully in {duration:.2f}s")
            else:
                logger.warning(f"Command failed with return code {return_code}")
                if stderr_str:
                    logger.warning(f"Error: {stderr_str}")

            return terraform_result

        except asyncio.TimeoutError:
            logger.error(f"Command timed out after {timeout} seconds")
            process.terminate()
            try:
                await process.wait()
            except:
                process.kill()
            return TerraformResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                command=" ".join(full_command),
                duration=timeout,
            )
        except Exception as e:
            logger.error(f"Failed to run command: {e}")
            return TerraformResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=str(e),
                command=" ".join(full_command),
                duration=0,
            )

    async def get_version(self) -> Optional[str]:
        """Get Terraform version"""
        if self._version_cache is None:
            result = await self._run_command(["version"])
            if result.success:
                # Extract version from output
                match = re.search(r"Terraform v(\d+\.\d+\.\d+)", result.stdout)
                if match:
                    self._version_cache = match.group(1)
                else:
                    self._version_cache = "unknown"
            else:
                self._version_cache = None
        return self._version_cache

    def is_initialized(self) -> bool:
        """Check if Terraform is initialized"""
        terraform_dir = self.working_dir / ".terraform"
        return terraform_dir.exists()

    async def init(self, upgrade: bool = False) -> TerraformResult:
        """Initialize Terraform"""
        command = ["init"]
        if upgrade:
            command.append("-upgrade")

        return await self._run_command(command)

    async def validate(self) -> TerraformResult:
        """Validate Terraform configuration"""
        return await self._run_command(["validate"])

    async def plan(
        self,
        out: Optional[str] = None,
        var_file: Optional[str] = None,
        var: Optional[Dict[str, Any]] = None,
        destroy: bool = False,
        detailed_exitcode: bool = True,
    ) -> TerraformResult:
        """Run terraform plan"""
        command = ["plan"]

        if detailed_exitcode:
            command.append("-detailed-exitcode")

        if out:
            command.extend(["-out", out])

        if var_file:
            command.extend(["-var-file", var_file])

        if var:
            for key, value in var.items():
                command.extend(["-var", f"{key}={value}"])

        if destroy:
            command.append("-destroy")

        return await self._run_command(command)

    async def apply(
        self,
        plan_file: Optional[str] = None,
        var_file: Optional[str] = None,
        var: Optional[Dict[str, Any]] = None,
        auto_approve: bool = False,
    ) -> TerraformResult:
        """Apply Terraform changes"""
        command = ["apply"]

        if plan_file:
            command.append(plan_file)
        else:
            if auto_approve:
                command.append("-auto-approve")

        if var_file:
            command.extend(["-var-file", var_file])

        if var:
            for key, value in var.items():
                command.extend(["-var", f"{key}={value}"])

        return await self._run_command(command)

    async def destroy(
        self,
        var_file: Optional[str] = None,
        var: Optional[Dict[str, Any]] = None,
        auto_approve: bool = False,
    ) -> TerraformResult:
        """Destroy Terraform resources"""
        command = ["destroy"]

        if auto_approve:
            command.append("-auto-approve")

        if var_file:
            command.extend(["-var-file", var_file])

        if var:
            for key, value in var.items():
                command.extend(["-var", f"{key}={value}"])

        return await self._run_command(command)

    async def show(self, plan_file: Optional[str] = None) -> TerraformResult:
        """Show Terraform plan or state"""
        command = ["show"]

        if plan_file:
            command.append(plan_file)

        command.append("-json")

        result = await self._run_command(command)

        # Parse JSON output if successful
        if result.success:
            try:
                result.stdout = json.loads(result.stdout)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON output from terraform show")

        return result

    async def output(
        self, name: Optional[str] = None, json: bool = True
    ) -> TerraformResult:
        """Get Terraform outputs"""
        command = ["output"]

        if json:
            command.append("-json")

        if name:
            command.append(name)

        result = await self._run_command(command)

        # Parse JSON output if successful
        if result.success and json:
            try:
                result.stdout = json.loads(result.stdout)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON output from terraform output")

        return result

    async def state_list(self) -> TerraformResult:
        """List resources in state"""
        result = await self._run_command(["state", "list"])

        if result.success:
            # Parse output into list
            resources = [
                line.strip() for line in result.stdout.split("\n") if line.strip()
            ]
            result.stdout = resources

        return result

    async def state_show(self, resource_address: str) -> TerraformResult:
        """Show resource state"""
        command = ["state", "show", resource_address]
        return await self._run_command(command)

    async def workspace_list(self) -> TerraformResult:
        """List workspaces"""
        result = await self._run_command(["workspace", "list"])

        if result.success:
            # Parse workspace list
            workspaces = []
            for line in result.stdout.split("\n"):
                line = line.strip()
                if line:
                    if line.startswith("* "):
                        workspaces.append(line[2:] + " (current)")
                    else:
                        workspaces.append(line)
            result.stdout = workspaces

        return result

    async def workspace_select(self, workspace: str) -> TerraformResult:
        """Select workspace"""
        return await self._run_command(["workspace", "select", workspace])

    async def workspace_new(self, workspace: str) -> TerraformResult:
        """Create new workspace"""
        return await self._run_command(["workspace", "new", workspace])

    async def import_resource(
        self, resource_address: str, resource_id: str
    ) -> TerraformResult:
        """Import existing resource"""
        command = ["import", resource_address, resource_id]
        return await self._run_command(command)

    def get_plan_summary(self, plan_output: str) -> Dict[str, int]:
        """Parse plan output to get summary"""
        summary = {"add": 0, "change": 0, "destroy": 0}

        # Look for plan summary in output
        lines = plan_output.split("\n")
        for line in lines:
            if "Plan:" in line:
                # Extract numbers from plan summary
                add_match = re.search(r"(\d+) to add", line)
                change_match = re.search(r"(\d+) to change", line)
                destroy_match = re.search(r"(\d+) to destroy", line)

                if add_match:
                    summary["add"] = int(add_match.group(1))
                if change_match:
                    summary["change"] = int(change_match.group(1))
                if destroy_match:
                    summary["destroy"] = int(destroy_match.group(1))
                break

        return summary

    def parse_plan_details(self, plan_output: str) -> Dict[str, Any]:
        """
        Parse detailed resource changes from plan output
        Returns structured information about what resources are being created, changed, or destroyed
        """
        # Strip ANSI escape codes from the output
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        plan_output = ansi_escape.sub('', plan_output)

        details = {
            "resources_to_create": [],
            "resources_to_change": [],
            "resources_to_destroy": [],
            "resources_to_replace": [],
        }

        lines = plan_output.split("\n")
        current_resource = None
        current_action = None
        current_resource_type = None
        attribute_changes = []
        in_resource_block = False

        for i, line in enumerate(lines):
            # Detect resource changes
            # Format: "  # module.x.resource_type.name will be created"
            # Format: "  # module.x.resource_type.name will be updated in-place"
            if " will be created" in line or " will be updated in-place" in line or \
               " will be destroyed" in line or " must be replaced" in line:

                # Save previous resource if any
                if current_resource:
                    resource_info = {
                        "address": current_resource,
                        "resource_type": current_resource_type,
                        "action": current_action,
                        "changes": attribute_changes.copy() if attribute_changes else []
                    }

                    if current_action == "create":
                        details["resources_to_create"].append(resource_info)
                    elif current_action == "update":
                        details["resources_to_change"].append(resource_info)
                    elif current_action == "destroy":
                        details["resources_to_destroy"].append(resource_info)
                    elif current_action == "replace":
                        details["resources_to_replace"].append(resource_info)

                # Extract resource address
                resource_match = re.search(r'#\s+([^\s]+)\s+will be', line)
                if resource_match:
                    current_resource = resource_match.group(1)
                    attribute_changes = []
                    in_resource_block = False

                    if "will be created" in line:
                        current_action = "create"
                    elif "will be updated in-place" in line or "will be changed" in line:
                        current_action = "update"
                    elif "will be destroyed" in line:
                        current_action = "destroy"
                    elif "must be replaced" in line:
                        current_action = "replace"

            # Extract resource type from resource block
            # Format: '  ~ resource "google_container_node_pool" "pools" {'
            elif current_resource and not current_resource_type:
                type_match = re.search(r'resource\s+"([^"]+)"\s+"[^"]+"', line)
                if type_match:
                    current_resource_type = type_match.group(1)
                    in_resource_block = True

            # Detect attribute changes (handles both direct and nested attributes)
            # Format: "      ~ attribute_name = "old" -> "new""
            # Format: "      + attribute_name = "value""
            # Format: "      - attribute_name = "value""
            # Also handles nested blocks like: "      ~ node_config {"
            elif current_resource and in_resource_block:
                # Match attribute changes with -> operator
                arrow_match = re.search(r'^\s*~\s+([^\s=]+)\s*=\s*"?([^"]+)"?\s*->\s*"?([^"]+)"?', line)
                if arrow_match:
                    attr_name = arrow_match.group(1)
                    old_value = arrow_match.group(2).strip('"')
                    new_value = arrow_match.group(3).strip('"')

                    attribute_changes.append({
                        "attribute": attr_name,
                        "change_type": "update",
                        "old_value": old_value,
                        "new_value": new_value
                    })
                else:
                    # Match additions and removals
                    simple_match = re.search(r'^\s*([~+\-])\s+([^\s=]+)\s*=\s*(.+?)$', line.strip())
                    if simple_match:
                        symbol = simple_match.group(1)
                        attr_name = simple_match.group(2)
                        value = simple_match.group(3).strip().strip('"')

                        change_type = {
                            '~': 'update',
                            '+': 'add',
                            '-': 'remove'
                        }.get(symbol, 'unknown')

                        if symbol == '~':
                            # For ~ without ->, we might need to check next lines
                            attribute_changes.append({
                                "attribute": attr_name,
                                "change_type": change_type,
                                "old_value": None,
                                "new_value": value if symbol == '+' else None
                            })
                        elif symbol == '+':
                            attribute_changes.append({
                                "attribute": attr_name,
                                "change_type": change_type,
                                "old_value": None,
                                "new_value": value
                            })
                        elif symbol == '-':
                            attribute_changes.append({
                                "attribute": attr_name,
                                "change_type": change_type,
                                "old_value": value,
                                "new_value": None
                            })

        # Save last resource if any
        if current_resource:
            resource_info = {
                "address": current_resource,
                "resource_type": current_resource_type,
                "action": current_action,
                "changes": attribute_changes.copy() if attribute_changes else []
            }

            if current_action == "create":
                details["resources_to_create"].append(resource_info)
            elif current_action == "update":
                details["resources_to_change"].append(resource_info)
            elif current_action == "destroy":
                details["resources_to_destroy"].append(resource_info)
            elif current_action == "replace":
                details["resources_to_replace"].append(resource_info)

        return details

    def get_resource_changes(self, plan_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract resource changes from plan JSON"""
        changes = []

        if "resource_changes" in plan_json:
            for change in plan_json["resource_changes"]:
                changes.append(
                    {
                        "address": change.get("address", ""),
                        "type": change.get("type", ""),
                        "name": change.get("name", ""),
                        "change": change.get("change", {}),
                        "mode": change.get("mode", ""),
                    }
                )

        return changes
