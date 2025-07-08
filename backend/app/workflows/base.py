"""
Base Workflow Infrastructure

Provides base classes and utilities for LangGraph workflows in WealthOS.
"""

import asyncio
import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar

from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from pydantic import BaseModel

# Import for proper type handling
try:
    from app.schemas.fund_analysis import PortfolioSummary
except ImportError:
    PortfolioSummary = None

# LangSmith setup
try:
    from langsmith import traceable
    from langsmith.run_trees import RunTree

    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    traceable = lambda x: x  # No-op decorator if LangSmith not available

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class WorkflowState(BaseModel):
    """Base state for all workflows."""

    workflow_id: str
    status: str = "pending"
    progress: float = 0.0
    current_step: str = "initialization"
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    messages: List[BaseMessage] = []
    context: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True


class WorkflowStep(ABC):
    """Base class for workflow steps."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{name}")

    @abstractmethod
    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Execute the workflow step."""
        pass

    async def on_error(self, state: WorkflowState, error: Exception) -> WorkflowState:
        """Handle step errors."""
        self.logger.error(f"Error in step {self.name}: {error}")
        state.status = "error"
        state.error_message = str(error)
        return state


class BaseWorkflow(ABC):
    """Base class for all LangGraph workflows."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.graph = None
        self.checkpointer = MemorySaver()
        self.steps: List[WorkflowStep] = []
        self.run_tree: Optional[RunTree] = None

        # Setup LangSmith tracing
        self._setup_langsmith()

    def _setup_langsmith(self) -> None:
        """Setup LangSmith tracing environment variables."""
        try:
            # Check if tracing should be enabled
            if os.getenv("LANGSMITH_TRACING", "false").lower() == "true":
                if LANGSMITH_AVAILABLE:
                    self.logger.info(
                        f"LangSmith tracing enabled for workflow: {self.name}"
                    )
                else:
                    self.logger.warning(
                        "LangSmith tracing requested but langsmith package not available"
                    )
            else:
                self.logger.debug("LangSmith tracing disabled")
        except Exception as e:
            self.logger.error(f"Failed to setup LangSmith: {e}")

    def _create_run_tree(self, workflow_id: str) -> Optional[RunTree]:
        """Create a LangSmith run tree for tracing."""
        if (
            not LANGSMITH_AVAILABLE
            or os.getenv("LANGSMITH_TRACING", "false").lower() != "true"
        ):
            return None

        try:
            run_tree = RunTree(
                name=f"Workflow: {self.name}",
                run_type="chain",
                inputs={
                    "workflow_id": workflow_id,
                    "workflow_name": self.name,
                    "description": self.description,
                },
                tags=["workflow", "langgraph", self.name],
            )
            return run_tree
        except Exception as e:
            self.logger.error(f"Failed to create LangSmith run tree: {e}")
            return None

    def add_step(self, step: WorkflowStep) -> None:
        """Add a step to the workflow."""
        self.steps.append(step)

    def _serialize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize complex objects for LangGraph storage."""
        import pandas as pd
        from pydantic import BaseModel

        def serialize_value(value):
            """Recursively serialize a value."""
            if isinstance(value, BaseModel):
                # For all Pydantic models, serialize to dict with type info
                return {
                    "_type": value.__class__.__name__,
                    "_module": value.__class__.__module__,
                    "_data": value.dict(),
                }
            elif isinstance(value, pd.Series):
                return {
                    "_type": "pandas.Series",
                    "_data": {
                        "values": value.values.tolist(),
                        "index": value.index.tolist(),
                        "name": value.name,
                    },
                }
            elif isinstance(value, pd.DataFrame):
                return {
                    "_type": "pandas.DataFrame",
                    "_data": {
                        "values": value.values.tolist(),
                        "columns": value.columns.tolist(),
                        "index": value.index.tolist(),
                    },
                }
            elif isinstance(value, dict):
                return {k: serialize_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [serialize_value(item) for item in value]
            else:
                # For primitive types, return as-is
                return value

        serialized = {}
        for key, value in context.items():
            serialized[key] = serialize_value(value)
        return serialized

    def _deserialize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize complex objects from LangGraph storage."""
        import pandas as pd
        from pydantic import BaseModel
        import importlib

        def deserialize_value(value):
            """Recursively deserialize a value."""
            if isinstance(value, dict):
                if "_type" in value and "_data" in value:
                    obj_type = value["_type"]
                    obj_data = value["_data"]

                    if obj_type == "pandas.Series":
                        return pd.Series(
                            data=obj_data["values"],
                            index=obj_data["index"],
                            name=obj_data["name"],
                        )
                    elif obj_type == "pandas.DataFrame":
                        return pd.DataFrame(
                            data=obj_data["values"],
                            columns=obj_data["columns"],
                            index=obj_data["index"],
                        )
                    else:
                        # For Pydantic models, reconstruct from module and class name
                        if "_module" in value:
                            try:
                                module = importlib.import_module(value["_module"])
                                model_class = getattr(module, obj_type)
                                if issubclass(model_class, BaseModel):
                                    return model_class(**obj_data)
                            except (ImportError, AttributeError) as e:
                                self.logger.warning(
                                    f"Failed to deserialize {obj_type}: {e}"
                                )

                        # Fallback: try to deserialize data recursively
                        return deserialize_value(obj_data)
                else:
                    # Regular dict, deserialize recursively
                    return {k: deserialize_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [deserialize_value(item) for item in value]
            else:
                # For primitive types, return as-is
                return value

        deserialized = {}
        for key, value in context.items():
            deserialized[key] = deserialize_value(value)
        return deserialized

    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow graph."""
        graph = StateGraph(WorkflowState)

        # Add nodes for each step
        for step in self.steps:
            graph.add_node(step.name, self._create_step_node(step))

        # Add edges between steps
        for i, step in enumerate(self.steps):
            if i == 0:
                graph.set_entry_point(step.name)
            if i < len(self.steps) - 1:
                graph.add_edge(step.name, self.steps[i + 1].name)
            else:
                graph.add_edge(step.name, END)

        return graph

    def _create_step_node(self, step: WorkflowStep):
        """Create a node function for a workflow step."""

        async def node_function(state: WorkflowState) -> WorkflowState:
            try:
                self.logger.info(f"Executing step: {step.name}")
                state.current_step = step.name

                # Deserialize context for step execution
                state.context = self._deserialize_context(state.context)

                # Execute the step
                result_state = await step.execute(state)

                # Update progress
                step_index = self.steps.index(step)
                result_state.progress = ((step_index + 1) / len(self.steps)) * 100

                # Serialize context back for storage
                result_state.context = self._serialize_context(result_state.context)

                return result_state

            except Exception as e:
                return await step.on_error(state, e)

        return node_function

    async def execute(
        self, initial_state: Optional[WorkflowState] = None
    ) -> WorkflowState:
        """Execute the workflow."""
        if not self.graph:
            self.graph = self.build_graph()

        # Create initial state if not provided
        if initial_state is None:
            initial_state = WorkflowState(
                workflow_id=str(uuid.uuid4()), started_at=datetime.now()
            )

        initial_state.status = "running"

        # Create LangSmith run tree for tracing
        self.run_tree = self._create_run_tree(initial_state.workflow_id)
        if self.run_tree:
            self.run_tree.inputs = {
                "workflow_id": initial_state.workflow_id,
                "workflow_name": self.name,
                "initial_state": initial_state.dict(),
            }

        try:
            # Compile and run the graph
            compiled_graph = self.graph.compile(checkpointer=self.checkpointer)

            # Serialize the context for LangGraph
            serialized_state = initial_state.copy()
            serialized_state.context = self._serialize_context(initial_state.context)

            # Execute the workflow
            result = await compiled_graph.ainvoke(
                serialized_state.dict(),
                config={"configurable": {"thread_id": initial_state.workflow_id}},
            )

            # Convert result back to WorkflowState and deserialize context
            final_state = WorkflowState(**result)
            final_state.context = self._deserialize_context(final_state.context)
            final_state.status = "completed"
            final_state.completed_at = datetime.now()

            # Log completion to LangSmith
            if self.run_tree:
                self.run_tree.outputs = {
                    "final_state": final_state.dict(),
                    "status": "completed",
                    "duration": (
                        final_state.completed_at - final_state.started_at
                    ).total_seconds(),
                }
                self.run_tree.end()

            self.logger.info(f"Workflow {self.name} completed successfully")
            return final_state

        except Exception as e:
            self.logger.error(f"Workflow {self.name} failed: {e}")
            error_state = WorkflowState(
                workflow_id=initial_state.workflow_id,
                started_at=initial_state.started_at,
                status="error",
                error_message=str(e),
                completed_at=datetime.now(),
            )

            # Log error to LangSmith
            if self.run_tree:
                self.run_tree.outputs = {
                    "error": str(e),
                    "status": "error",
                }
                self.run_tree.end()

            return error_state

    async def get_status(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get the current status of a workflow execution."""
        try:
            if not self.graph:
                return None

            compiled_graph = self.graph.compile(checkpointer=self.checkpointer)

            # Get the current state from checkpointer
            checkpoint = await compiled_graph.aget_state(
                config={"configurable": {"thread_id": workflow_id}}
            )

            if checkpoint and checkpoint.values:
                return WorkflowState(**checkpoint.values)

            return None

        except Exception as e:
            self.logger.error(f"Failed to get workflow status: {e}")
            return None


class ValidationStep(WorkflowStep):
    """Generic validation step for workflows."""

    def __init__(self, name: str, validator_func, description: str = ""):
        super().__init__(name, description)
        self.validator_func = validator_func

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Execute validation."""
        try:
            is_valid = await self.validator_func(state)
            if not is_valid:
                raise ValueError(f"Validation failed in step {self.name}")
            return state
        except Exception as e:
            raise ValueError(f"Validation error in step {self.name}: {e}")


class TransformStep(WorkflowStep):
    """Generic transformation step for workflows."""

    def __init__(self, name: str, transform_func, description: str = ""):
        super().__init__(name, description)
        self.transform_func = transform_func

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Execute transformation."""
        try:
            result = await self.transform_func(state)
            if isinstance(result, WorkflowState):
                return result
            else:
                # If transform_func returns data, add it to context
                state.context.update(
                    result if isinstance(result, dict) else {"result": result}
                )
                return state
        except Exception as e:
            raise ValueError(f"Transformation error in step {self.name}: {e}")


class WorkflowManager:
    """Manages multiple workflow instances."""

    def __init__(self):
        self.workflows: Dict[str, BaseWorkflow] = {}
        self.executions: Dict[str, WorkflowState] = {}
        self.logger = logging.getLogger(__name__)

    def register_workflow(self, workflow: BaseWorkflow) -> None:
        """Register a workflow."""
        self.workflows[workflow.name] = workflow
        self.logger.info(f"Registered workflow: {workflow.name}")

    async def execute_workflow(
        self, workflow_name: str, initial_state: Optional[WorkflowState] = None
    ) -> WorkflowState:
        """Execute a workflow by name."""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        workflow = self.workflows[workflow_name]
        result = await workflow.execute(initial_state)

        # Store execution result
        self.executions[result.workflow_id] = result

        return result

    async def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow execution status."""
        # Check stored executions first
        if workflow_id in self.executions:
            return self.executions[workflow_id]

        # Check active workflows
        for workflow in self.workflows.values():
            status = await workflow.get_status(workflow_id)
            if status:
                return status

        return None

    def list_workflows(self) -> List[str]:
        """List all registered workflows."""
        return list(self.workflows.keys())


# Global workflow manager instance
workflow_manager = WorkflowManager()


# Utility functions


async def create_timed_step(name: str, func, description: str = "") -> WorkflowStep:
    """Create a timed workflow step."""

    class TimedStep(WorkflowStep):
        async def execute(self, state: WorkflowState) -> WorkflowState:
            start_time = time.time()
            try:
                result = await func(state)
                execution_time = time.time() - start_time
                state.context[f"{name}_execution_time"] = execution_time
                return result if isinstance(result, WorkflowState) else state
            except Exception as e:
                execution_time = time.time() - start_time
                state.context[f"{name}_execution_time"] = execution_time
                raise e

    return TimedStep(name, description)


async def create_retry_step(
    name: str, func, max_retries: int = 3, delay: float = 1.0, description: str = ""
) -> WorkflowStep:
    """Create a workflow step with retry logic."""

    class RetryStep(WorkflowStep):
        async def execute(self, state: WorkflowState) -> WorkflowState:
            last_error = None

            for attempt in range(max_retries):
                try:
                    result = await func(state)
                    return result if isinstance(result, WorkflowState) else state
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2**attempt))  # Exponential backoff

            if last_error:
                raise last_error
            else:
                raise RuntimeError("Retry step failed with no recorded error")

    return RetryStep(name, description)
