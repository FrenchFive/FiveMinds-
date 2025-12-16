# Contributing to Five Minds

Thank you for your interest in contributing to Five Minds! This document provides guidelines and information for contributors.

## Getting Started

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/FrenchFive/FiveMinds-.git
   cd FiveMinds-
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"  # Install in development mode with dev dependencies
   ```

4. **Verify installation**
   ```bash
   python example.py
   python -m fiveminds.cli --help
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Follow existing code style
   - Add comments where necessary

3. **Test your changes**
   ```bash
   python example.py  # Run the example
   # Add unit tests if applicable
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

### Python Style Guidelines

- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

### Documentation Style

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ExceptionType: Description of when this exception is raised
    """
    pass
```

## Component Guidelines

### Adding a New Component

When adding a new component to Five Minds:

1. **Create the component file**
   - Place in `fiveminds/` directory
   - Use lowercase with underscores for filename

2. **Define the component class**
   - Clear class name describing purpose
   - Comprehensive docstrings
   - Type hints for all methods

3. **Update `__init__.py`**
   - Add import for new component
   - Add to `__all__` list

4. **Document the component**
   - Add section to ARCHITECTURE.md
   - Update README.md if user-facing
   - Include usage examples

### Extending Existing Components

**HeadMaster Extensions:**
```python
class CustomHeadMaster(HeadMaster):
    """Custom HeadMaster with specialized behavior"""
    
    def decompose_objective(self, objective: Objective) -> List[Ticket]:
        """Override with custom decomposition logic"""
        # Your implementation
        pass
```

**Runner Extensions:**
```python
class CustomRunner(Runner):
    """Custom Runner with specialized execution"""
    
    def _implement_ticket(self, ticket: Ticket) -> List[str]:
        """Override with custom implementation logic"""
        # Your implementation
        pass
```

**Reviewer Extensions:**
```python
class CustomReviewer(Reviewer):
    """Custom Reviewer with specialized review logic"""
    
    def review_result(self, ticket: Ticket, result: RunnerResult) -> ReviewResult:
        """Override with custom review logic"""
        # Your implementation
        pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fiveminds

# Run specific test file
pytest tests/test_headmaster.py
```

### Writing Tests

When adding new functionality, include tests:

```python
import pytest
from fiveminds import HeadMaster
from fiveminds.models import Objective

def test_headmaster_decompose():
    """Test that HeadMaster decomposes objectives correctly"""
    headmaster = HeadMaster(".")
    objective = Objective(
        description="Test objective",
        requirements=["Requirement 1", "Requirement 2"]
    )
    
    tickets = headmaster.decompose_objective(objective)
    
    assert len(tickets) == 2
    assert tickets[0].title == "Requirement 1"
    assert tickets[1].title == "Requirement 2"
```

## Areas for Contribution

### High Priority

1. **AI Integration**
   - Integrate with OpenAI/Anthropic APIs
   - Use LLMs for ticket decomposition
   - AI-powered code generation

2. **Git Integration**
   - Use git worktrees for sandboxes
   - Automatic branch creation
   - PR generation and management

3. **Testing Framework**
   - Unit tests for all components
   - Integration tests
   - End-to-end tests

### Medium Priority

4. **Performance Optimization**
   - Faster repository scanning
   - More efficient sandbox creation
   - Parallel review processing

5. **Enhanced Review System**
   - Code quality metrics
   - Security scanning
   - Performance analysis

6. **CLI Improvements**
   - Better progress visualization
   - Interactive mode
   - Configuration file support

### Lower Priority

7. **Web UI**
   - Real-time progress dashboard
   - Interactive ticket management
   - Visual diff viewer

8. **Distributed Execution**
   - Remote runner support
   - Cloud-based execution
   - Container integration

9. **Monitoring & Observability**
   - Metrics collection
   - Logging improvements
   - Performance profiling

## Documentation

### Documentation Standards

- Keep README.md up-to-date with user-facing changes
- Update ARCHITECTURE.md for architectural changes
- Add inline comments for complex logic
- Include examples in docstrings

### Documentation Structure

```
FiveMinds-/
├── README.md              # User guide and quick start
├── ARCHITECTURE.md        # Technical architecture
├── CONTRIBUTING.md        # This file
└── docs/                  # Additional documentation (future)
    ├── api.md            # API reference
    ├── examples/         # Usage examples
    └── tutorials/        # Step-by-step guides
```

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New code has tests (if applicable)
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Description of testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
```

## Code Review

### For Reviewers

- Be constructive and respectful
- Focus on code quality and maintainability
- Test the changes locally if possible
- Approve or request changes with clear feedback

### For Contributors

- Respond to feedback promptly
- Don't take criticism personally
- Ask questions if feedback is unclear
- Make requested changes or discuss alternatives

## Community

### Communication

- Use GitHub Issues for bug reports and feature requests
- Use GitHub Discussions for questions and ideas
- Be respectful and inclusive
- Help others when possible

### Code of Conduct

- Be respectful and welcoming
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

## Questions?

If you have questions about contributing:

1. Check existing documentation
2. Search GitHub Issues
3. Create a new issue with your question
4. Tag with "question" label

## License

By contributing to Five Minds, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

Thank you for contributing to Five Minds! 🧠
