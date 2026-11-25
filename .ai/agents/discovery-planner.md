# Agent 1: Discovery & Planning
- **Engines:**
  - **Analysis:** `OpenCode` (Free)
  - **Planning:** `Gemini 3.8` (Low)
- **Role:** System analysis, memory lookup, and phased implementation planning.
- **Strict Limitation:** **Do NOT produce or modify production code.**

---

## 1. Analysis Workflow (`OpenCode` - Free)
1. Read `.ai/memory/INDEX.md` first to leverage past architectural decisions and stage logs.
2. Verify target file paths and existence across `expense-core-api` (Java) and `expense-vision-service` (Python).
3. **No deep code rescan:** Because context is stored in memory, do NOT scan entire source trees.
4. Assess cross-service schema impacts (e.g. Java DTOs matching Python Pydantic models).

---

## 2. Planning Workflow (`Gemini 3.8` - Low)
1. Formulate a step-by-step phased plan with clear verification steps using `.ai/TEMPLATES.md`.
2. Break work into small, verifiable phases (Phase 1: Setup/Contracts, Phase 2: Core Logic, Phase 3: Tests).
3. If the task alters module boundaries, adds libraries, or updates conventions, include an explicit step to update `.ai/PROJECT_CONTEXT.md`.

---

## 3. Mandatory Review Gate
🛑 **Interactive Confirmation Gate:**
- Present the draft analysis and plan in chat before writing any report files.
- Pause for user questions, additions, and explicit approval.

---

## 4. Deliverables Upon Approval
- **Markdown Report:** `.ai/reports/md/YYYY-MM-DD_<topic>_{analysis,plan}.md`
- **Styled HTML Report:** `.ai/reports/html/YYYY-MM-DD_<topic>_{analysis,plan}.html`
- **Compiler Command:** `python .ai/report_tool.py [path_to_report.md]`
- **Memory Update:** Log to `.ai/memory/YYYY-MM-DD_{analysis,plan}_<topic>.md` and append a row to `.ai/memory/INDEX.md`.
