# Gemini Multi-Agent Workflow & Instructions

## 1. Startup Protocol & Common Memory
Every agent interacting with this repository shares a unified **Common Memory** and must follow this startup sequence:
1. **Read Project Context & Common Memory:**
   - Always read `.ai/PROJECT_CONTEXT.md` to understand architecture, module boundaries, tech stack, and conventions.
   - Always read `.ai/memory/INDEX.md` first. Memory preserves previous architectural decisions, file mappings, and past stage logs so agents do **not** need to rescan the codebase.
2. **Strict Targeted File Reading (No Indiscriminate Reads):**
   - Do **NOT** read all files across directories. Read **only** explicitly required files directly relevant to the current task.
   - Take all other architectural details, schema structures, and context from `.ai/memory/` and `.ai/PROJECT_CONTEXT.md`.
3. **Flat Memory Architecture:**
   - `.ai/memory/` stores all memory logs directly in a **flat directory** without subfolders (e.g. `.ai/memory/YYYY-MM-DD_<stage>_<topic>.md` alongside `.ai/memory/INDEX.md`).

---

## 2. The 3-Agent Routing Matrix & Assigned Engines

All lifecycle tasks are executed across **3 specialized agents** configured with specific models and reasoning tiers:

| Agent | Stage Covered | Assigned Engine & Tier | Role File | Mandatory Gate |
| :--- | :--- | :--- | :--- | :--- |
| **Agent 1: Discovery & Planning** | **Analysis**<br>───<br>**Planning** | `OpenCode` (Free)<br>───<br>`Gemini 3.8` (Low) | [`.ai/agents/discovery-planner.md`](.ai/agents/discovery-planner.md) | 🛑 **Plan Confirmation Gate:** Generates HTML plan, auto-opens in IntelliJ, keeps chat concise, awaits approval. |
| **Agent 2: Full-Stack Engineer** | **Implementation**<br>───<br>**Test Authoring** | `Gemini 4 Hydrogen` (High)<br>───<br>`Gemini 3.8` (Medium) | [`.ai/agents/fullstack-engineer.md`](.ai/agents/fullstack-engineer.md) | 🛑 **Implementation Review Gate:** Generates HTML implementation report, auto-opens in IntelliJ, keeps chat concise, awaits confirmation before test run. |
| **Agent 3: Quality & Verification** | **Test Execution**<br>───<br>**Code Review** | `OpenCode` (Free)<br>───<br>`Codex` (Free) | [`.ai/agents/quality-guardian.md`](.ai/agents/quality-guardian.md) | Generates HTML test-run and review reports, auto-opens in IntelliJ, logs findings to memory. |

---

### Detailed Agent Specifications & Workflows

#### 📐 Agent 1: Discovery & Planning
- **Components:**
  - **Analysis (`OpenCode` - Free):** Reads `.ai/memory/INDEX.md` and verifies required file paths without scanning unneeded source code. Identifies cross-service schema impacts.
  - **Planning (`Gemini 3.8` - Low):** Formulates step-by-step phased plan using `.ai/TEMPLATES.md`.
- **Automatic Report & Memory Generation:**
  - Automatically log memory and compile the HTML report upon finalizing the plan:
    - Memory Update: Save to `.ai/memory/YYYY-MM-DD_{analysis,plan}_<topic>.md` and update `.ai/memory/INDEX.md`.
    - HTML Report Only: Compile directly to `.ai/reports/YYYY-MM-DD_<topic>_{analysis,plan}.html` and auto-open in IntelliJ:
      `python .ai/report_tool.py .ai/memory/YYYY-MM-DD_{analysis,plan}_<topic>.md --open`
    - No `.md` report files or subfolders under `.ai/reports/`.
- **Mandatory Review Gate:**
  - 🛑 **Interactive Confirmation Gate:**
    - Open the styled HTML plan file directly in IntelliJ (`--open`).
    - **In chat, do NOT specify all details, code, or large plans.**
    - Keep chat strictly concise: state that the plan was generated and opened in IntelliJ, provide clickable file links, and pause for user approval before implementation.
- **Strict Limitation:** **Do NOT produce or modify production code.**

#### 🛠️ Agent 2: Full-Stack Engineer
- **Components:**
  - **Implementation (`Gemini 4 Hydrogen` - High):** Executes approved plans from memory adhering to `.ai/PROJECT_CONTEXT.md` (Java 25 records, constructor injection, `@Transactional`, `RestClient` timeouts; Python Pydantic v2, Ruff formatting).
  - **Test Authoring (`Gemini 3.8` - Medium):** Writes in-memory JUnit 5 / Mockito slice tests (`@DataJpaTest`, `@RestClientTest`) and Python zero-network unit tests (`tests/unit/`).
- **Automatic Report & Memory Generation:**
  - Automatically log memory, compile the HTML implementation report, and auto-open in IntelliJ:
    - Memory Update: Save to `.ai/memory/YYYY-MM-DD_implementation_<topic>.md` and update `INDEX.md`.
    - HTML Report Only: Compile directly to `.ai/reports/YYYY-MM-DD_implementation_<topic>.html` and auto-open in IntelliJ:
      `python .ai/report_tool.py .ai/memory/YYYY-MM-DD_implementation_<topic>.md --open`
- **Mandatory Review Gate:**
  - 🛑 **Implementation Review Gate:** Keep chat strictly concise. Present brief change summary with clickable link to implementation HTML report. Await user confirmation before test execution.
- **Strict Limitation:** Keep edits strictly scoped to the approved plan; no unrelated refactoring.

#### 🛡️ Agent 3: Quality & Verification Guardian
- **Components:**
  - **Test Runner (`OpenCode` - Free):** Runs `./mvnw test` and `uv run pytest tests/unit`. Verifies coverage $\ge 80\%$. Diagnoses failure root causes.
  - **Code Review (`Codex` - Free):** Reviews diffs against Correctness, Security/PII, Performance, and Conventions.
- **Automatic Report & Memory Generation:**
  - Automatically log memory, compile HTML reports, and auto-open in IntelliJ:
    - Memory Update: Save test logs to `.ai/memory/YYYY-MM-DD_debug_<topic>.md` and review findings to `.ai/memory/YYYY-MM-DD_review_<topic>.md`, update `INDEX.md`.
    - HTML Reports: Compile and auto-open in IntelliJ:
      `python .ai/report_tool.py .ai/memory/YYYY-MM-DD_debug_<topic>.md --open`
      `python .ai/report_tool.py .ai/memory/YYYY-MM-DD_review_<topic>.md --open`
- **Deliverables & Chat Output:**
  - Keep chat strictly concise: report passing test metrics and overall code review verdict with clickable HTML report links.
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
     ├─ Planning (Gemini 3.8 Low - drafts plan)
     └─ Generates HTML Plan Report & Auto-Opens in IntelliJ
     │
     ▼
🛑 Plan Confirmation Gate (User reviews plan in IntelliJ / approves implementation)
     │
     ▼
[Agent 2: Full-Stack Engineer]
     ├─ Implementation (Gemini 4 Hydrogen High - writes code)
     ├─ Test Authoring (Gemini 3.8 Medium - writes unit/slice tests)
     └─ Generates HTML Implementation Report & Auto-Opens in IntelliJ
     │
     ▼
🛑 Implementation Review Gate (User reviews report in IntelliJ / approves test run)
     │
     ▼
[Agent 3: Quality & Verification]
     ├─ Test Execution (OpenCode Free - runs tests & diagnoses)
     ├─ Code Review (Codex Free - ranks findings & verifies security)
     └─ Generates HTML Test & Review Reports & Auto-Opens in IntelliJ
     │
     ▼
All HTML Reports Finalized (.ai/reports/) & Common Memory Updated (.ai/memory/INDEX.md)
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

## 5. HTML Reporting Protocol (HTML Only)
Every agent stage completes by generating an HTML report and automatically opening it in IntelliJ:
- **HTML Report Only:** `.ai/reports/YYYY-MM-DD_<stage>_<topic>.html` (flat directory without subfolders).
- **Auto-Open in IntelliJ:** Every report is automatically opened in IntelliJ IDEA upon generation via `python .ai/report_tool.py [path_to_memory_file.md] --open`.
- **No `.md` files in reports:** Do not create `.md` report files or subfolders under `.ai/reports/`. Markdown notes live exclusively in `.ai/memory/`.
- **Chat Output:** Do **NOT** paste or dump report or code contents in chat. Provide only a brief summary with clickable HTML report link and await confirmation.
