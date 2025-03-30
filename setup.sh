#!/bin/bash
set -e

echo "Setting up vibes repository..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install uv
# uv pip install pytest pytest-cov black isort mypy

# Install Node.js dependencies if package.json exists
if [ -f "package.json" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    uv venv
fi

# Activate virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source .venv/bin/activate
uv pip install pytest pytest-cov black isort mypy

# Install script-specific requirements if available
if [ -f "scripts/requirements.txt" ]; then
    echo "Installing script requirements..."
    uv pip install -r scripts/requirements.txt
fi

# Initialize git hooks
if [ -d ".git" ]; then
    echo "Setting up git hooks..."
    # Add pre-commit hook for linting
    if [ ! -f ".git/hooks/pre-commit" ]; then
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
set -e

# Run formatters and linters before commit
if command -v black &> /dev/null; then
    echo "Running black..."
    black .
fi

if command -v isort &> /dev/null; then
    echo "Running isort..."
    isort .
fi
EOF
        chmod +x .git/hooks/pre-commit
    fi
fi

echo "Setup complete! You can now use the vibes repository."
echo "Run 'source .venv/bin/activate' to activate the virtual environment."