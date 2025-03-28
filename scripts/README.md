# Scripts

This directory contains one-off Python scripts for various tasks.

## Usage

Scripts in this directory can be run using uv:

```bash
# Run a script using uv without activating the environment
uv run python script_name.py

# Or run using uvx for an even simpler workflow
uvx script_name.py
```

## Managing Dependencies

Use uv to manage dependencies:

```bash
# Add a dependency
uv pip install package_name

# Add a dependency to requirements.txt
uv pip install package_name -r requirements.txt
```

## Adding New Scripts

When adding a new script:

1. Include a docstring at the top explaining what the script does
2. Add any required dependencies using uv
3. Follow the code style guidelines in the main CLAUDE.md file