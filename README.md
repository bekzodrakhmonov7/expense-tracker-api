# Expense Tracker API

A RESTful API for tracking personal expenses, built with FastAPI and PostgreSQL. This project was inspired by [roadmap.sh - Expense Tracker API](https://roadmap.sh/projects/expense-tracker-api).

## Features

- User registration and authentication (JWT-based)
- Create, read, update, and delete expenses
- Filter expenses by date range
- Expense categorization
- PostgreSQL database with SQLModel ORM

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLModel** - ORM for Python
- **JWT** - Token-based authentication
- **Pydantic** - Data validation

## Prerequisites

- Python 3.10+
- PostgreSQL 13+

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd expense-tracker-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This project uses `psycopg2-binary` so you do not need a separate local `libpq` installation just to run the app.

### 4. Configure environment variables

Create a `.env` file in the project root with the following variables:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=expense-tracker

JWT_TOKEN=your_jwt_secret_key
JWT_ALGO=HS256
```

### 5. Create the PostgreSQL database

```sql
CREATE DATABASE expense-tracker;
```

### 6. Run the application

```bash
python main.py
```

The API will be available at `http://localhost:8000`.

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## Authentication

This API uses JWT (JSON Web Token) for authentication. Include the token in the `Authorization` header for protected endpoints:

```
Authorization: Bearer <your_access_token>
```

## API Endpoints

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API health status |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get access token |
| GET | `/auth/me` | Get current user info |

### Expenses

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/expenses` | Create a new expense |
| GET | `/expenses` | Get all expenses (with optional date filters) |
| GET | `/expenses/{id}` | Get a specific expense |
| PUT | `/expenses/{id}` | Update an expense |
| DELETE | `/expenses/{id}` | Delete an expense |

## Usage Examples

### Register a new user

**Request:**

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Login

**Request:**

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Get current user

**Request:**

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <your_access_token>"
```

**Response:**

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com"
}
```

### Create an expense

**Request:**

```bash
curl -X POST "http://localhost:8000/expenses" \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Weekly groceries",
    "amount": 85.50,
    "category_id": 1
  }'
```

**Response:**

```json
{
  "id": 1,
  "description": "Weekly groceries",
  "amount": 85.5,
  "category_id": 1
}
```

### Get all expenses

**Request:**

```bash
curl -X GET "http://localhost:8000/expenses" \
  -H "Authorization: Bearer <your_access_token>"
```

**Response:**

```json
[
  {
    "id": 1,
    "description": "Weekly groceries",
    "amount": 85.5,
    "category_id": 1
  },
  {
    "id": 2,
    "description": "Movie night",
    "amount": 15.00,
    "category_id": 2
  }
]
```

### Get expenses by date range

**Request:**

```bash
curl -X GET "http://localhost:8000/expenses?start_date=2025-01-01&end_date=2025-01-31" \
  -H "Authorization: Bearer <your_access_token>"
```

### Get a specific expense

**Request:**

```bash
curl -X GET "http://localhost:8000/expenses/1" \
  -H "Authorization: Bearer <your_access_token>"
```

**Response:**

```json
{
  "id": 1,
  "description": "Weekly groceries",
  "amount": 85.5,
  "category_id": 1
}
```

### Update an expense

**Request:**

```bash
curl -X PUT "http://localhost:8000/expenses/1" \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Monthly groceries",
    "amount": 350.00,
    "category_id": 1
  }'
```

**Response:**

```json
{
  "id": 1,
  "description": "Monthly groceries",
  "amount": 350.0,
  "category_id": 1
}
```

### Delete an expense

**Request:**

```bash
curl -X DELETE "http://localhost:8000/expenses/1" \
  -H "Authorization: Bearer <your_access_token>"
```

**Response:** `204 No Content`

## Expense Categories

The following categories are pre-seeded in the database:

| ID | Category Name |
|----|---------------|
| 1 | Groceries |
| 2 | Leisure |
| 3 | Electronics |
| 4 | Utilities |
| 5 | Clothing |
| 6 | Health |
| 7 | Others |

## Error Responses

The API returns standard HTTP status codes with JSON error messages:

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized (invalid or expired token) |
| 404 | Resource not found |
| 409 | Conflict (e.g., duplicate email/username) |
| 422 | Unprocessable Entity (validation error) |

**Example error response:**

```json
{
  "detail": "Expense amount must be greater than 0"
}
```

## Project Structure

```
expense-tracker-api/
├── api/
│   └── api.py              # API endpoints
├── core/
│   ├── config.py           # Configuration settings
│   └── security.py         # JWT and password utilities
├── database/
│   ├── database.py         # Database connection and queries
│   └── schemas.py          # SQLModel schemas
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── README.md               # Documentation
```

## Development

Run the development server:

```bash
uvicorn main:router --reload
```

## License

This project is for educational purposes, inspired by [roadmap.sh](https://roadmap.sh/projects/expense-tracker-api).
