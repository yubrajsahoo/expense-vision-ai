# 🧾 Expense Vision AI

A polyglot enterprise application designed to automate expense tracking. The system uses a robust Java Spring Boot API Gateway to route uploaded receipts and UPI payment screenshots to a specialized Python FastAPI microservice. 

The Python AI worker acts as a "Gatekeeper," performing fast local validation (using OpenCV and Tesseract) to reject invalid images before extracting structured financial data using a Multimodal LLM (Gemini API).

---

## 🏗️ Architecture & Tech Stack

### 1. Shared Infrastructure
*   **Database:** Neon PostgreSQL (Stores user ledgers and extracted expense records)
*   **Blob Storage:** Cloudinary (Temporarily stores image uploads before processing)

### 2. The Core API (`expense-core-api`)
*   **Language:** Java 25
*   **Framework:** Spring Boot 4.x
*   **Responsibilities:** JWT Authentication, database ORM (JPA/Hibernate), file upload orchestration, and synchronous HTTP routing via `RestClient`.

### 3. The AI Worker (`expense-vision-service`)
*   **Language:** Python 3.12+
*   **Tooling:** `uv` (dependency management), `ruff` (linting), `pytest` (testing)
*   **Framework:** FastAPI + Pydantic
*   **Responsibilities:**
    1.  **Gatekeeper:** OpenCV/Tesseract for local validation (rejecting non-receipts instantly).
    2.  **Extractor:** Gemini API (Multimodal LLM) for reading receipts and UPI screenshots.
    3.  **Formatter:** Pydantic for strict JSON contract enforcement.

---

## 📂 Full Project Structure

```text
expense-vision-ai/
│
├── expense-core-api/                  # ☕ Java 25 + Spring Boot 4.x Service
│   ├── src/main/java/com/expensevision/
│   │   ├── config/                    # JWT Auth & Cloudinary SDK configurations
│   │   ├── controller/                # /api/expenses/upload endpoint
│   │   ├── model/                     # JPA/Hibernate Entities (Expense record)
│   │   ├── repository/                # Spring Data JPA Repositories
│   │   └── service/                   # File upload orchestration & RestClient routing
│   ├── src/main/resources/
│   │   └── application.yml            # Neon PostgreSQL and Cloudinary secrets
│   ├── pom.xml                        # Maven dependencies
│   └── README.md
│
├── expense-vision-service/            # 🐍 Python 3.12+ + FastAPI Service
│   ├── src/
│   │   ├── main.py                    # FastAPI app initialization & /process-image endpoint
│   │   ├── schemas.py                 # Pydantic models (ExpenseData)
│   │   └── services/
│   │       ├── gatekeeper.py          # OpenCV/Tesseract local validation logic
│   │       └── extractor.py           # Gemini API multimodal LLM integration
│   ├── tests/
│   │   └── test_vision.py             # Pytest cases
│   ├── pyproject.toml                 # Managed by 'uv', configures dependencies & 'ruff'
│   ├── .python-version                # Specifies Python 3.12+
│   └── README.md
│
├── expense-web-ui/                    # ⚛️ React + Vite + TypeScript (Version 1)
│   ├── src/
│   │   ├── components/                # Drag-and-drop uploader, Data Table
│   │   ├── hooks/                     # API integration hooks
│   │   └── App.tsx                    # Main dashboard layout
│   ├── package.json
│   └── README.md
│
└── expense-mobile-app/                # 📱 React Native Android App (Version 2)
    ├── src/
    │   ├── screens/                   # Mobile dashboard
    │   └── intent/                    # Native Android Share Target Intent logic
    ├── package.json
    └── README.md
```

---

## 🚀 Development Roadmap

### Version 1: The Web Application
The foundational version establishing the backend communication and web-based file uploads.

*   **Phase 1: Python Microservice**
    *   Initialize project with `uv` and install `fastapi`, `pydantic`, `google-genai`, `opencv-python`, `pytesseract`.
    *   Create Pydantic schema mapping `merchant_name`, `amount`, `date`, `payment_method`, and `utr_number`.
    *   Build `/process-image` POST endpoint.
    *   Implement OpenCV/Tesseract logic to scan for financial keywords (₹, UPI, Total) before triggering Gemini.
    *   Write `pytest` cases for various image types.
*   **Phase 2: Java Backend**
    *   Initialize Spring Boot project (Web, Data JPA, Security).
    *   Create Expense database entity and repository.
    *   Build `/api/expenses/upload` endpoint.
    *   Integrate Cloudinary SDK and `RestClient` to route to Python.
    *   Save returned JSON as a new Expense record in Neon PostgreSQL.
*   **Phase 3: React Dashboard (`expense-web-ui`)**
    *   Create Vite + React + TypeScript frontend.
    *   Build a drag-and-drop file upload component.
    *   Render returned data in an editable Data Table.

### Version 2: The Android Application
Upgrading the frontend to automatically handle UPI payment success screens using native mobile features.

*   **Phase 4: React Native Share Intent (`expense-mobile-app`)**
    *   Implement **Share Target Intent**: Configure the app to appear in the Android native OS "Share" menu.
    *   *Workflow:* User pays via UPI -> Takes a screenshot -> Taps "Share" -> Selects Expense Vision AI -> App grabs the image.
*   **Phase 5: Mobile API Integration**
    *   Send captured screenshot payload to the existing Java `/api/expenses/upload` endpoint.
    *   Display a success notification and update the mobile dashboard ledger.
