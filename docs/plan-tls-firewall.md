# Plan: Add TLS Support and Automatic Firewall Configuration

## Overview

Add HTTPS/TLS support to the Web API Example and automatically open the firewall port during app installation.

## References

- **mPower REST API Documentation**: https://multitechsystems.github.io/mpower-api
- Use the firewall API endpoints to open ports during installation

## Features to Implement

### 1. TLS/HTTPS Support

Enable the HTTP server to use TLS encryption for secure communications.

### 2. Automatic Firewall Port Opening

The Install script should automatically open the configured port in the gateway firewall.

---

## Implementation Details

### 1. TLS Configuration

#### Update `models/config.py`

Add TLS configuration options to `ServerConfig`:

```python
@dataclass
class TlsConfig:
    """TLS/SSL configuration.
    
    Attributes:
        enabled: Enable TLS/HTTPS.
        cert_file: Path to certificate file (PEM format).
        key_file: Path to private key file (PEM format).
    """
    enabled: bool = False
    cert_file: str = "/var/config/server.pem"
    key_file: str = "/var/config/server.pem"
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TlsConfig":
        return cls(
            enabled=data.get("enabled", False),
            cert_file=data.get("cert_file", "/var/config/server.pem"),
            key_file=data.get("key_file", "/var/config/server.pem"),
        )

@dataclass
class ServerConfig:
    """HTTP server configuration."""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    tls: TlsConfig = field(default_factory=TlsConfig)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServerConfig":
        return cls(
            host=data.get("host", "0.0.0.0"),
            port=data.get("port", 5000),
            debug=data.get("debug", False),
            tls=TlsConfig.from_dict(data.get("tls", {})),
        )
```

#### Update `server.py`

Wrap the HTTP server socket with SSL context:

```python
import ssl

def run_server(config: AppConfig, db_path: str) -> None:
    """Run the HTTP server with optional TLS."""
    init_db(db_path)
    handler = create_handler(config, db_path)
    server = HTTPServer((config.server.host, config.server.port), handler)
    
    if config.server.tls.enabled:
        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(
            certfile=config.server.tls.cert_file,
            keyfile=config.server.tls.key_file,
        )
        server.socket = context.wrap_socket(server.socket, server_side=True)
        logger.info("TLS enabled with cert: %s", config.server.tls.cert_file)
    
    protocol = "https" if config.server.tls.enabled else "http"
    logger.info("Server running on %s://%s:%d", protocol, config.server.host, config.server.port)
    server.serve_forever()
```

#### Example TLS Configuration

Using the gateway's default certificate (`/var/config/server.pem`):

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false,
    "tls": {
      "enabled": true,
      "cert_file": "/var/config/server.pem",
      "key_file": "/var/config/server.pem"
    }
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

---

### 2. Certificate Options

#### Using Gateway's Default Certificate (Recommended)

The gateway has a combined PEM file at `/var/config/server.pem` that contains both the certificate and private key. This is the recommended approach as it uses the gateway's existing infrastructure.

```json
{
  "server": {
    "tls": {
      "enabled": true,
      "cert_file": "/var/config/server.pem",
      "key_file": "/var/config/server.pem"
    }
  }
}
```

#### Custom Certificate Script

For custom certificates, create `scripts/generate-cert.sh`:

```bash
#!/bin/bash
# Generate self-signed certificate for development/testing
set -e

CERT_DIR="${1:-./certs}"
DAYS="${2:-365}"
CN="${3:-localhost}"

mkdir -p "$CERT_DIR"

openssl req -x509 -newkey rsa:4096 \
    -keyout "$CERT_DIR/server.key" \
    -out "$CERT_DIR/server.crt" \
    -days "$DAYS" \
    -nodes \
    -subj "/CN=$CN"

# Create combined PEM file
cat "$CERT_DIR/server.crt" "$CERT_DIR/server.key" > "$CERT_DIR/server.pem"

chmod 600 "$CERT_DIR/server.key"
chmod 600 "$CERT_DIR/server.pem"
chmod 644 "$CERT_DIR/server.crt"

echo "Generated certificates in $CERT_DIR"
echo "  - server.crt (certificate)"
echo "  - server.key (private key)"
echo "  - server.pem (combined)"
```

---

### 3. Firewall Port Opening on Install

#### Create `dist/Install` Script

The Install script runs during app installation and should open the firewall port.

```bash
#!/bin/bash
# Install script for webapi_example
# This runs during app installation via app-manager

set -e

APP_DIR="${APP_DIR:-/var/config/app/webapi_example}"
CONFIG_FILE="$APP_DIR/config/config.json"

# Default port if config doesn't exist yet
DEFAULT_PORT=5000

# Extract port from config if it exists
if [ -f "$CONFIG_FILE" ]; then
    # Use Python to parse JSON (available on gateway)
    PORT=$(python3 -c "
import json
try:
    with open('$CONFIG_FILE') as f:
        config = json.load(f)
    print(config.get('server', {}).get('port', $DEFAULT_PORT))
except:
    print($DEFAULT_PORT)
" 2>/dev/null || echo $DEFAULT_PORT)
else
    PORT=$DEFAULT_PORT
fi

echo "webapi_example: Opening firewall port $PORT..."

# Method 1: Using iptables directly (works on all mLinux versions)
# Check if rule already exists
if ! iptables -C INPUT -p tcp --dport "$PORT" -j ACCEPT 2>/dev/null; then
    iptables -I INPUT -p tcp --dport "$PORT" -j ACCEPT
    echo "webapi_example: Firewall rule added for port $PORT"
else
    echo "webapi_example: Firewall rule for port $PORT already exists"
fi

# Save iptables rules to persist across reboots
if [ -x /etc/init.d/firewall ]; then
    /etc/init.d/firewall save 2>/dev/null || true
fi

echo "webapi_example: Installation complete"
exit 0
```

#### Alternative: Using mPower API for Firewall

For installations via the API, the firewall can also be configured via the REST API. 
See https://multitechsystems.github.io/mpower-api for firewall endpoints.

Example using the API (for external automation):

```bash
# Login first
curl -k -c cookies.txt -X POST "https://{GATEWAY_IP}/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Add firewall rule via API
curl -k -b cookies.txt -X POST "https://{GATEWAY_IP}/api/firewall/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "protocol": "tcp",
    "dport": "5000",
    "target": "ACCEPT",
    "description": "webapi_example API port"
  }'

# Save and apply firewall changes
curl -k -b cookies.txt -X POST "https://{GATEWAY_IP}/api/command/save" \
  -H "Content-Type: application/json" \
  -d '{"command": "firewall"}'
```

---

### 4. Firewall Port Removal on Uninstall

#### Create `dist/Remove` Script

```bash
#!/bin/bash
# Remove script for webapi_example
# This runs during app removal

set -e

APP_DIR="${APP_DIR:-/var/config/app/webapi_example}"
CONFIG_FILE="$APP_DIR/config/config.json"
DEFAULT_PORT=5000

# Extract port from config if it exists
if [ -f "$CONFIG_FILE" ]; then
    PORT=$(python3 -c "
import json
try:
    with open('$CONFIG_FILE') as f:
        config = json.load(f)
    print(config.get('server', {}).get('port', $DEFAULT_PORT))
except:
    print($DEFAULT_PORT)
" 2>/dev/null || echo $DEFAULT_PORT)
else
    PORT=$DEFAULT_PORT
fi

echo "webapi_example: Removing firewall port $PORT..."

# Remove iptables rule if it exists
if iptables -C INPUT -p tcp --dport "$PORT" -j ACCEPT 2>/dev/null; then
    iptables -D INPUT -p tcp --dport "$PORT" -j ACCEPT
    echo "webapi_example: Firewall rule removed for port $PORT"
fi

# Save iptables rules
if [ -x /etc/init.d/firewall ]; then
    /etc/init.d/firewall save 2>/dev/null || true
fi

echo "webapi_example: Removal complete"
exit 0
```

---

### 5. Update manifest.json

Add Remove script reference:

```json
{
  "AppName": "webapi_example",
  "AppVersion": "1.0.1",
  "AppDescription": "Web API Example - A simple REST API for mPower gateways",
  "AppVersionNotes": "Added TLS support and automatic firewall configuration"
}
```

---

### 6. Update Documentation

#### Update `docs/configuration.md`

Add TLS configuration section:

```markdown
### TLS/HTTPS Configuration

Enable encrypted connections:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| tls.enabled | boolean | false | Enable TLS/HTTPS |
| tls.cert_file | string | "/var/config/server.pem" | Path to certificate file (PEM) |
| tls.key_file | string | "/var/config/server.pem" | Path to private key file (PEM) |

#### Example with TLS (using gateway certificate)

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000,
    "tls": {
      "enabled": true,
      "cert_file": "/var/config/server.pem",
      "key_file": "/var/config/server.pem"
    }
  }
}
```

The gateway's default certificate at `/var/config/server.pem` contains both the certificate and private key.
```

#### Update `docs/deployment.md`

Add firewall section:

```markdown
## Firewall Configuration

The application automatically opens its configured port in the gateway firewall during installation.

### Automatic Configuration

When installed via app-manager, the Install script:
1. Reads the configured port from config.json (default: 5000)
2. Adds an iptables rule to allow incoming TCP connections
3. Saves the firewall rules to persist across reboots

### Manual Configuration

If needed, manually open the port:

```bash
# Add firewall rule
sudo iptables -I INPUT -p tcp --dport 5000 -j ACCEPT

# Save rules
sudo /etc/init.d/firewall save
```

### Via mPower API

See the [mPower API documentation](https://multitechsystems.github.io/mpower-api) for firewall endpoints.
```

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mlinux-7/src/webapi_example/models/config.py` | Modify | Add TlsConfig dataclass |
| `mlinux-7/src/webapi_example/server.py` | Modify | Add SSL context wrapping |
| `mlinux-7/dist/Install` | Create | Firewall port opening script |
| `mlinux-7/dist/Remove` | Create | Firewall port removal script |
| `mlinux-7/dist/Start` | Create | App start script |
| `mlinux-7/dist/manifest.json` | Create | App manifest |
| `mlinux-7/dist/status.json` | Create | Initial status file |
| `mlinux-7/dist/config/config.json` | Create | Default configuration |
| `scripts/generate-cert.sh` | Create | Self-signed cert generator |
| `docs/configuration.md` | Modify | Add TLS documentation |
| `docs/deployment.md` | Modify | Add firewall documentation |
| `mlinux-6/...` | Mirror | Same changes for mLinux 6 |
| `.cursor/rules/multitech-gateway.mdc` | Modify | Add mPower API reference |

---

## Testing Plan

### TLS Testing

1. Enable TLS in config.json with `/var/config/server.pem`
2. Start application
3. Test with curl: `curl -k https://{GATEWAY_IP}:5000/health`
4. Verify certificate is served correctly

### Firewall Testing

1. Before install: Verify port 5000 is blocked
2. Install app via app-manager
3. After install: Verify port 5000 is open (`iptables -L INPUT`)
4. Test API access from external host
5. Uninstall app
6. Verify firewall rule is removed

---

## Security Considerations

1. **Default Certificate**: Using `/var/config/server.pem` shares the gateway's certificate
2. **Self-Signed Certs**: Only for development; use proper CA-signed certs in production
3. **Firewall Rules**: Only open necessary ports; consider source IP restrictions
4. **TLS Version**: Use TLS 1.2+ (Python's ssl module defaults are secure)
