from datetime import datetime
from typing import Dict, Any, List, Optional, Protocol
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship, validates
import enum
import uuid
from abc import ABC, abstractmethod

from .base import Base

# Custom exceptions for better error handling
class WorkflowError(Exception):
    """Base exception for workflow-related errors."""
    pass

class ValidationError(WorkflowError):
    """Raised when validation fails."""
    pass

class StateTransitionError(WorkflowError):
    """Raised when a state transition is invalid."""
    pass

# Validation protocols
class Validatable(Protocol):
    """Protocol for objects that can be validated."""
    def validate(self) -> bool: ...

class StatusTransitionValidator(Protocol):
    """Protocol for validating status transitions."""
    def validate_transition(self, current_status: str, new_status: str) -> bool: ...

class StepType(str, enum.Enum):
    PROCESSING = "processing"
    ANALYSIS = "analysis"
    DECISION = "decision"
    ACTION = "action"
    NOTIFICATION = "notification"

class WorkflowStatus(str, enum.Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class ExecutionStatus(str, enum.Enum):
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowModel(Base):
    """Model for storing workflow definitions."""
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.CREATED, nullable=False)
    metadata = Column(JSON, default=dict)
    is_template = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    tags = Column(JSON, default=list)

    # Relationships
    steps = relationship("WorkflowStepModel", back_populates="workflow", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecutionModel", back_populates="workflow", cascade="all, delete-orphan")

    @validates('name')
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError("Workflow name cannot be empty")
        if len(name) > 255:
            raise ValueError("Workflow name cannot exceed 255 characters")
        return name.strip()

    @validates('status')
    def validate_status(self, key, status):
        """Validate status transitions."""
        if hasattr(self, 'status') and self.status != status:
            if not self._is_valid_transition(self.status, status):
                raise StateTransitionError(
                    f"Invalid transition from {self.status} to {status}"
                )
        return status

    def _is_valid_transition(self, current: WorkflowStatus, new: WorkflowStatus) -> bool:
        """Validate workflow status transitions."""
        valid_transitions = {
            WorkflowStatus.CREATED: [WorkflowStatus.RUNNING],
            WorkflowStatus.RUNNING: [WorkflowStatus.PAUSED, WorkflowStatus.COMPLETED, WorkflowStatus.FAILED],
            WorkflowStatus.PAUSED: [WorkflowStatus.RUNNING, WorkflowStatus.FAILED],
            WorkflowStatus.COMPLETED: [],
            WorkflowStatus.FAILED: [WorkflowStatus.CREATED]
        }
        return new in valid_transitions.get(current, [])

    def validate(self) -> bool:
        """Validate the entire workflow."""
        if not self.steps:
            raise ValidationError("Workflow must have at least one step")
        
        # Validate step dependencies
        step_ids = {step.id for step in self.steps}
        for step in self.steps:
            invalid_deps = [dep for dep in step.dependencies if dep not in step_ids]
            if invalid_deps:
                raise ValidationError(f"Step {step.id} has invalid dependencies: {invalid_deps}")
        
        return True

    # Enhanced metrics collection
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive workflow metrics."""
        return {
            "total_steps": len(self.steps),
            "completed_steps": sum(1 for exec in self.executions if exec.status == ExecutionStatus.COMPLETED),
            "failed_steps": sum(1 for exec in self.executions if exec.status == ExecutionStatus.FAILED),
            "average_duration": self._calculate_average_duration(),
            "error_rate": self._calculate_error_rate(),
            "step_metrics": [step.collect_metrics() for step in self.steps]
        }

    def _calculate_average_duration(self) -> Optional[float]:
        """Calculate average workflow duration."""
        completed_execs = [
            exec for exec in self.executions 
            if exec.completed_at and exec.started_at
        ]
        if not completed_execs:
            return None
        
        durations = [
            (exec.completed_at - exec.started_at).total_seconds()
            for exec in completed_execs
        ]
        return sum(durations) / len(durations)

    def _calculate_error_rate(self) -> float:
        """Calculate workflow error rate."""
        total_execs = len(self.executions)
        if not total_execs:
            return 0.0
        failed_execs = sum(1 for exec in self.executions if exec.status == ExecutionStatus.FAILED)
        return failed_execs / total_execs

    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow model to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "status": self.status.value,
            "metadata": self.metadata or {},
            "is_template": self.is_template,
            "version": self.version,
            "tags": self.tags or [],
            "steps": [step.to_dict() for step in self.steps],
            "executions": [execution.to_dict() for execution in self.executions]
        }

class WorkflowStepModel(Base):
    """Model for storing workflow step configurations."""
    __tablename__ = "workflow_steps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(Enum(StepType), nullable=False)
    config = Column(JSON, default=dict)
    dependencies = Column(JSON, default=list)  # List of step IDs this step depends on
    timeout_seconds = Column(Integer, default=300)
    retry_config = Column(JSON, default=dict)
    position = Column(Integer, nullable=False)  # For ordering steps
    is_required = Column(Boolean, default=True)
    error_handling = Column(JSON, default=dict)

    # Relationships
    workflow = relationship("WorkflowModel", back_populates="steps")
    execution_results = relationship("StepExecutionResultModel", back_populates="step", cascade="all, delete-orphan")

    @validates('name')
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError("Step name cannot be empty")
        if len(name) > 255:
            raise ValueError("Step name cannot exceed 255 characters")
        return name.strip()

    @validates('timeout_seconds')
    def validate_timeout(self, key, timeout):
        if timeout < 1:
            raise ValueError("Timeout must be at least 1 second")
        return timeout

    @validates('position')
    def validate_position(self, key, position):
        if position < 0:
            raise ValueError("Position must be non-negative")
        return position

    @validates('config')
    def validate_config(self, key, config):
        """Validate step configuration."""
        if not isinstance(config, dict):
            raise ValidationError("Config must be a dictionary")
        
        required_fields = self._get_required_fields()
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            raise ValidationError(f"Missing required config fields: {missing_fields}")
        
        return config

    def _get_required_fields(self) -> List[str]:
        """Get required configuration fields based on step type."""
        type_requirements = {
            StepType.PROCESSING: ["input_format", "output_format"],
            StepType.ANALYSIS: ["analysis_type", "parameters"],
            StepType.DECISION: ["conditions", "outcomes"],
            StepType.ACTION: ["action_type", "parameters"],
            StepType.NOTIFICATION: ["template", "recipients"]
        }
        return type_requirements.get(self.type, [])

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect step-specific metrics."""
        executions = [result for result in self.execution_results]
        return {
            "total_executions": len(executions),
            "success_rate": self._calculate_success_rate(executions),
            "average_duration": self._calculate_average_duration(executions),
            "retry_rate": self._calculate_retry_rate(executions),
            "error_distribution": self._calculate_error_distribution(executions)
        }

    def _calculate_success_rate(self, executions: List['StepExecutionResultModel']) -> float:
        if not executions:
            return 0.0
        successful = sum(1 for exec in executions if exec.status == 'completed')
        return successful / len(executions)

    def _calculate_average_duration(self, executions: List['StepExecutionResultModel']) -> Optional[float]:
        completed = [exec for exec in executions if exec.duration_ms is not None]
        if not completed:
            return None
        return sum(exec.duration_ms for exec in completed) / len(completed)

    def _calculate_retry_rate(self, executions: List['StepExecutionResultModel']) -> float:
        if not executions:
            return 0.0
        total_retries = sum(exec.retry_count for exec in executions)
        return total_retries / len(executions)

    def _calculate_error_distribution(self, executions: List['StepExecutionResultModel']) -> Dict[str, int]:
        error_counts: Dict[str, int] = {}
        for exec in executions:
            if exec.error_details and 'type' in exec.error_details:
                error_type = exec.error_details['type']
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        return error_counts

    def to_dict(self) -> Dict[str, Any]:
        """Convert the step model to a dictionary."""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "name": self.name,
            "type": self.type.value,
            "config": self.config or {},
            "dependencies": self.dependencies or [],
            "timeout_seconds": self.timeout_seconds,
            "retry_config": self.retry_config or {},
            "position": self.position,
            "is_required": self.is_required,
            "error_handling": self.error_handling or {}
        }

class WorkflowExecutionModel(Base):
    """Model for tracking workflow executions."""
    __tablename__ = "workflow_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.RUNNING, nullable=False)
    current_step = Column(String(36), ForeignKey("workflow_steps.id"))
    results = Column(JSON, default=dict)
    error_details = Column(JSON)
    metrics = Column(JSON, default=dict)  # For storing execution metrics
    triggered_by = Column(String(255))  # User or system that triggered the execution
    execution_context = Column(JSON, default=dict)  # Additional execution context

    # Relationships
    workflow = relationship("WorkflowModel", back_populates="executions")
    step_results = relationship("StepExecutionResultModel", back_populates="execution", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the execution model to a dictionary."""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status.value,
            "current_step": self.current_step,
            "results": self.results or {},
            "error_details": self.error_details,
            "metrics": self.metrics or {},
            "triggered_by": self.triggered_by,
            "execution_context": self.execution_context or {},
            "step_results": [result.to_dict() for result in self.step_results]
        }

class StepExecutionResultModel(Base):
    """Model for storing individual step execution results."""
    __tablename__ = "step_execution_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String(36), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False)
    step_id = Column(String(36), ForeignKey("workflow_steps.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    status = Column(String(50), nullable=False)  # completed, failed, skipped
    result = Column(JSON)
    error_details = Column(JSON)
    metrics = Column(JSON, default=dict)  # Performance metrics for the step
    retry_count = Column(Integer, default=0)
    duration_ms = Column(Integer)  # Execution duration in milliseconds

    # Relationships
    execution = relationship("WorkflowExecutionModel", back_populates="step_results")
    step = relationship("WorkflowStepModel", back_populates="execution_results")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the step execution result to a dictionary."""
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "step_id": self.step_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "result": self.result,
            "error_details": self.error_details,
            "metrics": self.metrics or {},
            "retry_count": self.retry_count,
            "duration_ms": self.duration_ms
        } 