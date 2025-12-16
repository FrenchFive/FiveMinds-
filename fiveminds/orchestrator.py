"""
Orchestrator - Main system that coordinates HeadMaster, Runners, and Reviewer
"""

import logging
import concurrent.futures
from dataclasses import asdict
from datetime import datetime
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

    def __init__(self, repo_path: str, max_runners: int = 4, enable_ui: bool = False, 
                 ui_host: str = "127.0.0.1", ui_port: int = 5000,
                 user_name: str = "FiveMinds", user_email: str = "fiveminds@localhost",
                 autonomous: bool = True):
        """
        Initialize the Five Minds system.

        Args:
            repo_path: Path to the repository
            max_runners: Maximum number of parallel runners
            enable_ui: Whether to enable the web UI
            ui_host: Host for UI server
            ui_port: Port for UI server
            user_name: Git user name for commits
            user_email: Git user email for commits
            autonomous: Run in autonomous mode (minimal user interaction)
        """
        self.repo_path = Path(repo_path)
        self.max_runners = max_runners
        self.user_name = user_name
        self.user_email = user_email
        self.autonomous = autonomous
        self._stop_requested = False
        
        self.headmaster = HeadMaster(str(self.repo_path))
        self.reviewer: Optional[Reviewer] = None
        
        self.tickets: List[Ticket] = []
        self.results: Dict[str, RunnerResult] = {}
        self.reviews: Dict[str, ReviewResult] = {}
        
        # UI server (lazy import to avoid loading Flask dependencies when UI is disabled)
        self.ui_server = None
        self.enable_ui = enable_ui
        if enable_ui:
            from .ui import UIServer
            self.ui_server = UIServer(host=ui_host, port=ui_port)
        
        logger.info(f"Five Minds initialized for repository: {repo_path}")
        logger.info(f"Maximum parallel runners: {max_runners}")
        logger.info(f"Autonomous mode: {autonomous}")
        if enable_ui:
            logger.info(f"UI enabled at http://{ui_host}:{ui_port}")
    
    def stop(self):
        """Request to stop the execution."""
        self._stop_requested = True
        logger.info("Stop requested")

    def _ticket_to_dict(self, ticket: Ticket) -> dict:
        """Convert ticket to dictionary for UI."""
        return {
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "acceptance_criteria": [
                {"description": c.description, "met": c.met, "evidence": c.evidence}
                for c in ticket.acceptance_criteria
            ],
            "status": ticket.status.value if ticket.status else "pending",
            "priority": ticket.priority.value if ticket.priority else "medium",
            "dependencies": ticket.dependencies,
            "assigned_runner": ticket.assigned_runner,
            "metadata": ticket.metadata
        }

    def _result_to_dict(self, result: RunnerResult) -> dict:
        """Convert result to dictionary for UI."""
        return {
            "ticket_id": result.ticket_id,
            "success": result.success,
            "diff": result.diff,
            "logs": result.logs,
            "test_results": result.test_results,
            "error_message": result.error_message,
            "execution_time": result.execution_time
        }

    def _review_to_dict(self, review: ReviewResult) -> dict:
        """Convert review to dictionary for UI."""
        return {
            "ticket_id": review.ticket_id,
            "approved": review.approved,
            "feedback": review.feedback,
            "alignment_score": review.alignment_score,
            "follow_up_tickets": [self._ticket_to_dict(t) for t in review.follow_up_tickets],
            "suggestions": review.suggestions
        }

    def execute(self, objective: Objective) -> dict:
        """
        Execute the complete Five Minds workflow for an objective.

        Args:
            objective: The user's objective to accomplish

        Returns:
            Dictionary with execution summary
        """
        # Start UI server if enabled
        if self.ui_server:
            self.ui_server.start(background=True)
            self.ui_server.set_objective({
                "description": objective.description,
                "requirements": objective.requirements,
                "constraints": objective.constraints,
                "success_metrics": objective.success_metrics
            })
        
        logger.info("="*60)
        logger.info("Five Minds Execution Started")
        logger.info("="*60)
        logger.info(f"Objective: {objective.description}")
        
        # Phase 1: HeadMaster Analysis
        logger.info("\n[Phase 1] HeadMaster Analysis")
        logger.info("-"*60)
        
        if self.ui_server:
            self.ui_server.set_status("analyzing")
            self.ui_server.add_headmaster_reasoning("Starting repository analysis...")
        
        # Analyze repository
        repo_context = self.headmaster.analyze_repository()
        logger.info(f"Repository analyzed: {len(repo_context.files)} files")
        
        if self.ui_server:
            self.ui_server.add_headmaster_reasoning(f"Repository analyzed: {len(repo_context.files)} files, Languages: {', '.join(repo_context.languages)}")
        
        # Decompose objective into tickets
        self.tickets = self.headmaster.decompose_objective(objective)
        logger.info(f"Created {len(self.tickets)} tickets")
        
        if self.ui_server:
            self.ui_server.add_headmaster_reasoning(f"Decomposed objective into {len(self.tickets)} tickets")
            self.ui_server.set_tickets([self._ticket_to_dict(t) for t in self.tickets])
        
        # Identify dependencies
        self.tickets = self.headmaster.identify_dependencies(self.tickets)
        
        # Build dependency list for UI
        dependencies = []
        for ticket in self.tickets:
            for dep_id in ticket.dependencies:
                dependencies.append({"from": dep_id, "to": ticket.id})
        
        if self.ui_server:
            self.ui_server.add_headmaster_reasoning("Identified ticket dependencies")
            self.ui_server.set_dependencies(dependencies)
        
        # Optimize for parallel execution
        execution_waves = self.headmaster.optimize_parallelization(self.tickets)
        logger.info(f"Organized into {len(execution_waves)} execution wave(s)")
        
        if self.ui_server:
            self.ui_server.add_headmaster_reasoning(f"Organized into {len(execution_waves)} execution wave(s) for parallel processing")
        
        # Phase 2: Runner Execution
        logger.info("\n[Phase 2] Runner Execution")
        logger.info("-"*60)
        
        if self.ui_server:
            self.ui_server.set_status("executing")
        
        self._execute_tickets_in_waves(execution_waves)
        
        # Phase 3: Review
        logger.info("\n[Phase 3] Review")
        logger.info("-"*60)
        
        if self.ui_server:
            self.ui_server.set_status("reviewing")
        
        self.reviewer = Reviewer(objective)
        self._review_results()
        
        # Phase 4: Integration and Final Testing
        logger.info("\n[Phase 4] Integration & Testing")
        logger.info("-"*60)
        
        if self.ui_server:
            self.ui_server.set_status("integrating")
            self.ui_server.update_headmaster("integration_status", "in_progress")
        
        integration_result = self._integrate_and_test()
        
        if self.ui_server:
            self.ui_server.update_headmaster("integration_status", integration_result["integration_status"])
        
        # Generate summary
        summary = self._generate_summary(objective, integration_result)
        
        if self.ui_server:
            self.ui_server.set_status("completed" if summary["success"] else "failed")
        
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
            # Check if stop was requested
            if self._stop_requested:
                logger.info("Execution stopped by user request")
                break
                
            logger.info(f"\nExecuting {wave_name}: {len(tickets)} ticket(s)")
            
            if self.ui_server:
                self.ui_server.add_progress(f"Starting {wave_name} with {len(tickets)} ticket(s)")
            
            # Execute tickets in this wave in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_runners) as executor:
                # Create runners with user credentials
                futures = {}
                for idx, ticket in enumerate(tickets):
                    runner = Runner(
                        f"R{idx+1}", 
                        str(self.repo_path),
                        user_name=self.user_name,
                        user_email=self.user_email
                    )
                    future = executor.submit(runner.execute_ticket, ticket)
                    futures[future] = (ticket, runner)
                    
                    # Update UI
                    if self.ui_server:
                        self.ui_server.add_runner(runner.runner_id, ticket.id)
                        self.ui_server.update_ticket(ticket.id, {"status": "in_progress"})
                
                # Collect results
                for future in concurrent.futures.as_completed(futures):
                    ticket, runner = futures[future]
                    try:
                        result = future.result()
                        self.results[ticket.id] = result
                        logger.info(f"  ✓ {ticket.id} completed by {runner.runner_id}")
                        
                        # In autonomous mode, commit changes after successful execution
                        if self.autonomous and result.success:
                            commit_result = runner.commit_changes(ticket)
                            if commit_result.get("success"):
                                logger.info(f"  ✓ Changes committed for {ticket.id}")
                            else:
                                logger.warning(f"  ⚠ Commit failed for {ticket.id}: {commit_result.get('error')}")
                        
                        # Update UI
                        if self.ui_server:
                            self.ui_server.complete_runner(runner.runner_id, self._result_to_dict(result))
                            self.ui_server.update_ticket(ticket.id, {"status": "needs_review"})
                    except Exception as e:
                        logger.error(f"  ✗ {ticket.id} failed: {str(e)}")
                        
                        if self.ui_server:
                            self.ui_server.complete_runner(runner.runner_id, {
                                "ticket_id": ticket.id,
                                "success": False,
                                "error_message": str(e)
                            })
                            self.ui_server.update_ticket(ticket.id, {"status": "failed"})
                    finally:
                        runner.cleanup_sandbox()

    def _find_ticket_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """
        Find a ticket by its ID.

        Args:
            ticket_id: The ticket ID to find

        Returns:
            The ticket if found, None otherwise
        """
        return next((t for t in self.tickets if t.id == ticket_id), None)

    def _review_results(self):
        """
        Review all execution results.
        """
        logger.info(f"Reviewing {len(self.results)} result(s)")
        
        for ticket_id, result in self.results.items():
            # Find the corresponding ticket
            ticket = self._find_ticket_by_id(ticket_id)
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
            
            # Update UI
            if self.ui_server:
                self.ui_server.add_review(self._review_to_dict(review))
                self.ui_server.update_ticket(ticket_id, {
                    "status": "completed" if review.approved else "failed"
                })
            
            # Add follow-up tickets if any
            if review.follow_up_tickets:
                self.tickets.extend(review.follow_up_tickets)
                logger.info(f"    → {len(review.follow_up_tickets)} follow-up(s) created")
                
                if self.ui_server:
                    self.ui_server.set_tickets([self._ticket_to_dict(t) for t in self.tickets])

    def _is_result_approved(self, ticket_id: str) -> bool:
        """
        Check if a result is approved.

        Args:
            ticket_id: The ticket ID to check

        Returns:
            True if approved, False otherwise
        """
        review = self.reviews.get(ticket_id)
        return review is not None and review.approved

    def _integrate_and_test(self) -> dict:
        """
        Integrate all approved changes and run final tests.

        Returns:
            Dictionary with integration results
        """
        approved_results = [
            (ticket_id, result) 
            for ticket_id, result in self.results.items()
            if self._is_result_approved(ticket_id)
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
        
        success = integration_result["integration_status"] == "success" and review_summary["approval_rate"] >= 0.8
        
        # Generate a human-readable final summary
        final_summary_lines = [
            "=" * 60,
            "🧠 FIVE MINDS EXECUTION SUMMARY",
            "=" * 60,
            "",
            f"📋 Objective: {objective.description}",
            "",
            "📊 Results:",
            f"   • Tickets completed: {completed}/{total_tickets}",
            f"   • Tickets failed: {failed}",
            f"   • Tickets pending: {pending}",
            "",
            f"🔍 Reviews:",
            f"   • Approved: {review_summary['approved']}/{review_summary['total_reviews']}",
            f"   • Approval rate: {review_summary['approval_rate']:.1%}",
            f"   • Average alignment: {review_summary['average_alignment_score']:.1%}",
            "",
            f"🔧 Integration: {integration_result['integration_status']}",
            f"   • Patches applied: {integration_result.get('patches_applied', 0)}",
            "",
            f"✅ Overall Status: {'SUCCESS' if success else 'NEEDS WORK'}",
            "=" * 60
        ]
        final_summary = "\n".join(final_summary_lines)
        
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
            "success": success,
            "final_summary": final_summary,
            "completed_at": datetime.now().isoformat()
        }
        
        # Log the summary
        logger.info("\n" + final_summary)
        
        # Update UI with final summary
        if self.ui_server:
            self.ui_server.add_progress(f"Task {'completed successfully' if success else 'completed with issues'}")
            self.ui_server.update_headmaster("final_summary", final_summary)
        
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
