# User API

## Summary
This module provides RESTful API endpoints for managing User resources using Django REST Framework. It supports listing all users, creating new users, retrieving, updating, and deleting individual user records with authentication enforcement for update/delete operations.

## Classes

- **UserListCreateAPIView**: Handles GET (list all users) and POST (create new user) operations. No authentication required for listing or creation.
- **UserDetailAPIView**: Handles GET (retrieve), PUT (update), and DELETE (remove) operations for a specific user. Requires authenticated users via `IsAuthenticated` permission.

## Functions
None

## API Usage

### Endpoints

- `GET /users/` — List all users
- `POST /users/` — Create a new user
- `GET /users/{pk}/` — Retrieve a specific user by ID
- `PUT /users/{pk}/` — Update a specific user by ID
- `DELETE /users/{pk}/` — Delete a specific user by ID

### Sample Requests and Responses

#### POST /users/ — Create User
**Request Body (JSON):**
```json
{
  "username": "johndoe",
  "email": "john@example.com"
}
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com"
}
```

**Error Response (400 Bad Request):**
```json
{
  "username": ["This field may not be blank."],
  "email": ["Enter a valid email address."]
}
```

#### GET /users/ — List All Users
**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  },
  {
    "id": 2,
    "username": "janedoe",
    "email": "jane@example.com"
  }
]
```

#### GET /users/1/ — Retrieve User
**Success Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

#### PUT /users/1/ — Update User
**Request Body (JSON):**
```json
{
  "username": "johndoe_updated",
  "email": "john.updated@example.com"
}
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe_updated",
  "email": "john.updated@example.com"
}
```

**Error Response (400 Bad Request):**
```json
{
  "email": ["Enter a valid email address."]
}
```

#### DELETE /users/1/ — Delete User
**Success Response (204 No Content):**
No content returned.

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

### curl Examples

**Create a user:**
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe", "email": "john@example.com"}'
```

**List all users:**
```bash
curl http://localhost:8000/users/
```

**Retrieve a specific user:**
```bash
curl http://localhost:8000/users/1/
```

**Update a user:**
```bash
curl -X PUT http://localhost:8000/users/1/ \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe_updated", "email": "john.updated@example.com"}'
```

**Delete a user:**
```bash
curl -X DELETE http://localhost:8000/users/1/