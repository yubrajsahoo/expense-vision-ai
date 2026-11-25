# Agent 1: Discovery & Planning
- **Engines:**
  - **Analysis:** `OpenCode` (Free)
  - **Planning:** `Gemini 3.8` (Low)
- **Role:** System analysis, memory lookup, and phased implementation planning.
- **Strict Limitation:** **Do NOT produce or modify production code.**

---

## 1. Analysis Workflow (`OpenCode` - Free)
1. Read `.ai/memory/INDEX.md` first to leverage past architectural decisions and stage logs.
2. Read **only** explicitly required files for the current task. Do **NOT** read all files or scan source directories indiscriminately.
3. Take all other architectural details, module boundaries, and conventions from `.ai/memory/` and `.ai/PROJECT_CONTEXT.md`.
4. Assess cross-service schema impacts (e.g. Java DTOs matching Python Pydantic models).

---

## 2. Planning Workflow (`Gemini 3.8` - Low)
1. Formulate a step-by-step phased plan with clear verification steps using `.ai/TEMPLATES.md`.
2. Break work into small, verifiable phases (Phase 1: Setup/Contracts, Phase 2: Core Logic, Phase 3: Tests).
3. If the task alters module boundaries, adds libraries, or updates conventions, include an explicit step to update `.ai/PROJECT_CONTEXT.md`.

---

## 3. Automatic Report & Memory Generation
Immediately upon drafting the plan/analysis:
- **Memory Update:** Log to `.ai/memory/YYYY-MM-DD_{analysis,plan}_<topic>.md` and append a row to `.ai/memory/INDEX.md`.
- **HTML Report & Auto-Open in IntelliJ:**
  `python .ai/report_tool.py .ai/memory/YYYY-MM-DD_{analysis,plan}_<topic>.md --open`
- **HTML Only:** Generates `.ai/reports/YYYY-MM-DD_<topic>_{analysis,plan}.html` directly (no `.md` files or subfolders under `.ai/reports/`).

---

## 4. Mandatory Review Gate
🛑 **Interactive Confirmation Gate:**
- Automatically opens the HTML plan in IntelliJ IDEA for the user.
- **In chat, do NOT specify code dumps or lengthy plans.**
- Output ONLY a brief 2-3 sentence summary with clickable link to the HTML report.
- Pause for user confirmation before passing the task to Agent 2 (Full-Stack Engineer).
