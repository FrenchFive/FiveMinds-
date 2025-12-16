"""
Five Minds - An agentic, repo-native AI dev system

A system with a fast HeadMaster that analyzes objectives, reads repos, and decomposes
work into small, parallel tickets. Runners implement tickets in isolated sandboxes,
and a Reviewer compares outputs to objectives and creates follow-up tasks.

Tool System:
- RepoTools: Repository operations (tree, search, read, apply_patch, diff)
- ShellTools: Shell command execution (run, which)
- GitTools: Version control operations (status, checkout, create_branch, merge, diff)
"""

__version__ = "0.1.0"

from .headmaster import HeadMaster
from .runner import Runner
from .reviewer import Reviewer
from .orchestrator import FiveMinds
from .tools import RepoTools, ShellTools, GitTools

__all__ = [
    "HeadMaster",
    "Runner", 
    "Reviewer",
    "FiveMinds",
    "RepoTools",
    "ShellTools",
    "GitTools"
]
