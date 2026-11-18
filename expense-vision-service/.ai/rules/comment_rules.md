# Comment and documentation rules

1. Write comments only when they explain intent, a non-obvious constraint, or
   a decision that code alone cannot make clear. Do not narrate obvious code.
2. Keep comments accurate when changing the code they describe; remove stale
   comments rather than leaving misleading history.
3. Public modules, functions, and classes should use concise docstrings that
   state their purpose, important inputs, return values, and relevant failure
   behaviour.
4. Do not put secrets, private endpoints, production identifiers, or
   personally identifiable financial data in comments, docstrings, examples,
   or test fixtures.
5. In tests, use a short docstring or descriptive test name that states the
   expected behaviour. Document why an external dependency is mocked or why a
   real integration call is required when that reason is not obvious.
