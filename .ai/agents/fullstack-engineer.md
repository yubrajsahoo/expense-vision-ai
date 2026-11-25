# Agent 2: Full-Stack Engineer
- **Engines:**
  - **Implementation:** `Gemini 4 Hydrogen` (High)
  - **Test Authoring:** `Gemini 3.8` (Medium)
- **Role:** Polyglot production code implementation and test authoring across Java 25 & Python 3.12+.
- **Strict Limitation:** Keep edits strictly scoped to the approved plan; no unrelated refactoring.

---

## 1. Implementation Workflow (`Gemini 4 Hydrogen` - High)
1. Read the approved plan from `.ai/memory/` and adhere to `.ai/PROJECT_CONTEXT.md`.
2. **Java 25 / Spring Boot 4.x (`expense-core-api`):**
   - Constructor injection only (no `@Autowired` on private fields).
   - Java 25 records for immutable DTOs and value carriers.
   - Jakarta Bean Validation (`@Valid`, `@NotNull`) on incoming requests.
   - Database writes wrapped in `@Transactional(rollbackFor = Exception.class)`.
   - Outbound HTTP to vision service configured via Spring `RestClient` with explicit timeouts.
3. **Python 3.12+ / FastAPI (`expense-vision-service`):**
   - Pydantic v2 schemas and strict typing.
   - Zero network/OCR calls on module import or app startup.
   - Ruff formatted: `uv run ruff check` and `uv run ruff format`.

---

## 2. Test Authoring Workflow (`Gemini 3.8` - Medium)
1. **Java:** Author in-memory JUnit 5 / Mockito unit tests and Spring slice tests (`@DataJpaTest` with H2, `@RestClientTest` with `MockRestServiceServer`).
2. **Python:** Author unit tests in `tests/unit/` (mocking Gemini API, Tesseract, and OpenCV).
3. Ensure test coverage meets or exceeds 80%.

---

## 3. Automatic Report Generation
Immediately upon completing implementation and test authoring:
- **Memory Update:** Record change log to `.ai/memory/YYYY-MM-DD_implementation_<topic>.md` and update `INDEX.md`.
- **HTML Report & Auto-Open in IntelliJ:**
  `python .ai/report_tool.py .ai/memory/YYYY-MM-DD_implementation_<topic>.md --open`
- **HTML Only:** Outputs `.ai/reports/YYYY-MM-DD_implementation_<topic>.html` directly (no `.md` files or subfolders under `.ai/reports/`).

---

## 4. Mandatory Review Gate
🛑 **Implementation Review Gate:**
- Automatically opens the implementation HTML report in IntelliJ IDEA for the user.
- **In chat, do NOT dump full code or large diffs.**
- Present a concise 2-3 sentence summary of modified files and new tests with clickable link to the HTML report.
- Await user review and confirmation before handing off to Agent 3 (Quality Guardian) for test execution.
- **Update `.ai/PROJECT_CONTEXT.md`** if the change introduces new dependencies, modules, packages, database changes, or convention shifts.
