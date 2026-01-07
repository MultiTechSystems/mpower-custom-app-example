# Deployment Guide

Comprehensive instructions for deploying the Web API Example to MultiTech mPower gateways.

## Prerequisites

### Gateway Requirements

- MultiTech Conduit gateway with mPower firmware
- mLinux 6.x or mLinux 7.x
- SSH/SCP access enabled
- Admin API access (for API-based installation)
- Custom apps enabled (see [Enabling Custom Apps](#enabling-custom-apps))

### Required Package: python3-sqlite3

The application requires the `python3-sqlite3` package, which is not installed by default on mLinux. This is bundled in the `provisioning/` directory and installed automatically during app installation.

## Building the Tarball

Choose the directory matching your gateway's mLinux version:

```bash
# For mLinux 7 (Python 3.10)
cd mlinux-7
bash build-tarball.sh

# For mLinux 6 (Python 3.8)
cd mlinux-6
bash build-tarball.sh
```

The script creates a tarball: `webapi_example-{version}-mlinux{6|7}.tar.gz`

## Enabling Custom Apps

Before installing custom apps, ensure they are enabled on the gateway:

```bash
# Login and get session cookie
curl -k -s -c cookies.txt -X POST "https://{GATEWAY_IP}/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "{ADMIN_PASSWORD}"}'

# Check current config
curl -k -s -b cookies.txt "https://{GATEWAY_IP}/api/customAppsConfig"

# Enable custom apps
curl -k -s -b cookies.txt -X PUT "https://{GATEWAY_IP}/api/customAppsConfig" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "allowed": true}'

# Save configuration
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/command/save" \
  -H "Content-Length: 0"
```

## Installation via REST API (Recommended)

Use the gateway's REST API for full lifecycle management.

### Step 1: Login and Get Session Cookie

```bash
curl -k -s -c cookies.txt -X POST "https://{GATEWAY_IP}/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "{ADMIN_PASSWORD}"}'
```

### Step 2: Pre-Upload Notification

```bash
FILESIZE=$(stat -c%s webapi_example-1.0.0-mlinux7.tar.gz)
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/command/app_pre_upload" \
  -H "Content-Type: application/json" \
  -d "{\"info\":{\"fileName\":\"webapi_example-1.0.0-mlinux7.tar.gz\",\"fileSize\":$FILESIZE}}"
```

### Step 3: Upload Tarball

```bash
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/command/app_upload" \
  -F "archivo=@webapi_example-1.0.0-mlinux7.tar.gz;filename=webapi_example-1.0.0-mlinux7.tar.gz;type=application/x-gzip"
```

### Step 4: Install Application

The `appId` must be numeric (e.g., "1", "2"). Use "1" for the first app.

```bash
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/command/app_install" \
  -H "Content-Type: application/json" \
  -d '{"info":{"appId":"1","appFile":"webapi_example-1.0.0-mlinux7.tar.gz"}}'
```

### Step 5: Start Application

```bash
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/customApps/1/start" \
  -H "Content-Length: 0"
```

### Step 6: Verify Status

```bash
curl -k -s -b cookies.txt "https://{GATEWAY_IP}/api/customApps"
```

Expected response when running:

```json
{
  "code": 200,
  "result": [
    {
      "_id": "1",
      "name": "webapi_example",
      "status": "RUNNING",
      "info": "Running on 0.0.0.0:5000 @ 12:34:56",
      "pids": [{"pid": 1234, "exist": true}],
      "version": "1.0.0"
    }
  ],
  "status": "success"
}
```

## Updating an Existing Installation

### Via API

```bash
# Stop the app
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/customApps/1/stop" \
  -H "Content-Length: 0"

# Upload and install new version (same steps as initial install)
# ...

# Start the app
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/customApps/1/start" \
  -H "Content-Length: 0"
```

### Via SSH (Quick Update)

```bash
# Upload new tarball
scp webapi_example-*.tar.gz admin@{GATEWAY_IP}:/tmp/

# Stop, extract, start
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/customApps/1/stop" -H "Content-Length: 0"

ssh admin@{GATEWAY_IP} "cd /var/config/app/webapi_example && sudo tar xzf /tmp/webapi_example-*.tar.gz"

curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/customApps/1/start" -H "Content-Length: 0"
```

## Firewall Configuration

The Install script automatically opens port 5000 during installation using the mPower API. If you need to manually configure:

### Using mPower Web UI

1. Navigate to **Setup → Firewall**
2. Add a new rule allowing TCP port 5000
3. Save and apply changes

### Using mPower REST API (Recommended)

Create firewall rules programmatically. Rules require the `__v` version field (use `2` for current mLinux 7).

```bash
# Login first
curl -k -s -c cookies.txt -X POST "https://{GATEWAY_IP}/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "{ADMIN_PASSWORD}"}'

# Create INPUT rule to allow TCP port 5000
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/filters" \
  -H "Content-Type: application/json" \
  -d '{
    "__v": 2,
    "name": "webapi_example_port_5000",
    "description": "Allow inbound TCP to webapi_example port 5000",
    "enabled": true,
    "chain": "INPUT",
    "target": "ACCEPT",
    "protocol": "TCP",
    "srcAddr": "ANY",
    "srcMask": "",
    "srcPort": "ANY",
    "dstAddr": "ANY",
    "dstMask": "",
    "dstPort": "5000",
    "srcInterface": "ANY",
    "dstInterface": "ANY",
    "srcSpecInterface": "",
    "dstSpecInterface": "",
    "srcMac": "ANY"
  }'

# IMPORTANT: Save AND apply to activate the iptables rules
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/command/save_apply" \
  -H "Content-Length: 0"
```

**Important Notes**:
- The `__v` field is required - without it the API returns "Rule version is not defined"
- Use `/api/command/save_apply` (not just `/api/command/save`) to both persist AND activate the firewall rules
- `/api/command/save` alone only writes to config - rules won't be active until `save_apply` or reboot
- From localhost (127.0.0.1), API requests work without authentication

### Delete Firewall Rule

```bash
curl -k -s -b cookies.txt -X DELETE "https://{GATEWAY_IP}/api/filters/webapi_example_port_5000"
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/command/save_apply" -H "Content-Length: 0"
```

### Using iptables (Command Line)

```bash
ssh admin@{GATEWAY_IP}

# Allow incoming connections on port 5000
sudo iptables -I INPUT -p tcp --dport 5000 -j ACCEPT

# Save rules (persists across reboots)
sudo /etc/init.d/firewall save
```

Note: Rules added via iptables directly won't appear in `/api/filters` or the web UI.

## Application Management

### Start Application

```bash
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/customApps/1/start" \
  -H "Content-Length: 0"
```

### Stop Application

```bash
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/customApps/1/stop" \
  -H "Content-Length: 0"
```

### Check Status

```bash
curl -k -s -b cookies.txt "https://{GATEWAY_IP}/api/customApps"
```

### View Logs

```bash
# Syslog entries
ssh admin@{GATEWAY_IP} "grep webapi /var/log/messages | tail -50"

# Application log file
ssh admin@{GATEWAY_IP} "cat /var/log/webapi-example.log"
```

### View status.json

```bash
ssh admin@{GATEWAY_IP} "cat /var/config/app/webapi_example/status.json"
```

## Troubleshooting

### Check Application Logs

```bash
# View syslog entries
ssh admin@{GATEWAY_IP} "grep webapi /var/log/messages | tail -50"

# View application log
ssh admin@{GATEWAY_IP} "cat /var/log/webapi-example.log"
```

### Common Issues

#### Custom Apps Disabled

```
{"code": 400, "error": "Custom applications are disabled", "status": "fail"}
```

Solution: Enable custom apps via API (see [Enabling Custom Apps](#enabling-custom-apps)).

#### Application Shows FAILED Status

If the app shows FAILED but the process is running:
- Check that status.json is being written correctly
- Verify the `pid` field is an integer (not a string)
- Check logs for errors

#### App-Manager Lock Issues

```
Failed to acquire lock on file
```

Solution:
1. Check if Start script is calling app-manager (it should NOT)
2. Remove stale lock: `ssh admin@{GATEWAY_IP} "sudo rm /var/run/AppManager.lock"`
3. Reboot gateway if issue persists

#### Missing python3-sqlite3 Package

```
ModuleNotFoundError: No module named '_sqlite3'
```

Solution: The package should be installed automatically from provisioning. If not:

```bash
ssh admin@{GATEWAY_IP} "sudo opkg install /var/config/app/webapi_example/provisioning/python3-sqlite3_*.ipk"
```

#### Port Already in Use

```
OSError: [Errno 98] Address already in use
```

Solution: Change the port in config.json or stop the conflicting service.

#### Cannot Connect to API

1. **Firewall blocking port 5000** - Add firewall rule (see Firewall Configuration)
2. **Application not running** - Start the application
3. **Wrong IP/port** - Verify gateway IP and configured port

### Reset Application State

To completely reset the application (including database):

```bash
# Stop the app
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/customApps/1/stop" \
  -H "Content-Length: 0"

# Remove database
ssh admin@{GATEWAY_IP} "sudo rm /var/config/app/webapi_example/data.db"

# Start fresh
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/customApps/1/start" \
  -H "Content-Length: 0"
```

### Uninstall Application

```bash
# Stop the app
curl -k -s -b cookies.txt -X POST "https://{GATEWAY_IP}/api/customApps/1/stop" \
  -H "Content-Length: 0"

# Delete via API
curl -k -s -b cookies.txt -X DELETE "https://{GATEWAY_IP}/api/customApps/1"
```

## Related Documentation

- [Install and Start Script Requirements](app-scripts.md)
- [API Reference](api-reference.md)
- [Configuration Guide](configuration.md)
