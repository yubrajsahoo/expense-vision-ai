# Project Context & Engineering Rules

## 1. Architecture & Tech Stack

Expense Vision AI is a polyglot microservice platform designed to automate expense tracking from receipts and UPI payment screenshots.

### Monorepo Services
- **`expense-core-api` (Java Gateway & Core):**
  - **Runtime & Language:** Java 25
  - **Framework:** Spring Boot 4.1.2
  - **Build Tool:** Maven (`mvnw` / `mvnw.cmd`)
  - **Data & Persistence:** Spring Data JPA / Hibernate, Neon PostgreSQL (production), H2 Database (local/dev)
  - **Security & Network:** Spring Security, OAuth2 Resource Server (JWT verification), Spring `RestClient`
  - **Testing:** JUnit 5, Mockito, Spring Boot Test (`@DataJpaTest`, `@RestClientTest`)
- **`expense-vision-service` (Python AI Microservice):**
  - **Runtime & Language:** Python 3.12+
  - **Framework:** FastAPI, Uvicorn
  - **Dependency Manager:** `uv` (`pyproject.toml`, `uv.lock`)
  - **Data Contracts:** Pydantic v2, Pydantic Settings
  - **Computer Vision & AI:** OpenCV (`opencv-python`), Tesseract OCR (`pytesseract`), Google GenAI SDK (`google-genai` for Gemini multimodal)
  - **Code Quality & Testing:** Ruff (target py312, line length 88), Pytest, pytest-cov (threshold: >=80%)
- **Roadmap Frontend Modules:**
  - `expense-web-ui`: React + Vite + TypeScript
  - `expense-mobile-app`: React Native Android App

---

## 2. Monorepo Directory Map

```text
expense-vision-ai/
│
├── .ai/                                # Central AI System (Workflow, Memory, Reports, Rules)
│   ├── agents/                         # The 3 Streamlined Agent Role Specifications
│   │   ├── discovery-planner.md        # Agent 1: Discovery & Planning (OpenCode + Gemini 3.8 Low)
│   │   ├── fullstack-engineer.md       # Agent 2: Full-Stack Engineer (Gemini 4 Hydrogen + Gemini 3.8 Med)
│   │   └── quality-guardian.md         # Agent 3: Quality Guardian (OpenCode + Codex)
│   ├── memory/                         # Local execution memory (flat directory, git-ignored)
│   │   ├── INDEX.md                    # Chronological index of memory logs
│   │   └── YYYY-MM-DD_<stage>_<topic>.md # Memory logs stored directly in folder
│   ├── reports/                        # Analysis & test-run dual reports (git-ignored)
│   │   ├── md/                         # Markdown reports
│   │   └── html/                       # Interactive HTML reports
│   ├── PROJECT_CONTEXT.md              # Polyglot architecture, module map & engineering standards
│   ├── TEMPLATES.md                    # Structured templates for reports, reviews & memory logs
│   └── report_tool.py                  # HTML report compiler, memory logger & self-verification
│
├── GEMINI.md                           # Master AI agent instructions, routing, and review gates
├── .gitignore                          # Ignores .ai/memory/ and .ai/reports/
│
├── expense-core-api/                   # Java 25 + Spring Boot 4.1.2 Service
│   ├── src/main/java/io/github/yubrajsahoo/expense/expensecoreapi/
│   │   ├── config/                     # H2, Security, Cloudinary & RestClient configs
│   │   └── ExpenseCoreApiApplication.java
│   ├── src/main/resources/             # application.yaml, application-dev.yml, application-prod.yml
│   ├── src/test/java/                  # Unit and slice test suites
│   ├── pom.xml                         # Maven project definition
│   └── .gitignore
│
└── expense-vision-service/             # Python 3.12+ + FastAPI Service
    ├── src/
    │   ├── config/                     # Pydantic Settings configuration
    │   ├── exceptions/                 # Custom exceptions & HTTP exception handlers
    │   ├── router/                     # API routers (v1 endpoints, actuator health checks)
    │   ├── schemas/                    # Pydantic input/output schemas (ExpenseData)
    │   ├── security/                   # HMAC auth, rate limiting, image validators
    │   └── services/                   # Gatekeeper (OpenCV/OCR) and Extractor (Gemini LLM)
    ├── tests/
    │   ├── unit/                       # Deterministic in-memory unit tests (no network/OCR binaries)
    │   ├── integration/                # Opt-in external integration tests (marked with @pytest.mark.integration)
    │   └── helper/                     # Test fixtures and utilities
    ├── pyproject.toml                  # UV project configuration, Ruff and Pytest settings
    └── .gitignore
```

---

## 3. Core Engineering & Coding Rules

### A. Universal Monorepo Principles
1. **Layered Separation of Concerns:**
   - Controllers/Routers: Only handle HTTP deserialization, validation, and response status mapping. Delegate domain logic to services.
   - Services: Implement domain logic, orchestration, and transactions. Keep services decoupled from transport protocols.
   - Data & External Clients: Encapsulate data stores and external HTTP integrations (RestClient, Gemini, Cloudinary) behind injectable boundaries.
2. **Environment & Configuration Hygiene:**
   - Source all configuration values through settings layers (`application.yaml` / Pydantic `BaseSettings`). Never hard-code credentials or endpoints.
3. **Graceful Error Handling:**
   - Anticipate and handle malformed input and dependency outages explicitly with typed domain exceptions and standard HTTP status codes (400, 401, 403, 404, 422, 502).
   - Never leak internal stack traces, DB queries, or credentials in client error responses or logs.
4. **Minimal Scoped Changes:**
   - Keep changes tightly scoped to the current approved plan. Do not perform unrelated refactoring.

### B. Java (`expense-core-api`) Conventions
1. **Dependency Injection:** Use constructor-based injection for all components. Never use `@Autowired` on private fields.
2. **Data Transfer:** Prefer Java 25 records for immutable DTOs and value carriers across layers.
3. **JPA & Transactions:**
   - Always define explicit `@Column` names, indexes, and constraints.
   - Avoid eager fetching on relationships (prevent N+1 queries); use join fetches or entity graphs where appropriate.
   - Encapsulate write operations within `@Transactional(rollbackFor = Exception.class)`.
4. **Outbound Calls (`RestClient`):**
   - Inter-service calls to `expense-vision-service` must use configured `RestClient` beans with explicit connect and read timeouts.
   - Translate downstream HTTP 4xx/5xx responses into meaningful domain exceptions.
5. **Validation:** Enforce Jakarta Bean Validation (`@NotNull`, `@NotBlank`, `@Positive`, etc.) on all incoming DTO requests in controllers using `@Valid`.

### C. Python (`expense-vision-service`) Conventions
1. **Typing & Schemas:** Type annotate all function arguments, return types, and class attributes. Enforce strict Pydantic v2 schemas.
2. **Deterministic Startup:** Never make outbound network requests or execute heavy disk/OCR operations during module import or application initialization.
3. **Dependency Isolation:** External dependencies (Gemini SDK, OpenCV, `pytesseract`) must be accessed through service abstractions or injected dependencies.
4. **Code Quality:** Ensure all code conforms to Ruff settings: `uv run ruff check` and `uv run ruff format` (88-char limit, target `py312`).

---

## 4. Testing Rules & Test Isolation

### A. Java Service Testing (`expense-core-api`)
- **Unit Tests:** Must run purely in-memory using JUnit 5 and Mockito. Mock all repositories, REST clients, and Cloudinary clients. Zero external network dependency.
- **Spring Slice Tests:**
  - `@DataJpaTest`: Use embedded H2 in-memory database to verify repository queries.
  - `@RestClientTest`: Test HTTP client logic with `MockRestServiceServer`.
  - `@WebMvcTest`: Test endpoint input validation, serialization, and status codes using `MockMvc`.
- **Command:** `mvn test` or `./mvnw test` (Windows: `.\mvnw.cmd test`).

### B. Python Vision Service Testing (`expense-vision-service`)
- **Unit Tests (`tests/unit/`):**
  - Verify logic in isolation. Must run offline without Tesseract binary or network access.
  - Mock `pytesseract.image_to_string` and Gemini calls.
  - Command: `uv run pytest tests/unit` (maintain coverage >= 80%).
- **Integration Tests (`tests/integration/`):**
  - Exercise real external dependencies, decorated with `@pytest.mark.integration`.
  - Opt-in only: runs only when `RUN_INTEGRATION_TESTS=1` is provided.
  - Command: `$env:RUN_INTEGRATION_TESTS="1"; uv run pytest -m integration tests/integration` (PowerShell).

---

## 5. Security & Financial Privacy Rules
1. **Credentials & Secrets Protection:**
   - Never commit API keys, database passwords, JWT signing keys, HMAC secrets, or Cloudinary credentials.
   - Scan every diff to verify no private tokens or real customer data are committed.
2. **Financial Data & PII Protection:**
   - Do not log extracted receipt contents, UPI transaction IDs, customer names, or phone numbers in plaintext logs.
   - Use anonymized/synthetic test fixtures only. Never commit real customer receipts or bank screenshots.
3. **Input Validation & File Security:**
   - Enforce content-type inspection and magic byte checking on all uploaded images (`image/jpeg`, `image/png`, `image/webp`).
   - Limit file sizes explicitly (configured default: 10MB).
   - Sanitize original file names before saving to storage to prevent path traversal attacks.
