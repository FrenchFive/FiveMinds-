#!/usr/bin/env python3
"""
Example usage of the Five Minds system
"""

import logging
from fiveminds import FiveMinds
from fiveminds.models import Objective

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def main():
    """
    Demonstrate the Five Minds system with an example objective.
    """
    print("\n" + "="*60)
    print("Five Minds - Example Demonstration")
    print("="*60 + "\n")
    
    # Define an objective
    objective = Objective(
        description="Create a simple Python calculator library",
        requirements=[
            "Implement basic arithmetic operations (add, subtract, multiply, divide)",
            "Add input validation and error handling",
            "Create unit tests for all operations",
            "Write documentation and usage examples"
        ],
        constraints=[
            "Use Python 3.8+ features",
            "Follow PEP 8 style guidelines",
            "Maintain 100% test coverage"
        ],
        success_metrics=[
            "All operations work correctly",
            "All tests pass",
            "Documentation is complete"
        ]
    )
    
    # Initialize Five Minds with current repository
    five_minds = FiveMinds(repo_path=".", max_runners=2)
    
    # Execute the objective
    print("Starting Five Minds execution...\n")
    summary = five_minds.execute(objective)
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    print(f"\n📊 Objective: {summary['objective']}")
    print(f"📁 Repository: {summary['repository']}")
    
    print(f"\n🎫 Tickets:")
    print(f"   Total: {summary['tickets']['total']}")
    print(f"   ✓ Completed: {summary['tickets']['completed']}")
    print(f"   ✗ Failed: {summary['tickets']['failed']}")
    print(f"   ⏳ Pending: {summary['tickets']['pending']}")
    
    print(f"\n🔍 Review:")
    print(f"   Approved: {summary['review']['approved']}/{summary['review']['total_reviews']}")
    print(f"   Approval Rate: {summary['review']['approval_rate']:.1%}")
    print(f"   Avg Alignment: {summary['review']['average_alignment_score']:.2f}")
    print(f"   Follow-ups: {summary['review']['total_follow_up_tickets']}")
    
    print(f"\n🔧 Integration:")
    print(f"   Patches Applied: {summary['integration']['patches_applied']}")
    print(f"   Conflicts: {summary['integration']['conflicts']}")
    print(f"   Tests Passed: {'✓' if summary['integration']['tests_passed'] else '✗'}")
    print(f"   Status: {summary['integration']['integration_status']}")
    
    print(f"\n🎯 Overall Success: {'✓ YES' if summary['success'] else '✗ NO'}")
    
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
