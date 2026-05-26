# System Prompt / Project Rules

## Mandatory Handoff and Git Sync
This rule ensures that the project's progress is persistently documented and immediately backed up to the remote repository.

### Trigger
- Whenever a feature is implemented, modified, fixed, or any functional changes are completed.

### Mandatory Actions

#### 1. Update the Handoff File
- Immediately create or update a `HANDOFF.md` file at the root of the workspace.
- The `HANDOFF.md` file must contain:
  - **Summary of Changes**: Clear, bulleted details of the features added, modified, or fixed in this iteration.
  - **Current System State**: A description of what is currently working, what is in progress, and any known limitations.
  - **Verification & Testing**: Summary of how the changes were verified/tested and the outcome.
  - **Next Steps**: Next actions for the developers or AI agents to pick up.

#### 2. Git Commit and Push
- Check if Git is initialized and if there is a connected remote repository.
- Stage all changes, including the updated `HANDOFF.md` file (`git add .`).
- Commit the changes with a concise and descriptive message (e.g., `feat: [feature name] and updated handoff`).
- Push the commit to the active remote branch (`git push`).

## Python Clean Code Standards
All Python code written or refactored for this project MUST strictly adhere to the following clean code principles:

### 1. Structural Principles
- **Single Responsibility Principle (SRP):** Each class and function must do exactly one thing. UI logic must be strictly separated from business/controller logic.
- **Fail Fast:** Validate inputs and fail early (e.g., return early or raise an Exception) to avoid deeply nested `if/else` arrow code.

### 2. Typing and Documentation
- **Type Hinting:** 100% of function arguments and return types MUST have type hints (e.g., `def process(data: List[Dict[str, Any]]) -> None:`). Use `Optional` and `Union` where appropriate.
- **Docstrings:** All classes, methods, and functions must be documented using the **Google Docstring Format**, clearly specifying `Args:`, `Returns:`, and `Raises:` when applicable.

### 3. Naming Conventions (PEP 8)
- Classes: `PascalCase`.
- Functions and Variables: `snake_case`.
- Constants: `UPPER_SNAKE_CASE`.
- Avoid abbreviation; variable names must be fully descriptive (e.g., `user_list` instead of `ul`).

### 4. Tooling (Auto-Formatting)
- Code must be formatted using **Black** (for line lengths, quotes, spacing).
- Imports must be sorted using **isort** (Standard library -> Third Party -> Local/First Party).
