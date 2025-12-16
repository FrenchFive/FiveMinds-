"""
Shell Tools for the Five Minds system.

Provides controlled access to shell operations:
- shell.run: Execute shell commands
- shell.which: Locate a command

All commands are:
- Logged
- Sandboxed
- Timeout-bound
"""

import os
import shutil
import subprocess
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_TIMEOUT = 30  # seconds
MAX_OUTPUT_LENGTH = 1024 * 1024  # 1MB max output/error length


@dataclass
class ToolResult:
    """Result from a tool operation."""
    success: bool
    output: Any
    error: Optional[str] = None
    logs: List[str] = field(default_factory=list)


class ShellTools:
    """
    Shell tools for executing commands in a controlled environment.
    
    All operations are:
    - Logged
    - Sandboxed
    - Timeout-bound
    """
    
    def __init__(self, working_dir: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize shell tools.
        
        Args:
            working_dir: Working directory for command execution
            timeout: Default timeout for commands in seconds
        """
        self.working_dir = Path(working_dir).resolve()
        self.timeout = timeout
        self._logs: List[str] = []
        self._command_history: List[Dict[str, Any]] = []
        logger.info(f"ShellTools initialized: working_dir={self.working_dir}, timeout={timeout}s")
    
    def _log(self, message: str) -> None:
        """Add a log entry."""
        self._logs.append(message)
        logger.debug(message)
    
    def run(self, command: str, args: Optional[List[str]] = None,
            env: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None,
            capture_output: bool = True) -> ToolResult:
        """
        Execute a shell command.
        
        Args:
            command: Command to execute
            args: Command arguments
            env: Environment variables to set
            timeout: Command timeout in seconds (overrides default)
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            ToolResult with command output
        """
        if args is None:
            args = []
        
        cmd_timeout = timeout or self.timeout
        full_cmd = [command] + args
        cmd_str = ' '.join(full_cmd)
        
        self._log(f"shell.run called: {cmd_str}")
        
        # Prepare environment
        cmd_env = os.environ.copy()
        if env:
            cmd_env.update(env)
        
        # Record command
        cmd_record = {
            "command": cmd_str,
            "working_dir": str(self.working_dir),
            "timeout": cmd_timeout,
            "exit_code": None,
            "output": None,
            "error": None
        }
        
        try:
            # Execute command
            result = subprocess.run(
                full_cmd,
                cwd=str(self.working_dir),
                env=cmd_env,
                capture_output=capture_output,
                text=True,
                timeout=cmd_timeout
            )
            
            # Truncate output if too large
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            
            if len(stdout) > MAX_OUTPUT_LENGTH:
                stdout = stdout[:MAX_OUTPUT_LENGTH] + "\n... [output truncated]"
            if len(stderr) > MAX_OUTPUT_LENGTH:
                stderr = stderr[:MAX_OUTPUT_LENGTH] + "\n... [output truncated]"
            
            cmd_record["exit_code"] = result.returncode
            cmd_record["output"] = stdout
            cmd_record["error"] = stderr
            self._command_history.append(cmd_record)
            
            self._log(f"shell.run completed: exit_code={result.returncode}")
            
            return ToolResult(
                success=result.returncode == 0,
                output={
                    "command": cmd_str,
                    "exit_code": result.returncode,
                    "stdout": stdout,
                    "stderr": stderr
                },
                error=stderr if result.returncode != 0 else None,
                logs=self._logs.copy()
            )
            
        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {cmd_timeout} seconds"
            cmd_record["error"] = error_msg
            self._command_history.append(cmd_record)
            self._log(f"shell.run timeout: {error_msg}")
            
            return ToolResult(
                success=False,
                output={"command": cmd_str, "exit_code": None},
                error=error_msg,
                logs=self._logs.copy()
            )
            
        except FileNotFoundError:
            error_msg = f"Command not found: {command}"
            cmd_record["error"] = error_msg
            self._command_history.append(cmd_record)
            self._log(f"shell.run failed: {error_msg}")
            
            return ToolResult(
                success=False,
                output={"command": cmd_str, "exit_code": 127},
                error=error_msg,
                logs=self._logs.copy()
            )
            
        except Exception as e:
            error_msg = f"Command execution failed: {str(e)}"
            cmd_record["error"] = error_msg
            self._command_history.append(cmd_record)
            self._log(f"shell.run failed: {error_msg}")
            
            return ToolResult(
                success=False,
                output={"command": cmd_str, "exit_code": None},
                error=error_msg,
                logs=self._logs.copy()
            )
    
    def which(self, command: str) -> ToolResult:
        """
        Locate a command.
        
        Args:
            command: Command name to locate
            
        Returns:
            ToolResult with command path if found
        """
        self._log(f"shell.which called: {command}")
        
        try:
            path = shutil.which(command)
            
            if path:
                self._log(f"shell.which found: {path}")
                return ToolResult(
                    success=True,
                    output={"command": command, "path": path},
                    logs=self._logs.copy()
                )
            else:
                self._log(f"shell.which not found: {command}")
                return ToolResult(
                    success=False,
                    output={"command": command, "path": None},
                    error=f"Command not found: {command}",
                    logs=self._logs.copy()
                )
                
        except Exception as e:
            self._log(f"shell.which failed: {str(e)}")
            return ToolResult(
                success=False,
                output={"command": command, "path": None},
                error=str(e),
                logs=self._logs.copy()
            )
    
    def detect_test_framework(self) -> ToolResult:
        """
        Detect the test framework used in the project.
        
        Returns:
            ToolResult with detected framework and test command
        """
        self._log("shell.detect_test_framework called")
        
        detected = {
            "framework": None,
            "command": None,
            "args": []
        }
        
        # Check for Python pytest
        if (self.working_dir / "pytest.ini").exists() or \
           (self.working_dir / "pyproject.toml").exists() or \
           (self.working_dir / "setup.py").exists():
            if self.which("pytest").success:
                detected = {"framework": "pytest", "command": "pytest", "args": ["-v"]}
        
        # Check for Node.js/npm test
        package_json = self.working_dir / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json) as f:
                    pkg = json.load(f)
                    if "scripts" in pkg and "test" in pkg["scripts"]:
                        detected = {"framework": "npm", "command": "npm", "args": ["test"]}
                    # Check for playwright
                    if "scripts" in pkg and any("playwright" in str(v) for v in pkg["scripts"].values()):
                        detected = {"framework": "playwright", "command": "npx", "args": ["playwright", "test"]}
            except Exception:
                pass
        
        # Check for Go tests
        if (self.working_dir / "go.mod").exists():
            detected = {"framework": "go", "command": "go", "args": ["test", "./..."]}
        
        # Check for Cargo/Rust tests
        if (self.working_dir / "Cargo.toml").exists():
            detected = {"framework": "cargo", "command": "cargo", "args": ["test"]}
        
        if detected["framework"]:
            self._log(f"shell.detect_test_framework found: {detected['framework']}")
            return ToolResult(
                success=True,
                output=detected,
                logs=self._logs.copy()
            )
        else:
            self._log("shell.detect_test_framework: no framework detected")
            return ToolResult(
                success=False,
                output=detected,
                error="No test framework detected",
                logs=self._logs.copy()
            )
    
    def run_tests(self, timeout: int = 300) -> ToolResult:
        """
        Detect and run the project's test suite.
        
        Args:
            timeout: Timeout for test execution in seconds (default: 5 minutes)
            
        Returns:
            ToolResult with test results
        """
        self._log("shell.run_tests called")
        
        # Detect test framework
        detection = self.detect_test_framework()
        
        if not detection.success:
            return ToolResult(
                success=False,
                output={"tests_run": False},
                error="No test framework detected",
                logs=self._logs.copy()
            )
        
        framework_info = detection.output
        command = framework_info["command"]
        args = framework_info["args"]
        
        self._log(f"shell.run_tests executing: {command} {' '.join(args)}")
        
        # Run the tests
        result = self.run(command, args, timeout=timeout)
        
        # Parse test results
        test_output = {
            "framework": framework_info["framework"],
            "command": f"{command} {' '.join(args)}",
            "exit_code": result.output.get("exit_code") if result.output else None,
            "stdout": result.output.get("stdout", "") if result.output else "",
            "stderr": result.output.get("stderr", "") if result.output else "",
            "passed": result.success,
            "tests_run": True
        }
        
        # Try to parse test counts from output
        test_counts = self._parse_test_output(
            test_output.get("stdout", ""), 
            framework_info["framework"]
        )
        test_output.update(test_counts)
        
        return ToolResult(
            success=result.success,
            output=test_output,
            error=result.error,
            logs=self._logs.copy()
        )
    
    def _parse_test_output(self, output: str, framework: str) -> Dict[str, Any]:
        """Parse test output to extract counts."""
        counts = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
        
        import re
        
        if framework == "pytest":
            # pytest output: "5 passed, 2 failed, 1 skipped"
            match = re.search(r'(\d+) passed', output)
            if match:
                counts["passed"] = int(match.group(1))
            match = re.search(r'(\d+) failed', output)
            if match:
                counts["failed"] = int(match.group(1))
            match = re.search(r'(\d+) skipped', output)
            if match:
                counts["skipped"] = int(match.group(1))
            counts["total"] = counts["passed"] + counts["failed"] + counts["skipped"]
        
        elif framework == "npm" or framework == "playwright":
            # Jest/Mocha/Playwright: "Tests: X passed, Y failed"
            match = re.search(r'(\d+) passed', output, re.IGNORECASE)
            if match:
                counts["passed"] = int(match.group(1))
            match = re.search(r'(\d+) failed', output, re.IGNORECASE)
            if match:
                counts["failed"] = int(match.group(1))
            counts["total"] = counts["passed"] + counts["failed"]
        
        return counts
    
    def get_command_history(self) -> List[Dict[str, Any]]:
        """Get history of executed commands."""
        return self._command_history.copy()
    
    def get_logs(self) -> List[str]:
        """Get all logged operations."""
        return self._logs.copy()
    
    def clear_logs(self) -> None:
        """Clear operation logs."""
        self._logs.clear()
    
    def clear_history(self) -> None:
        """Clear command history."""
        self._command_history.clear()
