"""
Runner - Heavy coding model that implements tickets in isolated sandboxes
"""

import os
import time
import logging
import subprocess
from typing import List, Optional
from pathlib import Path
import tempfile
import shutil

from .models import Ticket, RunnerResult, TicketStatus


logger = logging.getLogger(__name__)


class Runner:
    """
    A Runner is a heavy coding model that:
    1. Implements one ticket at a time
    2. Works in an isolated sandbox environment
    3. Produces diffs, logs, and test results
    """

    def __init__(self, runner_id: str, repo_path: str):
        """
        Initialize a Runner with an ID and repository path.

        Args:
            runner_id: Unique identifier for this runner
            repo_path: Path to the repository
        """
        self.runner_id = runner_id
        self.repo_path = Path(repo_path)
        self.sandbox_path: Optional[Path] = None
        logger.info(f"Runner {runner_id} initialized")

    def create_sandbox(self) -> Path:
        """
        Create an isolated sandbox environment for this runner.

        Returns:
            Path to the sandbox directory
        """
        logger.info(f"Runner {self.runner_id}: Creating sandbox environment")
        
        # Create a temporary directory for the sandbox
        sandbox_dir = tempfile.mkdtemp(prefix=f"fiveminds_sandbox_{self.runner_id}_")
        self.sandbox_path = Path(sandbox_dir)
        
        # Copy repository contents to sandbox
        # In a real system, this might use git worktrees or other isolation mechanisms
        logger.info(f"Runner {self.runner_id}: Copying repository to sandbox")
        
        # Copy files while respecting .gitignore patterns
        for item in self.repo_path.iterdir():
            if item.name.startswith('.') and item.name not in ['.gitignore']:
                continue
            if item.is_dir() and item.name in ['__pycache__', 'node_modules', 'venv', 'env']:
                continue
            
            dest = self.sandbox_path / item.name
            if item.is_dir():
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))
            else:
                shutil.copy2(item, dest)
        
        logger.info(f"Runner {self.runner_id}: Sandbox created at {self.sandbox_path}")
        return self.sandbox_path

    def execute_ticket(self, ticket: Ticket) -> RunnerResult:
        """
        Execute a ticket in the sandbox environment.

        Args:
            ticket: The ticket to execute

        Returns:
            RunnerResult with execution details
        """
        logger.info(f"Runner {self.runner_id}: Executing ticket {ticket.id}")
        start_time = time.time()
        
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.assigned_runner = self.runner_id
        
        logs = [
            f"Runner {self.runner_id} started executing ticket {ticket.id}",
            f"Ticket: {ticket.title}",
            f"Description: {ticket.description}"
        ]
        
        try:
            # Create sandbox if not already created
            if not self.sandbox_path:
                self.create_sandbox()
            
            logs.append(f"Working in sandbox: {self.sandbox_path}")
            
            # This is where the actual implementation would happen
            # In a real system, this would involve:
            # 1. Analyzing the ticket requirements
            # 2. Making code changes
            # 3. Running tests
            # 4. Generating diffs
            
            # For this implementation, we'll simulate the process
            implementation_log = self._implement_ticket(ticket)
            logs.extend(implementation_log)
            
            # Generate diff
            diff = self._generate_diff()
            
            # Run tests
            test_results = self._run_tests()
            logs.append(f"Test results: {test_results}")
            
            execution_time = time.time() - start_time
            
            ticket.status = TicketStatus.NEEDS_REVIEW
            
            result = RunnerResult(
                ticket_id=ticket.id,
                success=True,
                diff=diff,
                logs=logs,
                test_results=test_results,
                execution_time=execution_time
            )
            
            logger.info(f"Runner {self.runner_id}: Ticket {ticket.id} completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error executing ticket: {str(e)}"
            logs.append(error_msg)
            logger.error(f"Runner {self.runner_id}: {error_msg}")
            
            ticket.status = TicketStatus.FAILED
            
            return RunnerResult(
                ticket_id=ticket.id,
                success=False,
                diff="",
                logs=logs,
                error_message=error_msg,
                execution_time=execution_time
            )

    def _implement_ticket(self, ticket: Ticket) -> List[str]:
        """
        Implement the ticket requirements in the sandbox.

        Args:
            ticket: The ticket to implement

        Returns:
            List of log messages
        """
        logs = []
        logs.append(f"Implementing ticket requirements...")
        
        # Simulate implementation
        for criterion in ticket.acceptance_criteria:
            logs.append(f"  - Working on: {criterion.description}")
            time.sleep(0.1)  # Simulate work
            criterion.met = True
            criterion.evidence = f"Implemented in sandbox by Runner {self.runner_id}"
            logs.append(f"  ✓ Completed: {criterion.description}")
        
        logs.append("Implementation complete")
        return logs

    def _generate_diff(self) -> str:
        """
        Generate a diff of changes made in the sandbox.

        Returns:
            Diff string
        """
        # In a real system, this would use git diff or similar
        diff = f"""
diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -1,3 +1,6 @@
+# Changes made by Runner {self.runner_id}
+
 def example_function():
-    pass
+    # Implementation added
+    return "Implemented"
"""
        return diff.strip()

    def _run_tests(self) -> dict:
        """
        Run tests in the sandbox environment.

        Returns:
            Dictionary with test results
        """
        logger.info(f"Runner {self.runner_id}: Running tests in sandbox")
        
        # In a real system, this would run actual tests
        # For now, we'll return a simulated result
        return {
            "total": 5,
            "passed": 5,
            "failed": 0,
            "skipped": 0,
            "duration": 1.23
        }

    def cleanup_sandbox(self):
        """
        Clean up the sandbox environment.
        """
        if self.sandbox_path and self.sandbox_path.exists():
            logger.info(f"Runner {self.runner_id}: Cleaning up sandbox at {self.sandbox_path}")
            shutil.rmtree(self.sandbox_path)
            self.sandbox_path = None

    def __del__(self):
        """
        Cleanup when the runner is destroyed.
        """
        self.cleanup_sandbox()
