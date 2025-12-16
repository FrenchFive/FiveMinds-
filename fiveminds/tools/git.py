"""
Git Tools for the Five Minds system.

Provides controlled access to Git operations:
- git.status: Get repository status
- git.checkout: Checkout a branch or file
- git.create_branch: Create a new branch
- git.merge: Merge branches
- git.diff: Show differences

All commands are:
- Logged
- Sandboxed
- Timeout-bound
"""

import subprocess
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_TIMEOUT = 30  # seconds


@dataclass
class ToolResult:
    """Result from a tool operation."""
    success: bool
    output: Any
    error: Optional[str] = None
    logs: List[str] = field(default_factory=list)


class GitTools:
    """
    Git tools for version control operations.
    
    All operations are:
    - Logged
    - Sandboxed
    - Timeout-bound
    """
    
    def __init__(self, repo_path: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize Git tools.
        
        Args:
            repo_path: Path to the Git repository
            timeout: Default timeout for git commands in seconds
        """
        self.repo_path = Path(repo_path).resolve()
        self.timeout = timeout
        self._logs: List[str] = []
        logger.info(f"GitTools initialized for: {self.repo_path}")
        
        # Verify it's a git repository
        if not (self.repo_path / '.git').exists():
            logger.warning(f"Not a git repository: {self.repo_path}")
    
    def _log(self, message: str) -> None:
        """Add a log entry."""
        self._logs.append(message)
        logger.debug(message)
    
    def _run_git(self, args: List[str], timeout: Optional[int] = None) -> ToolResult:
        """
        Run a git command.
        
        Args:
            args: Git command arguments
            timeout: Command timeout (overrides default)
            
        Returns:
            ToolResult with command output
        """
        cmd_timeout = timeout or self.timeout
        cmd = ['git'] + args
        cmd_str = ' '.join(cmd)
        
        self._log(f"Executing: {cmd_str}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=cmd_timeout
            )
            
            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    output=result.stdout.strip(),
                    logs=self._logs.copy()
                )
            else:
                return ToolResult(
                    success=False,
                    output=result.stdout.strip() if result.stdout else None,
                    error=result.stderr.strip(),
                    logs=self._logs.copy()
                )
                
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output=None,
                error=f"Git command timed out after {cmd_timeout} seconds",
                logs=self._logs.copy()
            )
            
        except FileNotFoundError:
            return ToolResult(
                success=False,
                output=None,
                error="Git is not installed or not in PATH",
                logs=self._logs.copy()
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                logs=self._logs.copy()
            )
    
    def status(self, short: bool = False, 
               untracked: str = "normal") -> ToolResult:
        """
        Get repository status.
        
        Args:
            short: Use short format output
            untracked: Show untracked files (normal, no, all)
            
        Returns:
            ToolResult with status information
        """
        self._log(f"git.status called: short={short}, untracked={untracked}")
        
        args = ['status']
        
        if short:
            args.append('-s')
        
        args.extend(['--untracked-files', untracked])
        
        result = self._run_git(args)
        
        if result.success:
            self._log("git.status completed successfully")
            
            # Parse status output for structured data
            status_info = self._parse_status(result.output, short)
            
            return ToolResult(
                success=True,
                output=status_info,
                logs=self._logs.copy()
            )
        
        return result
    
    def checkout(self, target: str, create: bool = False,
                 files: Optional[List[str]] = None) -> ToolResult:
        """
        Checkout a branch or files.
        
        Args:
            target: Branch name or commit to checkout
            create: Create branch if it doesn't exist (-b flag)
            files: Specific files to checkout (optional)
            
        Returns:
            ToolResult with checkout result
        """
        self._log(f"git.checkout called: target={target}, create={create}")
        
        args = ['checkout']
        
        if create:
            args.append('-b')
        
        args.append(target)
        
        if files:
            args.append('--')
            args.extend(files)
        
        result = self._run_git(args)
        
        if result.success:
            self._log(f"git.checkout completed: {target}")
        else:
            self._log(f"git.checkout failed: {result.error}")
        
        return result
    
    def create_branch(self, branch_name: str, 
                      start_point: Optional[str] = None) -> ToolResult:
        """
        Create a new branch.
        
        Args:
            branch_name: Name for the new branch
            start_point: Starting point for the branch (optional)
            
        Returns:
            ToolResult with branch creation result
        """
        self._log(f"git.create_branch called: branch_name={branch_name}")
        
        args = ['branch', branch_name]
        
        if start_point:
            args.append(start_point)
        
        result = self._run_git(args)
        
        if result.success:
            self._log(f"git.create_branch completed: {branch_name}")
        else:
            self._log(f"git.create_branch failed: {result.error}")
        
        return result
    
    def merge(self, branch: str, no_ff: bool = False,
              message: Optional[str] = None) -> ToolResult:
        """
        Merge a branch into current branch.
        
        Args:
            branch: Branch to merge
            no_ff: Create merge commit even for fast-forward
            message: Merge commit message
            
        Returns:
            ToolResult with merge result
        """
        self._log(f"git.merge called: branch={branch}, no_ff={no_ff}")
        
        args = ['merge']
        
        if no_ff:
            args.append('--no-ff')
        
        if message:
            args.extend(['-m', message])
        
        args.append(branch)
        
        result = self._run_git(args)
        
        if result.success:
            self._log(f"git.merge completed: {branch}")
        else:
            self._log(f"git.merge failed: {result.error}")
        
        return result
    
    def diff(self, target: Optional[str] = None,
             staged: bool = False,
             files: Optional[List[str]] = None,
             context_lines: int = 3) -> ToolResult:
        """
        Show differences.
        
        Args:
            target: Compare against target (branch, commit, etc.)
            staged: Show staged changes (--cached)
            files: Limit diff to specific files
            context_lines: Number of context lines
            
        Returns:
            ToolResult with diff output
        """
        self._log(f"git.diff called: target={target}, staged={staged}")
        
        args = ['diff', f'-U{context_lines}']
        
        if staged:
            args.append('--cached')
        
        if target:
            args.append(target)
        
        if files:
            args.append('--')
            args.extend(files)
        
        result = self._run_git(args)
        
        if result.success:
            self._log("git.diff completed successfully")
            
            # Parse diff for structured output
            diff_info = self._parse_diff(result.output)
            
            return ToolResult(
                success=True,
                output=diff_info,
                logs=self._logs.copy()
            )
        
        return result
    
    def _parse_status(self, output: str, short: bool) -> Dict[str, Any]:
        """Parse git status output into structured data."""
        result = {
            "raw": output,
            "staged": [],
            "unstaged": [],
            "untracked": [],
            "branch": None
        }
        
        if short:
            for line in output.split('\n'):
                if not line:
                    continue
                status = line[:2]
                file_path = line[3:]
                
                if status[0] == '?':
                    result["untracked"].append(file_path)
                elif status[0] != ' ':
                    result["staged"].append({"status": status[0], "file": file_path})
                elif status[1] != ' ':
                    result["unstaged"].append({"status": status[1], "file": file_path})
        else:
            # Parse long format
            section = None
            for line in output.split('\n'):
                if 'On branch' in line:
                    result["branch"] = line.replace('On branch ', '').strip()
                elif 'Changes to be committed' in line:
                    section = "staged"
                elif 'Changes not staged' in line:
                    section = "unstaged"
                elif 'Untracked files' in line:
                    section = "untracked"
                elif line.strip().startswith(('modified:', 'new file:', 'deleted:')):
                    parts = line.strip().split(':', 1)
                    if len(parts) == 2:
                        status = parts[0].strip()
                        file_path = parts[1].strip()
                        if section == "staged":
                            result["staged"].append({"status": status, "file": file_path})
                        elif section == "unstaged":
                            result["unstaged"].append({"status": status, "file": file_path})
                elif section == "untracked" and line.strip() and line.startswith('\t'):
                    # Git uses tab indentation for untracked files
                    result["untracked"].append(line.strip())
        
        return result
    
    def _parse_diff(self, output: str) -> Dict[str, Any]:
        """Parse git diff output into structured data."""
        result = {
            "raw": output,
            "files": [],
            "stats": {
                "additions": 0,
                "deletions": 0,
                "files_changed": 0
            }
        }
        
        current_file = None
        additions = 0
        deletions = 0
        
        for line in output.split('\n'):
            if line.startswith('diff --git'):
                if current_file:
                    result["files"].append({
                        "file": current_file,
                        "additions": additions,
                        "deletions": deletions
                    })
                # Extract file path
                parts = line.split(' b/')
                if len(parts) > 1:
                    current_file = parts[1]
                additions = 0
                deletions = 0
            elif line.startswith('+') and not line.startswith('+++'):
                additions += 1
                result["stats"]["additions"] += 1
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1
                result["stats"]["deletions"] += 1
        
        if current_file:
            result["files"].append({
                "file": current_file,
                "additions": additions,
                "deletions": deletions
            })
        
        result["stats"]["files_changed"] = len(result["files"])
        
        return result
    
    def get_logs(self) -> List[str]:
        """Get all logged operations."""
        return self._logs.copy()
    
    def clear_logs(self) -> None:
        """Clear operation logs."""
        self._logs.clear()
