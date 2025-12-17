"""
Command-line interface for Five Minds
"""

import sys
import logging
import argparse
from pathlib import Path

from .models import Objective
from .orchestrator import FiveMinds


def setup_logging(verbose: bool = False):
    """
    Setup logging configuration.

    Args:
        verbose: Whether to enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def interactive_mode():
    """
    Run in interactive mode to get objective from user.
    
    Returns:
        Objective from user input
    """
    print("\n🧠 Five Minds - Interactive Mode")
    print("=" * 50)
    
    # Get objective
    print("\nEnter your objective (what do you want to accomplish?):")
    description = input("> ").strip()
    
    if not description:
        print("Error: Objective cannot be empty")
        return None
    
    # Get requirements (optional)
    print("\nEnter requirements (one per line, empty line to finish):")
    requirements = []
    while True:
        req = input("  - ").strip()
        if not req:
            break
        requirements.append(req)
    
    if not requirements:
        requirements = [description]
    
    # Get constraints (optional)
    print("\nEnter constraints (one per line, empty line to finish):")
    constraints = []
    while True:
        constraint = input("  - ").strip()
        if not constraint:
            break
        constraints.append(constraint)
    
    return Objective(
        description=description,
        requirements=requirements,
        constraints=constraints,
        success_metrics=["All acceptance criteria met", "All tests pass"]
    )


def main():
    """
    Main CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description='Five Minds - Agentic, repo-native AI dev system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run in interactive mode (recommended for easy launch)
  python -m fiveminds.cli --interactive
  
  # Run with a simple objective
  python -m fiveminds.cli --repo /path/to/repo "Add user authentication"
  
  # Run with multiple requirements
  python -m fiveminds.cli --repo /path/to/repo \\
    --requirement "Add login page" \\
    --requirement "Add user model" \\
    "Implement user authentication system"
    
  # Run with UI enabled (default in interactive mode)
  python -m fiveminds.cli --repo /path/to/repo --ui "Your objective"
  
  # Run in autonomous mode (FiveMinds does everything)
  python -m fiveminds.cli --auto "Your objective"
        """
    )
    
    parser.add_argument(
        'objective',
        type=str,
        nargs='?',
        default=None,
        help='The objective description (optional if using --interactive)'
    )
    
    parser.add_argument(
        '--repo',
        type=str,
        default='.',
        help='Path to the repository (default: current directory)'
    )
    
    parser.add_argument(
        '--requirement',
        action='append',
        dest='requirements',
        help='Add a specific requirement (can be used multiple times)'
    )
    
    parser.add_argument(
        '--constraint',
        action='append',
        dest='constraints',
        help='Add a constraint (can be used multiple times)'
    )
    
    parser.add_argument(
        '--max-runners',
        type=int,
        default=4,
        help='Maximum number of parallel runners (default: 4)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--ui',
        action='store_true',
        default=True,
        help='Enable web UI dashboard (default: enabled, use --no-ui to disable)'
    )
    
    parser.add_argument(
        '--no-ui',
        action='store_false',
        dest='ui',
        help='Disable web UI dashboard'
    )
    
    parser.add_argument(
        '--ui-host',
        type=str,
        default='127.0.0.1',
        help='UI server host (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--ui-port',
        type=int,
        default=5000,
        help='UI server port (default: 5000)'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode (prompts for objective)'
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        dest='autonomous',
        default=True,
        help='Run in autonomous mode (FiveMinds handles everything)'
    )
    
    parser.add_argument(
        '--no-auto',
        action='store_false',
        dest='autonomous',
        help='Disable autonomous mode'
    )
    
    parser.add_argument(
        '--auto-discover',
        action='store_true',
        help='Run in auto-discovery mode where HeadMaster autonomously finds tasks'
    )
    
    parser.add_argument(
        '--user-name',
        type=str,
        default='FiveMinds',
        help='Git user name for commits (default: FiveMinds)'
    )
    
    parser.add_argument(
        '--user-email',
        type=str,
        default='fiveminds@localhost',
        help='Git user email for commits (default: fiveminds@localhost)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Validate repository path
    repo_path = Path(args.repo).resolve()
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}", file=sys.stderr)
        return 1
    
    # Get objective
    if args.auto_discover:
        # Auto-discovery mode: HeadMaster will analyze the repository and create tasks
        objective = Objective(
            description="Analyze repository and autonomously create improvement tasks",
            requirements=[
                "Analyze code quality and identify improvements",
                "Search for TODO/FIXME comments and create tasks",
                "Identify potential optimizations",
                "Check for missing tests or documentation",
                "Suggest new features based on existing patterns"
            ],
            constraints=[
                "Maintain existing functionality",
                "Follow project coding standards",
                "Ensure backward compatibility"
            ],
            success_metrics=[
                "Repository analysis complete",
                "Improvement tasks identified and prioritized",
                "Tasks can be executed by runners"
            ]
        )
        print(f"\n🔍 Auto-Discovery Mode: HeadMaster will analyze repository and create tasks")
    elif args.interactive:
        objective = interactive_mode()
        if objective is None:
            return 1
    elif args.objective:
        objective = Objective(
            description=args.objective,
            requirements=args.requirements or [args.objective],
            constraints=args.constraints or [],
            success_metrics=["All acceptance criteria met", "All tests pass"]
        )
    else:
        print("Error: Please provide an objective, use --interactive mode, or --auto-discover", file=sys.stderr)
        parser.print_help()
        return 1
    
    # Initialize Five Minds
    print(f"\n🧠 Five Minds - Agentic AI Dev System")
    print(f"=" * 50)
    print(f"Repository: {repo_path}")
    print(f"Objective: {objective.description}")
    print(f"Requirements: {len(objective.requirements)}")
    print(f"Autonomous mode: {'Enabled' if args.autonomous else 'Disabled'}")
    
    if args.ui:
        print(f"UI Dashboard: http://{args.ui_host}:{args.ui_port}")
    
    print()
    
    five_minds = FiveMinds(
        str(repo_path), 
        max_runners=args.max_runners,
        enable_ui=args.ui,
        ui_host=args.ui_host,
        ui_port=args.ui_port,
        user_name=args.user_name,
        user_email=args.user_email,
        autonomous=args.autonomous
    )
    
    # Execute
    try:
        summary = five_minds.execute(objective)
        
        # Print final summary
        if 'final_summary' in summary:
            print(summary['final_summary'])
        else:
            print("\n" + "="*60)
            print("EXECUTION SUMMARY")
            print("="*60)
            print(f"Success: {'✓' if summary['success'] else '✗'}")
            print(f"Tickets: {summary['tickets']['completed']}/{summary['tickets']['total']} completed")
            print(f"Reviews: {summary['review']['approved']}/{summary['review']['total_reviews']} approved")
            print(f"Alignment: {summary['review']['average_alignment_score']:.2%}")
            print("="*60)
        
        if args.ui:
            print(f"\n📊 UI Dashboard available at: http://{args.ui_host}:{args.ui_port}")
            print("Press Ctrl+C to stop the server...")
            try:
                # Keep the server running
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down...")
        
        return 0 if summary['success'] else 1
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
