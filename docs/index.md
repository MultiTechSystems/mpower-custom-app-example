# mPower Custom App Example - Web API

A complete example of a custom application for MultiTech mPower gateways, demonstrating REST API development with SQLite persistence using only Python standard library.

## Features

- **REST API** - HTTP server using Python's built-in `http.server` module
- **SQLite Database** - Persistent storage for users and LoRa messages
- **App-Manager Integration** - Full lifecycle management via mPower's app-manager
- **Syslog Support** - Native syslog logging for gateway integration
- **Multi-Platform** - Supports both mLinux 6 (Python 3.5) and mLinux 7 (Python 3.10)

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](getting-started.md) | Quick start guide for building and deploying |
| [API Reference](api-reference.md) | Complete REST API documentation |
| [Configuration](configuration.md) | Configuration file options |
| [Deployment](deployment.md) | Detailed gateway deployment instructions |
| [Development](development.md) | Local development and testing guide |

## Quick Start

```bash
# Build the tarball for mLinux 7
cd mlinux-7
bash build-tarball.sh

# Upload to gateway
scp webapi_example-*.tar.gz admin@{GATEWAY_IP}:/tmp/

# Install via app-manager API (see deployment guide for full steps)
```

## Requirements

### Gateway Requirements

- MultiTech Conduit gateway with mPower firmware
- mLinux 6.x or mLinux 7.x
- `python3-sqlite3` package installed

### Development Requirements

- Python 3.8+ (for local development)
- pytest (for running tests)
- ruff (for linting and formatting)

## License

MIT License - See LICENSE file for details.
