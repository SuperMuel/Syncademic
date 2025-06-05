- You use Python 3.11
- Prefer Pydantic models over raw dictionaries for input validation.
- You like functional, declarative programming. Strive for pure functions and immutable data structures where practical, as they are inherently easier to test and reason about.
- Respect the Single Responsibility Principle (SRP)


Error Handling and Validation
- Handle errors and edge cases at the beginning of functions.
- Use early returns for error conditions to avoid deeply nested if statements.
- Place the happy path last in the function for improved readability.
- Avoid unnecessary else statements; use the if-return pattern instead.
- Use guard clauses to handle preconditions and invalid states early.
- Implement proper error logging and user-friendly error messages.
- Use `assert` to catch developer errors.

Documentation & Comments
- Use docstrings for all public functions, methods and classes. 
- Write docstrings for public APIs that explain usage and purpose, not implementation
- Focus on "Why use this?" and "How to use this correctly?"
- Skip docstrings for trivial functions where name and type hints are self-explanatory
- Prefer self-documenting code over comments, but add comments for complex business logic or "why" decisions

Type hints
- Use type hints 
- Prefer `list[str | None]` over `List[Optional[str]]` (Python 3.9+ style)

Code Formatting
- Use Ruff (replaces `black`, `isort`, `flake8`)

Testing
- Use Pytest
- Aim for high test coverage
- Write testable code by minimizing patching. Favor Dependency Injection (DI).
- Use `pytest.mark.parametrize` when testing multiple inputs
- Use `uv run python -m pytest --cov` for coverage reports


Dependency and project management using UV (replaces pip, pip-tools, poetry...)
- Sync dependencies: `uv sync` (Automatically creates or updates `.venv`)
- Install dependencies: `uv add <package>`
- Install dev dependencies: `uv add --dev <package>`
- Remove dependencies: `uv remove <package>`

- `uv run` automatically updates the environment if needed
- Run a Python script with `uv run <script-name>.py`
- Run Python tools like Pytest with `uv run pytest` or `uv run ruff check`
