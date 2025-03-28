# vibes
This is where I'm going to keep all my small tools and one off scripts.

## Setup

To set up this repository for development:

1. Clone the repository:
   ```bash
   git clone https://github.com/brianlawrence2/vibes.git
   cd vibes
   ```

2. Run the setup script to install all necessary dependencies:
   ```bash
   ./setup.sh
   ```

3. Activate the Python virtual environment:
   ```bash
   source .venv/bin/activate
   ```

## Using Claude Code

This repository is configured to work with Claude Code. To use Claude Code:

1. Install the Claude Code CLI:
   ```bash
   pip install claude-cli
   ```

2. Authenticate with Claude:
   ```bash
   claude auth login
   ```

3. Start using Claude Code with this repository:
   ```bash
   claude code
   ```

Claude Code will use the guidelines in CLAUDE.md to assist with development tasks.

## Usage

Each tool is organized in its own directory with its own README and documentation. To use a tool, navigate to its directory and follow the instructions in its README.

## Development

See [CLAUDE.md](CLAUDE.md) for code style guidelines and development commands.
