# Development Guide

Guide for setting up a local development environment and contributing to the Web API Example.

## Local Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Setting Up the Environment

```bash
# Clone the repository
git clone https://github.com/your-org/mpower-custom-app-example.git
cd mpower-custom-app-example

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install pytest ruff mypy
```

### Running Locally

The application can run locally for development and testing:

```bash
# Navigate to the mlinux-7 source (compatible with Python 3.8+)
cd mlinux-7/src

# Create a local config file
cat > config.json << 'EOF'
{
  "server": {
    "host": "127.0.0.1",
    "port": 8080,
    "debug": true
  },
  "database": {
    "path": "./dev_data.db"
  },
  "log": {
    "level": "DEBUG",
    "use_syslog": false
  }
}
EOF

# Run the application
python -m webapi_example
```

The API will be available at `http://localhost:8080`.

## Running Tests

### Run All Tests

```bash
# From the repository root
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_server.py -v
```

### Run with Coverage

```bash
pip install pytest-cov
pytest tests/ -v --cov=mlinux-7/src/webapi_example --cov-report=term-missing
```

## Code Quality

### Linting

Use ruff for linting:

```bash
# Check for issues
ruff check mlinux-7/src tests

# Auto-fix issues
ruff check --fix mlinux-7/src tests
```

### Formatting

Use ruff for code formatting:

```bash
# Check formatting
ruff format --check mlinux-7/src tests

# Apply formatting
ruff format mlinux-7/src tests
```

### Type Checking

Use mypy for static type checking:

```bash
mypy mlinux-7/src --ignore-missing-imports
```

### Pre-Commit Checks

Run all checks before committing:

```bash
# Lint
ruff check mlinux-7/src tests

# Format
ruff format mlinux-7/src tests

# Type check
mypy mlinux-7/src --ignore-missing-imports

# Tests
pytest tests/ -v
```

## Project Structure

```
mpower-custom-app-example/
├── mlinux-6/                    # Python 3.5 compatible version
│   ├── src/
│   │   └── webapi_example/      # Application source code
│   ├── dist/                    # Deployment files
│   ├── build-tarball.sh         # Build script
│   └── pyproject.toml           # Python project config
│
├── mlinux-7/                    # Python 3.10 compatible version
│   ├── src/
│   │   └── webapi_example/      # Application source code
│   │       ├── __init__.py
│   │       ├── __main__.py      # Entry point
│   │       ├── server.py        # HTTP server and request handling
│   │       ├── database.py      # SQLite database operations
│   │       ├── config.py        # Configuration loading
│   │       └── logging_setup.py # Logging configuration
│   ├── dist/                    # Deployment files
│   │   ├── manifest.json        # App-manager manifest
│   │   ├── Install              # Installation script
│   │   ├── Start                # Start script
│   │   └── config/              # Default configuration
│   ├── build-tarball.sh         # Build script
│   └── pyproject.toml           # Python project config
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_server.py           # Server tests
│   └── test_database.py         # Database tests
│
├── docs/                        # Documentation
│   ├── index.md
│   ├── getting-started.md
│   ├── api-reference.md
│   ├── configuration.md
│   ├── deployment.md
│   └── development.md
│
└── .cursor/                     # Cursor AI rules
    └── rules/
```

### mLinux 6 vs mLinux 7

The project maintains two versions for compatibility:

| Version | Python | Target Gateway |
|---------|--------|----------------|
| mlinux-6 | 3.5 | Older gateways with mLinux 6.x |
| mlinux-7 | 3.10 | Current gateways with mLinux 7.x |

Key differences:
- **mlinux-6**: Uses older Python syntax (no f-strings in some places, no walrus operator)
- **mlinux-7**: Uses modern Python features (type hints, f-strings, etc.)

When making changes, update both versions to maintain feature parity.

## Adding New Endpoints

To add a new endpoint to the API:

### Step 1: Define the Handler Method

In `server.py`, add a handler method to the `RequestHandler` class:

```python
def handle_new_endpoint(self):
    """Handle GET /new-endpoint."""
    data = {"key": "value"}
    self.send_json_response(data)
```

### Step 2: Add Route

In the `do_GET` or `do_POST` method, add the route:

```python
def do_GET(self):
    if self.path == "/":
        self.handle_root()
    elif self.path == "/health":
        self.handle_health()
    elif self.path == "/new-endpoint":  # Add new route
        self.handle_new_endpoint()
    # ... rest of routes
```

### Step 3: Add Tests

Create tests for the new endpoint in `tests/test_server.py`:

```python
def test_new_endpoint(client):
    """Test GET /new-endpoint."""
    response = client.get("/new-endpoint")
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "value"
```

### Step 4: Update Documentation

Add the new endpoint to `docs/api-reference.md`.

## Cursor AI Development

This project includes Cursor AI rules in `.cursor/rules/` to assist with development:

- Code style guidelines
- Project-specific conventions
- Common patterns and practices

When using Cursor AI, these rules help maintain consistency with the project's coding standards.

## Building for Distribution

### Build Tarball

```bash
# For mLinux 7
cd mlinux-7
bash build-tarball.sh

# For mLinux 6
cd mlinux-6
bash build-tarball.sh
```

### Tarball Contents

The build script creates a tarball containing:

```
webapi_example/
├── manifest.json          # App-manager configuration
├── Install                # Installation script
├── Start                  # Start script  
├── config/
│   └── config.json        # Default configuration
└── src/
    └── webapi_example/    # Python source code
```

## Contributing

### Workflow

1. Create a feature branch
2. Make changes
3. Run all quality checks
4. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Write docstrings for public functions
- Keep functions focused and small

### Testing Requirements

- All new features must have tests
- Maintain or improve test coverage
- Tests must pass before merging

### Documentation

- Update API reference for new endpoints
- Update configuration docs for new options
- Keep README and guides current
