# Five Minds 🧠

An agentic, repo-native AI dev system that autonomously analyzes objectives, decomposes work into parallel tasks, executes them in isolated sandboxes, and intelligently reviews results.

## Overview

**Five Minds** is a sophisticated development automation system consisting of three main components:

1. **HeadMaster** 🎓 - A fast analyzer that:
   - Analyzes user objectives and repository structure
   - Decomposes work into small, parallel tickets
   - Creates clear acceptance criteria for each ticket
   - Optimizes task execution for maximum parallelism

2. **Runners** 🏃 - Heavy coding agents that:
   - Implement one ticket each in isolated sandboxes
   - Produce diffs, logs, and test results
   - Work in parallel for maximum efficiency
   - Ensure changes don't interfere with each other

3. **Reviewer** 🔍 - An intelligent evaluator that:
   - Compares outputs to the original objective
   - Validates acceptance criteria are met
   - Creates follow-up tasks when needed
   - Ensures alignment with the original plan

The system integrates approved patches, runs final tests, and provides comprehensive feedback on the entire process.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Five Minds                          │
│                        Orchestrator                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        HeadMaster                           │
│  • Analyzes repository and objective                        │
│  • Creates tickets with acceptance criteria                 │
│  • Identifies dependencies and optimizes parallelization    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Parallel Execution                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ Runner1 │  │ Runner2 │  │ Runner3 │  │ Runner4 │       │
│  │Sandbox 1│  │Sandbox 2│  │Sandbox 3│  │Sandbox 4│       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│     Ticket 1    Ticket 2    Ticket 3    Ticket 4          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         Reviewer                            │
│  • Reviews all results against objectives                   │
│  • Validates acceptance criteria                            │
│  • Creates follow-up tickets                                │
│  • Calculates alignment scores                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Integration & Testing                      │
│  • Applies approved patches                                 │
│  • Runs final test suite                                    │
│  • Generates summary report                                 │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone the repository
git clone https://github.com/FrenchFive/FiveMinds-.git
cd FiveMinds-

# Install dependencies
pip install -r requirements.txt
```

### Windows Quick Start

For Windows users, simply double-click `run.bat` or run it from the command prompt:

```batch
REM This will automatically run setup if needed and launch Five Minds
run.bat

REM Or run setup manually first
setup.bat
run.bat
```

The `run.bat` script will:
1. Check if the environment is set up correctly
2. Run `setup.bat` automatically if dependencies are missing
3. Launch Five Minds in interactive mode with the web UI

## Usage

### Quick Start (Interactive Mode)

The easiest way to launch Five Minds is with interactive mode:

```bash
# Launch interactive mode (prompts for objective, auto-starts UI)
python -m fiveminds.cli --interactive
```

This will:
1. Prompt you for your objective and requirements
2. Automatically start the web UI dashboard
3. Execute everything autonomously - no further input needed!

### Command Line Interface

```bash
# Basic usage
python -m fiveminds.cli --repo /path/to/repo "Your objective description"

# With specific requirements
python -m fiveminds.cli --repo /path/to/repo \
  --requirement "Add user authentication" \
  --requirement "Create user model" \
  --requirement "Add login page" \
  "Implement user authentication system"

# With constraints
python -m fiveminds.cli --repo . \
  --requirement "Implement feature X" \
  --constraint "Use Python 3.8+" \
  --constraint "Follow PEP 8" \
  --max-runners 8 \
  "Add new feature"

# Verbose mode for detailed logging
python -m fiveminds.cli --repo . --verbose "Your objective"

# With Web UI Dashboard
python -m fiveminds.cli --repo . --ui "Your objective"

# Custom UI host and port
python -m fiveminds.cli --repo . --ui --ui-host 0.0.0.0 --ui-port 8080 "Your objective"

# With user credentials for git commits
python -m fiveminds.cli --repo . --user-name "Your Name" --user-email "you@example.com" "Your objective"
```

### Autonomous Mode

Five Minds runs in **autonomous mode by default**. This means:
- You define the objective
- Five Minds handles EVERYTHING automatically
- Runners execute and commit changes with your credentials
- Reviews happen automatically
- Tests are run automatically (pytest, npm test, playwright, etc.)
- A final summary is generated when complete

You can disable autonomous mode with `--no-auto` if you need more control.

### Python API

```python
from fiveminds import FiveMinds
from fiveminds.models import Objective

# Create an objective
objective = Objective(
    description="Create a REST API for user management",
    requirements=[
        "Implement user CRUD operations",
        "Add authentication middleware",
        "Create API documentation",
        "Write integration tests"
    ],
    constraints=[
        "Use Flask framework",
        "Follow REST best practices"
    ],
    success_metrics=[
        "All endpoints work correctly",
        "100% test coverage",
        "Documentation is complete"
    ]
)

# Initialize and execute (autonomous mode by default)
five_minds = FiveMinds(
    repo_path="/path/to/repo", 
    max_runners=4,
    user_name="Your Name",      # For git commits
    user_email="you@example.com" # For git commits
)
summary = five_minds.execute(objective)

# Check results
if summary['success']:
    print("✓ Objective completed successfully!")
    print(summary['final_summary'])  # Detailed summary of what was accomplished
else:
    print("✗ Objective needs more work")
```

### With Web UI

```python
from fiveminds import FiveMinds
from fiveminds.models import Objective

objective = Objective(
    description="Your objective",
    requirements=["Requirement 1", "Requirement 2"]
)

# Initialize with UI enabled and autonomous mode
five_minds = FiveMinds(
    repo_path="/path/to/repo",
    max_runners=4,
    enable_ui=True,
    ui_host="127.0.0.1",
    ui_port=5000,
    user_name="Your Name",
    user_email="you@example.com",
    autonomous=True  # Default
)

# Execute - UI will be available at http://127.0.0.1:5000
summary = five_minds.execute(objective)
```

### Example

Run the included example:

```bash
python example.py
```

This demonstrates the system with a sample objective to create a Python calculator library.

## Web UI Dashboard

Five Minds includes a comprehensive web-based UI for monitoring and controlling the system in real-time.

### UI Features

The UI system provides four main views:

#### 1. Dashboard View 📊
- **Objective**: Display current objective description and requirements
- **Status**: Real-time system status with visual indicators
- **Progress Timeline**: Chronological list of execution events
- **Cost Usage**: Token count, API calls, and estimated cost tracking
- **Active Jobs**: List of currently running tasks
- **Tickets Overview**: Grid view of all tickets with status

#### 2. Runner View 🏃
- **Ticket Details**: Full ticket information with acceptance criteria
- **Live Logs**: Real-time streaming logs from runner execution
- **Files Touched**: List of files modified by the runner
- **Runtime**: Elapsed execution time with live updates
- **Cancel Control**: Ability to cancel running jobs

#### 3. HeadMaster View 🎓
- **Reasoning Log**: HeadMaster's planning and analysis decisions
- **Ticket Graph**: Visual graph showing tickets and their relationships
- **Dependency View**: List of ticket dependencies
- **Integration Status**: Current integration state and metrics
- **Execution Waves**: Parallel execution wave organization

#### 4. Review View 🔍
- **Diff Viewer**: Code diff visualization with syntax highlighting
- **Acceptance Checklist**: Criteria with pass/fail indicators
- **Risk List**: Identified risks and warnings
- **Follow-up Buttons**: Quick creation of follow-up tickets
- **Review Summary**: Approval rates and alignment scores

### Starting the UI

```bash
# Via CLI
python -m fiveminds.cli --repo . --ui "Your objective"

# Via Python API
from fiveminds import FiveMinds
five_minds = FiveMinds(repo_path=".", enable_ui=True)
```

### UI Screenshots

**Dashboard View**
![Dashboard](https://github.com/user-attachments/assets/100afdf7-414f-46fc-aed1-65413d88a96e)

**HeadMaster View**
![HeadMaster](https://github.com/user-attachments/assets/2cb86d4b-98bc-4f20-8340-72aad14c03be)

**Review View**
![Review](https://github.com/user-attachments/assets/9782c964-e269-4494-a5f0-3501e9820dd8)

## Features

### 🚀 Autonomous Execution
- **Minimal User Actions**: Just define your objective - Five Minds does everything else
- **Automatic Test Running**: Detects and runs pytest, npm test, playwright, go test, cargo test
- **Git Integration**: Every Runner commits changes with your credentials
- **Final Summary**: Get a comprehensive summary when the task is complete

### Smart Ticket Decomposition
- Automatically breaks down complex objectives into manageable tickets
- Identifies dependencies between tickets
- Creates clear acceptance criteria for each ticket
- Optimizes for parallel execution

### Isolated Sandbox Execution
- Each Runner works in its own isolated sandbox
- Prevents conflicts between parallel work
- Produces clean diffs and detailed logs
- Captures test results and execution metrics
- Commits changes automatically with user credentials

### Intelligent Review System
- Evaluates alignment with original objectives
- Checks acceptance criteria completion
- Analyzes code quality and test results
- Creates follow-up tickets automatically
- Provides actionable feedback

### Parallel Processing
- Executes independent tickets simultaneously
- Respects dependencies between tickets
- Maximizes resource utilization
- Configurable number of parallel runners

### Modern Web UI
- Real-time progress monitoring with WebSocket updates
- Welcome screen for easy onboarding
- Status animations and visual feedback
- Final summary display on completion
- Stop/control buttons for autonomous execution

## Components

### HeadMaster
The HeadMaster analyzes your repository and objectives to create an execution plan:
- Scans repository structure and files
- Detects languages and frameworks
- Decomposes objectives into tickets
- Identifies dependencies
- Optimizes parallelization

### Runner
Runners execute tickets in isolated environments:
- Creates sandbox for isolated execution
- Implements ticket requirements
- Runs tests and generates diffs
- **Commits changes with user credentials**
- Produces detailed logs
- Cleans up after execution

### Reviewer
The Reviewer ensures quality and alignment:
- Reviews execution results
- Validates acceptance criteria
- Calculates alignment scores
- Identifies follow-up work
- Provides improvement suggestions

### Orchestrator
The main system coordinator:
- Manages the entire workflow
- Coordinates HeadMaster, Runners, and Reviewer
- Handles parallel execution
- Integrates results
- Generates summary reports

## Configuration

### Environment Variables
- `FIVEMINDS_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `FIVEMINDS_MAX_RUNNERS`: Default maximum number of parallel runners

### Runtime Options
- `--max-runners`: Number of parallel runners (default: 4)
- `--verbose`: Enable detailed logging
- `--repo`: Repository path (default: current directory)
- `--ui`: Enable web UI dashboard
- `--ui-host`: UI server host (default: 127.0.0.1)
- `--ui-port`: UI server port (default: 5000)

## Development

### Project Structure
```
FiveMinds-/
├── fiveminds/
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Module entry point
│   ├── models.py           # Data models
│   ├── headmaster.py       # HeadMaster component
│   ├── runner.py           # Runner component
│   ├── reviewer.py         # Reviewer component
│   ├── orchestrator.py     # Main orchestrator
│   ├── cli.py              # Command-line interface
│   └── ui/                 # Web UI system
│       ├── __init__.py     # UI module initialization
│       ├── server.py       # Flask server with WebSocket
│       ├── templates/      # HTML templates
│       │   ├── base.html
│       │   ├── dashboard.html
│       │   ├── runner.html
│       │   ├── runner_detail.html
│       │   ├── headmaster.html
│       │   ├── review.html
│       │   └── review_detail.html
│       └── static/         # Static assets
│           ├── css/style.css
│           └── js/
│               ├── main.js
│               ├── dashboard.js
│               ├── runner.js
│               ├── runner_detail.js
│               ├── headmaster.js
│               ├── review.js
│               └── review_detail.js
│   └── tools/              # Tool system
│       ├── __init__.py     # Tools package
│       ├── repo.py         # Repository tools
│       ├── shell.py        # Shell tools
│       └── git.py          # Git tools
├── example.py              # Example usage
├── demo_ui.py              # UI demo script
├── requirements.txt        # Dependencies
├── README.md              # Documentation
└── LICENSE                # License file
```

## Tool System

Five Minds provides a formal tool system for controlled interaction with the environment. All tools are logged, sandboxed, and timeout-bound.

### Repository Tools (`RepoTools`)

```python
from fiveminds import RepoTools

repo = RepoTools("/path/to/repo")

# List directory structure
result = repo.tree(".", max_depth=3)

# Search for content in files
result = repo.search(r"def \w+\(", path="src/")

# Read file contents
result = repo.read("README.md", start_line=0, end_line=50)

# Apply a unified diff patch
result = repo.apply_patch(patch_content, dry_run=True)

# Generate diff between files
result = repo.diff("file1.py", "file2.py")
```

### Shell Tools (`ShellTools`)

```python
from fiveminds import ShellTools

shell = ShellTools("/path/to/workdir", timeout=30)

# Execute a command
result = shell.run("pytest", args=["tests/", "-v"])

# Locate a command
result = shell.which("python3")

# Get command history
history = shell.get_command_history()
```

### Git Tools (`GitTools`)

```python
from fiveminds import GitTools

git = GitTools("/path/to/repo")

# Get repository status
result = git.status(short=True)

# Checkout a branch
result = git.checkout("feature-branch", create=True)

# Create a new branch
result = git.create_branch("new-feature", start_point="main")

# Merge branches
result = git.merge("feature-branch", no_ff=True, message="Merge feature")

# Show differences
result = git.diff(target="HEAD~1", files=["src/main.py"])
```

### Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

See [LICENSE](LICENSE) file for details.

## Acknowledgments

Five Minds is an agentic, repo-native AI dev system designed to automate and optimize software development workflows through intelligent task decomposition, parallel execution, and comprehensive review processes. 
