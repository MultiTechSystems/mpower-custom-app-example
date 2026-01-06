# API Reference

Complete documentation of the Web API Example REST endpoints.

**Base URL:** `http://{GATEWAY_IP}:5000`

## Root Endpoints

### GET /

Returns a welcome message.

**Request:**

```bash
curl http://{GATEWAY_IP}:5000/
```

**Response:**

```json
{"message": "Welcome to the Web API Example"}
```

---

### GET /health

Health check endpoint for monitoring.

**Request:**

```bash
curl http://{GATEWAY_IP}:5000/health
```

**Response:**

```json
{"status": "ok"}
```

---

## User Endpoints

### GET /users

List all users in the database.

**Request:**

```bash
curl http://{GATEWAY_IP}:5000/users
```

**Response:**

```json
{
  "users": [
    {"id": 1, "username": "admin"},
    {"id": 2, "username": "operator"}
  ]
}
```

---

### GET /users/{username}

Get a specific user by username.

**Request:**

```bash
curl http://{GATEWAY_IP}:5000/users/admin
```

**Success Response (200):**

```json
{
  "user": {"id": 1, "username": "admin"}
}
```

**Error Response (404):**

```json
{"error": "User not found"}
```

---

### POST /users

Create a new user.

**Request:**

```bash
curl -X POST http://{GATEWAY_IP}:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret123"}'
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | Unique username |
| password | string | Yes | User password |

**Success Response (201):**

```json
{"message": "User created", "username": "admin"}
```

**Error Responses:**

Missing required fields (400):

```json
{"error": "Username and password required"}
```

User already exists (400):

```json
{"error": "User already exists"}
```

---

### DELETE /users/{username}

Delete a user by username.

**Request:**

```bash
curl -X DELETE http://{GATEWAY_IP}:5000/users/admin
```

**Success Response (200):**

```json
{"message": "User deleted"}
```

**Error Response (404):**

```json
{"error": "User not found"}
```

---

## Message Endpoints

### GET /messages

List all LoRa messages, ordered by newest first.

**Request:**

```bash
curl http://{GATEWAY_IP}:5000/messages
```

**Response:**

```json
{
  "messages": [
    {
      "id": 2,
      "deviceName": "Sensor2",
      "deveui": "AABBCCDDEEFF0011",
      "data": "V29ybGQ=",
      "size": 5,
      "sqn": 2,
      "timestamp": "2024-01-15T10:30:00"
    },
    {
      "id": 1,
      "deviceName": "Sensor1",
      "deveui": "0011223344556677",
      "data": "SGVsbG8=",
      "size": 5,
      "sqn": 1,
      "timestamp": "2024-01-15T10:00:00"
    }
  ]
}
```

---

### GET /messages/{deveui}

Get all messages from a specific device by its EUI.

**Request:**

```bash
curl http://{GATEWAY_IP}:5000/messages/0011223344556677
```

**Success Response (200):**

```json
{
  "messages": [
    {
      "id": 1,
      "deviceName": "Sensor1",
      "deveui": "0011223344556677",
      "data": "SGVsbG8=",
      "size": 5,
      "sqn": 1,
      "timestamp": "2024-01-15T10:00:00"
    }
  ]
}
```

**Error Response (404):**

```json
{"error": "No messages found"}
```

---

### POST /messages

Create a new LoRa message record.

**Request:**

```bash
curl -X POST http://{GATEWAY_IP}:5000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "deveui": "0011223344556677",
    "deviceName": "Sensor1",
    "data": "SGVsbG8=",
    "size": 5,
    "sqn": 1
  }'
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| deveui | string | Yes | Device EUI (16 hex characters) |
| deviceName | string | No | Human-readable device name |
| data | string | No | Base64-encoded payload data |
| size | integer | No | Payload size in bytes |
| sqn | integer | No | Sequence number |

**Success Response (201):**

```json
{"message": "Message created"}
```

**Error Response (400):**

```json
{"error": "deveui is required"}
```

---

## Error Handling

All endpoints return errors in a consistent JSON format:

```json
{"error": "Error description"}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (invalid input) |
| 404 | Not Found |
| 405 | Method Not Allowed |
| 500 | Internal Server Error |

---

## Content Types

- All requests with a body should use `Content-Type: application/json`
- All responses are `application/json`
