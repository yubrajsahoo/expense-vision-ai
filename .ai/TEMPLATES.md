# Standard Templates for Multi-Agent Artifacts

Use these standardized Markdown templates when generating analysis drafts, plans, test-run logs, and code reviews.

---

## 1. Analysis & Planning Template
Save to: `.ai/memory/YYYY-MM-DD_{analysis,plan}_<topic>.md` (compiled to HTML via `python .ai/report_tool.py [file] --open`)

```markdown
# [Analysis / Plan]: [Topic Name]

- **Date:** YYYY-MM-DD
- **Agent:** Antigravity Gemini 3.8
- **Scope:** [Module or Feature Affected]
- **Status:** DRAFT | APPROVED

---

## 1. Executive Summary
[Brief 2-3 sentence overview of the requirement, issue, or objective.]

---

## 2. Requirements & Edge Cases
- **Requirement 1:** [Description]
- **Requirement 2:** [Description]
- **Constraints & Edge Cases:**
  - [Constraint 1]
  - [Constraint 2]

---

## 3. Module Boundaries & Affected Files

| Affected File | Action (New / Modified) | Responsibility |
| :--- | :--- | :--- |
| `path/to/file` | New / Modified | [Description] |

---

## 4. Phased Execution Steps (For Plans)
- [ ] Phase 1: [Preparation & Interface Design]
- [ ] Phase 2: [Core Implementation]
- [ ] Phase 3: [Integration, Error Handling & Tests]

---

## 5. Security & Performance Considerations
- **Security:** [Auth, secret handling, input sanitization]
- **Performance:** [Query efficiency, caching, timeouts]

---

## 6. Verification Strategy
- **Unit / Slice Tests:** [Target classes / functions]
- **Execution Command:** `[Command to verify]`

---

## 7. Interactive Review Gate (🛑 Approval Checkpoint)
- **Draft Status:** Ready for user review.
- **Questions for User:** [Any open decisions or scope questions]
```

---

## 2. Implementation Report Template
Save to: `.ai/memory/YYYY-MM-DD_implementation_<topic>.md` (compiled to HTML via `python .ai/report_tool.py [file] --open`)

```markdown
# Implementation Report: [Topic Name]

- **Date:** YYYY-MM-DD
- **Agent:** Gemini 4 Hydrogen (Implementation) & Gemini 3.8 (Test Authoring)
- **Scope:** [Module or Feature Affected]
- **Status:** COMPLETED

---

## 1. Summary of Changes
[Brief 2-3 sentence overview of files modified, logic implemented, and tests authored.]

---

## 2. Modified & Created Files

| File | Status | Description |
| :--- | :--- | :--- |
| `path/to/file` | New / Modified | [Summary of code added] |

---

## 3. Authored Tests

| Test Class / Function | Test Type | Coverage Focus |
| :--- | :--- | :--- |
| `path/to/test` | Unit / Slice | [Target functionality tested] |

---

## 4. Architectural & Convention Checks
- [ ] Conforms to Java 25 / Python 3.12+ conventions
- [ ] No secrets committed; configurations abstracted into environment properties
- [ ] Tests authored in-memory without external network dependencies
- [ ] Ready for Quality Guardian verification
```

---

## 3. Test Run Report Template
Save to: `.ai/memory/YYYY-MM-DD_debug_<topic>.md` (compiled to HTML via `python .ai/report_tool.py [file] --open`)

```markdown
# Test Run Report: [Topic Name]

- **Date:** YYYY-MM-DD
- **Agent:** OpenCode (Test Runner)
- **Target Suite:** [Java / Python]
- **Command:** `[Executed Command]`

---

## 1. Execution Summary

| Metric | Value |
| :--- | :--- |
| **Overall Status** | PASSED / FAILED |
| **Total Tests** | [Number] |
| **Passed** | [Number] |
| **Failed** | [Number] |
| **Skipped** | [Number] |
| **Duration** | [Seconds]s |
| **Code Coverage** | [Percentage]% (Threshold: 80%) |

---

## 2. Test Suite Breakdown

| Test Suite / Class | Passed | Failed | Duration | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `SuiteName` | X | Y | Z.s | ... |

---

## 3. Failure Analysis & Diagnostics (If Any)
- **Failing Test:** `[ClassName.testMethod]`
- **Stack Trace / Error:**
  ```text
  [Error message]
  ```
- **Root Cause Diagnosis:** [Detailed explanation]
- **Recommended Fix:** [Concrete action needed to resolve]
```

---

## 4. Code Review Template
Save to: `.ai/memory/YYYY-MM-DD_review_<topic>.md` (compiled to HTML via `python .ai/report_tool.py [file] --open`)

```markdown
# Code Review: [Topic Name]

- **Date:** YYYY-MM-DD
- **Agent:** Codex
- **Commit / Scope:** [Branch or Diff Scope]
- **Overall Verdict:** APPROVED / REVISIONS REQUESTED

---

## 1. Executive Summary
[Brief assessment of code quality, adherence to conventions, and architectural soundness.]

---

## 2. Findings Summary

| Severity | Count | Blocking? |
| :--- | :--- | :--- |
| **Critical** | 0 | Yes |
| **Major** | 0 | Recommended |
| **Minor** | 0 | Optional |

---

## 3. Detailed Findings
- **Critical (Must Fix):** None.
- **Major (Recommended):**
  - **File:** `path/to/file#L10`
  - **Issue:** [Description]
  - **Recommendation:** [Suggested code improvement]
- **Minor (Style / Nitpicks):**
  - **File:** `path/to/file#L25`
  - **Note:** [Description]

---

## 4. Convention Adherence Checklist
- [ ] Layer boundaries respected (Controllers -> Services -> Repositories)
- [ ] Secrets and credentials managed safely (no leakage in code/logs)
- [ ] Tests authored and passing with >=80% coverage
- [ ] Coding styles and formatting rules respected (Ruff / Java conventions)
```
