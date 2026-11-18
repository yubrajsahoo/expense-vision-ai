# Implementation rules

1. Maintain clear boundaries between routing, configuration, and services.
   Route handlers should delegate business work to services; configuration must
   be obtained through the settings layer rather than hard-coded values.
2. Isolate external dependencies (for example, Gemini, HTTP clients,
   databases, queues, file stores, and command-line tools) behind a small,
   injectable boundary. This keeps unit tests deterministic and lets
   integration tests use the real dependency deliberately.
3. Handle expected malformed input and dependency failures explicitly. Return
   safe, documented errors and log useful context without logging secrets or
   sensitive image/receipt contents.
4. Prefer typed interfaces and validated Pydantic models at application
   boundaries. Preserve existing FastAPI response contracts unless the task
   explicitly changes them.
5. Do not make outbound calls during import, application creation, or module
   initialization. Calls to external services must occur only as part of an
   explicit request or service operation.
6. Do not add retry loops, background jobs, schema migrations, or new external
   services without explicit task scope and corresponding tests.
