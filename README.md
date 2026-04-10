# EasyBook 📅

A full-stack appointment booking system built with Flask, PostgreSQL, and vanilla HTML/CSS/JS — containerised with Docker and deployed via GitHub Actions CI/CD.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Modules](#modules)
4. [Prerequisites](#prerequisites)
5. [Local Development Setup](#local-development-setup)
6. [Running with Docker](#running-with-docker)
7. [Running Tests Locally](#running-tests-locally)
8. [GitHub Actions CI/CD](#github-actions-cicd)
9. [Deploying from GitHub](#deploying-from-github)
10. [API Reference](#api-reference)
11. [Environment Variables](#environment-variables)

---

## Project Overview

EasyBook lets customers discover and book services across categories (Medical, Salon, Fitness, Dental, Legal, Spa), and lets providers manage their services, availability, and appointments.

**Tech Stack:**
- **Frontend:** HTML5, CSS3, Vanilla JavaScript — served via Nginx
- **Backend:** Python 3.11, Flask, SQLAlchemy, Flask-JWT-Extended
- **Database:** PostgreSQL 15
- **Containerisation:** Docker & Docker Compose
- **CI/CD:** GitHub Actions
- **Tests:** pytest (unit, backend, integration), Jest (frontend), Selenium (E2E)

---

## Project Structure

```
easybook/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions — all 5 test suites + Docker build
├── backend/
│   ├── app/
│   │   ├── __init__.py         # Flask app factory
│   │   ├── models/             # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── category.py
│   │   │   ├── service.py
│   │   │   ├── appointment.py
│   │   │   └── availability.py (+ Review)
│   │   ├── routes/             # Blueprint route handlers (full CRUD)
│   │   │   ├── auth.py
│   │   │   ├── services.py
│   │   │   ├── appointments.py
│   │   │   ├── providers.py
│   │   │   ├── reviews.py
│   │   │   └── categories.py
│   │   └── tests/
│   │       ├── conftest.py     # Shared pytest fixtures
│   │       ├── test_unit.py    # Unit tests (models)
│   │       ├── test_backend.py # Backend/validation tests
│   │       └── test_integration.py # API integration tests
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini
│   └── run.py
├── frontend/
│   ├── templates/              # HTML pages
│   │   ├── index.html          # Homepage
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── services.html       # Browse & book services
│   │   ├── dashboard.html      # Customer + Provider dashboard
│   │   └── providers.html
│   ├── static/
│   │   ├── css/main.css
│   │   └── js/
│   │       ├── api.js          # Fetch wrapper
│   │       ├── auth.js         # Auth state management
│   │       └── utils.js        # Shared UI helpers
│   ├── nginx.conf
│   └── Dockerfile
├── tests/
│   ├── frontend/
│   │   ├── package.json        # Jest config
│   │   └── test_frontend.test.js # 30+ Jest tests
│   └── selenium/
│       └── test_selenium.py    # Selenium E2E tests
├── docker/
│   └── init.sql                # DB schema + seed data
├── docker-compose.yml          # Production stack
├── docker-compose.test.yml     # Test stack
└── README.md
```

---

## Modules

The application has **6 core modules** (excluding login/signup):

| Module | Description | CRUD |
|--------|-------------|------|
| **Services** | Browse, search, filter available services by category | ✅ Full |
| **Appointments** | Book, view, cancel, and manage appointments | ✅ Full |
| **Providers** | View providers, manage availability schedules | ✅ Full |
| **Reviews** | Leave, edit, and delete reviews on completed appointments | ✅ Full |
| **Categories** | Organise services into categories (admin-managed) | ✅ Full |
| **Dashboard** | Unified control panel for customers and providers | ✅ Full |

---

## Prerequisites

Make sure the following are installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- [Git](https://git-scm.com/)
- [VS Code](https://code.visualstudio.com/) (recommended)

Optional (for running tests locally without Docker):
- Python 3.11+
- Node.js 20+
- Google Chrome (for Selenium)

---

## Local Development Setup

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/easybook.git
cd easybook
```

### Step 2 — Open in VS Code

```bash
code .
```

Install the recommended extensions when prompted:
- Python
- Docker
- REST Client (optional, for API testing)

---

## Running with Docker

This is the **recommended** way to run the full stack.

### Step 1 — Start all services

```bash
docker compose up --build
```

This starts:
- **PostgreSQL** on port `5432`
- **Flask backend** on port `5000`
- **Nginx frontend** on port `8080`

### Step 2 — Open the app

Visit **http://localhost:8080** in your browser.

### Step 3 — Create an account

- Click **Get Started** and register as a **Customer** or **Provider**
- Providers can then add services and set their availability
- Customers can browse services and book appointments

### Step 4 — Stop the app

```bash
docker compose down
```

To also remove the database volume (fresh start):

```bash
docker compose down -v
```

---

## Running Tests Locally

You can run each test suite independently.

### Prerequisites — Python tests

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 1. Unit Tests

Tests individual model methods in isolation using SQLite in-memory.

```bash
cd backend
pytest app/tests/test_unit.py -v
```

### 2. Backend Tests

Tests business logic, validation, and edge cases.

```bash
cd backend
pytest app/tests/test_backend.py -v
```

### 3. Integration Tests

Tests full API request/response cycles. Requires PostgreSQL running.

```bash
# Start just the database
docker compose up db -d

# Run integration tests
export DATABASE_URL=postgresql://easybook_user:easybook_pass@localhost:5432/easybook
cd backend
pytest app/tests/test_integration.py -v
```

### 4. Frontend Tests (Jest)

Tests JavaScript utility functions — no browser required.

```bash
cd tests/frontend
npm install
npm test
```

### 5. Selenium E2E Tests

Tests the full user flow in a real Chrome browser. Requires the full stack running.

```bash
# Start full stack first
docker compose up --build -d

# Wait ~15 seconds for services to be ready, then:
cd tests/selenium
pip install selenium webdriver-manager pytest
pytest test_selenium.py -v
```

### Run ALL backend tests at once

```bash
cd backend
pytest -v
```

---

## GitHub Actions CI/CD

The CI pipeline runs **5 labelled test jobs** automatically on every push and pull request.

### Test Jobs in the Pipeline

| Job | Label | What it tests |
|-----|-------|---------------|
| `unit-tests` | 🔬 Unit Tests | Model methods, password hashing, serialisation |
| `backend-tests` | ⚙️ Backend Tests | Validation logic, conflict detection, auth rules |
| `integration-tests` | 🔗 Integration Tests | Full API endpoints with real PostgreSQL |
| `frontend-tests` | 🎨 Frontend Tests | JS utilities via Jest (30+ tests) |
| `selenium-tests` | 🌐 Selenium E2E Tests | Browser flow: page loads, forms, navigation |
| `docker-build` | 🐳 Build Docker Images | Validates Docker images build (main branch only) |
| `test-summary` | 📊 Test Summary | Aggregated pass/fail report |

All jobs run in parallel where possible. The `selenium-tests` job depends on `backend-tests` passing first.

---

## Deploying from GitHub

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/easybook.git
git push -u origin main
```

### Step 2 — Watch CI run

1. Go to your repo on GitHub
2. Click the **Actions** tab
3. You will see **"EasyBook CI/CD"** running automatically
4. All 5 test suites will appear as separate labelled jobs
5. Each job shows green ✅ or red ❌ with full logs

### Step 3 — Deploy to a server (e.g. a VPS or EC2)

On your server:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Clone your repo
git clone https://github.com/YOUR_USERNAME/easybook.git
cd easybook

# Set production environment variables
cp .env.example .env
nano .env   # Edit SECRET_KEY and other vars

# Start
docker compose up --build -d

# View logs
docker compose logs -f
```

### Step 4 — Set up GitHub Secrets (optional, for Docker Hub push)

In your GitHub repo → **Settings → Secrets and variables → Actions**, add:

| Secret | Value |
|--------|-------|
| `DOCKERHUB_TOKEN` | Your Docker Hub access token |

And in **Variables**:

| Variable | Value |
|----------|-------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |

---

## API Reference

All endpoints are prefixed with `/api`.

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and receive JWT token |
| GET | `/api/auth/me` | Get current user (auth required) |
| PUT | `/api/auth/me` | Update profile (auth required) |

### Services
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/services` | List services (supports `?search=`, `?category_id=`) |
| GET | `/api/services/:id` | Get single service |
| POST | `/api/services` | Create service (provider only) |
| PUT | `/api/services/:id` | Update service (owner/admin) |
| DELETE | `/api/services/:id` | Deactivate service |
| GET | `/api/services/:id/slots?date=YYYY-MM-DD` | Get available time slots |

### Appointments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/appointments` | List my appointments |
| POST | `/api/appointments` | Book an appointment |
| GET | `/api/appointments/:id` | Get single appointment |
| PUT | `/api/appointments/:id` | Update status |
| DELETE | `/api/appointments/:id` | Cancel appointment |

### Providers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/providers` | List all providers |
| GET | `/api/providers/:id` | Get provider with services |
| GET | `/api/providers/availability` | Get my availability |
| POST | `/api/providers/availability` | Set availability |
| DELETE | `/api/providers/availability/:id` | Remove availability slot |

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reviews?service_id=` | List reviews |
| POST | `/api/reviews` | Create review (completed appointments only) |
| PUT | `/api/reviews/:id` | Update review |
| DELETE | `/api/reviews/:id` | Delete review |

### Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories` | List all categories |
| POST | `/api/categories` | Create category (admin only) |
| PUT | `/api/categories/:id` | Update category (admin only) |
| DELETE | `/api/categories/:id` | Deactivate category (admin only) |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://easybook_user:easybook_pass@db:5432/easybook` | PostgreSQL connection string |
| `SECRET_KEY` | `super-secret-key-change-in-production` | Flask + JWT secret — **change this in production** |
| `FLASK_ENV` | `production` | Flask environment |

---

## Default Test Credentials

After running the app with Docker, you can register any account. For quick testing use:

| Role | Action |
|------|--------|
| Customer | Register via `/register.html` |
| Provider | Register via `/register.html?role=provider` |

---

## Troubleshooting

**Port already in use:**
```bash
docker compose down
# then try again
docker compose up --build
```

**Database won't start:**
```bash
docker compose down -v   # removes volumes
docker compose up --build
```

**Tests fail with "connection refused":**
Make sure the DB service is healthy before running integration/selenium tests:
```bash
docker compose up db -d
docker compose ps   # wait for db to show "healthy"
```

**Chrome not found (Selenium locally):**
```bash
# Ubuntu/Debian
sudo apt-get install -y google-chrome-stable
# macOS
brew install --cask google-chrome
```
