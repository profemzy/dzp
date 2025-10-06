"""
Model Context Protocol (MCP) Client Integration
Connects to MCP servers to extend Claude's capabilities with external tools and data sources
"""

import asyncio
from typing import Any, Dict, List, Optional

from src.core.logger import get_logger

logger = get_logger(__name__)


class MCPClient:
    """Client for connecting to MCP servers"""

    def __init__(self):
        self.servers: Dict[str, Any] = {}
        self.available_tools: List[Dict[str, Any]] = []
        self.connected = False

    async def connect_server(
        self, server_name: str, server_config: Dict[str, Any]
    ) -> bool:
        """
        Connect to an MCP server

        Args:
            server_name: Identifier for the server
            server_config: Configuration including command, args, env

        Returns:
            True if connection successful
        """
        try:
            logger.info(f"Connecting to MCP server: {server_name}")

            # For now, we'll create a placeholder for MCP server connection
            # In production, this would use the actual MCP protocol
            self.servers[server_name] = {
                "name": server_name,
                "config": server_config,
                "status": "connected",
            }

            # Discover tools from the server
            await self._discover_tools(server_name)

            self.connected = True
            logger.info(
                f"Successfully connected to MCP server: {server_name} with {len(self.available_tools)} tools"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to connect to MCP server {server_name}: {e}")
            return False

    async def _discover_tools(self, server_name: str):
        """
        Discover available tools from an MCP server

        Args:
            server_name: Name of the server to discover tools from
        """
        # Placeholder for tool discovery
        # In production, this would query the MCP server's tool catalog

        # Example tools that would come from Terraform MCP server
        if "terraform" in server_name.lower():
            terraform_tools = [
                {
                    "name": "terraform_best_practices",
                    "description": "Get Terraform best practices and style guide recommendations",
                    "server": server_name,
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Category: naming, security, modules, state, etc.",
                            }
                        },
                    },
                },
                {
                    "name": "terraform_module_search",
                    "description": "Search Terraform Registry for modules matching criteria",
                    "server": server_name,
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "provider": {
                                "type": "string",
                                "description": "Provider: aws, azure, gcp, etc.",
                            },
                            "resource_type": {
                                "type": "string",
                                "description": "Type of resource needed",
                            },
                        },
                        "required": ["provider"],
                    },
                },
                {
                    "name": "terraform_security_scan",
                    "description": "Scan Terraform configuration for security issues using tfsec/checkov rules",
                    "server": server_name,
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "config_path": {
                                "type": "string",
                                "description": "Path to Terraform configuration",
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Minimum severity level to report",
                            },
                        },
                    },
                },
            ]

            self.available_tools.extend(terraform_tools)

    async def execute_tool(
        self, tool_name: str, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool on the connected MCP server

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result
        """
        try:
            logger.info(f"Executing MCP tool: {tool_name} with input: {tool_input}")

            # Find the tool
            tool = next(
                (t for t in self.available_tools if t["name"] == tool_name), None
            )

            if not tool:
                return {
                    "error": f"Tool {tool_name} not found",
                    "available_tools": [t["name"] for t in self.available_tools],
                }

            # Execute the tool (placeholder implementation)
            result = await self._execute_tool_impl(tool, tool_input)

            logger.info(f"MCP tool {tool_name} executed successfully")
            return result

        except Exception as e:
            logger.error(f"MCP tool execution failed for {tool_name}: {e}")
            return {"error": str(e)}

    async def _execute_tool_impl(
        self, tool: Dict[str, Any], tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Internal implementation of tool execution
        This would communicate with the actual MCP server in production

        Args:
            tool: Tool definition
            tool_input: Input parameters

        Returns:
            Execution result
        """
        tool_name = tool["name"]

        # Placeholder implementations for demonstration
        if tool_name == "terraform_best_practices":
            category = tool_input.get("category", "general")
            return await self._get_terraform_best_practices(category)

        elif tool_name == "terraform_module_search":
            provider = tool_input.get("provider")
            resource_type = tool_input.get("resource_type", "")
            return await self._search_terraform_modules(provider, resource_type)

        elif tool_name == "terraform_security_scan":
            config_path = tool_input.get("config_path", ".")
            severity = tool_input.get("severity", "medium")
            return await self._scan_security(config_path, severity)

        return {"error": f"Tool {tool_name} implementation not found"}

    async def _get_terraform_best_practices(self, category: str) -> Dict[str, Any]:
        """Get Terraform best practices for a category"""
        best_practices = {
            "naming": {
                "practices": [
                    "Use lowercase with hyphens for resource names",
                    "Include environment in resource names (e.g., prod, dev)",
                    "Use descriptive names that indicate purpose",
                    "Avoid abbreviations unless widely understood",
                ],
                "examples": {
                    "good": "resource_group-web-prod",
                    "bad": "rg1, webRG, ResourceGroup_Production",
                },
            },
            "security": {
                "practices": [
                    "Never commit sensitive data or credentials",
                    "Use remote state with encryption",
                    "Implement least privilege access policies",
                    "Enable encryption at rest and in transit",
                    "Use private endpoints when possible",
                ],
                "tools": ["tfsec", "checkov", "terrascan", "sentinel"],
            },
            "modules": {
                "practices": [
                    "Keep modules focused on single responsibility",
                    "Version your modules using semantic versioning",
                    "Document inputs and outputs clearly",
                    "Use variables for all configurable values",
                    "Include examples and README",
                ],
            },
            "state": {
                "practices": [
                    "Always use remote state for team environments",
                    "Enable state locking to prevent conflicts",
                    "Encrypt state files at rest",
                    "Never modify state files manually",
                    "Implement state backup strategy",
                ],
            },
            "general": {
                "practices": [
                    "Use consistent formatting (terraform fmt)",
                    "Validate configurations (terraform validate)",
                    "Review plans before applying",
                    "Use workspaces for environment separation",
                    "Implement CI/CD pipelines for Terraform",
                    "Pin provider versions",
                ],
            },
        }

        result = best_practices.get(
            category, best_practices["general"]
        )
        return {
            "category": category,
            "best_practices": result,
            "source": "Terraform Style Guide (MCP Server)",
        }

    async def _search_terraform_modules(
        self, provider: str, resource_type: str
    ) -> Dict[str, Any]:
        """Search for Terraform modules"""
        # Placeholder - would query actual Terraform Registry
        modules = {
            "aws": [
                {
                    "name": "terraform-aws-vpc",
                    "namespace": "terraform-aws-modules",
                    "version": "5.1.0",
                    "description": "Terraform module to create AWS VPC resources",
                    "downloads": 100000000,
                },
                {
                    "name": "terraform-aws-eks",
                    "namespace": "terraform-aws-modules",
                    "version": "19.16.0",
                    "description": "Terraform module to create AWS EKS cluster",
                    "downloads": 50000000,
                },
            ],
            "azure": [
                {
                    "name": "terraform-azurerm-network",
                    "namespace": "Azure",
                    "version": "3.5.0",
                    "description": "Terraform module for Azure Virtual Network",
                    "downloads": 5000000,
                },
            ],
            "gcp": [
                {
                    "name": "terraform-google-network",
                    "namespace": "terraform-google-modules",
                    "version": "7.1.0",
                    "description": "Terraform module for Google Cloud VPC",
                    "downloads": 3000000,
                },
            ],
        }

        provider_modules = modules.get(provider.lower(), [])

        # Filter by resource type if provided
        if resource_type:
            provider_modules = [
                m
                for m in provider_modules
                if resource_type.lower() in m["name"].lower()
                or resource_type.lower() in m["description"].lower()
            ]

        return {
            "provider": provider,
            "resource_type": resource_type,
            "modules": provider_modules,
            "count": len(provider_modules),
        }

    async def _scan_security(
        self, config_path: str, severity: str
    ) -> Dict[str, Any]:
        """Scan Terraform configuration for security issues"""
        # Placeholder - would run actual security scanning tools
        findings = [
            {
                "rule": "AWS001",
                "severity": "high",
                "resource": "aws_s3_bucket.data",
                "message": "S3 bucket does not have encryption enabled",
                "recommendation": "Enable server-side encryption using aws_s3_bucket_server_side_encryption_configuration",
            },
            {
                "rule": "AWS018",
                "severity": "medium",
                "resource": "aws_security_group.web",
                "message": "Security group allows ingress from 0.0.0.0/0 on port 22",
                "recommendation": "Restrict SSH access to specific IP ranges",
            },
            {
                "rule": "AZURE003",
                "severity": "high",
                "resource": "azurerm_storage_account.data",
                "message": "Storage account does not enforce HTTPS",
                "recommendation": "Set enable_https_traffic_only = true",
            },
        ]

        # Filter by severity
        severity_levels = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        min_severity = severity_levels.get(severity, 1)

        filtered_findings = [
            f
            for f in findings
            if severity_levels.get(f["severity"], 0) >= min_severity
        ]

        return {
            "config_path": config_path,
            "severity_threshold": severity,
            "findings": filtered_findings,
            "total_issues": len(filtered_findings),
            "scan_tool": "tfsec/checkov (via MCP)",
        }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of all available tools from connected MCP servers"""
        return self.available_tools

    async def disconnect_all(self):
        """Disconnect from all MCP servers"""
        logger.info("Disconnecting from all MCP servers")
        self.servers.clear()
        self.available_tools.clear()
        self.connected = False


class MCPManager:
    """Manages MCP client lifecycle and server connections"""

    def __init__(self):
        self.client = MCPClient()
        self.initialized = False

    async def initialize(self):
        """Initialize MCP client and connect to configured servers"""
        if self.initialized:
            return

        try:
            # Connect to Terraform MCP server
            terraform_config = {
                "command": "terraform-mcp-server",
                "args": [],
                "env": {},
            }

            await self.client.connect_server("terraform-mcp", terraform_config)

            self.initialized = True
            logger.info("MCP Manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize MCP Manager: {e}")

    async def shutdown(self):
        """Shutdown MCP client and disconnect from servers"""
        await self.client.disconnect_all()
        self.initialized = False
        logger.info("MCP Manager shutdown complete")

    def get_client(self) -> MCPClient:
        """Get the MCP client instance"""
        return self.client
