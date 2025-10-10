"""
Human-in-the-Loop approval system for critical operations
"""

import asyncio
from typing import Any, Dict, Optional, Tuple
from enum import Enum

from src.core.config import Config
from src.core.logger import get_logger

logger = get_logger(__name__)


class ApprovalStatus(Enum):
    """Approval status enum"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class HumanInTheLoop:
    """Human-in-the-Loop approval system for critical operations"""

    def __init__(self, config: Config):
        self.config = config
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.approval_history: list[Dict[str, Any]] = []

    def requires_approval(self, tool_name: str, tool_input: Dict[str, Any]) -> bool:
        """
        Check if a tool execution requires human approval
        
        Args:
            tool_name: Name of the tool being executed
            tool_input: Input parameters for the tool
            
        Returns:
            True if approval is required
        """
        if not self.config.human_in_the_loop:
            return False

        # Define critical operations that require approval
        critical_operations = {
            "execute_terraform_apply",
            "execute_terraform_destroy",
            "terraform_apply",
            "terraform_destroy",
        }

        # Additional checks for production environments
        production_indicators = [
            "prod", "production", "live", "main", "master"
        ]
        
        is_production = any(
            indicator in str(tool_input).lower() 
            for indicator in production_indicators
        )

        return tool_name in critical_operations or is_production

    async def request_approval(
        self, 
        tool_name: str, 
        tool_input: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[ApprovalStatus, Optional[Dict[str, Any]]]:
        """
        Request human approval for a critical operation
        
        Args:
            tool_name: Name of the tool requiring approval
            tool_input: Input parameters for the tool
            context: Additional context about the operation
            
        Returns:
            Tuple of (approval_status, modified_input)
        """
        approval_id = f"{tool_name}_{len(self.pending_approvals)}"
        
        approval_request = {
            "id": approval_id,
            "tool_name": tool_name,
            "tool_input": tool_input,
            "context": context or {},
            "status": ApprovalStatus.PENDING,
            "timestamp": str(asyncio.get_event_loop().time()),
            "risk_level": self._assess_risk_level(tool_name, tool_input),
        }

        self.pending_approvals[approval_id] = approval_request
        
        logger.info(f"Requesting approval for {tool_name} (ID: {approval_id})")
        
        # Display approval request to user
        approval_status, modified_input = await self._display_approval_request(approval_request)
        
        # Update approval status
        approval_request["status"] = approval_status
        approval_request["modified_input"] = modified_input
        
        # Move to history
        self.approval_history.append(approval_request)
        del self.pending_approvals[approval_id]
        
        return approval_status, modified_input

    def _assess_risk_level(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Assess the risk level of an operation"""
        if "destroy" in tool_name.lower():
            return "HIGH"
        elif "apply" in tool_name.lower():
            return "MEDIUM"
        else:
            return "LOW"

    async def _display_approval_request(self, approval_request: Dict[str, Any]) -> Tuple[ApprovalStatus, Optional[Dict[str, Any]]]:
        """
        Display approval request to user and get response
        
        In a real implementation, this would display a rich UI prompt
        For now, we'll simulate the approval process
        """
        print(f"\n🔔 APPROVAL REQUIRED")
        print(f"Operation: {approval_request['tool_name']}")
        print(f"Risk Level: {approval_request['risk_level']}")
        print(f"Details: {approval_request['tool_input']}")
        
        # Simulate user input - in real implementation this would be interactive
        # For now, auto-approve for development
        if self.config.human_in_the_loop:
            # In production, this would wait for actual user input
            print("⚠️  Auto-approving for development (enable interactive prompts for production)")
            return ApprovalStatus.APPROVED, approval_request["tool_input"]
        else:
            return ApprovalStatus.APPROVED, approval_request["tool_input"]

    def get_pending_approvals(self) -> list[Dict[str, Any]]:
        """Get list of pending approvals"""
        return list(self.pending_approvals.values())

    def get_approval_history(self) -> list[Dict[str, Any]]:
        """Get approval history"""
        return self.approval_history.copy()

    def clear_pending_approvals(self):
        """Clear all pending approvals"""
        self.pending_approvals.clear()

    def auto_approve_pending(self, pattern: Optional[str] = None) -> int:
        """
        Auto-approve pending approvals (useful for automated workflows)
        
        Args:
            pattern: Optional pattern to match for selective approval
            
        Returns:
            Number of approvals granted
        """
        approved_count = 0
        
        for approval_id, approval in list(self.pending_approvals.items()):
            should_approve = True
            
            if pattern:
                if pattern.lower() not in approval["tool_name"].lower():
                    should_approve = False
            
            if should_approve:
                approval["status"] = ApprovalStatus.APPROVED
                self.approval_history.append(approval)
                del self.pending_approvals[approval_id]
                approved_count += 1
        
        logger.info(f"Auto-approved {approved_count} pending operations")
        return approved_count

    def get_approval_summary(self) -> Dict[str, Any]:
        """Get summary of approval activity"""
        return {
            "pending_count": len(self.pending_approvals),
            "total_approved": len([a for a in self.approval_history if a["status"] == ApprovalStatus.APPROVED]),
            "total_rejected": len([a for a in self.approval_history if a["status"] == ApprovalStatus.REJECTED]),
            "total_modified": len([a for a in self.approval_history if a["status"] == ApprovalStatus.MODIFIED]),
            "high_risk_operations": len([a for a in self.approval_history if a.get("risk_level") == "HIGH"]),
        }


class ToolInterceptor:
    """Interceptor for tool execution with human-in-the-loop approval"""
    
    def __init__(self, config: Config):
        self.config = config
        self.hil = HumanInTheLoop(config)
    
    async def intercept_tool_execution(
        self, 
        tool_name: str, 
        tool_input: Dict[str, Any], 
        tool_executor: callable,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Intercept tool execution and request approval if needed
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            tool_executor: Function to execute the tool
            context: Additional context about the operation
            
        Returns:
            Result of tool execution
        """
        # Check if approval is required
        if self.hil.requires_approval(tool_name, tool_input):
            approval_status, modified_input = await self.hil.request_approval(
                tool_name, tool_input, context
            )
            
            if approval_status == ApprovalStatus.REJECTED:
                raise Exception(f"Operation {tool_name} was rejected by human approval")
            
            elif approval_status == ApprovalStatus.MODIFIED and modified_input:
                tool_input = modified_input
            
            elif approval_status == ApprovalStatus.PENDING:
                raise Exception(f"Operation {tool_name} is pending approval")
        
        # Execute the tool
        return await tool_executor(tool_input)
