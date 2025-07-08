"""
LangSmith Service

Provides centralized LangSmith tracing and monitoring functionality for WealthOS.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from ..core.config import settings

# LangSmith setup
try:
    from langsmith import Client, traceable
    from langsmith.run_trees import RunTree

    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    traceable = lambda x: x  # No-op decorator if LangSmith not available

logger = logging.getLogger(__name__)


class LangSmithService:
    """Service for managing LangSmith tracing and monitoring."""

    def __init__(self):
        self.client: Optional[Client] = None
        self.project_name = settings.LANGSMITH_PROJECT
        self.tracing_enabled = settings.LANGSMITH_TRACING
        self._setup_client()

    def _setup_client(self) -> None:
        """Setup LangSmith client."""
        if not LANGSMITH_AVAILABLE:
            logger.warning("LangSmith package not available")
            return

        if not self.tracing_enabled:
            logger.info("LangSmith tracing disabled")
            return

        try:
            # Set environment variables for LangSmith
            os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
            os.environ["LANGSMITH_PROJECT"] = self.project_name
            os.environ["LANGSMITH_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
            os.environ["LANGSMITH_TRACING"] = str(self.tracing_enabled).lower()

            # Create client
            self.client = Client(
                api_key=settings.LANGSMITH_API_KEY,
                api_url=settings.LANGSMITH_ENDPOINT,
            )

            logger.info(
                f"LangSmith client initialized for project: {self.project_name}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize LangSmith client: {e}")
            self.client = None

    def create_run_tree(
        self,
        name: str,
        run_type: str = "chain",
        inputs: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[RunTree]:
        """Create a new run tree for tracing."""
        if not self.client or not self.tracing_enabled:
            return None

        try:
            run_tree = RunTree(
                name=name,
                run_type=run_type,
                inputs=inputs or {},
                tags=tags or [],
                project_name=self.project_name,
            )
            return run_tree
        except Exception as e:
            logger.error(f"Failed to create run tree: {e}")
            return None

    def create_child_run(
        self,
        parent_run: RunTree,
        name: str,
        run_type: str = "chain",
        inputs: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[RunTree]:
        """Create a child run under a parent run."""
        if not self.client or not self.tracing_enabled or not parent_run:
            return None

        try:
            # Ensure run_type is valid
            valid_run_types = [
                "tool",
                "chain",
                "llm",
                "retriever",
                "embedding",
                "prompt",
                "parser",
            ]
            if run_type not in valid_run_types:
                run_type = "chain"

            child_run = parent_run.create_child(
                name=name,
                run_type=run_type,  # type: ignore
                inputs=inputs or {},
                tags=tags or [],
            )
            return child_run
        except Exception as e:
            logger.error(f"Failed to create child run: {e}")
            return None

    def log_llm_call(
        self,
        run_tree: Optional[RunTree],
        model_name: str,
        prompt: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an LLM call to LangSmith."""
        if not run_tree or not self.tracing_enabled:
            return

        try:
            llm_run = run_tree.create_child(
                name=f"LLM: {model_name}",
                run_type="llm",  # type: ignore
                inputs={
                    "prompt": prompt,
                    "model": model_name,
                    **(metadata or {}),
                },
                tags=["llm", model_name],
            )
            llm_run.outputs = {"response": response}
            llm_run.end()
        except Exception as e:
            logger.error(f"Failed to log LLM call: {e}")

    def log_tool_call(
        self,
        run_tree: Optional[RunTree],
        tool_name: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a tool call to LangSmith."""
        if not run_tree or not self.tracing_enabled:
            return

        try:
            tool_run = run_tree.create_child(
                name=f"Tool: {tool_name}",
                run_type="tool",  # type: ignore
                inputs={
                    "tool_name": tool_name,
                    "inputs": inputs,
                    **(metadata or {}),
                },
                tags=["tool", tool_name],
            )
            tool_run.outputs = outputs
            tool_run.end()
        except Exception as e:
            logger.error(f"Failed to log tool call: {e}")

    def is_available(self) -> bool:
        """Check if LangSmith is available and configured."""
        return LANGSMITH_AVAILABLE and self.client is not None and self.tracing_enabled

    def get_project_stats(self) -> Optional[Dict[str, Any]]:
        """Get project statistics from LangSmith."""
        if not self.client:
            return None

        try:
            # This would require implementing LangSmith API calls
            # For now, return basic info
            return {
                "project_name": self.project_name,
                "tracing_enabled": self.tracing_enabled,
                "client_available": self.client is not None,
            }
        except Exception as e:
            logger.error(f"Failed to get project stats: {e}")
            return None


# Global instance
langsmith_service = LangSmithService()


def get_langsmith_service() -> LangSmithService:
    """Get the global LangSmith service instance."""
    return langsmith_service


# Convenience decorator for tracing functions
def trace_function(name: Optional[str] = None, tags: Optional[List[str]] = None):
    """Decorator to trace function calls with LangSmith."""
    if not LANGSMITH_AVAILABLE:
        return lambda func: func

    def decorator(func):
        return traceable(name=name, tags=tags)(func)

    return decorator
