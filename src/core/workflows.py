"""
Workflow templates for common Infrastructure as Code patterns
"""

from typing import Any, Dict, List, Optional
from enum import Enum

from src.core.config import Config
from src.core.logger import get_logger

logger = get_logger(__name__)


class WorkflowType(Enum):
    """Types of IaC workflows"""
    DEPLOYMENT = "deployment"
    SECURITY_AUDIT = "security_audit"
    COST_OPTIMIZATION = "cost_optimization"
    MIGRATION = "migration"
    DISASTER_RECOVERY = "disaster_recovery"
    COMPLIANCE_CHECK = "compliance_check"
    MONITORING_SETUP = "monitoring_setup"


class WorkflowTemplate:
    """Base class for workflow templates"""
    
    def __init__(self, name: str, description: str, workflow_type: WorkflowType):
        self.name = name
        self.description = description
        self.workflow_type = workflow_type
        self.steps: List[Dict[str, Any]] = []
        self.required_tools: List[str] = []
        self.approval_required: bool = False
    
    def add_step(self, step: Dict[str, Any]):
        """Add a step to the workflow"""
        self.steps.append(step)
    
    def add_required_tool(self, tool: str):
        """Add a required tool for this workflow"""
        self.required_tools.append(tool)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.workflow_type.value,
            "steps": self.steps,
            "required_tools": self.required_tools,
            "approval_required": self.approval_required,
        }


class WorkflowTemplates:
    """Collection of pre-defined workflow templates for common IaC patterns"""
    
    def __init__(self, config: Config):
        self.config = config
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, WorkflowTemplate]:
        """Initialize all workflow templates"""
        
        templates = {}
        
        # 1. Infrastructure Deployment Workflow
        deployment_workflow = WorkflowTemplate(
            name="Infrastructure Deployment",
            description="Complete infrastructure deployment with validation and monitoring",
            workflow_type=WorkflowType.DEPLOYMENT
        )
        deployment_workflow.approval_required = True
        deployment_workflow.add_required_tool("execute_terraform_plan")
        deployment_workflow.add_required_tool("execute_terraform_apply")
        
        deployment_workflow.add_step({
            "name": "Pre-deployment validation",
            "description": "Validate Terraform configuration and check for syntax errors",
            "tool": "execute_terraform_validate",
            "subagent": "deployment-validator",
            "required": True,
        })
        
        deployment_workflow.add_step({
            "name": "Generate execution plan",
            "description": "Create detailed execution plan showing what will be created/modified",
            "tool": "execute_terraform_plan",
            "required": True,
        })
        
        deployment_workflow.add_step({
            "name": "Security analysis",
            "description": "Analyze planned infrastructure for security vulnerabilities",
            "subagent": "security-auditor",
            "required": True,
        })
        
        deployment_workflow.add_step({
            "name": "Cost estimation",
            "description": "Calculate estimated monthly costs and identify optimization opportunities",
            "subagent": "cost-optimizer",
            "required": False,
        })
        
        deployment_workflow.add_step({
            "name": "Human approval",
            "description": "Review plan and approve execution",
            "approval_required": True,
        })
        
        deployment_workflow.add_step({
            "name": "Execute deployment",
            "description": "Apply the infrastructure changes",
            "tool": "execute_terraform_apply",
            "approval_required": True,
        })
        
        deployment_workflow.add_step({
            "name": "Post-deployment validation",
            "description": "Verify deployed resources are functioning correctly",
            "subagent": "deployment-validator",
            "required": True,
        })
        
        deployment_workflow.add_step({
            "name": "Setup monitoring",
            "description": "Configure monitoring and alerting for new resources",
            "subagent": "deployment-validator",
            "required": False,
        })
        
        templates["deployment"] = deployment_workflow
        
        # 2. Security Audit Workflow
        security_audit = WorkflowTemplate(
            name="Security Audit & Compliance",
            description="Comprehensive security analysis and compliance checking",
            workflow_type=WorkflowType.SECURITY_AUDIT
        )
        security_audit.add_required_tool("analyze_infrastructure")
        security_audit.add_required_tool("get_resources")
        
        security_audit.add_step({
            "name": "Inventory resources",
            "description": "Create comprehensive inventory of all infrastructure resources",
            "tool": "get_resources",
            "required": True,
        })
        
        security_audit.add_step({
            "name": "Security scanning",
            "description": "Perform comprehensive security vulnerability scan",
            "subagent": "security-auditor",
            "required": True,
        })
        
        security_audit.add_step({
            "name": "Compliance checking",
            "description": "Verify compliance with selected frameworks (CIS, NIST, SOC2, etc.)",
            "subagent": "security-auditor",
            "required": True,
        })
        
        security_audit.add_step({
            "name": "Risk assessment",
            "description": "Assess security risks and categorize by severity",
            "subagent": "security-auditor",
            "required": True,
        })
        
        security_audit.add_step({
            "name": "Remediation planning",
            "description": "Create detailed remediation plan for identified issues",
            "subagent": "security-auditor",
            "required": True,
        })
        
        templates["security_audit"] = security_audit
        
        # 3. Cost Optimization Workflow
        cost_optimization = WorkflowTemplate(
            name="Cost Optimization Analysis",
            description="Analyze and optimize infrastructure costs",
            workflow_type=WorkflowType.COST_OPTIMIZATION
        )
        cost_optimization.add_required_tool("get_terraform_state")
        cost_optimization.add_required_tool("get_resources")
        
        cost_optimization.add_step({
            "name": "Resource inventory",
            "description": "Catalog all deployed resources and their configurations",
            "tool": "get_resources",
            "required": True,
        })
        
        cost_optimization.add_step({
            "name": "Usage analysis",
            "description": "Analyze resource utilization patterns and identify underutilized resources",
            "subagent": "cost-optimizer",
            "required": True,
        })
        
        cost_optimization.add_step({
            "name": "Cost breakdown",
            "description": "Generate detailed cost breakdown by service and resource type",
            "subagent": "cost-optimizer",
            "required": True,
        })
        
        cost_optimization.add_step({
            "name": "Optimization recommendations",
            "description": "Provide specific recommendations for cost savings",
            "subagent": "cost-optimizer",
            "required": True,
        })
        
        cost_optimization.add_step({
            "name": "Savings estimation",
            "description": "Calculate potential savings and ROI for optimization measures",
            "subagent": "cost-optimizer",
            "required": True,
        })
        
        templates["cost_optimization"] = cost_optimization
        
        # 4. Infrastructure Migration Workflow
        migration_workflow = WorkflowTemplate(
            name="Infrastructure Migration",
            description="Plan and execute infrastructure migration between environments or providers",
            workflow_type=WorkflowType.MIGRATION
        )
        migration_workflow.approval_required = True
        migration_workflow.add_required_tool("execute_terraform_plan")
        migration_workflow.add_required_tool("execute_terraform_apply")
        
        migration_workflow.add_step({
            "name": "Source analysis",
            "description": "Analyze current infrastructure configuration and state",
            "tool": "get_terraform_state",
            "required": True,
        })
        
        migration_workflow.add_step({
            "name": "Target planning",
            "description": "Design target infrastructure architecture",
            "subagent": "migration-planner",
            "required": True,
        })
        
        migration_workflow.add_step({
            "name": "Migration strategy",
            "description": "Create detailed migration strategy with rollback procedures",
            "subagent": "migration-planner",
            "required": True,
        })
        
        migration_workflow.add_step({
            "name": "Risk assessment",
            "description": "Identify and assess migration risks",
            "subagent": "migration-planner",
            "required": True,
        })
        
        migration_workflow.add_step({
            "name": "Pre-migration validation",
            "description": "Validate source and target configurations",
            "subagent": "deployment-validator",
            "required": True,
        })
        
        migration_workflow.add_step({
            "name": "Human approval",
            "description": "Review migration plan and approve execution",
            "approval_required": True,
        })
        
        migration_workflow.add_step({
            "name": "Execute migration",
            "description": "Execute the migration plan step by step",
            "subagent": "migration-planner",
            "approval_required": True,
        })
        
        migration_workflow.add_step({
            "name": "Post-migration validation",
            "description": "Verify successful migration and functionality",
            "subagent": "deployment-validator",
            "required": True,
        })
        
        templates["migration"] = migration_workflow
        
        # 5. Disaster Recovery Testing Workflow
        dr_test = WorkflowTemplate(
            name="Disaster Recovery Test",
            description="Test disaster recovery procedures and backup restoration",
            workflow_type=WorkflowType.DISASTER_RECOVERY
        )
        dr_test.approval_required = True
        
        dr_test.add_step({
            "name": "Backup verification",
            "description": "Verify all critical backups are current and accessible",
            "subagent": "deployment-validator",
            "required": True,
        })
        
        dr_test.add_step({
            "name": "Recovery planning",
            "description": "Create detailed recovery test plan with success criteria",
            "subagent": "migration-planner",
            "required": True,
        })
        
        dr_test.add_step({
            "name": "Isolate test environment",
            "description": "Create isolated environment for recovery testing",
            "subagent": "deployment-validator",
            "required": True,
        })
        
        dr_test.add_step({
            "name": "Execute recovery",
            "description": "Execute disaster recovery procedures",
            "subagent": "migration-planner",
            "approval_required": True,
        })
        
        dr_test.add_step({
            "name": "Validation testing",
            "description": "Test recovered systems functionality and data integrity",
            "subagent": "deployment-validator",
            "required": True,
        })
        
        dr_test.add_step({
            "name": "Cleanup",
            "description": "Clean up test environment and document results",
            "subagent": "deployment-validator",
            "required": True,
        })
        
        templates["disaster_recovery"] = dr_test
        
        logger.info(f"Initialized {len(templates)} workflow templates")
        return templates
    
    def get_template(self, name: str) -> Optional[WorkflowTemplate]:
        """Get a workflow template by name"""
        return self.templates.get(name)
    
    def get_all_templates(self) -> Dict[str, WorkflowTemplate]:
        """Get all available workflow templates"""
        return self.templates.copy()
    
    def get_templates_by_type(self, workflow_type: WorkflowType) -> List[WorkflowTemplate]:
        """Get all templates of a specific type"""
        return [
            template for template in self.templates.values()
            if template.workflow_type == workflow_type
        ]
    
    def create_workflow_execution_plan(
        self, 
        template_name: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create an execution plan from a template
        
        Args:
            template_name: Name of the template to use
            parameters: Optional parameters to customize the workflow
            
        Returns:
            Execution plan or None if template not found
        """
        template = self.get_template(template_name)
        if not template:
            return None
        
        plan = {
            "template": template.to_dict(),
            "parameters": parameters or {},
            "execution_steps": [],
            "estimated_duration": self._estimate_duration(template),
            "required_approvals": self._count_required_approvals(template),
        }
        
        # Generate execution steps with parameters
        for i, step in enumerate(template.steps):
            execution_step = step.copy()
            execution_step["step_number"] = i + 1
            execution_step["status"] = "pending"
            
            # Apply parameters to step if applicable
            if parameters:
                execution_step = self._apply_parameters_to_step(execution_step, parameters)
            
            plan["execution_steps"].append(execution_step)
        
        return plan
    
    def _estimate_duration(self, template: WorkflowTemplate) -> str:
        """Estimate workflow execution duration"""
        base_durations = {
            WorkflowType.DEPLOYMENT: "15-30 minutes",
            WorkflowType.SECURITY_AUDIT: "10-20 minutes",
            WorkflowType.COST_OPTIMIZATION: "5-15 minutes",
            WorkflowType.MIGRATION: "30-60 minutes",
            WorkflowType.DISASTER_RECOVERY: "45-90 minutes",
            WorkflowType.COMPLIANCE_CHECK: "15-30 minutes",
            WorkflowType.MONITORING_SETUP: "10-20 minutes",
        }
        
        return base_durations.get(template.workflow_type, "10-30 minutes")
    
    def _count_required_approvals(self, template: WorkflowTemplate) -> int:
        """Count required approvals in a template"""
        return sum(1 for step in template.steps if step.get("approval_required", False))
    
    def _apply_parameters_to_step(
        self, 
        step: Dict[str, Any], 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply parameters to a workflow step"""
        # This is a simple implementation - could be more sophisticated
        modified_step = step.copy()
        
        for param_key, param_value in parameters.items():
            if param_key in modified_step:
                modified_step[param_key] = param_value
        
        return modified_step
