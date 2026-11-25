# Gemini Multi-Agent Workflow & Instructions

## 1. Startup Protocol & Common Memory
Every agent interacting with this repository shares a unified **Common Memory** and must follow this startup sequence:
1. **Read Project Context & Common Memory:**
   - Always read `.ai/PROJECT_CONTEXT.md` to understand architecture, module boundaries, tech stack, and conventions.
   - Always read `.ai/memory/INDEX.md` first. Memory preserves previous architectural decisions, file mappings, and past stage logs so agents do **not** need to rescan the codebase.
2. **Minimal Targeted File Inspection:**
   - Verify file names and locations only. Do **never** read source directories indiscriminately.
3. **Flat Memory Architecture:**
   - `.ai/memory/` stores all memory logs directly in a **flat directory** without subfolders (e.g. `.ai/memory/YYYY-MM-DD_<stage>_<topic>.md` alongside `.ai/memory/INDEX.md`).

---

## 2. The 3-Agent Routing Matrix & Assigned Engines

All lifecycle tasks are executed across **3 specialized agents** configured with specific models and reasoning tiers:

| Agent | Stage Covered | Assigned Engine & Tier | Role File | Mandatory Gate |
| :--- | :--- | :--- | :--- | :--- |
| **Agent 1: Discovery & Planning** | **Analysis**<br>───<br>**Planning** | `OpenCode` (Free)<br>───<br>`Gemini 3.8` (Low) | [`.ai/agents/discovery-planner.md`](.ai/agents/discovery-planner.md) | 🛑 **Interactive Confirmation Gate:** Present draft, answer user questions, obtain approval before creating report. |
| **Agent 2: Full-Stack Engineer** | **Implementation**<br>───<br>**Test Authoring** | `Gemini 4 Hydrogen` (High)<br>───<br>`Gemini 3.8` (Medium) | [`.ai/agents/fullstack-engineer.md`](.ai/agents/fullstack-engineer.md) | 🛑 **Implementation Review Gate:** Present code & test diff summary to user before running test suite. |
| **Agent 3: Quality & Verification** | **Test Execution**<br>───<br>**Code Review** | `OpenCode` (Free)<br>───<br>`Codex` (Free) | [`.ai/agents/quality-guardian.md`](.ai/agents/quality-guardian.md) | Dual test reports generated; severity-ranked review findings logged to memory. |

---

### Detailed Agent Specifications & Workflows

#### 📐 Agent 1: Discovery & Planning
- **Components:**
  - **Analysis (`OpenCode` - Free):** Reads `.ai/memory/INDEX.md` and verifies file existence/paths without scanning all source code. Identifies cross-service schema impacts (`expense-core-api` DTOs vs `expense-vision-service` Pydantic models).
  - **Planning (`Gemini 3.8` - Low):** Formulates step-by-step phased plan using `.ai/TEMPLATES.md`.
- **Mandatory Review Gate:**
  - 🛑 **Interactive Confirmation Gate:** Present draft plan & analysis in chat. Pause for user questions, additions, and approval.
- **Deliverables:**
  - On user approval, generate dual reports:
    - Markdown: `.ai/reports/md/YYYY-MM-DD_<topic>_{analysis,plan}.md`
    - Styled HTML: `.ai/reports/html/YYYY-MM-DD_<topic>_{analysis,plan}.html`
    - Run: `python .ai/report_tool.py [path_to_report.md]`
  - Log stage to `.ai/memory/YYYY-MM-DD_{analysis,plan}_<topic>.md` and update `.ai/memory/INDEX.md`.
- **Strict Limitation:** **Do NOT produce or modify production code.**

#### 🛠️ Agent 2: Full-Stack Engineer
- **Components:**
  - **Implementation (`Gemini 4 Hydrogen` - High):** Executes approved plans from memory adhering to `.ai/PROJECT_CONTEXT.md` (Java 25 records, constructor injection, `@Transactional`, `RestClient` timeouts; Python Pydantic v2, Ruff formatting).
  - **Test Authoring (`Gemini 3.8` - Medium):** Writes in-memory JUnit 5 / Mockito slice tests (`@DataJpaTest`, `@RestClientTest`) and Python zero-network unit tests (`tests/unit/`).
- **Mandatory Review Gate:**
  - 🛑 **Implementation Review Gate:** Present the diff summary and authored tests to the user for review. Await user confirmation before test execution.
- **Deliverables:**
  - Change log recorded to `.ai/memory/YYYY-MM-DD_implementation_<topic>.md` and updated in `INDEX.md`.
- **Strict Limitation:** Keep edits strictly scoped to the approved plan; no unrelated refactoring.

#### 🛡️ Agent 3: Quality & Verification Guardian
- **Components:**
  - **Test Runner (`OpenCode` - Free):** Runs `./mvnw test` and `uv run pytest tests/unit`. Verifies coverage $\ge 80\%$. Diagnoses failure root causes.
  - **Code Review (`Codex` - Free):** Reviews diffs against Correctness, Security/PII, Performance, and Conventions.
- **Deliverables:**
  - Dual test-run report: `.ai/reports/md/YYYY-MM-DD_<topic>_test-run.md` and HTML via `python .ai/report_tool.py`.
  - Severity-ranked review report (🔴 Critical / 🟡 Major / 🟢 Minor) saved to `.ai/memory/YYYY-MM-DD_review_<topic>.md`.
  - Log update in `.ai/memory/INDEX.md`.
- **Strict Limitation:** **Do NOT alter business logic or weaken assertions to make tests pass.**

---

## 3. Unified Request Lifecycle Flow

For any single user request, the agents execute sequentially through the shared memory pipeline:

```
User Request
     │
     ▼
[Agent 1: Discovery & Planning]
     ├─ Analysis (OpenCode Free - reads memory & checks files)
     └─ Planning (Gemini 3.8 Low - drafts plan)
     │
     ▼
🛑 Plan Confirmation Gate (User questions / refinements / approval)
     │
     ▼
[Agent 2: Full-Stack Engineer]
     ├─ Implementation (Gemini 4 Hydrogen High - writes code)
     └─ Test Authoring (Gemini 3.8 Medium - writes unit/slice tests)
     │
     ▼
🛑 Implementation Review Gate (User reviews diff / approves test execution)
     │
     ▼
[Agent 3: Quality & Verification]
     ├─ Test Execution (OpenCode Free - runs tests & diagnoses)
     └─ Code Review (Codex Free - ranks findings & verifies security)
     │
     ▼
Dual Reports Finalized (.ai/reports/) & Common Memory Updated (.ai/memory/INDEX.md)
```

---

## 4. Common Memory & Context Maintenance Protocol

### A. Memory Update Protocol (Every Change)
1. **Destination:** Save every task output directly into `.ai/memory/YYYY-MM-DD_<stage>_<short-kebab-case-topic>.md` (flat directory without subfolders; `<stage>` is `analysis`, `plan`, `implementation`, `testing`, `review`, or `debug`).
2. **Registration:** Immediately append a 1-line row to `.ai/memory/INDEX.md`:
   `| Date | Stage | Agent | File | Summary |`
   *(Or run: `python .ai/report_tool.py --log --stage <stage> --agent <agent> --topic <topic> --summary <summary>`)*

### B. Project Context Update Protocol (`PROJECT_CONTEXT.md`)
- **When to Update:** Whenever a change impacts the broader architecture, including:
  1. Adding, removing, or renaming modules, packages, or services (e.g. adding `expense-web-ui`).
  2. Introducing new external libraries, databases, or cloud integrations (e.g. Redis, new Spring starters, new Pydantic packages).
  3. Modifying public endpoint routes, core DTO/Pydantic contracts, or security filters.
  4. Adding or refining engineering, testing, or formatting conventions.
- **When NOT to Update:** Do **not** modify `PROJECT_CONTEXT.md` for routine bug fixes or internal logic tweaks that stay within existing module conventions. Memory logs (`.ai/memory/`) capture those.

---

## 5. Dual Reporting Protocol (Markdown & HTML)
For every **Analysis/Plan** and **Test Run**:
- Markdown: `.ai/reports/md/YYYY-MM-DD_<topic>_{analysis,plan,test-run}.md`
- HTML: `.ai/reports/html/YYYY-MM-DD_<topic>_{analysis,plan,test-run}.html`
- Compile using: `python .ai/report_tool.py [path_to_report.md]`
