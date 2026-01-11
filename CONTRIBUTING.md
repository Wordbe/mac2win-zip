# Contributing to mac2win-zip

Thank you for your interest in contributing to mac2win-zip! We welcome contributions from the community.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)
- Example files or commands if applicable

### Suggesting Features

We welcome feature suggestions! Please:
- Check if the feature has already been requested
- Explain the use case and benefits
- Provide examples of how it would work

### Submitting Code

#### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone git@github.com:YOUR_USERNAME/mac2win-zip.git
   cd mac2win-zip
   ```

3. Install development dependencies:
   ```bash
   # Using uv (recommended)
   uv pip install -e ".[dev]"

   # Or using pip
   pip install -e ".[dev]"
   ```

4. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Code Standards

We maintain high code quality standards:

- **Code Style**: We use [Black](https://github.com/psf/black) for formatting
  ```bash
  black mac2win_zip/ tests/
  ```

- **Linting**: We use [Ruff](https://github.com/astral-sh/ruff) for linting
  ```bash
  ruff check mac2win_zip/ tests/
  ruff check --fix mac2win_zip/ tests/  # Auto-fix issues
  ```

- **Type Hints**: Add type hints to new functions
- **Docstrings**: Add docstrings to public functions
- **Line Length**: Maximum 100 characters

#### Testing

All code changes must include tests:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=mac2win_zip --cov-report=term-missing

# Aim for >90% coverage
```

#### Before Submitting

Run the complete check:

```bash
# Format code
black mac2win_zip/ tests/

# Lint code
ruff check --fix mac2win_zip/ tests/

# Run tests
pytest tests/ -v --cov=mac2win_zip
```

All checks should pass before submitting your PR.

#### Commit Messages

Write clear, descriptive commit messages:

```
Add support for custom character replacements

- Add new sanitize_custom() function
- Update tests for custom replacements
- Document in README
```

#### Pull Request Process

1. Update documentation if needed (README.md, docstrings)
2. Add tests for new features or bug fixes
3. Ensure all tests pass and coverage remains high
4. Update CHANGELOG.md with your changes
5. Create a pull request with:
   - Clear description of changes
   - Link to related issues
   - Screenshots/examples if applicable

6. Wait for review:
   - Address reviewer feedback
   - Keep the PR focused (one feature/fix per PR)
   - Be patient and respectful

#### Review Process

- Maintainers will review PRs as time allows
- First-time contributors' PRs require approval before CI runs (security measure)
- We may request changes or ask questions
- Once approved, a maintainer will merge your PR

## Development Guidelines

### Project Structure

```
mac2win-zip/
├── mac2win_zip/          # Main package
│   ├── __init__.py       # Package metadata
│   └── cli.py            # CLI and core logic
├── tests/                # Test suite
│   └── test_cli.py       # All tests
├── README.md             # User documentation
├── CONTRIBUTING.md       # This file
└── pyproject.toml        # Project configuration
```

### Key Principles

1. **Simplicity**: Keep the codebase simple and focused
2. **Compatibility**: Ensure macOS and Windows compatibility
3. **Security**: Validate all user inputs
4. **Testing**: Test all code paths
5. **Documentation**: Document public APIs

### Security Considerations

When contributing:
- Validate all file paths (prevent path traversal)
- Sanitize filenames (remove forbidden characters)
- Handle errors gracefully (no stack traces to users)
- Don't add dependencies unless absolutely necessary

## Questions?

Feel free to:
- Open an issue for questions
- Ask in your PR if you're unsure about something
- Check existing issues and PRs for similar discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for making mac2win-zip better! 🎉
