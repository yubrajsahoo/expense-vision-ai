# AI agent rules

These rules apply to every change in this repository. Read all files in
`.ai/rules/` before making a change.

1. Inspect the relevant implementation, configuration, and existing tests
   before proposing or making a change. Preserve established behaviour unless
   the task explicitly asks to change it.
2. Keep changes small and scoped to the request. Do not refactor unrelated
   code, rename public APIs, or alter application configuration as incidental
   cleanup.
3. Follow the existing stack and conventions: Python 3.12+, FastAPI,
   Pydantic Settings, pytest, and Ruff. Keep source code under `src/` and
   tests under `tests/`.
4. Treat API keys, credentials, and service URLs as configuration. Never add
   real secrets, tokens, or customer data to source code, tests, fixtures, or
   documentation.
5. Any behaviour change must include appropriately classified tests as defined
   in `test_rules.md`.
6. Before completing a change, run the relevant formatter, linter, and test
   commands when the environment permits. Report commands that could not run
   and why.
