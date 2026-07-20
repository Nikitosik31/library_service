# Library Service API

A DRF-based backend for a library management system: book inventory, borrowings with
inventory tracking, JWT authentication, Stripe payments (regular + overdue fines),
Telegram notifications, and a daily Celery Beat job for overdue checks.

## Features

- **Books** — CRUD, public read access, admin-only write
- **Users** — email-based JWT authentication (custom `Authorize` header instead of `Authorization`)
- **Borrowings** — create/list/detail/return, inventory tracking, own-vs-all filtering (`is_active`, `user_id`)
- **Payments** — Stripe Checkout sessions for regular payments and overdue fines, success/cancel confirmation endpoints
- **Notifications** — Telegram message on borrowing creation
- **Scheduled task** — daily Celery Beat job that reports borrowings due tomorrow or overdue
- **API docs** — Swagger / ReDoc via drf-spectacular

## Tech stack

Django 6, Django REST Framework, PostgreSQL, Redis, Celery + Celery Beat,
Stripe, Telegram Bot API, simplejwt, drf-spectacular, python-dotenv.

## Environment variables

Copy `.env.sample` to `.env` and fill in the values:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | database connection |
| `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | Redis connection for Celery |
| `TELEGRAM_BOT_KEY`, `TELEGRAM_CHAT_ID` | bot token and chat to notify |
| `STRIPE_KEY` | Stripe secret key (test mode) |

## Run with Docker (recommended)

```bash
docker-compose up --build
```

This starts: `web` (Django), `db` (PostgreSQL), `redis`, `celery` (worker) and
`celery-beat` (scheduler). Migrations run automatically on startup.

Open the API at **http://localhost:8000/** (use `localhost`, not `0.0.0.0`, in the browser).

## Run locally without Docker

Requires a running PostgreSQL and Redis instance locally, with matching `.env` values.

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Celery worker and beat (in separate terminals):

```bash
celery -A library_service worker -l info
celery -A library_service beat -l info
```

## API documentation

- Swagger UI: `/api/doc/swagger/`
- ReDoc: `/api/doc/redoc/`
- Raw schema: `/api/schema/`

## Main endpoints

| Endpoint | Description |
|---|---|
| `POST /api/users/` | register |
| `POST /api/users/token/` | obtain JWT pair |
| `POST /api/users/token/refresh/` | refresh access token |
| `GET/PUT /api/users/me/` | current user profile |
| `GET /api/books/` | list books (public) |
| `POST /api/books/` | create book (admin only) |
| `GET/POST /api/borrowings/` | list own (or all, for admins) / create a borrowing |
| `GET /api/borrowings/?is_active=true` | filter active (not yet returned) borrowings |
| `GET /api/borrowings/?user_id=<id>` | filter by user (admin only) |
| `POST /api/borrowings/{id}/return/` | return a borrowed book |
| `GET /api/payments/` | list own (or all, for admins) payments |
| `GET /api/payments/success/` | confirm a Stripe payment (Stripe redirect target) |
| `GET /api/payments/cancel/` | payment cancelled notice (Stripe redirect target) |

### Authentication note

This project uses a custom JWT header name: send the token as

```
Authorize: Bearer <access_token>
```

instead of the default `Authorization` header.

## Tests

```bash
python manage.py test
```

With coverage:

```bash
coverage run --source=. manage.py test
coverage report
```
