# CLAUDE.md - Guidelines for the vibes repository

## Setup
- Run `./setup.sh` to install required dependencies
- Activates Python venv with: `source .venv/bin/activate`

## Build/Lint/Test Commands
- Format Python: `uv pip run black .`
- Sort imports: `uv pip run isort .`
- Type check: `uv pip run mypy .`
- Test Python: `uv pip run pytest`
- Test single file: `uv pip run pytest path/to/test.py`

## Code Style Guidelines
- **Imports**: Group imports by type (built-in, external, internal)
- **Formatting**: Use Black with default settings for Python
- **Types**: Use type hints for Python, TypeScript for JS/TS
- **Naming**: snake_case for Python, camelCase for JS/TS
- **Error Handling**: Use try/except blocks with specific exceptions
- **Documentation**: Docstrings for Python, JSDoc for JS/TS
- **Commits**: Follow conventional commits format
- **Test Coverage**: Aim for 80% coverage for new code
- **Architecture**: Favor functional programming patterns

This repository contains small tools and one-off scripts. New tools should be self-contained in their own directories with proper documentation.