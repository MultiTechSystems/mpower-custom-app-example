# Deployment Guide

Comprehensive instructions for deploying the Web API Example to MultiTech mPower gateways.

## Prerequisites

### Gateway Requirements

- MultiTech Conduit gateway with mPower firmware
- mLinux 6.x or mLinux 7.x
- SSH/SCP access enabled
- Admin API access (for API-based installation)

### Required Package: python3-sqlite3

The application requires the `python3-sqlite3` package, which is not installed by default on mLinux.

#### Installing on mLinux 7

```bash
# Download the IPK package
wget https://multitech.net/mlinux/feeds/7.1.0/cortexa7t2hf-neon/python3-sqlite3_3.10.15-r0.0_cortexa7t2hf-neon.ipk

# Copy to gateway
scp python3-sqlite3_3.10.15-r0.0_cortexa7t2hf-neon.ipk admin@{GATEWAY_IP}:/tmp/

# Install on gateway
ssh admin@{GATEWAY_IP} "sudo opkg install /tmp/python3-sqlite3_3.10.15-r0.0_cortexa7t2hf-neon.ipk"
```

#### Installing on mLinux 6

```bash
# Download the IPK package for mLinux 6
wget https://multitech.net/mlinux/feeds/6.0/cortexa7t2hf-neon/python3-sqlite3_3.5.3-r0.0_cortexa7t2hf-neon.ipk

# Copy to gateway
scp python3-sqlite3_3.5.3-r0.0_cortexa7t2hf-neon.ipk admin@{GATEWAY_IP}:/tmp/

# Install on gateway
ssh admin@{GATEWAY_IP} "sudo opkg install /tmp/python3-sqlite3_3.5.3-r0.0_cortexa7t2hf-neon.ipk"
```

## Building the Tarball

Choose the directory matching your gateway's mLinux version:

```bash
# For mLinux 7 (Python 3.10)
cd mlinux-7
bash build-tarball.sh

# For mLinux 6 (Python 3.5)
cd mlinux-6
bash build-tarball.sh
```

The script creates a tarball: `webapi_example-{version}-mlinux{6|7}.tar.gz`

## Installation Methods

### Method 1: Quick Deploy via SCP (Development)

The fastest method for development and testing:

```bash
# Upload the tarball
scp webapi_example-*.tar.gz admin@{GATEWAY_IP}:/tmp/

# SSH into gateway
ssh admin@{GATEWAY_IP}

# Extract to app directory
cd /var/config/app
sudo tar xzf /tmp/webapi_example-*.tar.gz

# Start the application
sudo app-manager --command start webapi_example

# Verify it's running
app-manager --command status
```

### Method 2: App-Manager REST API (Production)

For production deployments, use the gateway's REST API for full lifecycle management.

#### Step 1: Login and Get Session Cookie

```bash
curl -k -c cookies.txt -X POST \
  "https://{GATEWAY_IP}/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "{ADMIN_PASSWORD}"}'
```

#### Step 2: Pre-Upload Notification

```bash
curl -k -b cookies.txt -X POST \
  "https://{GATEWAY_IP}/api/file/preupload" \
  -H "Content-Type: application/json" \
  -d '{"path": "/tmp/webapi_example.tar.gz"}'
```

#### Step 3: Upload Tarball

```bash
curl -k -b cookies.txt -X POST \
  "https://{GATEWAY_IP}/api/file/upload" \
  -F "file=@webapi_example-1.0.0-mlinux7.tar.gz;filename=webapi_example.tar.gz"
```

#### Step 4: Install Application

```bash
curl -k -b cookies.txt -X POST \
  "https://{GATEWAY_IP}/api/apps/install" \
  -H "Content-Type: application/json" \
  -d '{"file": "/tmp/webapi_example.tar.gz"}'
```

#### Step 5: Start Application

```bash
curl -k -b cookies.txt -X POST \
  "https://{GATEWAY_IP}/api/apps/webapi_example/start"
```

#### Step 6: Verify Status

```bash
curl -k -b cookies.txt \
  "https://{GATEWAY_IP}/api/apps/webapi_example/status"
```

## Updating an Existing Installation

### Via SCP (Quick Update)

```bash
# Upload new tarball
scp webapi_example-*.tar.gz admin@{GATEWAY_IP}:/tmp/

# SSH and update
ssh admin@{GATEWAY_IP}

# Stop the app
sudo app-manager --command stop webapi_example

# Extract new version (overwrites existing)
cd /var/config/app
sudo tar xzf /tmp/webapi_example-*.tar.gz

# Start the app
sudo app-manager --command start webapi_example
```

### Via API (Re-upload)

Follow the same API steps as initial installation. The install endpoint will update an existing application.

## Firewall Configuration

By default, port 5000 is not accessible from outside the gateway. To enable external access:

### Using mPower Web UI

1. Navigate to **Setup → Firewall**
2. Add a new rule allowing TCP port 5000
3. Save and apply changes

### Using iptables (Command Line)

```bash
ssh admin@{GATEWAY_IP}

# Allow incoming connections on port 5000
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT

# Save rules (persists across reboots)
sudo /etc/init.d/firewall save
```

## Application Management

### Start Application

```bash
ssh admin@{GATEWAY_IP} "sudo app-manager --command start webapi_example"
```

### Stop Application

```bash
ssh admin@{GATEWAY_IP} "sudo app-manager --command stop webapi_example"
```

### Restart Application

```bash
ssh admin@{GATEWAY_IP} "sudo app-manager --command restart webapi_example"
```

### Check Status

```bash
ssh admin@{GATEWAY_IP} "app-manager --command status"
```

### Enable Auto-Start

The application is configured to auto-start by default via `autoStart: true` in the manifest. To disable:

```bash
# Edit manifest.json
ssh admin@{GATEWAY_IP} "sudo vi /var/config/app/webapi_example/manifest.json"
# Change "autoStart": true to "autoStart": false
```

## Troubleshooting

### Check Application Logs

```bash
# View recent log entries
ssh admin@{GATEWAY_IP} "grep webapi /var/log/messages | tail -50"

# Follow logs in real-time
ssh admin@{GATEWAY_IP} "tail -f /var/log/messages | grep webapi"
```

### Check Application Status

```bash
ssh admin@{GATEWAY_IP} "app-manager --command status"
```

### Common Issues

#### Application Won't Start

1. **Missing python3-sqlite3 package**
   
   ```
   ModuleNotFoundError: No module named '_sqlite3'
   ```
   
   Solution: Install the python3-sqlite3 package (see Prerequisites).

2. **Port already in use**
   
   ```
   OSError: [Errno 98] Address already in use
   ```
   
   Solution: Change the port in config.json or stop the conflicting service.

3. **Permission denied on database**
   
   ```
   sqlite3.OperationalError: unable to open database file
   ```
   
   Solution: Ensure the database path is writable by the app user.

#### Cannot Connect to API

1. **Firewall blocking port 5000**
   
   Solution: Add firewall rule to allow port 5000 (see Firewall Configuration).

2. **Application not running**
   
   Solution: Start the application via app-manager.

3. **Wrong IP/port**
   
   Solution: Verify the gateway IP and check config.json for the configured port.

#### API Returns Errors

1. **500 Internal Server Error**
   
   Check logs for the specific error. Common causes:
   - Database corruption
   - Missing dependencies
   - Configuration errors

2. **404 Not Found**
   
   Verify the endpoint URL and HTTP method are correct.

### Reset Application State

To completely reset the application (including database):

```bash
ssh admin@{GATEWAY_IP}

# Stop the app
sudo app-manager --command stop webapi_example

# Remove database
sudo rm /var/config/app/webapi_example/data.db

# Start fresh
sudo app-manager --command start webapi_example
```

### Uninstall Application

```bash
ssh admin@{GATEWAY_IP}

# Stop the app
sudo app-manager --command stop webapi_example

# Remove app directory
sudo rm -rf /var/config/app/webapi_example
```
