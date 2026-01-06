# mPower Custom App Example

A complete example of building a custom Python application for MultiTech Conduit gateways running mPower (mLinux).

This project demonstrates best practices for developing custom applications that integrate with the mPower app-manager system, including:

- Proper project structure for mLinux 6 (Python 3.8) and mLinux 7 (Python 3.10)
- Dataclass-based configuration (no pydantic dependency)
- Status writer for app-manager integration
- Syslog logging for mLinux
- Build scripts for creating deployment tarballs
- Cursor rules for AI-assisted development

## Features

- Simple REST API using Flask
- SQLite database for data persistence
- User management endpoints (CRUD)
- LoRa message storage endpoints
- Health check endpoint
- Automatic status reporting to app-manager

## Project Structure

```
mpower-custom-app-example/
├── .cursor/rules/           # Cursor AI development rules
├── mlinux-6/               # Python 3.8 compatible version
│   ├── src/webapi_example/
│   ├── dist/               # Deployment files
│   ├── build-tarball.sh
│   └── pyproject.toml
├── mlinux-7/               # Python 3.10 compatible version
│   ├── src/webapi_example/
│   ├── dist/               # Deployment files
│   ├── build-tarball.sh
│   └── pyproject.toml
├── tests/                  # Test suite
├── config/                 # Example configurations
└── docs/                   # Documentation
```

## Quick Start

### Build Tarball

```bash
# For mLinux 7 (Python 3.10)
cd mlinux-7
bash build-tarball.sh

# For mLinux 6 (Python 3.8)
cd mlinux-6
bash build-tarball.sh
```

### Deploy to Gateway

See the deployment instructions in `.cursor/rules/multitech-gateway.mdc` or use:

```bash
# Upload tarball
scp mlinux-7/webapi_example-1.0.0-mlinux7.tar.gz admin@{GATEWAY_IP}:/tmp/

# Extract on gateway
ssh admin@{GATEWAY_IP} "cd /var/config/app/webapi_example && tar -xzf /tmp/webapi_example-1.0.0-mlinux7.tar.gz --overwrite"

# Start via API (after logging in)
curl -k -b cookies.txt -X POST "https://{GATEWAY_IP}/api/customApps/{APP_ID}/start" -H "Content-Length: 0"
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/health` | GET | Health check |
| `/users` | GET | List all users |
| `/users` | POST | Create a user |
| `/users/<username>` | GET | Get a user |
| `/users/<username>` | DELETE | Delete a user |
| `/messages` | GET | List all messages |
| `/messages` | POST | Create a message |
| `/messages/<deveui>` | GET | Get messages by device |

## Configuration

Create a `config/config.json` file:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  },
  "database": {
    "path": "data.db"
  },
  "log": {
    "level": "INFO",
    "use_syslog": true
  }
}
```

## Development

### Run Tests

```bash
pip install pytest flask
pytest tests/ -v
```

### Code Quality

```bash
pip install ruff mypy
ruff check mlinux-7/src tests
ruff format mlinux-7/src tests
mypy mlinux-7/src --ignore-missing-imports
```

## Cursor AI Development

This project includes Cursor rules in `.cursor/rules/` for AI-assisted development:

- `multitech-gateway.mdc` - Gateway deployment and app-manager integration
- `python-coding-standards.mdc` - Python coding standards and CI/CD
- `testing-standards.mdc` - Testing requirements with pytest

## License

Apache License 2.0
