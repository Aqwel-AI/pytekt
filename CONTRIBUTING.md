# Contributing to PyTekt

Thank you for your interest in contributing to PyTekt! We welcome contributions from the AI research and development community. PyTekt is **authored by Aksel Aghajanyan** and **developed by the Aqwel AI Team**.

## How to Contribute

### Reporting Bugs

1. **Check existing issues** first to avoid duplicates
2. **Use the bug report template** when creating new issues
3. **Provide detailed information**:
   - Operating system and Python version
   - PyTekt version
   - Steps to reproduce the bug
   - Expected vs actual behavior
   - Error messages and stack traces

### Suggesting Features

1. **Check the roadmap** to see if your feature is already planned
2. **Open a feature request** with detailed description
3. **Explain the use case** and why it would benefit AI researchers
4. **Provide examples** of how the feature would be used

### Code Contributions

#### Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/aqwelai/pytekt.git
   cd pytekt
   ```

2. **Set up development environment**
   ```bash
   pip install -e .[dev,full]
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Guidelines

**Code Style:**
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write comprehensive docstrings with examples
- Keep functions focused and modular

**Testing:**
- Write tests for all new functionality
- Ensure existing tests pass: `pytest`
- Aim for >90% test coverage

**Documentation:**
- Update docstrings for any changed functions
- Add examples to demonstrate usage
- Update README.md if adding new modules

**Commit Messages:**
- Use clear, descriptive commit messages
- Follow conventional commits format:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation changes
  - `test:` for adding tests
  - `refactor:` for code refactoring

#### Code Review Process

1. **Submit a Pull Request** with clear description
2. **Link related issues** using keywords (fixes #123)
3. **Ensure CI passes** (tests, linting, type checking)
4. **Respond to feedback** from maintainers
5. **Update documentation** if needed

## Priority Areas for Contributions

### High Priority
- **Statistical Testing Module** - Hypothesis tests, p-values, confidence intervals
- **Experiment Tracking** - Research reproducibility and version control
- **Scientific Visualization** - Publication-ready plots and charts
- **Performance Optimization** - Speed improvements for mathematical operations

### Medium Priority
- **Data Pipeline Tools** - Enhanced preprocessing workflows
- **Model Validation** - Advanced cross-validation techniques
- **Benchmarking Suite** - Standard datasets and baselines
- **Documentation Improvements** - More examples and tutorials

### Always Welcome
- **Bug fixes** and error handling improvements
- **Performance optimizations** for existing functions
- **Additional test coverage** for edge cases
- **Documentation updates** and typo fixes
- **Example notebooks** and tutorials

## Development Resources

### Project Structure
```
pytekt/
├── pytekt/           # Main package
│   ├── maths.py    # Mathematical operations (71+ functions)
│   ├── embed.py    # Text embeddings and similarity
│   ├── evaluate.py # Model evaluation metrics
│   ├── code.py     # Code analysis tools
│   ├── prompt.py   # AI prompt templates
│   ├── pdf.py      # Documentation generation
│   └── ...         # Other modules
├── tests/          # Test suite
├── docs/           # Documentation
└── examples/       # Usage examples
```

### Key Dependencies
- **NumPy** - Numerical operations
- **SciPy** - Advanced mathematics (optional)
- **scikit-learn** - Machine learning utilities (optional)
- **sentence-transformers** - Text embeddings (optional)
- **reportlab** - PDF generation (optional)

### Running Tests
```bash
# Run all tests
pytest

# Run specific module tests
pytest tests/test_maths.py

# Run with coverage
pytest --cov=pytekt
```

### Building Documentation
```bash
# Generate API documentation
python -c "import pytekt.pdf; pytekt.pdf.generate_complete_documentation('docs')"
```

## Community Guidelines

### Code of Conduct
- **Be respectful** and inclusive in all interactions
- **Focus on constructive feedback** and collaborative problem-solving
- **Welcome newcomers** and help them get started
- **Maintain professional standards** in all communications

### Communication Channels
- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and community discussion
- **Company Gmail** - aqwelai.company@gmail.com for private matters

### Recognition
- All contributors will be acknowledged in the CONTRIBUTORS.md file
- Significant contributions may be highlighted in release notes
- Regular contributors may be invited to join the core team

## Getting Help

### For New Contributors
- Start with **"good first issue"** labels
- Ask questions in GitHub Discussions
- Review existing code to understand patterns
- Read through the comprehensive documentation

### For Experienced Developers
- Look for **"help wanted"** labels for challenging issues
- Consider contributing to high-priority areas
- Help review pull requests from other contributors
- Mentor new contributors

### Research-Specific Contributions
- **Mathematical accuracy** is critical - provide references for algorithms
- **Performance benchmarks** should be included for optimization PRs
- **Academic citations** should be included for research-based features
- **Reproducibility** is essential - include seeds and version information

## Legal

By contributing to PyTekt, you agree that your contributions will be licensed under the Apache License 2.0, the same license as the project.

---

**Thank you for helping make PyTekt the premier AI research and development library!**

For questions about contributing, contact us at aqwelai.company@gmail.com (Company Gmail).
