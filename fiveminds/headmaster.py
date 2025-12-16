"""
HeadMaster - Fast analyzer that reads repos and decomposes work into parallel tickets
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .models import (
    Objective,
    Ticket,
    AcceptanceCriteria,
    TicketPriority,
    TicketStatus,
    RepositoryContext
)


logger = logging.getLogger(__name__)


class HeadMaster:
    """
    The HeadMaster is a fast analyzer that:
    1. Analyzes user objectives
    2. Reads the repository structure and content
    3. Decomposes work into small, parallel tickets with clear acceptance criteria
    """

    def __init__(self, repo_path: str):
        """
        Initialize the HeadMaster with a repository path.

        Args:
            repo_path: Path to the repository to analyze
        """
        self.repo_path = Path(repo_path)
        self.repo_context: Optional[RepositoryContext] = None
        logger.info(f"HeadMaster initialized for repository: {repo_path}")

    def analyze_repository(self) -> RepositoryContext:
        """
        Analyze the repository structure, files, and characteristics.

        Returns:
            RepositoryContext with information about the repository
        """
        logger.info("Analyzing repository structure...")
        
        files = []
        structure = {}
        languages = set()
        frameworks = set()

        # Walk through the repository
        for root, dirs, filenames in os.walk(self.repo_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
            
            rel_root = os.path.relpath(root, self.repo_path)
            if rel_root == '.':
                rel_root = ''
            
            for filename in filenames:
                if filename.startswith('.'):
                    continue
                    
                file_path = os.path.join(rel_root, filename) if rel_root else filename
                files.append(file_path)
                
                # Detect languages and frameworks
                ext = os.path.splitext(filename)[1]
                if ext in ['.py']:
                    languages.add('Python')
                elif ext in ['.js', '.jsx']:
                    languages.add('JavaScript')
                elif ext in ['.ts', '.tsx']:
                    languages.add('TypeScript')
                elif ext in ['.java']:
                    languages.add('Java')
                elif ext in ['.go']:
                    languages.add('Go')
                elif ext in ['.rs']:
                    languages.add('Rust')
                
                # Detect frameworks
                if filename in ['package.json']:
                    frameworks.add('Node.js')
                elif filename in ['requirements.txt', 'setup.py', 'pyproject.toml']:
                    frameworks.add('Python')
                elif filename in ['Cargo.toml']:
                    frameworks.add('Rust/Cargo')
                elif filename in ['go.mod']:
                    frameworks.add('Go/Modules')

        self.repo_context = RepositoryContext(
            path=str(self.repo_path),
            files=sorted(files),
            structure=structure,
            languages=sorted(list(languages)),
            frameworks=sorted(list(frameworks)),
            metadata={
                'total_files': len(files)
            }
        )
        
        logger.info(f"Repository analysis complete: {len(files)} files, "
                   f"{len(languages)} languages, {len(frameworks)} frameworks")
        
        return self.repo_context

    def decompose_objective(self, objective: Objective) -> List[Ticket]:
        """
        Decompose a user objective into small, parallel tickets with clear acceptance criteria.

        Args:
            objective: The user's objective to accomplish

        Returns:
            List of Tickets to be executed
        """
        logger.info(f"Decomposing objective: {objective.description}")
        
        if not self.repo_context:
            self.analyze_repository()

        tickets = []
        
        # Generate tickets based on the objective and repository context
        # This is a simplified version - in a real system, this would use AI/LLM
        
        for idx, requirement in enumerate(objective.requirements, 1):
            ticket_id = f"TKT-{idx:03d}"
            
            # Create acceptance criteria
            criteria = [
                AcceptanceCriteria(
                    description=f"Implement: {requirement}",
                    met=False
                ),
                AcceptanceCriteria(
                    description="Code passes all tests",
                    met=False
                ),
                AcceptanceCriteria(
                    description="Changes are documented",
                    met=False
                )
            ]
            
            ticket = Ticket(
                id=ticket_id,
                title=requirement,
                description=f"Implement requirement: {requirement}",
                acceptance_criteria=criteria,
                status=TicketStatus.PENDING,
                priority=TicketPriority.MEDIUM,
                dependencies=[],
                metadata={
                    'objective': objective.description,
                    'requirement_index': idx
                }
            )
            
            tickets.append(ticket)
        
        logger.info(f"Created {len(tickets)} tickets from objective")
        return tickets

    def identify_dependencies(self, tickets: List[Ticket]) -> List[Ticket]:
        """
        Analyze tickets and identify dependencies between them.

        Args:
            tickets: List of tickets to analyze

        Returns:
            Updated list of tickets with dependencies identified
        """
        logger.info("Identifying ticket dependencies...")
        
        # Simplified dependency detection
        # In a real system, this would use more sophisticated analysis
        
        for i, ticket in enumerate(tickets):
            # If ticket mentions 'build' or 'setup', it might be a dependency for others
            if any(keyword in ticket.description.lower() for keyword in ['setup', 'initialize', 'configure']):
                ticket.priority = TicketPriority.HIGH
                # Other tickets might depend on this
                for other_ticket in tickets[i+1:]:
                    if ticket.id not in other_ticket.dependencies:
                        other_ticket.dependencies.append(ticket.id)
        
        logger.info("Dependency analysis complete")
        return tickets

    def optimize_parallelization(self, tickets: List[Ticket]) -> Dict[str, List[Ticket]]:
        """
        Organize tickets into parallel execution groups based on dependencies.

        Args:
            tickets: List of tickets with dependencies

        Returns:
            Dictionary mapping execution waves to lists of tickets
        """
        logger.info("Optimizing ticket parallelization...")
        
        waves = {}
        processed = set()
        wave_num = 0
        
        while len(processed) < len(tickets):
            current_wave = []
            
            for ticket in tickets:
                if ticket.id in processed:
                    continue
                
                # Check if all dependencies are satisfied
                deps_satisfied = all(dep_id in processed for dep_id in ticket.dependencies)
                
                if deps_satisfied:
                    current_wave.append(ticket)
            
            if not current_wave:
                # No tickets can be processed - circular dependency or error
                logger.warning("Unable to process remaining tickets - possible circular dependency")
                break
            
            waves[f"wave_{wave_num}"] = current_wave
            processed.update(ticket.id for ticket in current_wave)
            wave_num += 1
        
        logger.info(f"Created {len(waves)} execution waves for parallel processing")
        return waves
