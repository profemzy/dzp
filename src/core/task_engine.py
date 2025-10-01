"""
Simplified task execution engine for processing and executing user requests
Now uses LangChain for NLP processing instead of custom NLP processor
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any, Optional, Callable

from src.core.config import Config
from src.core.logger import get_logger
from src.terraform.cli import TerraformCLI
from src.terraform.parser import TerraformParser

logger = get_logger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a task to be executed"""
    id: str
    query: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: float = 0.0
    created_at: Optional[float] = None
    completed_at: Optional[float] = None


class TaskEngine:
    """Simplified task execution engine focused on Terraform operations"""
    
    def __init__(self, config: Config):
        self.config = config
        self.parser = TerraformParser(config.terraform_dir)
        self.terraform_cli = TerraformCLI(
            terraform_path=config.terraform_path,
            working_dir=config.terraform_dir
        )
        
        self.tasks: Dict[str, Task] = {}
        self.task_callbacks: List[Callable[[Task], None]] = []
        
        # Cache for parsed project
        self._project_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[float] = None
        self._cache_ttl = 60  # seconds
    
    def add_task_callback(self, callback: Callable[[Task], None]):
        """Add callback for task status updates"""
        self.task_callbacks.append(callback)
    
    def _notify_task_update(self, task: Task):
        """Notify callbacks of task update"""
        for callback in self.task_callbacks:
            try:
                callback(task)
            except Exception as e:
                logger.error(f"Task callback failed: {e}")
    
    def get_project_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get parsed project data with caching"""
        import time
        
        current_time = time.time()
        
        if (force_refresh or 
            self._project_cache is None or 
            self._cache_timestamp is None or 
            current_time - self._cache_timestamp > self._cache_ttl):
            
            logger.info("Parsing Terraform project")
            self._project_cache = self.parser.parse_project()
            self._cache_timestamp = current_time
        
        return self._project_cache
    
    def create_task(self, query: str) -> Task:
        """Create a new task from user query"""
        import time
        import uuid
        
        # Create task
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            query=query,
            status=TaskStatus.PENDING,
            created_at=time.time()
        )
        
        self.tasks[task_id] = task
        logger.info(f"Created task {task_id} for query: {query}")
        
        return task
    
    async def execute_task(self, task_id: str) -> Task:
        """Execute a task"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = TaskStatus.RUNNING
        self._notify_task_update(task)
        
        try:
            # For now, just return project data since LangChain handles the actual processing
            result = await self._execute_simple_query(task)
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.progress = 1.0
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            task.error = str(e)
            task.status = TaskStatus.FAILED
        
        import time
        task.completed_at = time.time()
        self._notify_task_update(task)
        
        return task
    
    async def _execute_simple_query(self, task: Task) -> Dict[str, Any]:
        """Execute simple query - just return project data for LangChain to process"""
        logger.info(f"Executing query: {task.query}")
        task.progress = 0.5
        
        # Get project data
        project_data = self.get_project_data()
        task.progress = 0.8
        
        return {
            "action": "query",
            "query": task.query,
            "project_data": project_data
        }
    
    async def execute_terraform_init(self) -> Dict[str, Any]:
        """Execute terraform init"""
        logger.info("Executing terraform init")
        result = await self.terraform_cli.init()
        
        return {
            "action": "terraform_init",
            "success": result.success,
            "output": result.stdout,
            "error": result.stderr if not result.success else None,
            "duration": result.duration
        }
    
    async def execute_terraform_plan(self, detailed: bool = True) -> Dict[str, Any]:
        """Execute terraform plan"""
        logger.info("Executing terraform plan")
        result = await self.terraform_cli.plan(detailed_exitcode=detailed)
        
        # Parse plan output for summary
        summary = {}
        if result.success and isinstance(result.stdout, str):
            summary = self.terraform_cli.get_plan_summary(result.stdout)
        
        return {
            "action": "terraform_plan",
            "success": result.success,
            "output": result.stdout,
            "error": result.stderr if not result.success else None,
            "summary": summary,
            "duration": result.duration
        }
    
    async def execute_terraform_apply(self, auto_approve: bool = False) -> Dict[str, Any]:
        """Execute terraform apply"""
        logger.info("Executing terraform apply")
        result = await self.terraform_cli.apply(auto_approve=auto_approve)
        
        return {
            "action": "terraform_apply",
            "success": result.success,
            "output": result.stdout,
            "error": result.stderr if not result.success else None,
            "duration": result.duration
        }
    
    async def execute_terraform_destroy(self, auto_approve: bool = False) -> Dict[str, Any]:
        """Execute terraform destroy"""
        logger.info("Executing terraform destroy")
        result = await self.terraform_cli.destroy(auto_approve=auto_approve)
        
        return {
            "action": "terraform_destroy",
            "success": result.success,
            "output": result.stdout,
            "error": result.stderr if not result.success else None,
            "duration": result.duration
        }
    
    async def execute_terraform_validate(self) -> Dict[str, Any]:
        """Execute terraform validate"""
        logger.info("Executing terraform validate")
        result = await self.terraform_cli.validate()
        
        return {
            "action": "terraform_validate",
            "success": result.success,
            "output": result.stdout,
            "error": result.stderr if not result.success else None,
            "duration": result.duration
        }
    
    async def execute_terraform_show(self) -> Dict[str, Any]:
        """Execute terraform show"""
        logger.info("Executing terraform show")
        result = await self.terraform_cli.show()
        
        return {
            "action": "terraform_show",
            "success": result.success,
            "output": result.stdout,
            "error": result.stderr if not result.success else None,
            "duration": result.duration
        }
    
    async def execute_terraform_output(self, name: str = None) -> Dict[str, Any]:
        """Execute terraform output"""
        logger.info(f"Executing terraform output{' for ' + name if name else ''}")
        result = await self.terraform_cli.output(name=name)
        
        return {
            "action": "terraform_output",
            "success": result.success,
            "output": result.stdout,
            "error": result.stderr if not result.success else None,
            "duration": result.duration
        }
    
    async def execute_terraform_state_list(self) -> Dict[str, Any]:
        """Execute terraform state list"""
        logger.info("Executing terraform state list")
        result = await self.terraform_cli.state_list()
        
        return {
            "action": "terraform_state_list",
            "success": result.success,
            "output": result.stdout,
            "error": result.stderr if not result.success else None,
            "duration": result.duration
        }
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return list(self.tasks.values())
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                task.status = TaskStatus.CANCELLED
                self._notify_task_update(task)
                return True
        return False
