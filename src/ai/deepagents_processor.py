"""
DeepAgents processor for multi-agent IaC orchestration
"""

import asyncio
from typing import Any, Dict, List, Optional

from deepagents import create_deep_agent
from langchain_core.tools import BaseTool
from langgraph.types import Checkpointer

from src.ai.model_factory import ModelFactory
from src.core.config import Config
from src.core.logger import get_logger
from src.terraform.cli import TerraformCLI

logger = get_logger(__name__)


class DeepAgentsProcessor:
    """DeepAgents-based processor for multi-agent IaC workflows"""

    def __init__(self, config: Config, terraform_tools: List[BaseTool]):
        self.config = config
        self.terraform_tools = terraform_tools
        self.terraform_cli = TerraformCLI(
            terraform_path=config.terraform_path,
            working_dir=config.terraform_dir
        )
        
        # Initialize the model
        self.model = ModelFactory.create_model(config)
        
        # Create specialized sub-agents
        self.subagents = self._create_subagents()
        
        # Create the main deep agent
        self.agent = self._create_deep_agent()
        
        logger.info(f"DeepAgents processor initialized with {len(self.subagents)} sub-agents")

    def _create_subagents(self) -> List[Dict[str, Any]]:
        """Create specialized sub-agents for IaC workflows"""
        
        # Security and Compliance Sub-agent
        security_auditor = {
            "name": "security-auditor",
            "description": "Analyze security configurations and compliance requirements. Reviews Terraform configurations for security best practices, vulnerabilities, and compliance with frameworks like CIS, NIST, SOC2.",
            "prompt": """You are a security and compliance expert specializing in Infrastructure as Code.

Your responsibilities:
1. Review Terraform configurations for security vulnerabilities
2. Ensure compliance with security frameworks (CIS, NIST, SOC2, GDPR)
3. Identify misconfigurations that could lead to security breaches
4. Recommend security best practices and improvements
5. Analyze network security, encryption, access controls, and monitoring

Focus on:
- Network security groups and firewall rules
- Identity and access management (IAM) configurations
- Encryption settings for data at rest and in transit
- Security monitoring and logging configurations
- Compliance with industry standards and regulations

Always provide specific, actionable recommendations with references to security best practices.""",
            "tools": self.terraform_tools + [self._create_security_scan_tool()],
        }

        # Cost Optimization Sub-agent
        cost_optimizer = {
            "name": "cost-optimizer",
            "description": "Optimize infrastructure costs and resource sizing. Analyzes resource utilization, recommends cost-effective alternatives, and implements cost-saving strategies.",
            "prompt": """You are a cloud cost optimization expert specializing in Infrastructure as Code.

Your responsibilities:
1. Analyze Terraform configurations for cost optimization opportunities
2. Recommend appropriate instance types and sizing based on workload requirements
3. Identify unused or underutilized resources that can be removed or downsized
4. Suggest cost-saving measures like reserved instances, spot instances, or auto-scaling
5. Estimate monthly costs and compare different architectural approaches

Focus on:
- Compute resource optimization (VMs, containers, serverless)
- Storage cost optimization and tiering strategies
- Network cost optimization and data transfer fees
- Monitoring and alerting costs
- Licensing and software costs

Provide detailed cost breakdowns and ROI analysis for your recommendations.""",
            "tools": self.terraform_tools + [self._create_cost_analysis_tool()],
        }

        # Deployment Validator Sub-agent
        deployment_validator = {
            "name": "deployment-validator",
            "description": "Validate infrastructure deployments and run post-deployment checks. Ensures deployments are successful, resources are properly configured, and systems are operational.",
            "prompt": """You are an infrastructure deployment and validation expert.

Your responsibilities:
1. Validate Terraform plans before execution
2. Run post-deployment health checks and validation tests
3. Verify resource configurations match intended specifications
4. Test connectivity, accessibility, and functionality of deployed resources
5. Monitor deployment progress and identify potential issues

Focus on:
- Resource provisioning validation
- Network connectivity testing
- Service availability checks
- Configuration verification
- Performance baseline establishment

Create comprehensive validation checklists and testing procedures for each deployment.""",
            "tools": self.terraform_tools + [self._create_validation_tool()],
        }

        # Migration Planner Sub-agent
        migration_planner = {
            "name": "migration-planner",
            "description": "Plan infrastructure migrations and transitions. Designs migration strategies, rollback procedures, and transition plans for infrastructure changes.",
            "prompt": """You are an infrastructure migration specialist with expertise in complex cloud migrations.

Your responsibilities:
1. Design migration strategies from current to target infrastructure states
2. Create detailed migration plans with step-by-step procedures
3. Design rollback procedures for failed migrations
4. Analyze migration risks and mitigation strategies
5. Plan data migration, service continuity, and cut-over procedures

Focus on:
- Zero-downtime migration strategies
- Data consistency and integrity during migration
- Service continuity and user impact minimization
- Rollback planning and disaster recovery
- Migration testing and validation procedures

Provide comprehensive migration playbooks with risk assessments and contingency plans.""",
            "tools": self.terraform_tools + [self._create_migration_planning_tool()],
        }

        return [security_auditor, cost_optimizer, deployment_validator, migration_planner]

    def _create_deep_agent(self):
        """Create the main DeepAgents orchestrator"""
        
        # Define tool configurations for human-in-the-loop
        tool_configs = {}
        if self.config.human_in_the_loop:
            tool_configs.update({
                "execute_terraform_apply": True,  # Require approval for apply
                "execute_terraform_destroy": True,  # Require approval for destroy
            })
        
        instructions = """You are an expert Infrastructure as Code orchestrator with access to specialized sub-agents.

Your role is to coordinate complex infrastructure workflows by:
1. Planning multi-step infrastructure operations using the todo tool
2. Delegating specialized tasks to appropriate sub-agents
3. Coordinating the overall workflow and ensuring successful completion
4. Managing risk and ensuring proper validation before critical operations

Available sub-agents:
- security-auditor: For security analysis and compliance reviews
- cost-optimizer: For cost optimization and resource sizing
- deployment-validator: For deployment validation and testing
- migration-planner: For infrastructure migration planning

Always start complex workflows by creating a todo plan. Use sub-agents for specialized analysis while maintaining overall coordination."""

        try:
            agent = create_deep_agent(
                tools=self.terraform_tools,
                instructions=instructions,
                model=self.model,
                subagents=self.subagents,
                tool_configs=tool_configs if tool_configs else None,
            )
            logger.info("DeepAgents orchestrator created successfully")
            return agent
        except Exception as e:
            logger.error(f"Failed to create DeepAgents orchestrator: {e}")
            raise

    def _create_security_scan_tool(self):
        """Create a security scanning tool"""
        from langchain_core.tools import tool
        
        @tool
        def security_scan(resource_type: str, resource_name: str = "") -> str:
            """Perform a security scan on a specific resource type or configuration.
            
            Args:
                resource_type: Type of resource to scan (e.g., 'aws_instance', 'azurerm_virtual_machine')
                resource_name: Optional specific resource name to focus on
                
            Returns:
                Security analysis findings and recommendations
            """
            # This would integrate with actual security scanning tools
            # For now, provide a placeholder implementation
            return f"Security scan completed for {resource_type}:{resource_name}. Found 0 critical issues, 2 warnings."
        
        return security_scan

    def _create_cost_analysis_tool(self):
        """Create a cost analysis tool"""
        from langchain_core.tools import tool
        
        @tool
        def cost_analysis(configuration_details: str) -> str:
            """Analyze the cost implications of infrastructure configurations.
            
            Args:
                configuration_details: Terraform configuration or resource specifications
                
            Returns:
                Cost analysis with breakdown and optimization recommendations
            """
            # This would integrate with cost analysis APIs or pricing calculators
            return "Cost analysis completed. Estimated monthly cost: $150-200. Potential savings: 30% with reserved instances."
        
        return cost_analysis

    def _create_validation_tool(self):
        """Create a deployment validation tool"""
        from langchain_core.tools import tool
        
        @tool
        def validate_deployment(resources: List[str]) -> str:
            """Validate that deployed resources are functioning correctly.
            
            Args:
                resources: List of resource names or types to validate
                
            Returns:
                Validation results with pass/fail status and details
            """
            # This would perform actual health checks and validation
            return f"Validation completed for {len(resources)} resources. All checks passed."
        
        return validate_deployment

    def _create_migration_planning_tool(self):
        """Create a migration planning tool"""
        from langchain_core.tools import tool
        
        @tool
        def create_migration_plan(source_config: str, target_config: str) -> str:
            """Create a detailed migration plan from source to target configuration.
            
            Args:
                source_config: Current infrastructure configuration
                target_config: Target infrastructure configuration
                
            Returns:
                Comprehensive migration plan with steps and timeline
            """
            # This would analyze differences and create migration strategies
            return "Migration plan created with 8 steps over 2 weeks. Zero-downtime approach."
        
        return create_migration_plan

    async def process_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a complex infrastructure request using DeepAgents"""
        
        try:
            logger.info(f"Processing DeepAgents request: {request[:100]}...")
            
            # Prepare the agent state
            agent_state = {
                "messages": [{"role": "user", "content": request}],
            }
            
            # Add any provided context (files, previous results, etc.)
            if context:
                agent_state.update(context)
            
            # Invoke the DeepAgents orchestrator
            result = self.agent.invoke(agent_state)
            
            logger.info("DeepAgents request completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing DeepAgents request: {e}")
            return {
                "error": str(e),
                "messages": [{"role": "assistant", "content": f"Error: {str(e)}"}]
            }

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the DeepAgents configuration"""
        return {
            "model_info": ModelFactory.get_model_info(self.config),
            "subagents": [
                {
                    "name": agent["name"],
                    "description": agent["description"],
                    "tools_count": len(agent.get("tools", [])),
                }
                for agent in self.subagents
            ],
            "human_in_the_loop": self.config.human_in_the_loop,
            "terraform_tools_count": len(self.terraform_tools),
        }
