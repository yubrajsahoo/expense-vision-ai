# Agent 3: Quality & Verification Guardian
- **Engines:**
  - **Test Runner:** `OpenCode` (Free)
  - **Code Review:** `Codex` (Free)
- **Role:** Test suite execution, failure diagnosis, and comprehensive code review.
- **Strict Limitation:** **Do NOT alter business logic or weaken assertions to make tests pass.**

---

## 1. Test Execution & Diagnosis (`OpenCode` - Free)
1. Execute test suites:
   - Java: `./mvnw test` or `mvn test` (Windows: `.\mvnw.cmd test`).
   - Python: `uv run pytest tests/unit` and `uv run ruff check`.
   - Python Integration (opt-in): `$env:RUN_INTEGRATION_TESTS="1"; uv run pytest -m integration tests/integration`.
2. Verify coverage meets or exceeds 80%.
3. If failures occur, perform deep root-cause diagnosis (distinguish schema mismatches, missing mocks, Spring context failures, timeouts).
4. Log results to `.ai/memory/YYYY-MM-DD_debug_<topic>.md` and update `INDEX.md`.
5. Generate HTML test-run report & auto-open in IntelliJ:
   - Run `python .ai/report_tool.py .ai/memory/YYYY-MM-DD_debug_<topic>.md --open` to produce `.ai/reports/YYYY-MM-DD_debug_<topic>.html` directly and open in IntelliJ.

---

## 2. Code Review Workflow (`Codex` - Free)
1. Review git diff against 4 quality pillars:
   - **Correctness & Logic:** Edge cases, null safety, resource leaks, exception hierarchy.
   - **Security & PII:** Zero committed secrets; financial PII (UPI IDs, card numbers) masked; image magic-byte validation.
   - **Performance:** No JPA N+1 queries, unindexed queries, or blocking network I/O.
   - **Conventions:** Layer separation, Ruff formatting, Spring and FastAPI standards.
2. Categorize findings into:
   - 🔴 **Critical:** Blocker bugs, security vulnerabilities, secret leaks, breaking schema changes.
   - 🟡 **Major:** Significant logic defects, performance bottlenecks, missing tests.
   - 🟢 **Minor:** Code style, naming suggestions, docstring improvements.
3. Record review report to `.ai/memory/YYYY-MM-DD_review_<topic>.md` and update `.ai/memory/INDEX.md`.
4. Generate HTML review report & auto-open in IntelliJ:
   - Run `python .ai/report_tool.py .ai/memory/YYYY-MM-DD_review_<topic>.md --open` to produce `.ai/reports/YYYY-MM-DD_review_<topic>.html` directly and open in IntelliJ.
5. In chat, keep output strictly concise: provide test execution metrics and review verdict with clickable HTML report links.
