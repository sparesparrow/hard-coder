from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload
import json
from collections import deque
import uuid
from contextlib import asynccontextmanager

from ..models.workflows import WorkflowModel, WorkflowStepModel, WorkflowExecutionModel
from ..models.metrics import Metric
from ..websockets.manager import ConnectionManager

logger = logging.getLogger(__name__)

class WorkflowExecutionEngine:
    def __init__(self):
        self.active_executions: Dict[str, asyncio.Task] = {}
        self.execution_locks: Dict[str, asyncio.Lock] = {}
        self.step_handlers: Dict[str, callable] = {}

    def register_step_handler(self, step_type: str, handler: callable):
        """Register a handler for a specific step type."""
        self.step_handlers[step_type] = handler

    async def execute_step(self, step: WorkflowStepModel, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step."""
        handler = self.step_handlers.get(step.type)
        if not handler:
            raise ValueError(f"No handler registered for step type: {step.type}")

        try:
            result = await handler(step, context)
            return {
                "status": "completed",
                "result": result,
                "step_id": step.id
            }
        except Exception as e:
            logger.error(f"Error executing step {step.id}: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "step_id": step.id
            }

    async def execute_workflow(self, workflow: WorkflowModel, execution: WorkflowExecutionModel) -> None:
        """Execute a workflow with proper error handling and retries."""
        context = {
            "workflow_id": workflow.id,
            "execution_id": execution.id,
            "results": {},
            "start_time": datetime.utcnow()
        }

        try:
            # Create execution lock if not exists
            if workflow.id not in self.execution_locks:
                self.execution_locks[workflow.id] = asyncio.Lock()

            async with self.execution_locks[workflow.id]:
                # Execute steps in order, respecting dependencies
                steps_to_execute = deque(workflow.steps)
                completed_steps = set()

                while steps_to_execute:
                    step = steps_to_execute.popleft()

                    # Check dependencies
                    if not all(dep in completed_steps for dep in step.dependencies):
                        steps_to_execute.append(step)
                        continue

                    # Execute step with retry logic
                    retry_count = 0
                    max_retries = step.retry_config.get("max_retries", 3)
                    retry_delay = step.retry_config.get("delay_seconds", 5)

                    while retry_count <= max_retries:
                        try:
                            result = await asyncio.wait_for(
                                self.execute_step(step, context),
                                timeout=step.timeout_seconds
                            )

                            if result["status"] == "completed":
                                context["results"][step.id] = result["result"]
                                completed_steps.add(step.id)
                                break
                            else:
                                retry_count += 1
                                if retry_count <= max_retries:
                                    await asyncio.sleep(retry_delay)
                                else:
                                    raise Exception(f"Step {step.id} failed after {max_retries} retries")

                        except asyncio.TimeoutError:
                            retry_count += 1
                            if retry_count <= max_retries:
                                await asyncio.sleep(retry_delay)
                            else:
                                raise Exception(f"Step {step.id} timed out after {max_retries} retries")

            # Update execution status
            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            execution.results = context["results"]

        except Exception as e:
            logger.error(f"Error executing workflow {workflow.id}: {str(e)}")
            execution.status = "failed"
            execution.completed_at = datetime.utcnow()
            execution.error_details = {
                "error": str(e),
                "step_id": step.id if 'step' in locals() else None,
                "context": context
            }

        finally:
            # Cleanup
            self.active_executions.pop(execution.id, None)

class WorkflowQueue:
    def __init__(self, max_concurrent: int = 10):
        self.queue: deque = deque()
        self.max_concurrent = max_concurrent
        self.current_executions = 0
        self.queue_lock = asyncio.Lock()

    async def enqueue(self, workflow_id: str, priority: int = 0) -> None:
        """Add a workflow to the execution queue."""
        async with self.queue_lock:
            self.queue.append((priority, workflow_id))
            self.queue = deque(sorted(self.queue, key=lambda x: x[0], reverse=True))

    async def dequeue(self) -> Optional[str]:
        """Get the next workflow to execute."""
        async with self.queue_lock:
            if self.current_executions >= self.max_concurrent:
                return None
            
            if not self.queue:
                return None

            self.current_executions += 1
            return self.queue.popleft()[1]

    async def complete_execution(self) -> None:
        """Mark an execution as completed."""
        async with self.queue_lock:
            self.current_executions = max(0, self.current_executions - 1)

class WorkflowService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.execution_engine = WorkflowExecutionEngine()
        self.queue = WorkflowQueue()
        self.register_default_handlers()

    def register_default_handlers(self):
        """Register default step handlers."""
        self.execution_engine.register_step_handler("processing", self.handle_processing_step)
        self.execution_engine.register_step_handler("analysis", self.handle_analysis_step)
        self.execution_engine.register_step_handler("decision", self.handle_decision_step)
        self.execution_engine.register_step_handler("action", self.handle_action_step)
        self.execution_engine.register_step_handler("notification", self.handle_notification_step)

    async def create_workflow(self, workflow_data: Dict[str, Any]) -> WorkflowModel:
        """Create a new workflow."""
        workflow = WorkflowModel(**workflow_data)
        self.session.add(workflow)
        await self.session.commit()
        return workflow

    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowModel]:
        """Get a workflow by ID."""
        query = select(WorkflowModel).where(WorkflowModel.id == workflow_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_workflows(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[WorkflowModel]:
        """Get workflows with optional filtering."""
        query = select(WorkflowModel)
        if status:
            query = query.where(WorkflowModel.status == status)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def execute_workflow(self, workflow_id: str) -> WorkflowExecutionModel:
        """Start workflow execution."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        execution = WorkflowExecutionModel(
            workflow_id=workflow_id,
            status="running"
        )
        self.session.add(execution)
        await self.session.commit()

        # Add to execution queue
        await self.queue.enqueue(workflow_id)

        return execution

    async def pause_workflow(self, workflow_id: str) -> WorkflowModel:
        """Pause a running workflow."""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        if workflow.status != "running":
            raise ValueError(f"Workflow {workflow_id} is not running")

        workflow.status = "paused"
        await self.session.commit()
        return workflow

    async def process_workflow_execution(self, execution_id: str, ws_manager: ConnectionManager) -> None:
        """Process a workflow execution with WebSocket updates."""
        try:
            execution = await self.session.get(WorkflowExecutionModel, execution_id)
            if not execution:
                raise ValueError(f"Execution {execution_id} not found")

            workflow = await self.get_workflow(execution.workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {execution.workflow_id} not found")

            # Create execution task
            task = asyncio.create_task(
                self.execution_engine.execute_workflow(workflow, execution)
            )
            self.execution_engine.active_executions[execution_id] = task

            # Wait for execution to complete
            await task

            # Broadcast completion
            await ws_manager.broadcast({
                "type": "workflow_execution",
                "workflow_id": workflow.id,
                "execution_id": execution_id,
                "status": execution.status,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "results": execution.results
            })

        except Exception as e:
            logger.error(f"Error processing workflow execution {execution_id}: {str(e)}")
            if execution:
                execution.status = "failed"
                execution.error_details = {"error": str(e)}
                await self.session.commit()

        finally:
            await self.queue.complete_execution()

    # Step handlers
    async def handle_processing_step(self, step: WorkflowStepModel, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle processing step type."""
        # Implementation specific to processing steps
        pass

    async def handle_analysis_step(self, step: WorkflowStepModel, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analysis step type."""
        # Implementation specific to analysis steps
        pass

    async def handle_decision_step(self, step: WorkflowStepModel, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle decision step type."""
        # Implementation specific to decision steps
        pass

    async def handle_action_step(self, step: WorkflowStepModel, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle action step type."""
        # Implementation specific to action steps
        pass

    async def handle_notification_step(self, step: WorkflowStepModel, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle notification step type."""
        # Implementation specific to notification steps
        pass 