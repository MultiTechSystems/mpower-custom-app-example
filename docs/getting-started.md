# Getting Started

This guide walks you through building and deploying the Web API Example application to your MultiTech gateway.

## Prerequisites

### Gateway Requirements

- MultiTech Conduit gateway with mPower firmware
- mLinux 6.x or mLinux 7.x
- SSH access to the gateway
- `python3-sqlite3` package (see [Deployment Guide](deployment.md) for installation)

### Development Requirements

- Bash shell
- tar utility
- SSH/SCP client

## Building the Tarball

Choose the appropriate directory for your gateway's mLinux version:

```bash
# For mLinux 7 (recommended)
cd mlinux-7
bash build-tarball.sh

# For mLinux 6 (older gateways)
cd mlinux-6
bash build-tarball.sh
```

This creates a tarball named `webapi_example-{version}-mlinux{6|7}.tar.gz`.

## Deploying to Gateway

### Quick Deploy via SCP

For the fastest deployment during development:

```bash
# Upload the tarball
scp webapi_example-*.tar.gz admin@{GATEWAY_IP}:/tmp/

# SSH into gateway and extract
ssh admin@{GATEWAY_IP}
cd /var/config/app
sudo tar xzf /tmp/webapi_example-*.tar.gz
sudo app-manager --command start webapi_example
```

### Deploy via App-Manager API

For production deployment, use the app-manager REST API. See the [Deployment Guide](deployment.md) for complete instructions.

## Testing the API

Once the application is running, test the endpoints:

### Health Check

```bash
curl http://{GATEWAY_IP}:5000/health
```

Expected response:

```json
{"status": "ok"}
```

### Welcome Message

```bash
curl http://{GATEWAY_IP}:5000/
```

Expected response:

```json
{"message": "Welcome to the Web API Example"}
```

### Create a User

```bash
curl -X POST http://{GATEWAY_IP}:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "secret123"}'
```

Expected response:

```json
{"message": "User created", "username": "testuser"}
```

### List Users

```bash
curl http://{GATEWAY_IP}:5000/users
```

Expected response:

```json
{"users": [{"id": 1, "username": "testuser"}]}
```

### Create a Message

```bash
curl -X POST http://{GATEWAY_IP}:5000/messages \
  -H "Content-Type: application/json" \
  -d '{"deveui": "0011223344556677", "deviceName": "Sensor1", "data": "SGVsbG8=", "size": 5, "sqn": 1}'
```

Expected response:

```json
{"message": "Message created"}
```

### List Messages

```bash
curl http://{GATEWAY_IP}:5000/messages
```

## Verifying Application Status

Check that the application is running via app-manager:

```bash
ssh admin@{GATEWAY_IP} "app-manager --command status"
```

You should see `webapi_example` listed with status `running`.

To view application logs:

```bash
ssh admin@{GATEWAY_IP} "grep webapi /var/log/messages | tail -20"
```

## Next Steps

- [API Reference](api-reference.md) - Complete endpoint documentation
- [Configuration](configuration.md) - Customize application settings
- [Deployment](deployment.md) - Production deployment guide
- [Development](development.md) - Local development setup
