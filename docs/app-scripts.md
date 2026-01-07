# Install and Start Script Requirements

This document describes the requirements for the `Install` and `Start` scripts that app-manager uses to manage custom applications on MultiTech mPower gateways.

## Overview

Custom applications on mPower gateways require two shell scripts:

| Script | Purpose |
|--------|---------|
| `Install` | Handles dependency installation/removal and post-install tasks |
| `Start` | Manages the application process lifecycle (start/stop/restart) |

Both scripts are called by `app-manager` during different phases of the application lifecycle.

## Install Script

The `Install` script is responsible for:
- Installing dependencies from bundled IPK packages
- Post-install tasks (firewall rules, directory creation, etc.)
- Cleanup during uninstallation

### Required Arguments

App-manager calls the Install script with one of these arguments:

| Argument | When Called | Purpose |
|----------|-------------|---------|
| `install` | During app installation | Install dependencies from `provisioning/` |
| `postinstall` | After installation | Firewall rules, create directories, etc. |
| `remove` | During app removal | Remove dependencies (usually skip shared packages) |
| `postremove` | After removal | Final cleanup |

### Template

```bash
#!/bin/bash
# Install script for {app_name}

OPKG_CMD_PREFIX="opkg install --force-depends ./provisioning/"
OPKG_CMD_PREFIX_R="opkg remove --force-depends "
MANIFEST="./provisioning/p_manifest.json"
NAME="Install"

function install_packages {
    logger -t Install "Installing {app_name} dependencies"
    
    if [ -f "$MANIFEST" ]; then
        JSONTXT=$(<./provisioning/p_manifest.json)
        PKGCNT=$(echo $JSONTXT | jsparser --count -p /pkgs 2>/dev/null)
        
        if [ -n "$PKGCNT" ] && [ "$PKGCNT" -gt 0 ]; then
            for ((i=0; i < PKGCNT; i++)); do
                PKG=$(echo $JSONTXT | jsparser --jsobj -p /pkgs/$i 2>/dev/null)
                PKGNM=$(echo $PKG | jsparser -p /FileName 2>/dev/null)
                PKGTYPE=$(echo $PKG | jsparser -p /type 2>/dev/null)
                
                if [ "$PKGTYPE" == "ipk" ] && [ -f "./provisioning/$PKGNM" ]; then
                    PKGCMD=$OPKG_CMD_PREFIX$PKGNM
                    echo "Executing: $PKGCMD"
                    logger -t Install "Executing: $PKGCMD"
                    eval $PKGCMD
                    if [ $? != 0 ]; then
                        echo "Command [$PKGCMD] failed with status $?"
                        logger -t Install "Command [$PKGCMD] failed with status $?"
                        exit $?
                    fi
                    logger -t Install "Command [$PKGCMD] succeeded"
                fi
            done
        fi
    else
        logger -t Install "No provisioning manifest found"
    fi
    
    logger -t Install "{app_name} dependencies installed successfully"
}

function post_install {
    echo "post_install"
    logger -t Install "{app_name} post-install starting"
    
    # Example: Open firewall port
    # PORT=5000
    # if ! iptables -C INPUT -p tcp --dport "$PORT" -j ACCEPT 2>/dev/null; then
    #     iptables -I INPUT -p tcp --dport "$PORT" -j ACCEPT
    #     logger -t Install "Firewall rule added for port $PORT"
    # fi
    
    logger -t Install "{app_name} post-install completed"
}

function remove_packages {
    logger -t Install "Removing {app_name} dependencies"
    
    # Usually skip removal of shared packages
    # Other apps might depend on them
    
    logger -t Install "{app_name} dependencies removal completed"
}

function post_remove {
    echo "post_remove"
    logger -t Install "{app_name} post-remove completed"
}

case "$1" in
    install)
        echo -n "Installing dependencies: "
        logger -t Install "Installing Dependencies: "
        install_packages
        echo "$NAME."
        ;;
    remove)
        echo -n "Removing Dependencies: "
        logger -t Install "Removing Dependencies: "
        remove_packages
        echo "$NAME."
        ;;
    postinstall)
        echo -n "Running app post install "
        logger -t Install "Running app post install "
        post_install
        echo "$NAME."
        ;;
    postremove)
        echo -n "Running app post remove "
        logger -t Install "Running app post remove "
        post_remove
        echo "$NAME."
        ;;
    *)
        N=$NAME
        echo "Usage: $N {install|remove|postinstall|postremove}" >&2
        exit 1
        ;;
esac

exit 0
```

### Provisioning Manifest

Create `provisioning/p_manifest.json` to list bundled IPK packages:

```json
{
  "pkgs": [
    {
      "FileName": "python3-sqlite3_3.10.15-r0.0_cortexa7t2hf-neon.ipk",
      "PkgName": "python3-sqlite3",
      "type": "ipk"
    }
  ]
}
```

Place IPK files in the `provisioning/` directory alongside the manifest.

## Start Script

The `Start` script manages the application process. App-manager calls this script to start, stop, restart, and reload the application.

### Critical Rule

**Never call app-manager from within the Start script.** App-manager calls this script directly - calling app-manager back causes lock issues and process hangs.

### Required Arguments

| Argument | Purpose |
|----------|---------|
| `start` | Start the application |
| `stop` | Stop the application |
| `restart` | Stop then start |
| `reload` | Reload configuration (usually restart) |

### Required Functions

| Function | Purpose |
|----------|---------|
| `SetEnv` | Set environment variables (PYTHONPATH, etc.) |
| `CreateAccess` | Create necessary directories |
| `ChangeUser` | Switch user if needed (usually root) |
| `Execute` | Start the process using start-stop-daemon |
| `Start` | Calls SetEnv → CreateAccess → ChangeUser → Execute |
| `Stop` | Stop the process using start-stop-daemon |
| `Restart` | Stop then Start |
| `Reload` | Restart to pick up new configuration |

### Environment Variables

App-manager provides these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `APP_DIR` | Application directory | `/var/config/app/{app_name}` |
| `CONFIG_DIR` | Config directory | `/var/config/app/{app_name}/config` |
| `APP_ID` | Numeric app ID | `1` |

### Template

```bash
#!/bin/bash

# Start script for {app_name} custom application
# This script is used by app-manager to start and stop the application

NAME="{app_name}"
DESC="{App Description}"
DAEMON="$APP_DIR/{app_name}/main.py"
PID="/var/run/{app_name}.pid"
LOG_FILE="/var/log/{app_name}.log"

function SetEnv {
    echo "SetEnv"
    
    # Set PYTHONPATH to include our application
    export PYTHONPATH="$APP_DIR:$PYTHONPATH"
    
    echo "CONFIG_DIR: $CONFIG_DIR"
    logger -t Start "CONFIG_DIR: $CONFIG_DIR"
    echo "APP_DIR: $APP_DIR"
    logger -t Start "APP_DIR: $APP_DIR"
    echo "APP_ID: $APP_ID"
    logger -t Start "APP_ID: $APP_ID"
}

function CreateAccess {
    echo "CreateAccess:"
    # Create log directory if needed
    mkdir -p /var/log
}

function ChangeUser {
    echo "ChangeUser:"
    # Run as root for now
}

function Execute {
    echo "Execute:"
    
    # Determine config file location
    if [ -f "$CONFIG_DIR/config.json" ]; then
        CONFIG_ARG="-c $CONFIG_DIR/config.json"
    elif [ -f "$APP_DIR/config/config.json" ]; then
        CONFIG_ARG="-c $APP_DIR/config/config.json"
    else
        echo "No config file found"
        logger -t Start "No config file found, using defaults"
        CONFIG_ARG=""
    fi
    
    # Start the application using Python module invocation
    /usr/sbin/start-stop-daemon --start --background \
        --pidfile "$PID" --make-pidfile \
        --startas /bin/bash -- -c "cd $APP_DIR && exec python3 -m {app_name} $CONFIG_ARG >> $LOG_FILE 2>&1"
    
    logger -t Start "{app_name} started with config: $CONFIG_ARG"
}

function Restart {
    echo "Restart:"
    Stop
    sleep 2
    Start
}

function Stop {
    echo "Stop:"
    /usr/sbin/start-stop-daemon --stop -p "$PID" --retry 60
    rm -f "$PID"
    logger -t Start "{app_name} stopped"
}

function Start {
    SetEnv
    CreateAccess
    ChangeUser
    Execute
}

# Notify the application process that new config files are available
function Reload {
    echo "Reload:"
    # Restart to pick up new configuration
    Restart
}

case "$1" in
    start)
        echo -n "Starting $DESC: "
        Start
        echo "$NAME."
        ;;
    stop)
        echo -n "Stopping $DESC: "
        Stop
        echo "$NAME."
        ;;
    restart)
        echo -n "Restarting $DESC: "
        Restart
        echo "$NAME."
        ;;
    reload)
        echo -n "Reloading $DESC: "
        Reload
        echo "$NAME."
        ;;
    *)
        N=$NAME
        echo "Usage: $N {start|stop|restart|reload}" >&2
        exit 1
        ;;
esac

exit 0
```

### Key Points

1. **Use start-stop-daemon**: Provides proper process management with PID file tracking
2. **Background execution**: Use `--background` flag to daemonize the process
3. **PID file**: Use `--pidfile` and `--make-pidfile` for process tracking
4. **Logging**: Redirect stdout/stderr to a log file
5. **Config resolution**: Check multiple locations for config file
6. **No app-manager calls**: Never call app-manager from this script

## Troubleshooting

### Lock Issues

If you see "Failed to acquire lock on file" errors:
1. Check if Start script calls app-manager (remove any such calls)
2. Remove stale lock: `rm /var/run/AppManager.lock`
3. Restart app-manager or reboot gateway

### App Shows FAILED Status

If app shows FAILED but process is running:
1. Verify status.json is being written with correct format: `{"pid": 12345, "AppInfo": "message"}`
2. Ensure `pid` is an integer, not a string
3. Check app-manager can read status.json

### Process Doesn't Start

1. Check logs: `grep {app_name} /var/log/messages | tail -50`
2. Verify Python path is correct
3. Check for syntax errors in Python code
4. Ensure dependencies are installed

## File Locations

| File | Location |
|------|----------|
| Install script | `/var/config/app/{app_name}/Install` |
| Start script | `/var/config/app/{app_name}/Start` |
| Config | `/var/config/app/{app_name}/config/config.json` |
| Status | `/var/config/app/{app_name}/status.json` |
| PID file | `/var/run/{app_name}.pid` |
| Log file | `/var/log/{app_name}.log` |
| Syslog | `/var/log/messages` |
