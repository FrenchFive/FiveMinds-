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
