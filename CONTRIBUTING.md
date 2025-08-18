# Contributing to VN Stock Advisory Notifier

Thank you for your interest in contributing to VN Stock Advisory Notifier! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Testing](#testing)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment
- Respect differing viewpoints and experiences

## Getting Started

### Prerequisites

- Python 3.6+
- Git
- Google Gemini API access (for full testing)
- Basic knowledge of Vietnamese stock market (helpful but not required)

### Setup Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/vn-stock-service.git
   cd vn-stock-service
   ```
3. **Set up virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Create configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings (can use mock data for testing)
   ```
6. **Run tests**:
   ```bash
   python3 -m pytest tests/
   ```

## Development Process

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `docs/description` - Documentation updates

### Workflow

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our [code style](#code-style)

3. **Add tests** for any new functionality

4. **Run tests** to ensure nothing is broken:
   ```bash
   python3 -m pytest tests/ -v
   python3 main.py  # Test basic functionality
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## Submitting Changes

### Pull Request Guidelines

- **Clear title** describing the change
- **Detailed description** of what was changed and why
- **Link to related issues** if applicable
- **Screenshots** for UI changes
- **Test results** showing your changes work

### Commit Message Format

We follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

Examples:
```
feat(ai): add enhanced portfolio advisory with risk analysis
fix(email): resolve template rendering issue for empty data
docs(readme): update installation instructions
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 120 characters max
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Organized with isort
- **Formatting**: Use black for automatic formatting

### Code Quality Tools

Run these before submitting:

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking (optional but recommended)
mypy src/ --ignore-missing-imports
```

### Naming Conventions

- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private methods**: `_underscore_prefix`
- **Files/Modules**: `snake_case.py`

## Testing

### Test Structure

- `tests/` - Unit tests
- `tests/fixtures/` - Test data and fixtures
- Mock data should be used for external APIs
- Each module should have corresponding tests

### Writing Tests

```python
import pytest
from src.advisory.engine import AdvisoryEngine

def test_advisory_engine_basic():
    """Test basic advisory engine functionality."""
    engine = AdvisoryEngine(mock_ai_advisor)
    result = engine.generate_stock_advisory(mock_position, mock_market_data)
    assert result["advisory"]["action"] in ["hold", "buy", "sell"]
```

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/

# Run specific test file
python3 -m pytest tests/test_advisory.py -v

# Run tests with coverage
python3 -m pytest tests/ --cov=src/

# Run integration tests
python3 test_gemini.py  # Requires API key
```

## Issue Reporting

### Bug Reports

Include:
- **Clear title** describing the bug
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment information** (OS, Python version, etc.)
- **Error messages** and stack traces
- **Configuration** (sanitized, no API keys)

### Feature Requests

Include:
- **Clear description** of the proposed feature
- **Use case** explaining why it would be useful
- **Proposed implementation** (if you have ideas)
- **Potential drawbacks** or concerns

### Enhancement Ideas

We welcome suggestions for:
- New data providers
- Additional technical indicators
- Email template improvements
- Performance optimizations
- Documentation improvements

## Areas for Contribution

### High Priority

- **Data Provider Implementations**: Real Vietnam stock APIs
- **Technical Indicators**: New analysis methods
- **Email Templates**: Better designs and layouts
- **Error Handling**: More robust error recovery
- **Documentation**: User guides and API docs

### Medium Priority

- **Performance Optimization**: Faster data processing
- **Caching**: Intelligent data caching strategies
- **Mobile Support**: Responsive email templates
- **Internationalization**: Multi-language support

### Good First Issues

Look for issues labeled `good-first-issue`:
- Documentation improvements
- Simple bug fixes
- Test coverage improvements
- Code style updates

## Questions?

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: For security issues or private matters

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for their contributions
- GitHub contributors page
- Special thanks in major releases

Thank you for contributing to VN Stock Advisory Notifier! 🚀
