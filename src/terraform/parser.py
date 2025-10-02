"""
Terraform code parser and analyzer
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from hcl2 import loads as hcl_loads

from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TerraformResource:
    """Represents a Terraform resource"""

    resource_type: str
    resource_name: str
    config: Dict[str, Any]
    file_path: str
    line_number: Optional[int] = None


@dataclass
class TerraformVariable:
    """Represents a Terraform variable"""

    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    default: Any = None
    file_path: str = ""


@dataclass
class TerraformOutput:
    """Represents a Terraform output"""

    name: str
    value: Any
    description: Optional[str] = None
    file_path: str = ""


@dataclass
class TerraformProvider:
    """Represents a Terraform provider"""

    name: str
    alias: Optional[str] = None
    config: Dict[str, Any] = None
    file_path: str = ""


class TerraformParser:
    """Parser for Terraform configuration files"""

    def __init__(self, terraform_dir: str = "."):
        self.terraform_dir = Path(terraform_dir)
        self.resources: List[TerraformResource] = []
        self.variables: List[TerraformVariable] = []
        self.outputs: List[TerraformOutput] = []
        self.providers: List[TerraformProvider] = []
        self.modules: List[Dict[str, Any]] = []
        self.data_sources: List[TerraformResource] = []

    def parse_project(self) -> Dict[str, Any]:
        """Parse entire Terraform project"""
        logger.info(f"Parsing Terraform project in {self.terraform_dir}")

        # Reset collections
        self.resources.clear()
        self.variables.clear()
        self.outputs.clear()
        self.providers.clear()
        self.modules.clear()
        self.data_sources.clear()

        # Find all .tf files
        tf_files = list(self.terraform_dir.rglob("*.tf"))

        for tf_file in tf_files:
            if tf_file.is_file():
                self._parse_file(tf_file)

        return self.get_project_summary()

    def _parse_file(self, file_path: Path) -> None:
        """Parse a single Terraform file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse HCL content
            parsed = hcl_loads(content)

            # Extract different sections
            self._extract_resources(parsed, str(file_path))
            self._extract_variables(parsed, str(file_path))
            self._extract_outputs(parsed, str(file_path))
            self._extract_providers(parsed, str(file_path))
            self._extract_modules(parsed, str(file_path))
            self._extract_data_sources(parsed, str(file_path))

        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")

    def _extract_resources(self, parsed: Dict[str, Any], file_path: str) -> None:
        """Extract resources from parsed HCL"""
        if "resource" in parsed:
            for resource_block in parsed["resource"]:
                for resource_type, resources in resource_block.items():
                    for resource_name, config in resources.items():
                        resource = TerraformResource(
                            resource_type=resource_type,
                            resource_name=resource_name,
                            config=config,
                            file_path=file_path,
                        )
                        self.resources.append(resource)

    def _extract_variables(self, parsed: Dict[str, Any], file_path: str) -> None:
        """Extract variables from parsed HCL"""
        if "variable" in parsed:
            for variable_block in parsed["variable"]:
                for var_name, var_config in variable_block.items():
                    variable = TerraformVariable(
                        name=var_name,
                        type=var_config.get("type"),
                        description=var_config.get("description"),
                        default=var_config.get("default"),
                        file_path=file_path,
                    )
                    self.variables.append(variable)

    def _extract_outputs(self, parsed: Dict[str, Any], file_path: str) -> None:
        """Extract outputs from parsed HCL"""
        if "output" in parsed:
            for output_block in parsed["output"]:
                for output_name, output_config in output_block.items():
                    output = TerraformOutput(
                        name=output_name,
                        value=output_config.get("value"),
                        description=output_config.get("description"),
                        file_path=file_path,
                    )
                    self.outputs.append(output)

    def _extract_providers(self, parsed: Dict[str, Any], file_path: str) -> None:
        """Extract providers from parsed HCL"""
        if "provider" in parsed:
            for provider_block in parsed["provider"]:
                for provider_name, provider_config in provider_block.items():
                    provider = TerraformProvider(
                        name=provider_name,
                        alias=provider_config.get("alias"),
                        config=provider_config,
                        file_path=file_path,
                    )
                    self.providers.append(provider)

    def _extract_modules(self, parsed: Dict[str, Any], file_path: str) -> None:
        """Extract modules from parsed HCL"""
        if "module" in parsed:
            for module_block in parsed["module"]:
                for module_name, module_config in module_block.items():
                    module_info = {
                        "name": module_name,
                        "source": module_config.get("source"),
                        "config": module_config,
                        "file_path": file_path,
                    }
                    self.modules.append(module_info)

    def _extract_data_sources(self, parsed: Dict[str, Any], file_path: str) -> None:
        """Extract data sources from parsed HCL"""
        if "data" in parsed:
            for data_block in parsed["data"]:
                for data_type, data_sources in data_block.items():
                    for data_name, config in data_sources.items():
                        data_source = TerraformResource(
                            resource_type=f"data.{data_type}",
                            resource_name=data_name,
                            config=config,
                            file_path=file_path,
                        )
                        self.data_sources.append(data_source)

    def get_project_summary(self) -> Dict[str, Any]:
        """Get summary of parsed Terraform project"""
        return {
            "resources": {
                "count": len(self.resources),
                "by_type": self._count_resources_by_type(),
                "details": [self._resource_to_dict(r) for r in self.resources],
            },
            "variables": {
                "count": len(self.variables),
                "details": [self._variable_to_dict(v) for v in self.variables],
            },
            "outputs": {
                "count": len(self.outputs),
                "details": [self._output_to_dict(o) for o in self.outputs],
            },
            "providers": {
                "count": len(self.providers),
                "details": [self._provider_to_dict(p) for p in self.providers],
            },
            "modules": {"count": len(self.modules), "details": self.modules},
            "data_sources": {
                "count": len(self.data_sources),
                "details": [self._resource_to_dict(d) for d in self.data_sources],
            },
        }

    def _count_resources_by_type(self) -> Dict[str, int]:
        """Count resources by type"""
        counts = {}
        for resource in self.resources:
            resource_type = resource.resource_type
            counts[resource_type] = counts.get(resource_type, 0) + 1
        return counts

    def _resource_to_dict(self, resource: TerraformResource) -> Dict[str, Any]:
        """Convert resource to dictionary"""
        return {
            "type": resource.resource_type,
            "name": resource.resource_name,
            "config": resource.config,
            "file_path": resource.file_path,
            "line_number": resource.line_number,
        }

    def _variable_to_dict(self, variable: TerraformVariable) -> Dict[str, Any]:
        """Convert variable to dictionary"""
        return {
            "name": variable.name,
            "type": variable.type,
            "description": variable.description,
            "default": variable.default,
            "file_path": variable.file_path,
        }

    def _output_to_dict(self, output: TerraformOutput) -> Dict[str, Any]:
        """Convert output to dictionary"""
        return {
            "name": output.name,
            "value": output.value,
            "description": output.description,
            "file_path": output.file_path,
        }

    def _provider_to_dict(self, provider: TerraformProvider) -> Dict[str, Any]:
        """Convert provider to dictionary"""
        return {
            "name": provider.name,
            "alias": provider.alias,
            "config": provider.config,
            "file_path": provider.file_path,
        }

    def find_resource_by_name(self, resource_name: str) -> Optional[TerraformResource]:
        """Find resource by name"""
        for resource in self.resources:
            if resource.resource_name == resource_name:
                return resource
        return None

    def find_resources_by_type(self, resource_type: str) -> List[TerraformResource]:
        """Find resources by type"""
        return [r for r in self.resources if r.resource_type == resource_type]

    def search_resources(self, query: str) -> List[TerraformResource]:
        """Search resources by name or type"""
        query_lower = query.lower()
        results = []

        for resource in self.resources:
            if (
                query_lower in resource.resource_name.lower()
                or query_lower in resource.resource_type.lower()
            ):
                results.append(resource)

        return results
