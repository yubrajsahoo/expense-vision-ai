# 🧾 Expense Vision Service

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.163%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![uv](https://img.shields.io/badge/managed%20by-uv-de5fe9.svg)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/badge/linter-ruff-261230.svg)](https://github.com/astral-sh/ruff)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC.svg)](https://docs.pytest.org/)

An asynchronous AI microservice built with **Python 3.12+** and **FastAPI** for the **Expense Vision AI** platform. It acts as an intelligent worker and gatekeeper responsible for validating, pre-processing, and extracting structured financial information from uploaded receipts and UPI payment screenshots.

---

## 📑 Table of Contents

- [🥗 Ingredients](#ingredients)
- [📌 Overview & Role](#overview--role)
- [📋 Prerequisites & Installation](#prerequisites--installation)
- [⚙️ Configuration & Environment Variables](#configuration--environment-variables)
- [🚀 All Required Commands (Bash)](#all-required-commands-bash)
  - [1. Installation & Environment Setup](#1-installation--environment-setup)
  - [2. Running the Application](#2-running-the-application)
  - [3. Code Quality & Linting (`ruff`)](#3-code-quality--linting-ruff)
  - [4. Testing & Code Coverage (`pytest`)](#4-testing--code-coverage-pytest)
  - [5. Dependency Management (`uv`)](#5-dependency-management-uv)
- [📡 API Endpoints](#api-endpoints)
- [📂 Project Structure](#project-structure)
- [🧪 Developer Workflow Checklist](#developer-workflow-checklist)

---

<a id="ingredients"></a>
## 🥗 Ingredients

Everything that powers this microservice:

### 1. Framework & Core Runtime
- **Python 3.12+**: Modern Python runtime with enhanced performance and typing.
- **FastAPI (`>=0.163.1`)**: High-performance asynchronous web framework for building APIs.
- **Uvicorn (`>=0.54.0`)**: Production-ready, lightning-fast ASGI server.
- **Pydantic v2 (`>=2.14.3`)**: Strict data validation, schema modeling, and JSON serialization.
- **Pydantic Settings (`>=2.16.3`)**: Type-safe settings and environment variable management.

### 2. AI, Computer Vision & OCR
- **Google GenAI SDK (`google-genai >=3.3.0`)**: Official client for Google Gemini Multimodal LLMs (receipt and screenshot extraction).
- **OpenCV (`opencv-python >=5.0.0.93`)**: Image pre-processing, noise reduction, and image manipulation.
- **Tesseract OCR (`pytesseract >=0.3.13`)**: Optical Character Recognition engine for fast local keyword validation.

### 3. Developer Tooling & Testing
- **Astral `uv`**: Ultra-fast Python package and project manager.
- **Ruff (`>=0.17.5`)**: High-speed Python linter and code formatter.
- **Pytest (`>=9.2.0`)**: Test framework with support for fixtures and async testing (`anyio`).
- **Pytest-Cov (`>=7.1.0`)**: Test coverage reporting with 80%+ threshold enforcement.

### 4. External Credentials & System Binaries
- **Google Gemini API Key**: API key from [Google AI Studio](https://aistudio.google.com/) for LLM inference.
- **Tesseract OCR Binary**: System-level executable installed and present in system `PATH`.

---

<a id="overview--role"></a>
<a id="overview-and-role"></a>
## 📌 Overview & Role

In the larger Expense Vision AI polyglot architecture, `expense-vision-service` works alongside the Java Spring Boot gateway (`expense-core-api`):

1. **Gatekeeper (Pre-filter):** Fast local validation using **OpenCV** and **Tesseract OCR** to detect financial keywords (e.g. ₹, UPI, Total, invoice patterns) and reject invalid images instantly before invoking external LLMs.
2. **Extractor (Multimodal AI):** Uses the **Google Gemini API** (`google-genai`) to parse receipts and UPI screenshots into structured data.
3. **Structured Contracts:** Enforces strict data schemas using **Pydantic** models (e.g., merchant name, transaction amount, date, payment method, UTR number).
4. **Actuators & Monitoring:** Provides health check endpoints (`/actuators/health`) for readiness and liveness probes.

---

<a id="prerequisites--installation"></a>
## 📋 Prerequisites & Installation

Before running the service, install system prerequisites:

### 1. Install `uv` Package Manager (Bash)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install Tesseract OCR Engine (Bash)
- **Ubuntu / Debian:**
  ```bash
  sudo apt-get update && sudo apt-get install -y tesseract-ocr
  ```
- **macOS:**
  ```bash
  brew install tesseract
  ```
- **Windows (Git Bash):**
  Download the installer from [UB-Mannheim Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) and ensure the install location (e.g. `C:\Program Files\Tesseract-OCR`) is in your `PATH`.

---

<a id="configuration--environment-variables"></a>
## ⚙️ Configuration & Environment Variables

Create your local `.env` configuration file from the template:

```bash
cp .env.example .env
```

### Environment Variables Reference

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `GEMINI_API_KEY` | **Yes** | — | API key for Google Gemini multimodal processing |
| `GEMINI_MODEL` | No | `gemini-3.8-flash` | Gemini model identifier used for extraction |
| `HOST` | No | `0.0.0.0` | Host address to bind the Uvicorn server |
| `PORT` | No | `8000` | Port to bind the server |
| `RELOAD` | No | `true` | Enable/disable auto-reload during development |
| `MAX_FILE_SIZE_MB` | No | `10` | Maximum allowed image upload size in megabytes |

---

<a id="all-required-commands-bash"></a>
## 🚀 All Required Commands (Bash)

All commands below are designed to be run directly in **Bash** (Linux, macOS, WSL, or Git Bash on Windows).

<a id="1-installation--environment-setup"></a>
### 1. Installation & Environment Setup

```bash
# Sync and install all project dependencies into a local virtual environment (.venv)
uv sync

# (Optional) Activate the virtual environment
source .venv/bin/activate
# Note: On Git Bash for Windows, run: source .venv/Scripts/activate
```

---

<a id="2-running-the-application"></a>
### 2. Running the Application

#### Option A: Run via Uvicorn (Recommended for development)
```bash
uv run python -m uvicorn main:app --app-dir src --host 127.0.0.1 --port 8000 --reload
```

#### Option B: Run via Main Entrypoint
```bash
PYTHONPATH=src uv run python -m src.main
```

#### Option C: With Activated Virtual Environment
```bash
python -m uvicorn main:app --app-dir src --reload
```

#### Service URLs
- **Interactive API Docs (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative API Docs (ReDoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Actuator:** [http://127.0.0.1:8000/actuators/health](http://127.0.0.1:8000/actuators/health)

---

<a id="3-code-quality--linting-ruff"></a>
### 3. Code Quality & Linting (`ruff`)

`ruff` handles both fast linting and formatting as configured in `pyproject.toml`.

```bash
# Check for lint errors across codebase
uv run python -m ruff check

# Automatically fix fixable lint errors
uv run python -m ruff check --fix

# Check code formatting without modifying files
uv run python -m ruff format --check

# Format all code files
uv run python -m ruff format
```

---

<a id="4-testing--code-coverage-pytest"></a>
### 4. Testing & Code Coverage (`pytest`)

`pytest` is configured via `pyproject.toml` with default coverage enforcement (target: 80%+).

```bash
# Run full test suite with coverage report
uv run python -m pytest

# Run tests without coverage check
uv run python -m pytest --no-cov

# Run a specific test file
uv run python -m pytest tests/unit/config/test_config.py

# Run tests with verbose output
uv run python -m pytest -v

# Run tests matching a keyword expression
uv run python -m pytest -k "test_setting"

# Open HTML coverage report after a test run
xdg-open htmlcov/index.html 2>/dev/null || open htmlcov/index.html 2>/dev/null || start htmlcov/index.html
```

---

<a id="5-dependency-management-uv"></a>
### 5. Dependency Management (`uv`)

Manage libraries without editing `pyproject.toml` manually:

```bash
# Add a new runtime dependency
uv add <package-name>

# Add a development-only dependency
uv add --dev <package-name>

# Remove a dependency
uv remove <package-name>

# Regenerate and lock dependencies
uv lock

# Upgrade all packages to their latest compatible versions
uv lock --upgrade

# Inspect the dependency graph
uv tree
```

---

<a id="api-endpoints"></a>
## 📡 API Endpoints

| Method | Endpoint | Description | Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/actuators/health` | Service liveness / health check | Active |
| `POST` | `/api/v1/expense` | Validate and extract structured receipt data | Active |
| `GET` | `/docs` | Interactive Swagger API documentation | Active |
| `GET` | `/redoc` | ReDoc API documentation | Active |

### Health Check Response Example

**Request:**
```http
GET /actuators/health HTTP/1.1
Host: 127.0.0.1:8000
```

**Response (200 OK):**
```json
{
  "name": "expense-vision-service",
  "status": "healthy"
}
```

---

<a id="project-structure"></a>
## 📂 Project Structure

```text
expense-vision-service/
├── .env.example               # Sample environment variables template
├── .gitignore                 # Git ignore patterns
├── pyproject.toml             # Dependencies, ruff & pytest configuration
├── uv.lock                    # Dependency lockfile
├── README.md                  # Project documentation and command reference
├── src/
│   ├── __init__.py
│   ├── main.py                # FastAPI application initialization & server startup
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py          # Settings model (pydantic-settings)
│   ├── exceptions/
│   │   ├── __init__.py
│   │   ├── custom_exceptions.py # Custom domain exceptions
│   │   └── handlers.py        # Global exception handlers
│   ├── router/
│   │   ├── __init__.py
│   │   ├── routers.py         # Router registry (Actuators & API v1)
│   │   ├── actuators/
│   │   │   ├── __init__.py
│   │   │   └── health.py      # Health check endpoint
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── expense.py     # Expense extraction endpoint
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic schemas (ExpenseData)
│   └── services/
│       ├── __init__.py
│       ├── expense.py         # Expense orchestration service
│       ├── extractor.py       # Gemini multimodal extraction service
│       └── gatekeeper.py      # Local OCR gatekeeper validation
└── tests/
    ├── __init__.py
    ├── conftest.py            # Global test fixtures (FastAPI TestClient)
    ├── helper/
    │   ├── __init__.py
    │   ├── mock_helper.py     # Test mocking helpers
    │   └── resource_utils.py  # Test resource loading utilities
    ├── integration/           # Integration tests (--integration)
    │   ├── router/
    │   └── services/
    ├── resources/             # Test images and JSON fixtures
    └── unit/                  # Fast isolated unit tests
        ├── config/
        ├── exceptions/
        ├── router/
        ├── schemas/
        └── services/
```

---

<a id="developer-workflow-checklist"></a>
## 🧪 Developer Workflow Checklist

When developing or submitting changes:
1. Ensure dependencies are in sync:
   ```bash
   uv sync
   ```
2. Apply formatting:
   ```bash
   uv run python -m ruff format
   ```
3. Verify lint checks:
   ```bash
   uv run python -m ruff check
   ```
4. Run tests & maintain coverage:
   ```bash
   uv run python -m pytest
   ```
