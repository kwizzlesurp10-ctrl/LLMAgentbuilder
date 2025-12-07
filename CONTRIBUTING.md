# Contributing to LLM Agent Builder

First off, thank you for considering contributing to LLM Agent Builder! It's people like you that make this project such a great tool.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How Can I Contribute?](#how-can-i-contribute)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 18+ (for frontend development)
- Git
- Basic knowledge of FastAPI, React, and Anthropic API

### Development Setup

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/YOUR-USERNAME/LLMAgentbuilder.git
   cd LLMAgentbuilder
   ```

2. **Create a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   # Install package in editable mode with dev dependencies
   pip install -e ".[dev]"
   
   # Install frontend dependencies
   cd frontend
   npm install
   cd ..
   ```

4. **Set up environment variables:**

   Create a `.env` file in the project root:

   ```bash
   ANTHROPIC_API_KEY=your-api-key-here
   ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
   ```

5. **Verify installation:**

   ```bash
   # Run tests
   pytest tests/ -v
   
   # Build frontend
   cd frontend && npm run build && cd ..
   
   # Start the application
   python main.py
   ```

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, screenshots)
- **Describe the behavior you observed and what you expected**
- **Include your environment details** (OS, Python version, Node.js version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the proposed enhancement**
- **Explain why this enhancement would be useful**
- **List any alternative solutions you've considered**

### Your First Code Contribution

Unsure where to begin? Look for issues labeled:

- `good first issue` - Simple issues perfect for beginners
- `help wanted` - Issues where we need community help
- `documentation` - Documentation improvements

### Pull Requests

1. Fork the repo and create your branch from `main` or `develop`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows our style guidelines
6. Issue the pull request!

## Style Guidelines

### Python Code Style

We follow PEP 8 with some modifications:

- Line length: 120 characters
- Use Black for code formatting
- Use isort for import sorting
- Use type hints where appropriate

```bash
# Format code
black llm_agent_builder server tests

# Sort imports
isort llm_agent_builder server tests

# Check linting
flake8 llm_agent_builder server tests --max-line-length=120
```

### JavaScript/React Code Style

- Use ES6+ features
- Follow React best practices and hooks guidelines
- Use functional components with hooks
- Maintain consistent indentation (2 spaces)

```bash
# Lint frontend code
cd frontend
npm run lint
```

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Examples:

```
Add batch generation endpoint for CLI

- Implement new batch_generate function
- Add JSON config file validation
- Update CLI documentation
- Add tests for batch operations

Fixes #123
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=llm_agent_builder --cov=server --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common setup

Example:

```python
def test_agent_generation_with_custom_model():
    """Test that agents can be generated with custom models."""
    # Arrange
    builder = AgentBuilder()
    
    # Act
    code = builder.build_agent(
        agent_name="CustomAgent",
        prompt="Test prompt",
        example_task="Test task",
        model="claude-3-opus-20240229"
    )
    
    # Assert
    assert "CustomAgent" in code
    assert "claude-3-opus-20240229" in code
```

## Pull Request Process

1. **Update documentation** - Ensure README.md and relevant docs are updated
2. **Add tests** - All new functionality must include tests
3. **Run the full test suite** - Ensure all tests pass
4. **Run linters** - Ensure code follows style guidelines
5. **Update CHANGELOG** - Add your changes to the unreleased section
6. **Request review** - Request reviews from maintainers
7. **Address feedback** - Respond to review comments promptly
8. **Squash commits** - Clean up your commit history if needed

### PR Checklist

- [ ] Tests pass locally and in CI
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] No merge conflicts
- [ ] Commits are clean and descriptive

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Test additions or changes

### Local Development

```bash
# Start backend in dev mode
uvicorn server.main:app --reload

# Start frontend in dev mode
cd frontend
npm run dev
```

### Building for Production

```bash
# Build frontend
cd frontend
npm run build
cd ..

# Run with Docker
docker build -t llm-agent-builder .
docker run -p 7860:7860 -e ANTHROPIC_API_KEY=your-key llm-agent-builder
```

## Code Review Process

All submissions require review. We use GitHub pull requests for this purpose. The review process:

1. Automated checks run (CI/CD)
2. Maintainers review code
3. Feedback is provided
4. Changes are requested if needed
5. PR is approved and merged

## Community

### Getting Help

- **GitHub Issues** - For bugs and feature requests
- **Discussions** - For questions and general discussion
- **Documentation** - Check README and docs first

### Recognition

Contributors will be recognized in:

- CHANGELOG.md for their contributions
- README.md contributors section
- GitHub contributors page

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Don't hesitate to ask questions. We're here to help!

Thank you for contributing to LLM Agent Builder! 🚀
