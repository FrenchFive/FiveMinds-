# Five Minds Architecture

## System Overview

Five Minds is a sophisticated agentic AI development system that automates software development through intelligent decomposition, parallel execution, and comprehensive review processes.

## Core Components

### 1. HeadMaster (`headmaster.py`)

The HeadMaster is the analytical brain of the system, responsible for understanding objectives and planning work.

**Responsibilities:**
- Repository Analysis
  - Scans file structure
  - Detects languages and frameworks
  - Identifies existing patterns and conventions
  
- Objective Decomposition
  - Breaks down complex objectives into small, manageable tickets
  - Creates clear acceptance criteria for each ticket
  - Ensures tickets are independently implementable
  
- Dependency Management
  - Identifies dependencies between tickets
  - Ensures proper execution order
  - Marks critical setup/initialization tasks
  
- Parallelization Optimization
  - Organizes tickets into execution waves
  - Maximizes parallel processing opportunities
  - Respects dependency constraints

**Key Algorithms:**
```python
decompose_objective(objective) -> List[Ticket]
  1. Parse objective requirements
  2. For each requirement:
     a. Create ticket with unique ID
     b. Generate acceptance criteria
     c. Assign priority
  3. Return ticket list

identify_dependencies(tickets) -> List[Ticket]
  1. Analyze ticket descriptions
  2. Identify setup/initialization tickets
  3. Mark dependencies for other tickets
  4. Adjust priorities accordingly

optimize_parallelization(tickets) -> Dict[wave, List[Ticket]]
  1. Initialize wave 0
  2. While unprocessed tickets exist:
     a. Find tickets with satisfied dependencies
     b. Add to current wave
     c. Mark as processed
     d. Move to next wave
  3. Return wave mapping
```

### 2. Runner (`runner.py`)

Runners are the execution engines that implement individual tickets in isolated environments.

**Responsibilities:**
- Sandbox Creation
  - Creates isolated temporary directory
  - Copies repository content
  - Respects ignore patterns
  
- Ticket Execution
  - Implements ticket requirements
  - Tracks progress and logs
  - Captures metrics
  
- Testing
  - Runs test suites
  - Captures test results
  - Reports pass/fail status
  
- Diff Generation
  - Generates clean diffs of changes
  - Provides before/after comparison
  - Facilitates code review
  
- Cleanup
  - Removes sandbox environment
  - Frees system resources
  - Ensures no residual state

**Isolation Strategy:**
```
Original Repository
       │
       ├─→ Runner 1 Sandbox (Ticket A)
       │   /tmp/fiveminds_sandbox_R1_xxxxx/
       │
       ├─→ Runner 2 Sandbox (Ticket B)
       │   /tmp/fiveminds_sandbox_R2_xxxxx/
       │
       └─→ Runner N Sandbox (Ticket N)
           /tmp/fiveminds_sandbox_RN_xxxxx/
```

**Execution Flow:**
```python
execute_ticket(ticket) -> RunnerResult
  1. Update ticket status to IN_PROGRESS
  2. Create sandbox if needed
  3. Implement ticket requirements:
     a. Parse acceptance criteria
     b. Make code changes
     c. Mark criteria as met
  4. Run tests in sandbox
  5. Generate diff
  6. Create RunnerResult
  7. Update ticket status to NEEDS_REVIEW
  8. Return result
```

### 3. Reviewer (`reviewer.py`)

The Reviewer ensures quality and alignment with original objectives.

**Responsibilities:**
- Result Validation
  - Checks execution success
  - Validates acceptance criteria
  - Reviews test results
  
- Quality Analysis
  - Analyzes code diffs
  - Identifies potential issues
  - Checks for debug statements
  - Flags TODOs and FIXMEs
  
- Alignment Scoring
  - Calculates alignment with objective
  - Considers multiple factors
  - Provides quantitative measure
  
- Follow-up Identification
  - Creates tickets for test failures
  - Tracks TODO items
  - Identifies improvement opportunities
  
- Feedback Generation
  - Provides actionable suggestions
  - Highlights issues
  - Recommends improvements

**Alignment Score Calculation:**
```python
calculate_alignment_score(ticket, result) -> float
  score = 0.0
  
  # Execution success: 30%
  if result.success:
    score += 0.3
  
  # Acceptance criteria: 40%
  criteria_met = count(criteria.met)
  criteria_total = count(all_criteria)
  score += 0.4 * (criteria_met / criteria_total)
  
  # Test results: 30%
  if has_tests:
    passed = result.tests_passed
    total = result.tests_total
    score += 0.3 * (passed / total)
  else:
    score += 0.15  # Partial credit
  
  return min(1.0, score)
```

**Review Decision Flow:**
```
Result Received
      │
      ├─→ Check Execution Success
      │   └─→ Failed? → Reject
      │
      ├─→ Check Acceptance Criteria
      │   └─→ Not Met? → Reject
      │
      ├─→ Check Test Results
      │   └─→ Tests Failed? → Reject
      │
      ├─→ Calculate Alignment Score
      │   └─→ < 0.7? → Reject
      │
      └─→ All Checks Pass → Approve
```

### 4. Orchestrator (`orchestrator.py`)

The Orchestrator (FiveMinds class) coordinates all components and manages the overall workflow.

**Responsibilities:**
- Workflow Coordination
  - Manages execution phases
  - Coordinates components
  - Handles state transitions
  
- Parallel Execution
  - Manages thread pool
  - Distributes work to runners
  - Collects results
  
- Result Aggregation
  - Collects execution results
  - Gathers review feedback
  - Tracks overall progress
  
- Integration
  - Applies approved patches
  - Runs final tests
  - Ensures consistency
  
- Reporting
  - Generates summaries
  - Provides metrics
  - Reports success/failure

**Execution Phases:**

```
Phase 1: HeadMaster Analysis
├─ Analyze repository structure
├─ Decompose objective into tickets
├─ Identify dependencies
└─ Optimize for parallelization

Phase 2: Runner Execution
├─ For each wave:
│  ├─ Create runners for tickets
│  ├─ Execute in parallel (ThreadPool)
│  └─ Collect results
└─ All waves complete

Phase 3: Review
├─ Initialize Reviewer with objective
├─ For each result:
│  ├─ Review against criteria
│  ├─ Calculate alignment
│  ├─ Create follow-ups if needed
│  └─ Approve or reject
└─ Generate review summary

Phase 4: Integration & Testing
├─ Filter approved results
├─ Apply patches (simulated)
├─ Run final tests
└─ Generate summary
```

## Data Flow

```
User Objective
     │
     ▼
┌─────────────┐
│ HeadMaster  │ Analyzes & Plans
└─────────────┘
     │
     ├─→ RepositoryContext
     └─→ List[Ticket]
          │
          ▼
┌──────────────────────────┐
│   Wave-based Execution   │
│  ┌──────┐ ┌──────┐      │
│  │ R1   │ │ R2   │ ...  │
│  │TKT-1 │ │TKT-2 │      │
│  └──────┘ └──────┘      │
└──────────────────────────┘
     │
     └─→ Dict[ticket_id, RunnerResult]
          │
          ▼
┌─────────────┐
│  Reviewer   │ Evaluates & Validates
└─────────────┘
     │
     └─→ Dict[ticket_id, ReviewResult]
          │
          ▼
┌─────────────┐
│ Integration │ Applies & Tests
└─────────────┘
     │
     ▼
Final Summary
```

## Data Models

### Core Models (`models.py`)

**Ticket**
```python
@dataclass
class Ticket:
    id: str                              # Unique identifier
    title: str                           # Short description
    description: str                     # Detailed explanation
    acceptance_criteria: List[AcceptanceCriteria]
    status: TicketStatus                 # Current state
    priority: TicketPriority             # Importance level
    dependencies: List[str]              # Ticket IDs
    assigned_runner: Optional[str]       # Runner ID
    metadata: Dict[str, Any]             # Additional info
```

**RunnerResult**
```python
@dataclass
class RunnerResult:
    ticket_id: str                       # Ticket identifier
    success: bool                        # Execution outcome
    diff: str                            # Code changes
    logs: List[str]                      # Execution logs
    test_results: Optional[Dict]         # Test outcomes
    error_message: Optional[str]         # Error details
    execution_time: float                # Duration in seconds
```

**ReviewResult**
```python
@dataclass
class ReviewResult:
    ticket_id: str                       # Ticket identifier
    approved: bool                       # Review decision
    feedback: str                        # Detailed feedback
    alignment_score: float               # 0.0 to 1.0
    follow_up_tickets: List[Ticket]      # New tickets
    suggestions: List[str]               # Improvements
```

## Concurrency Model

Five Minds uses thread-based parallelism for Runner execution:

```python
ThreadPoolExecutor(max_workers=max_runners)
├─ Thread 1: Runner 1 → Ticket A
├─ Thread 2: Runner 2 → Ticket B
├─ Thread 3: Runner 3 → Ticket C
└─ Thread 4: Runner 4 → Ticket D
```

**Synchronization Points:**
- Wave boundaries (all tickets in wave must complete)
- Review phase (all results must be collected)
- Integration phase (all reviews must be complete)

**Thread Safety:**
- Each Runner has isolated sandbox
- No shared state during execution
- Results collected via futures
- Main thread aggregates outcomes

## Tool System

Tools are the only way agents interact with the world. All tool operations are logged, sandboxed, and timeout-bound.

### Tool Contract

Every tool must:
1. Log all operations
2. Respect timeout constraints
3. Return structured results (`ToolResult`)
4. Handle errors gracefully
5. Never execute simulated actions

### Repository Tools (`tools/repo.py`)

Provides controlled access to repository operations:

| Tool | Description |
|------|-------------|
| `repo.tree(path, max_depth)` | List directory structure |
| `repo.search(pattern, path)` | Search for content in files |
| `repo.read(path, start_line, end_line)` | Read file contents |
| `repo.apply_patch(patch, dry_run)` | Apply unified diff patch |
| `repo.diff(path1, path2)` | Generate diff between files |

**Security Features:**
- Path validation prevents directory traversal
- File size limits prevent memory exhaustion
- All operations scoped to repository

### Shell Tools (`tools/shell.py`)

Provides controlled shell command execution:

| Tool | Description |
|------|-------------|
| `shell.run(command, args, timeout)` | Execute shell command |
| `shell.which(command)` | Locate a command |

**Security Features:**
- All commands logged with exit codes
- Timeout enforcement prevents hanging
- Output size limits prevent memory issues
- Command history tracking

### Git Tools (`tools/git.py`)

Provides controlled version control operations:

| Tool | Description |
|------|-------------|
| `git.status(short)` | Get repository status |
| `git.checkout(target, create)` | Checkout branch or files |
| `git.create_branch(name, start_point)` | Create new branch |
| `git.merge(branch, no_ff, message)` | Merge branches |
| `git.diff(target, staged, files)` | Show differences |

**Security Features:**
- Operations scoped to repository
- Timeout enforcement
- Structured output parsing

### Tool Result Structure

All tools return a `ToolResult` object:

```python
@dataclass
class ToolResult:
    success: bool          # Whether operation succeeded
    output: Any            # Operation output (structured)
    error: Optional[str]   # Error message if failed
    logs: List[str]        # Operation logs
```

## Extension Points

### Custom Runners
Subclass `Runner` to implement specific behavior:
```python
class AIRunner(Runner):
    def _implement_ticket(self, ticket):
        # Use AI model to generate code
        pass
```

### Custom Reviewers
Subclass `Reviewer` for specialized review logic:
```python
class SecurityReviewer(Reviewer):
    def review_result(self, ticket, result):
        # Add security checks
        pass
```

### Custom HeadMaster Strategies
Override decomposition logic:
```python
class AIHeadMaster(HeadMaster):
    def decompose_objective(self, objective):
        # Use AI to create better tickets
        pass
```

## Performance Characteristics

**Time Complexity:**
- Repository Analysis: O(n) where n = number of files
- Ticket Decomposition: O(m) where m = number of requirements
- Dependency Analysis: O(t²) where t = number of tickets
- Parallelization: O(t) with dependency constraints
- Execution: O(waves) where each wave runs in parallel
- Review: O(t) for sequential reviews

**Space Complexity:**
- Each sandbox: O(repository_size)
- Total space: O(max_runners × repository_size)
- Results storage: O(t × result_size)

**Scalability:**
- Horizontal: Add more runners for more parallelism
- Vertical: Larger repositories handled efficiently
- Bottleneck: Repository copying to sandboxes

## Error Handling

**Levels of Error Handling:**

1. **Ticket Execution Errors**
   - Caught by Runner
   - Logged in RunnerResult
   - Marked as failed
   - Does not block other tickets

2. **Review Errors**
   - Logged but does not crash system
   - Ticket marked as failed
   - Follow-up tickets may be created

3. **Integration Errors**
   - Logged in integration results
   - Summary reflects partial success

4. **System Errors**
   - Logged at orchestrator level
   - Cleanup performed
   - Summary generated with error state

## Future Enhancements

1. **AI Integration**
   - Use LLMs for ticket decomposition
   - AI-powered code generation in Runners
   - Smarter dependency detection

2. **Git Integration**
   - Use git worktrees for sandboxes
   - Automatic branch creation
   - PR generation

3. **Distributed Execution**
   - Run Runners on different machines
   - Cloud-based execution
   - Container-based isolation

4. **Advanced Review**
   - Code quality metrics
   - Security vulnerability scanning
   - Performance impact analysis

5. **Learning System**
   - Learn from past executions
   - Improve ticket decomposition
   - Optimize parallelization

6. **Web UI**
   - Real-time progress monitoring
   - Interactive ticket management
   - Visual diff viewing
