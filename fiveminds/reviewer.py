"""
Reviewer - Compares outputs to objectives and creates follow-up tasks
"""

import logging
from typing import List, Optional

from .models import (
    Ticket,
    RunnerResult,
    ReviewResult,
    Objective,
    AcceptanceCriteria,
    TicketStatus,
    TicketPriority
)


logger = logging.getLogger(__name__)


class Reviewer:
    """
    The Reviewer:
    1. Compares Runner outputs to the original objective and plan
    2. Evaluates if acceptance criteria are met
    3. Creates follow-up tasks when needed
    4. Provides feedback on implementation quality
    """

    def __init__(self, objective: Optional[Objective] = None):
        """
        Initialize the Reviewer with an optional objective.

        Args:
            objective: The original objective to compare against
        """
        self.objective = objective
        logger.info("Reviewer initialized")

    def review_result(self, ticket: Ticket, result: RunnerResult) -> ReviewResult:
        """
        Review a Runner's result for a ticket.

        Args:
            ticket: The original ticket
            result: The result from the Runner

        Returns:
            ReviewResult with approval, feedback, and follow-up tasks
        """
        logger.info(f"Reviewing result for ticket {ticket.id}")
        
        feedback_items = []
        follow_up_tickets = []
        approved = True
        
        # Check if execution was successful
        if not result.success:
            approved = False
            feedback_items.append(f"Execution failed: {result.error_message}")
            logger.warning(f"Ticket {ticket.id} execution failed")
        
        # Check acceptance criteria
        criteria_met = sum(1 for c in ticket.acceptance_criteria if c.met)
        criteria_total = len(ticket.acceptance_criteria)
        
        feedback_items.append(f"Acceptance criteria: {criteria_met}/{criteria_total} met")
        
        if criteria_met < criteria_total:
            approved = False
            unmet_criteria = [c.description for c in ticket.acceptance_criteria if not c.met]
            feedback_items.append(f"Unmet criteria: {', '.join(unmet_criteria)}")
        
        # Check test results
        if result.test_results:
            total_tests = result.test_results.get('total', 0)
            passed_tests = result.test_results.get('passed', 0)
            failed_tests = result.test_results.get('failed', 0)
            
            feedback_items.append(f"Tests: {passed_tests}/{total_tests} passed")
            
            if failed_tests > 0:
                approved = False
                feedback_items.append(f"⚠ {failed_tests} test(s) failed")
        
        # Calculate alignment score
        alignment_score = self._calculate_alignment_score(ticket, result)
        feedback_items.append(f"Alignment score: {alignment_score:.2f}")
        
        if alignment_score < 0.7:
            approved = False
            feedback_items.append("Low alignment with original objective")
        
        # Check for potential follow-up work
        follow_ups = self._identify_follow_ups(ticket, result)
        if follow_ups:
            follow_up_tickets.extend(follow_ups)
            feedback_items.append(f"Identified {len(follow_ups)} follow-up task(s)")
        
        # Analyze diff for quality
        diff_feedback = self._analyze_diff(result.diff)
        feedback_items.extend(diff_feedback)
        
        # Final verdict
        if approved:
            ticket.status = TicketStatus.COMPLETED
            feedback_items.insert(0, "✓ Review passed - ticket approved")
            logger.info(f"Ticket {ticket.id} approved")
        else:
            ticket.status = TicketStatus.FAILED
            feedback_items.insert(0, "✗ Review failed - needs revision")
            logger.warning(f"Ticket {ticket.id} failed review")
        
        review = ReviewResult(
            ticket_id=ticket.id,
            approved=approved,
            feedback="\n".join(feedback_items),
            alignment_score=alignment_score,
            follow_up_tickets=follow_up_tickets,
            suggestions=self._generate_suggestions(ticket, result, approved)
        )
        
        return review

    def _calculate_alignment_score(self, ticket: Ticket, result: RunnerResult) -> float:
        """
        Calculate how well the result aligns with the original objective and ticket.

        Args:
            ticket: The original ticket
            result: The result from the Runner

        Returns:
            Alignment score between 0.0 and 1.0
        """
        score = 0.0
        
        # Base score on success
        if result.success:
            score += 0.3
        
        # Score based on acceptance criteria
        criteria_met = sum(1 for c in ticket.acceptance_criteria if c.met)
        criteria_total = len(ticket.acceptance_criteria)
        if criteria_total > 0:
            score += 0.4 * (criteria_met / criteria_total)
        
        # Score based on test results
        if result.test_results:
            total_tests = result.test_results.get('total', 0)
            passed_tests = result.test_results.get('passed', 0)
            if total_tests > 0:
                score += 0.3 * (passed_tests / total_tests)
        else:
            # No tests - partial score
            score += 0.15
        
        return min(1.0, score)

    def _analyze_diff(self, diff: str) -> List[str]:
        """
        Analyze the diff for code quality indicators.

        Args:
            diff: The diff string to analyze

        Returns:
            List of feedback messages
        """
        feedback = []
        
        if not diff or diff.strip() == "":
            feedback.append("⚠ No code changes detected")
            return feedback
        
        lines = diff.split('\n')
        added_lines = [l for l in lines if l.startswith('+') and not l.startswith('+++')]
        removed_lines = [l for l in lines if l.startswith('-') and not l.startswith('---')]
        
        feedback.append(f"Changes: +{len(added_lines)} -{len(removed_lines)} lines")
        
        # Check for common issues
        if any('print(' in line or 'console.log(' in line for line in added_lines):
            feedback.append("⚠ Debug statements detected - consider removing")
        
        if any('TODO' in line or 'FIXME' in line for line in added_lines):
            feedback.append("⚠ TODO/FIXME comments found - consider tracking as follow-up")
        
        return feedback

    def _identify_follow_ups(self, ticket: Ticket, result: RunnerResult) -> List[Ticket]:
        """
        Identify potential follow-up tasks based on the result.

        Args:
            ticket: The original ticket
            result: The result from the Runner

        Returns:
            List of follow-up tickets
        """
        follow_ups = []
        
        # If there were test failures, create follow-up for fixes
        if result.test_results and result.test_results.get('failed', 0) > 0:
            follow_ups.append(Ticket(
                id=f"{ticket.id}-FU-1",
                title=f"Fix test failures for {ticket.title}",
                description=f"Address {result.test_results['failed']} failing test(s)",
                acceptance_criteria=[
                    AcceptanceCriteria(description="All tests pass", met=False)
                ],
                status=TicketStatus.PENDING,
                priority=TicketPriority.HIGH,
                dependencies=[ticket.id]
            ))
        
        # Check logs for indicators of follow-up work
        for log in result.logs:
            if 'TODO' in log or 'follow-up' in log.lower():
                follow_ups.append(Ticket(
                    id=f"{ticket.id}-FU-{len(follow_ups)+1}",
                    title=f"Follow-up for {ticket.title}",
                    description=f"Address item from logs: {log[:100]}",
                    acceptance_criteria=[
                        AcceptanceCriteria(description="Complete follow-up work", met=False)
                    ],
                    status=TicketStatus.PENDING,
                    priority=TicketPriority.MEDIUM,
                    dependencies=[ticket.id]
                ))
        
        return follow_ups

    def _generate_suggestions(self, ticket: Ticket, result: RunnerResult, 
                             approved: bool) -> List[str]:
        """
        Generate suggestions for improvement.

        Args:
            ticket: The original ticket
            result: The result from the Runner
            approved: Whether the review was approved

        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        if not approved:
            suggestions.append("Review the acceptance criteria and ensure all are met")
            suggestions.append("Check test results and fix any failing tests")
        
        if result.execution_time > 300:  # 5 minutes
            suggestions.append("Consider breaking down into smaller tasks for faster execution")
        
        if self.objective:
            suggestions.append(f"Ensure changes align with objective: {self.objective.description}")
        
        return suggestions

    def create_summary(self, reviews: List[ReviewResult]) -> dict:
        """
        Create a summary of multiple reviews.

        Args:
            reviews: List of review results

        Returns:
            Dictionary with summary statistics
        """
        total = len(reviews)
        approved = sum(1 for r in reviews if r.approved)
        
        avg_alignment = sum(r.alignment_score for r in reviews) / total if total > 0 else 0.0
        
        total_follow_ups = sum(len(r.follow_up_tickets) for r in reviews)
        
        summary = {
            "total_reviews": total,
            "approved": approved,
            "rejected": total - approved,
            "approval_rate": approved / total if total > 0 else 0.0,
            "average_alignment_score": avg_alignment,
            "total_follow_up_tickets": total_follow_ups
        }
        
        logger.info(f"Review summary: {approved}/{total} approved, "
                   f"{avg_alignment:.2f} avg alignment, "
                   f"{total_follow_ups} follow-ups")
        
        return summary
