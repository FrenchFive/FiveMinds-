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


def main():
    """
    Main CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description='Five Minds - Agentic, repo-native AI dev system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with a simple objective
  python -m fiveminds.cli --repo /path/to/repo "Add user authentication"
  
  # Run with multiple requirements
  python -m fiveminds.cli --repo /path/to/repo \\
    --requirement "Add login page" \\
    --requirement "Add user model" \\
    "Implement user authentication system"
    
  # Run with UI enabled
  python -m fiveminds.cli --repo /path/to/repo --ui "Your objective"
        """
    )
    
    parser.add_argument(
        'objective',
        type=str,
        help='The objective description'
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
        help='Enable web UI dashboard'
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
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Validate repository path
    repo_path = Path(args.repo).resolve()
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}", file=sys.stderr)
        return 1
    
    # Create objective
    objective = Objective(
        description=args.objective,
        requirements=args.requirements or [args.objective],
        constraints=args.constraints or [],
        success_metrics=["All acceptance criteria met", "All tests pass"]
    )
    
    # Initialize Five Minds
    print(f"\n🧠 Five Minds - Agentic AI Dev System")
    print(f"Repository: {repo_path}")
    print(f"Objective: {objective.description}")
    print(f"Requirements: {len(objective.requirements)}")
    
    if args.ui:
        print(f"UI Dashboard: http://{args.ui_host}:{args.ui_port}")
    
    print()
    
    five_minds = FiveMinds(
        str(repo_path), 
        max_runners=args.max_runners,
        enable_ui=args.ui,
        ui_host=args.ui_host,
        ui_port=args.ui_port
    )
    
    # Execute
    try:
        summary = five_minds.execute(objective)
        
        # Print summary
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
