# Task Manager API

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red)

Simple REST API for personal task management built with FastAPI and SQLAlchemy.
Includes user registration, JWT authentication and full CRUD functionality for tasks, with filters and pagination.

## Features

- JWT authentication (registration, login, Bearer tokens)
- Full CRUD functionality for user tasks
- Filtering tasks by status, title, and free-text search
- Sorting tasks by any field, and pagination
- Input data validation using Pydantic v2
- Hashed passwords using Argon2

## Stack

| Layer | Technology |
| ------- | ------------ |
| Framework | FastAPI 0.115+ |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (dev) |
| Authentication | JWT (PyJWT) |
| Hashing | pwdlib + Argon2 |
| Validation | Pydantic v2 |
| Package manager | uv |

## Installation

**Requirements:** Python 3.10+, uv

1. Clone this repository

   ```bash
   git clone https://github.com/gemadrid/task-manager.git
   cd task-manager
   ```

2. Install the dependencies using uv

   ```bash
   uv sync
   ```

3. Create a `.env` configuration file. You can use `.env.example` as a basis, replacing the fields with your own values. You can generate a secure `SECRET_KEY` using the command `openssl rand -hex 32`.

   ```bash
   # Generate the .env file from .env.example
   cp .env.example .env

   # Generate a secret key
   openssl rand -hex 32
   ```

4. Start the server

   ```bash
   uv run fastapi dev
   ```

The API will be available at `http://localhost:8000`.
The interactive API documentation will be available at `http://localhost:8000/docs`.

## Configuration

These are the variables present in the `.env` configuration files, with examples of possible values:

| Variable | Description | Example |
| -------- | ----------- | ------- |
| `SECRET_KEY` | Secret key used to sign JWT tokens | A value can be generated with the command `openssl rand -hex 32` |
| `ALGORITHM` | Algorithm used to sign JWT tokens | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Time in minutes until the JWT token expires | 30 |
| `DATABASE_URL` | Database connection URL | `sqlite:///./test.db` |

## API

These are the available endpoints:

### Authentication

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| POST | `/register` | Registers a new user |
| POST | `/token` | Login, returns a JWT token |

### Tasks (requiring authentication)

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/tasks` | Returns a list of tasks, with optional filters |
| GET | `/tasks/{task_id}` | Returns a task by id |
| POST | `/tasks` | Creates a new task |
| PATCH | `/tasks/{task_id}` | Modifies a task |
| DELETE | `/tasks/{task_id}` | Deletes a task |

### Users (requiring authentication)

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/users/me` | Returns the current user's profile |
| PATCH | `/users/me` | Updates the current user's email or password |
| DELETE | `/users/me` | Deletes the current user |

## Project structure

```text
app/
├── core/            # Global configuration and security (JWT, hashing)
├── crud/            # Database access logic
├── db/              # Database configuration (engine, session)
├── dependencies/    # Dependency injection (auth, db)
├── models/          # SQLAlchemy models
├── routers/         # API endpoints
├── schemas/         # Pydantic schemas
├── services/        # Business logic (authentication)
└── main.py          # FastAPI entry point
```
