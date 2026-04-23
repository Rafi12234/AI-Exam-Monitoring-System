# API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication
Currently no authentication required (for testing). In production, implement JWT tokens.

---

## Endpoints

### 1. Get All Flagged Students

**Endpoint**: `GET /api/flagged_students`

**Description**: Retrieve list of all flagged students

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "student_id": "STU_0001",
      "offenses_count": 5,
      "flagged_at": "2024-04-23T10:30:00",
      "status": "active"
    }
  ]
}
```

**Status Codes**:
- `200`: Success
- `500`: Server error

---

### 2. Get Student Offenses

**Endpoint**: `GET /api/students/<student_id>/offenses`

**Description**: Retrieve all offenses for a specific student

**Path Parameters**:
- `student_id` (string, required): Student ID (e.g., "STU_0001")

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "student_id": "STU_0001",
      "behavior_type": "back",
      "timestamp": "2024-04-23T10:30:00"
    }
  ]
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad request
- `500`: Server error

---

### 3. Log Offense

**Endpoint**: `POST /api/log_offense`

**Description**: Log a new offense for a student

**Request Body**:
```json
{
  "student_id": "STU_0001",
  "behavior_type": "back"
}
```

**Query Parameters**:
- `student_id` (string, required): Student ID
- `behavior_type` (string, optional): Type of behavior ('back', 'left', 'right', 'talking', 'unethical'). Default: 'unethical'

**Response**:
```json
{
  "status": "success",
  "offenses_count": 3,
  "flagged": true
}
```

**Status Codes**:
- `200`: Success
- `400`: Missing student_id
- `500`: Server error

**Example**:
```bash
curl -X POST http://localhost:5000/api/log_offense \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU_0001",
    "behavior_type": "back"
  }'
```

---

### 4. Reset Student

**Endpoint**: `POST /api/reset_student/<student_id>`

**Description**: Mark a student as no longer flagged (but keep offense history)

**Path Parameters**:
- `student_id` (string, required): Student ID

**Response**:
```json
{
  "status": "success",
  "message": "Student reset"
}
```

**Status Codes**:
- `200`: Success
- `500`: Server error

**Example**:
```bash
curl -X POST http://localhost:5000/api/reset_student/STU_0001
```

---

### 5. Clear Offenses

**Endpoint**: `POST /api/clear_offenses/<student_id>`

**Description**: Delete all offenses for a student and remove from flagged list

**Path Parameters**:
- `student_id` (string, required): Student ID

**Response**:
```json
{
  "status": "success",
  "message": "Offenses cleared"
}
```

**Status Codes**:
- `200`: Success
- `500`: Server error

**Example**:
```bash
curl -X POST http://localhost:5000/api/clear_offenses/STU_0001
```

---

### 6. Get Statistics

**Endpoint**: `GET /api/stats`

**Description**: Get overall system statistics

**Response**:
```json
{
  "status": "success",
  "data": {
    "flagged_students": 3,
    "students_with_offenses": 5,
    "total_offenses": 18
  }
}
```

**Status Codes**:
- `200`: Success
- `500`: Server error

---

### 7. Health Check

**Endpoint**: `GET /health`

**Description**: Check if backend is running

**Response**:
```json
{
  "status": "healthy"
}
```

**Status Codes**:
- `200`: Healthy

---

## WebSocket Events

### Connection
```javascript
// Client connects to server
socket.on('connect', () => {
  console.log('Connected to backend');
});
```

### Student Flagged (Server → Client)
```javascript
socket.on('student_flagged', (data) => {
  console.log({
    student_id: "STU_0001",
    offenses_count: 3,
    behavior_type: "back",
    timestamp: "2024-04-23T10:30:00"
  });
});
```

### Student Reset (Server → Client)
```javascript
socket.on('student_reset', (data) => {
  console.log({
    student_id: "STU_0001"
  });
});
```

### Student Cleared (Server → Client)
```javascript
socket.on('student_cleared', (data) => {
  console.log({
    student_id: "STU_0001"
  });
});
```

### Request Flagged Students (Client → Server)
```javascript
socket.emit('request_flagged_students', {});

socket.on('flagged_students_update', (data) => {
  console.log(data.data); // Array of flagged students
});
```

---

## Error Responses

All error responses follow this format:

```json
{
  "status": "error",
  "message": "Error description"
}
```

### Common Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 400 | Student ID required | Missing required parameter |
| 404 | Not found | Resource doesn't exist |
| 500 | Internal server error | Server-side issue |

---

## Usage Examples

### Python (using requests)
```python
import requests
import json

BASE_URL = 'http://localhost:5000'

# Get flagged students
response = requests.get(f'{BASE_URL}/api/flagged_students')
students = response.json()

# Log an offense
offense_data = {
    'student_id': 'STU_0001',
    'behavior_type': 'back'
}
response = requests.post(
    f'{BASE_URL}/api/log_offense',
    json=offense_data
)
print(response.json())

# Get statistics
response = requests.get(f'{BASE_URL}/api/stats')
stats = response.json()
print(stats)
```

### JavaScript (using Axios)
```javascript
import axios from 'axios';

const BASE_URL = 'http://localhost:5000';

// Get flagged students
axios.get(`${BASE_URL}/api/flagged_students`)
  .then(response => console.log(response.data))
  .catch(error => console.error(error));

// Log an offense
const offenseData = {
  student_id: 'STU_0001',
  behavior_type: 'back'
};
axios.post(`${BASE_URL}/api/log_offense`, offenseData)
  .then(response => console.log(response.data))
  .catch(error => console.error(error));
```

### cURL
```bash
# Get flagged students
curl http://localhost:5000/api/flagged_students

# Log an offense
curl -X POST http://localhost:5000/api/log_offense \
  -H "Content-Type: application/json" \
  -d '{"student_id":"STU_0001","behavior_type":"back"}'

# Get statistics
curl http://localhost:5000/api/stats

# Health check
curl http://localhost:5000/health
```

---

## Rate Limiting

Currently no rate limiting. In production, implement:
- 100 requests per minute per IP
- 1000 offenses per minute per camera

---

## Versioning

Current API version: v1 (no version prefix)

Future versions: `/api/v2/...`

---

## Changelog

### v1.0 (Current)
- Basic CRUD operations for students
- WebSocket real-time updates
- Statistics endpoint
- Health check endpoint

### Future v1.1
- Authentication and authorization
- Rate limiting
- Request logging
- Advanced filtering
- Pagination

---

For more information, see README.md and ARCHITECTURE.md
