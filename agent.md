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
