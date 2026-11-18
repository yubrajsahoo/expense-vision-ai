# Test rules

This project has two deliberately different test suites. Classify every new
test before writing it; do not blur the boundary between them.

## Unit tests: `tests/unit/`

Unit tests verify one unit of behaviour in isolation. They must be fast,
deterministic, and runnable on any developer or CI machine without credentials
or infrastructure.

- Unit tests **must not** make network requests or call an external service.
  This includes real Gemini/API calls, databases, caches, message brokers,
  cloud storage, SMTP, and services started outside the test process.
- Mock or fake every external client at the boundary where this project calls
  it. Assert relevant request arguments and the handled success/failure result.
- Treat local executables and system services as external dependencies too.
  In particular, unit tests for `services.gatekeeper` must mock
  `pytesseract.image_to_string`; they must not require an installed Tesseract
  executable.
- FastAPI's `TestClient` is permitted in unit tests only when it runs the app
  in-process and the exercised endpoint does not call an external dependency.
  It must not target a running server by URL.
- Use generated values, small local fixtures, and `monkeypatch`/`unittest.mock`
  instead of real credentials, live data, time, randomness, or network state.

## Integration tests: `tests/integration/`

Integration tests verify this service against a real, externally running
dependency. They **must** make the intended external call; mocking that
dependency makes the test a unit test and it belongs in `tests/unit/` instead.

- Each integration test must be marked `@pytest.mark.integration` and clearly
  name the dependency it exercises.
- Integration tests must be opt-in. They may run only when
  `RUN_INTEGRATION_TESTS=1` is set and all required test-environment
  configuration is present. The default local and CI test command must exclude
  the `integration` marker.
- Use a dedicated non-production test account, project, endpoint, and data.
  Never point integration tests at production or use real customer receipts.
- Read credentials and endpoints from environment variables. Never hard-code,
  print, or assert a secret. Skip with a clear reason when opt-in configuration
  is absent; fail normally once an opted-in test has started and the service is
  unavailable or returns an unexpected result.
- Keep assertions focused on the contract that crosses the boundary. Make test
  data uniquely identifiable and clean it up when the external service creates
  persistent resources.

## Test execution and maintenance

1. Run unit tests independently with `uv run pytest tests/unit`.
2. Run opted-in integration tests with
   `RUN_INTEGRATION_TESTS=1 uv run pytest -m integration tests/integration`
   (use the shell-appropriate environment-variable syntax on Windows).
3. When adding the first marked integration test, register the `integration`
   pytest marker and configure the default pytest command to exclude it. Keep
   this test policy and `pyproject.toml` in sync.
4. Tests must assert observable behaviour, including meaningful error paths;
   avoid assertions that only duplicate implementation details.
