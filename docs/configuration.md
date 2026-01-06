# Configuration

The Web API Example uses a JSON configuration file to control server settings, database location, and logging behavior.

## Configuration File

### File Structure

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

### Configuration Options

#### Server Section

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| host | string | "0.0.0.0" | IP address to bind to. Use "0.0.0.0" for all interfaces. |
| port | integer | 5000 | TCP port number for the HTTP server. |
| debug | boolean | false | Debug mode flag (reserved for future use). |

#### Database Section

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| path | string | "data.db" | Path to the SQLite database file. Relative paths are resolved from the application directory. |

#### Log Section

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| level | string | "INFO" | Logging level. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| use_syslog | boolean | true | Enable syslog output (recommended for mLinux). |

## Configuration File Locations

The application searches for configuration files in the following order:

1. `/var/config/app/{app_name}/config/config.json` - Primary location on gateway
2. `./config/config.json` - Relative to application directory
3. `./config.json` - Application directory root

The first file found is used. If no configuration file exists, default values are applied.

## Environment Variables

| Variable | Description |
|----------|-------------|
| APP_DIR | Override the application directory path. Used by app-manager. |

## Configuration Examples

### Production Configuration (Gateway)

Typical configuration for deployment on a MultiTech gateway:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  },
  "database": {
    "path": "/var/config/app/webapi_example/data.db"
  },
  "log": {
    "level": "INFO",
    "use_syslog": true
  }
}
```

### Development Configuration (Local)

Configuration for local development and testing:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8080,
    "debug": true
  },
  "database": {
    "path": "./test_data.db"
  },
  "log": {
    "level": "DEBUG",
    "use_syslog": false
  }
}
```

### Alternative Port Configuration

To run the API on a different port (e.g., to avoid conflicts):

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
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

## Default Values

If a configuration option is not specified, these defaults are used:

| Section | Option | Default |
|---------|--------|---------|
| server | host | "0.0.0.0" |
| server | port | 5000 |
| server | debug | false |
| database | path | "data.db" |
| log | level | "INFO" |
| log | use_syslog | true |

## Applying Configuration Changes

Configuration is read at application startup. To apply changes:

1. Edit the configuration file
2. Restart the application:

```bash
ssh admin@{GATEWAY_IP} "app-manager --command restart webapi_example"
```

## Validating Configuration

The application will log configuration errors at startup. Check the logs if the application fails to start:

```bash
ssh admin@{GATEWAY_IP} "grep webapi /var/log/messages | tail -20"
```

Common configuration errors:

- Invalid JSON syntax
- Invalid port number (must be 1-65535)
- Invalid log level (must be DEBUG, INFO, WARNING, ERROR, or CRITICAL)
- Database path not writable
