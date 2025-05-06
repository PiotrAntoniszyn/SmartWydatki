# SmartWydatki API Documentation

## Overview

The SmartWydatki API allows developers to interact with the SmartWydatki expense tracking application programmatically. The API follows RESTful principles and uses JSON for data exchange.

## Authentication

All API endpoints require authentication using a JSON Web Token (JWT). To authenticate, include the token in the Authorization header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

You can obtain a token by authenticating with Supabase using the email/password authentication flow.

## Base URL

```
https://api.smartwydatki.com/
```

In development, the API is available at:

```
http://localhost:5000/
```

## Content Type

All requests and responses use JSON format. Set the Content-Type header in your requests:

```
Content-Type: application/json
```

## API Endpoints

### Categories

- [Categories API Documentation](./api/categories.md) (TBD)
  - `GET /categories` - Get all categories
  - `POST /categories` - Create a new category
  - `PUT /categories/{id}` - Update a category
  - `DELETE /categories/{id}` - Delete a category

### Expenses

- [Expenses API Documentation](./api/expenses.md) (TBD)
  - `GET /expenses` - Get all expenses with pagination
  - `POST /expenses` - Create a new expense
  - `GET /expenses/{id}` - Get a specific expense
  - `PUT /expenses/{id}` - Update an expense
  - `DELETE /expenses/{id}` - Delete an expense

### AI Features

- [AI Tips API Documentation](./api/ai_tips.md)
  - `GET /ai/tips` - Get AI-generated financial tips based on expense data

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- `200 OK` - The request was successful
- `400 Bad Request` - The request was invalid or cannot be served
- `401 Unauthorized` - Authentication is required or failed
- `404 Not Found` - The requested resource does not exist
- `409 Conflict` - The request conflicts with the current state of the server
- `500 Internal Server Error` - An error occurred on the server
- `502 Bad Gateway` - External service error (e.g., AI service)

Error responses include a JSON object with error details:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

## Rate Limiting

API requests are limited to 100 requests per minute per user. If you exceed this limit, the API will return a 429 Too Many Requests response.

## Version History

- v1.0.0 - Initial API release with categories, expenses, and AI tips endpoints 