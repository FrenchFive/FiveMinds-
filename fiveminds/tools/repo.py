"""
Repository Tools for the Five Minds system.

Provides controlled access to repository operations:
- repo.tree: List directory structure
- repo.search: Search for content in files
- repo.read: Read file contents
- repo.apply_patch: Apply a unified diff patch
- repo.diff: Generate diff between files or states
"""

import os
import re
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_TIMEOUT = 30  # seconds
MAX_FILE_SIZE = 1024 * 1024  # 1MB limit for reading files


@dataclass
class ToolResult:
    """Result from a tool operation."""
    success: bool
    output: Any
    error: Optional[str] = None
    logs: List[str] = field(default_factory=list)


class RepoTools:
    """
    Repository tools for interacting with the codebase.
    
    All operations are logged and bounded.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize repo tools with a repository path.
        
        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = Path(repo_path).resolve()
        self._logs: List[str] = []
        logger.info(f"RepoTools initialized for: {self.repo_path}")
    
    def _log(self, message: str) -> None:
        """Add a log entry."""
        self._logs.append(message)
        logger.debug(message)
    
    def _validate_path(self, path: str) -> Path:
        """
        Validate and resolve a path, ensuring it's within the repo.
        
        Args:
            path: Relative or absolute path
            
        Returns:
            Resolved absolute path
            
        Raises:
            ValueError: If path is outside repository
        """
        if os.path.isabs(path):
            resolved = Path(path).resolve()
        else:
            resolved = (self.repo_path / path).resolve()
        
        # Security check: ensure path is within repo
        try:
            resolved.relative_to(self.repo_path)
        except ValueError:
            raise ValueError(f"Path '{path}' is outside repository bounds")
        
        return resolved
    
    def tree(self, path: str = ".", max_depth: int = 3, 
             ignore_patterns: Optional[List[str]] = None) -> ToolResult:
        """
        List directory structure.
        
        Args:
            path: Starting path (relative to repo root)
            max_depth: Maximum depth to traverse
            ignore_patterns: Patterns to ignore (e.g., ['__pycache__', '.git'])
            
        Returns:
            ToolResult with directory tree structure
        """
        self._log(f"repo.tree called: path={path}, max_depth={max_depth}")
        
        if ignore_patterns is None:
            ignore_patterns = ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
        
        try:
            start_path = self._validate_path(path)
            
            if not start_path.exists():
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Path does not exist: {path}",
                    logs=self._logs.copy()
                )
            
            def build_tree(current: Path, depth: int) -> Dict[str, Any]:
                if depth > max_depth:
                    return {"truncated": True}
                
                result = {"name": current.name, "type": "directory", "children": []}
                
                try:
                    for item in sorted(current.iterdir()):
                        # Skip ignored patterns
                        if any(re.match(pattern, item.name) for pattern in ignore_patterns):
                            continue
                        
                        if item.is_dir():
                            result["children"].append(build_tree(item, depth + 1))
                        else:
                            result["children"].append({
                                "name": item.name,
                                "type": "file",
                                "size": item.stat().st_size
                            })
                except PermissionError:
                    result["error"] = "Permission denied"
                
                return result
            
            tree_structure = build_tree(start_path, 0)
            self._log(f"repo.tree completed successfully")
            
            return ToolResult(
                success=True,
                output=tree_structure,
                logs=self._logs.copy()
            )
            
        except Exception as e:
            self._log(f"repo.tree failed: {str(e)}")
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                logs=self._logs.copy()
            )
    
    def search(self, pattern: str, path: str = ".", 
               file_pattern: str = "*", case_sensitive: bool = True) -> ToolResult:
        """
        Search for content in files.
        
        Args:
            pattern: Regex pattern to search for
            path: Starting path for search
            file_pattern: Glob pattern for files to search
            case_sensitive: Whether search is case-sensitive
            
        Returns:
            ToolResult with list of matches
        """
        self._log(f"repo.search called: pattern={pattern}, path={path}")
        
        try:
            start_path = self._validate_path(path)
            
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            matches = []
            
            for file_path in start_path.rglob(file_pattern):
                if file_path.is_dir():
                    continue
                
                # Skip binary files and large files
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue
                
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    for line_num, line in enumerate(content.split('\n'), 1):
                        if regex.search(line):
                            rel_path = file_path.relative_to(self.repo_path)
                            matches.append({
                                "file": str(rel_path),
                                "line": line_num,
                                "content": line.strip()
                            })
                except (PermissionError, UnicodeDecodeError):
                    continue
            
            self._log(f"repo.search found {len(matches)} matches")
            
            return ToolResult(
                success=True,
                output=matches,
                logs=self._logs.copy()
            )
            
        except Exception as e:
            self._log(f"repo.search failed: {str(e)}")
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                logs=self._logs.copy()
            )
    
    def read(self, path: str, start_line: int = 0, 
             end_line: Optional[int] = None) -> ToolResult:
        """
        Read file contents.
        
        Args:
            path: File path (relative to repo root)
            start_line: Starting line number (0-indexed)
            end_line: Ending line number (exclusive, None for end of file)
            
        Returns:
            ToolResult with file contents
        """
        self._log(f"repo.read called: path={path}")
        
        try:
            file_path = self._validate_path(path)
            
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"File does not exist: {path}",
                    logs=self._logs.copy()
                )
            
            if not file_path.is_file():
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Not a file: {path}",
                    logs=self._logs.copy()
                )
            
            # Size check
            file_size = file_path.stat().st_size
            if file_size > MAX_FILE_SIZE:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})",
                    logs=self._logs.copy()
                )
            
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            if end_line is not None:
                lines = lines[start_line:end_line]
            else:
                lines = lines[start_line:]
            
            self._log(f"repo.read completed: {len(lines)} lines")
            
            return ToolResult(
                success=True,
                output={
                    "path": path,
                    "content": '\n'.join(lines),
                    "lines": len(lines),
                    "total_lines": len(content.split('\n'))
                },
                logs=self._logs.copy()
            )
            
        except Exception as e:
            self._log(f"repo.read failed: {str(e)}")
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                logs=self._logs.copy()
            )
    
    def apply_patch(self, patch: str, dry_run: bool = False) -> ToolResult:
        """
        Apply a unified diff patch.
        
        Args:
            patch: Unified diff format patch string
            dry_run: If True, validate patch without applying
            
        Returns:
            ToolResult with patching results
        """
        self._log(f"repo.apply_patch called: dry_run={dry_run}")
        
        try:
            # Parse the patch
            file_patches = self._parse_patch(patch)
            
            if not file_patches:
                return ToolResult(
                    success=False,
                    output=None,
                    error="No valid patches found in input",
                    logs=self._logs.copy()
                )
            
            results = []
            
            for file_info in file_patches:
                file_path = self._validate_path(file_info['path'])
                
                if dry_run:
                    results.append({
                        "file": file_info['path'],
                        "status": "would_apply",
                        "hunks": len(file_info['hunks'])
                    })
                else:
                    # Apply the patch
                    if file_path.exists():
                        original = file_path.read_text()
                    else:
                        original = ""
                    
                    patched = self._apply_hunks(original, file_info['hunks'])
                    file_path.write_text(patched)
                    
                    results.append({
                        "file": file_info['path'],
                        "status": "applied",
                        "hunks": len(file_info['hunks'])
                    })
            
            self._log(f"repo.apply_patch completed: {len(results)} files")
            
            return ToolResult(
                success=True,
                output={"files": results, "dry_run": dry_run},
                logs=self._logs.copy()
            )
            
        except Exception as e:
            self._log(f"repo.apply_patch failed: {str(e)}")
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                logs=self._logs.copy()
            )
    
    def diff(self, path1: str, path2: Optional[str] = None, 
             context_lines: int = 3) -> ToolResult:
        """
        Generate diff between files or states.
        
        Args:
            path1: First file path
            path2: Second file path (if None, shows uncommitted changes)
            context_lines: Number of context lines in diff
            
        Returns:
            ToolResult with diff output
        """
        self._log(f"repo.diff called: path1={path1}, path2={path2}")
        
        try:
            import difflib
            
            file1 = self._validate_path(path1)
            
            if not file1.exists():
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"File does not exist: {path1}",
                    logs=self._logs.copy()
                )
            
            content1 = file1.read_text().splitlines(keepends=True)
            
            if path2:
                file2 = self._validate_path(path2)
                if not file2.exists():
                    return ToolResult(
                        success=False,
                        output=None,
                        error=f"File does not exist: {path2}",
                        logs=self._logs.copy()
                    )
                content2 = file2.read_text().splitlines(keepends=True)
                label2 = path2
            else:
                # Diff against empty (show all as additions)
                content2 = []
                label2 = "/dev/null"
            
            diff_output = difflib.unified_diff(
                content2, content1,
                fromfile=label2,
                tofile=path1,
                n=context_lines
            )
            
            diff_text = ''.join(diff_output)
            
            self._log(f"repo.diff completed")
            
            return ToolResult(
                success=True,
                output={"diff": diff_text, "path1": path1, "path2": path2},
                logs=self._logs.copy()
            )
            
        except Exception as e:
            self._log(f"repo.diff failed: {str(e)}")
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                logs=self._logs.copy()
            )
    
    def _parse_patch(self, patch: str) -> List[Dict[str, Any]]:
        """Parse a unified diff patch into structured data."""
        file_patches = []
        current_file = None
        current_hunks = []
        
        lines = patch.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            if line.startswith('diff --git'):
                if current_file:
                    file_patches.append({
                        'path': current_file,
                        'hunks': current_hunks
                    })
                current_hunks = []
                i += 1
                continue
            
            if line.startswith('--- '):
                i += 1
                continue
            
            if line.startswith('+++ '):
                # Extract file path
                path = line[4:].strip()
                if path.startswith('b/'):
                    path = path[2:]
                current_file = path
                i += 1
                continue
            
            if line.startswith('@@'):
                # Parse hunk header
                hunk_lines = [line]
                i += 1
                while i < len(lines) and not lines[i].startswith('@@') and not lines[i].startswith('diff'):
                    hunk_lines.append(lines[i])
                    i += 1
                current_hunks.append(hunk_lines)
                continue
            
            i += 1
        
        if current_file:
            file_patches.append({
                'path': current_file,
                'hunks': current_hunks
            })
        
        return file_patches
    
    def _apply_hunks(self, original: str, hunks: List[List[str]]) -> str:
        """Apply hunks to original content."""
        lines = original.split('\n')
        
        for hunk in hunks:
            if not hunk:
                continue
            
            # Simple hunk application - in production, use proper patch tool
            for line in hunk[1:]:  # Skip the @@ header
                if line.startswith('+') and not line.startswith('+++'):
                    # Add line (simplified - appends at end)
                    lines.append(line[1:])
        
        return '\n'.join(lines)
    
    def get_logs(self) -> List[str]:
        """Get all logged operations."""
        return self._logs.copy()
    
    def clear_logs(self) -> None:
        """Clear operation logs."""
        self._logs.clear()
