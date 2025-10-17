# Contributing to Jira-Outlook Sync

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/jira-outlook-sync.git
   cd jira-outlook-sync
   ```
3. **Set up development environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/your-bugfix-name
```

### 2. Make Your Changes
- Follow PEP 8 style guide
- Add type hints to functions
- Write tests for new features
- Update documentation as needed

### 3. Test Your Changes
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=scripts tests/

# Format code
black scripts/ tests/

# Lint code
flake8 scripts/ tests/

# Type check
mypy scripts/
```

### 4. Commit Your Changes
Use [Conventional Commits](https://www.conventionalcommits.org/) format:
```bash
feat: add new feature
fix: fix a bug
docs: update documentation
test: add or update tests
refactor: refactor code
chore: update dependencies
```

Examples:
```bash
git commit -m "feat: add support for recurring calendar events"
git commit -m "fix: handle timezone conversion edge case"
git commit -m "docs: update setup instructions"
```

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```
Then open a pull request on GitHub.

## Code Style

### Python
- Follow PEP 8
- Use Black for formatting (line length 100)
- Use type hints for all functions
- Write Google-style docstrings

Example:
```python
def sync_ticket_to_calendar(ticket_key: str, calendar_id: str) -> Dict[str, Any]:
    """Synchronizes a Jira ticket to an Outlook calendar event.
    
    Args:
        ticket_key: The Jira ticket key (e.g., 'SRE-123')
        calendar_id: The Outlook calendar ID
        
    Returns:
        Dictionary containing event details and sync status
        
    Raises:
        JiraAPIError: If ticket cannot be retrieved
        OutlookAPIError: If calendar event cannot be created
    """
    pass
```

## Testing Guidelines

- Write unit tests for all new functions
- Use pytest fixtures for common setup
- Mock external API calls
- Aim for >80% code coverage
- Test edge cases and error handling

## Documentation

- Update README.md for user-facing changes
- Update OpenSpec proposal if changing requirements
- Add inline comments for complex logic
- Update configuration templates if needed

## OpenSpec Workflow

This project uses OpenSpec for specification-driven development:

1. **Review the proposal**: `openspec/changes/add-jira-outlook-reminder-automation/`
2. **Follow the tasks**: See `tasks.md` for implementation checklist
3. **Update specs**: Modify spec files if requirements change
4. **Validate changes**: Run `openspec validate --strict`

## Pull Request Process

1. Ensure all tests pass
2. Update documentation
3. Update CHANGELOG (if exists)
4. Request review from maintainers
5. Address review feedback
6. Once approved, maintainer will merge

## Code Review Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No sensitive data in commits
- [ ] Commit messages follow conventional commits
- [ ] Changes align with OpenSpec proposal

## Questions or Issues?

- Open an issue on GitHub
- Tag maintainers for urgent questions
- Check existing issues and discussions first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
