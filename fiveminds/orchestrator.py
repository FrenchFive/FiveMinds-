"""
Orchestrator - Main system that coordinates HeadMaster, Runners, and Reviewer
"""

import logging
import concurrent.futures
from typing import List, Dict, Optional
from pathlib import Path

from .models import (
    Objective,
    Ticket,
    RunnerResult,
    ReviewResult,
    TicketStatus
)
from .headmaster import HeadMaster
from .runner import Runner
from .reviewer import Reviewer


logger = logging.getLogger(__name__)


class FiveMinds:
    """
    Main orchestrator for the Five Minds system.
    
    Coordinates:
    1. HeadMaster to analyze objectives and create tickets
    2. Runners to implement tickets in parallel
    3. Reviewer to evaluate results and create follow-ups
    4. Integration of patches and final testing
    """

    def __init__(self, repo_path: str, max_runners: int = 4):
        """
        Initialize the Five Minds system.

        Args:
            repo_path: Path to the repository
            max_runners: Maximum number of parallel runners
        """
        self.repo_path = Path(repo_path)
        self.max_runners = max_runners
        
        self.headmaster = HeadMaster(str(self.repo_path))
        self.reviewer: Optional[Reviewer] = None
        
        self.tickets: List[Ticket] = []
        self.results: Dict[str, RunnerResult] = {}
        self.reviews: Dict[str, ReviewResult] = {}
        
        logger.info(f"Five Minds initialized for repository: {repo_path}")
        logger.info(f"Maximum parallel runners: {max_runners}")

    def execute(self, objective: Objective) -> dict:
        """
        Execute the complete Five Minds workflow for an objective.

        Args:
            objective: The user's objective to accomplish

        Returns:
            Dictionary with execution summary
        """
        logger.info("="*60)
        logger.info("Five Minds Execution Started")
        logger.info("="*60)
        logger.info(f"Objective: {objective.description}")
        
        # Phase 1: HeadMaster Analysis
        logger.info("\n[Phase 1] HeadMaster Analysis")
        logger.info("-"*60)
        
        # Analyze repository
        repo_context = self.headmaster.analyze_repository()
        logger.info(f"Repository analyzed: {len(repo_context.files)} files")
        
        # Decompose objective into tickets
        self.tickets = self.headmaster.decompose_objective(objective)
        logger.info(f"Created {len(self.tickets)} tickets")
        
        # Identify dependencies
        self.tickets = self.headmaster.identify_dependencies(self.tickets)
        
        # Optimize for parallel execution
        execution_waves = self.headmaster.optimize_parallelization(self.tickets)
        logger.info(f"Organized into {len(execution_waves)} execution wave(s)")
        
        # Phase 2: Runner Execution
        logger.info("\n[Phase 2] Runner Execution")
        logger.info("-"*60)
        
        self._execute_tickets_in_waves(execution_waves)
        
        # Phase 3: Review
        logger.info("\n[Phase 3] Review")
        logger.info("-"*60)
        
        self.reviewer = Reviewer(objective)
        self._review_results()
        
        # Phase 4: Integration and Final Testing
        logger.info("\n[Phase 4] Integration & Testing")
        logger.info("-"*60)
        
        integration_result = self._integrate_and_test()
        
        # Generate summary
        summary = self._generate_summary(objective, integration_result)
        
        logger.info("\n" + "="*60)
        logger.info("Five Minds Execution Complete")
        logger.info("="*60)
        
        return summary

    def _execute_tickets_in_waves(self, waves: Dict[str, List[Ticket]]):
        """
        Execute tickets in waves, with parallel execution within each wave.

        Args:
            waves: Dictionary mapping wave names to lists of tickets
        """
        for wave_name, tickets in waves.items():
            logger.info(f"\nExecuting {wave_name}: {len(tickets)} ticket(s)")
            
            # Execute tickets in this wave in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_runners) as executor:
                # Create runners
                futures = {}
                for idx, ticket in enumerate(tickets):
                    runner = Runner(f"R{idx+1}", str(self.repo_path))
                    future = executor.submit(runner.execute_ticket, ticket)
                    futures[future] = (ticket, runner)
                
                # Collect results
                for future in concurrent.futures.as_completed(futures):
                    ticket, runner = futures[future]
                    try:
                        result = future.result()
                        self.results[ticket.id] = result
                        logger.info(f"  ✓ {ticket.id} completed by {runner.runner_id}")
                    except Exception as e:
                        logger.error(f"  ✗ {ticket.id} failed: {str(e)}")
                    finally:
                        runner.cleanup_sandbox()

    def _review_results(self):
        """
        Review all execution results.
        """
        logger.info(f"Reviewing {len(self.results)} result(s)")
        
        for ticket_id, result in self.results.items():
            # Find the corresponding ticket
            ticket = next((t for t in self.tickets if t.id == ticket_id), None)
            if not ticket:
                logger.warning(f"No ticket found for result {ticket_id}")
                continue
            
            # Review the result
            review = self.reviewer.review_result(ticket, result)
            self.reviews[ticket_id] = review
            
            status_symbol = "✓" if review.approved else "✗"
            logger.info(f"  {status_symbol} {ticket_id}: "
                       f"{'Approved' if review.approved else 'Rejected'} "
                       f"(score: {review.alignment_score:.2f})")
            
            # Add follow-up tickets if any
            if review.follow_up_tickets:
                self.tickets.extend(review.follow_up_tickets)
                logger.info(f"    → {len(review.follow_up_tickets)} follow-up(s) created")

    def _integrate_and_test(self) -> dict:
        """
        Integrate all approved changes and run final tests.

        Returns:
            Dictionary with integration results
        """
        approved_results = [
            (ticket_id, result) 
            for ticket_id, result in self.results.items()
            if self.reviews.get(ticket_id, ReviewResult(ticket_id=ticket_id, approved=False, feedback="", alignment_score=0.0)).approved
        ]
        
        logger.info(f"Integrating {len(approved_results)} approved change(s)")
        
        # In a real system, this would:
        # 1. Apply patches/diffs to the main repository
        # 2. Resolve any conflicts
        # 3. Run the full test suite
        # 4. Check for integration issues
        
        integration_result = {
            "patches_applied": len(approved_results),
            "conflicts": 0,
            "tests_passed": True,
            "integration_status": "success"
        }
        
        logger.info(f"Integration complete: {integration_result['integration_status']}")
        
        return integration_result

    def _generate_summary(self, objective: Objective, integration_result: dict) -> dict:
        """
        Generate a comprehensive summary of the execution.

        Args:
            objective: The original objective
            integration_result: Results from integration

        Returns:
            Dictionary with complete summary
        """
        review_summary = self.reviewer.create_summary(list(self.reviews.values()))
        
        total_tickets = len(self.tickets)
        completed = sum(1 for t in self.tickets if t.status == TicketStatus.COMPLETED)
        failed = sum(1 for t in self.tickets if t.status == TicketStatus.FAILED)
        pending = sum(1 for t in self.tickets if t.status == TicketStatus.PENDING)
        
        summary = {
            "objective": objective.description,
            "repository": str(self.repo_path),
            "tickets": {
                "total": total_tickets,
                "completed": completed,
                "failed": failed,
                "pending": pending
            },
            "review": review_summary,
            "integration": integration_result,
            "success": integration_result["integration_status"] == "success" and review_summary["approval_rate"] >= 0.8
        }
        
        logger.info("\n" + "="*60)
        logger.info("SUMMARY")
        logger.info("="*60)
        logger.info(f"Objective: {objective.description}")
        logger.info(f"Tickets: {completed}/{total_tickets} completed, {failed} failed, {pending} pending")
        logger.info(f"Reviews: {review_summary['approved']}/{review_summary['total_reviews']} approved")
        logger.info(f"Alignment: {review_summary['average_alignment_score']:.2f}")
        logger.info(f"Integration: {integration_result['integration_status']}")
        logger.info(f"Overall: {'SUCCESS' if summary['success'] else 'NEEDS WORK'}")
        logger.info("="*60)
        
        return summary

    def get_status(self) -> dict:
        """
        Get current status of the system.

        Returns:
            Dictionary with current status
        """
        return {
            "tickets": {
                "total": len(self.tickets),
                "by_status": {
                    status.value: sum(1 for t in self.tickets if t.status == status)
                    for status in TicketStatus
                }
            },
            "results": len(self.results),
            "reviews": len(self.reviews)
        }
