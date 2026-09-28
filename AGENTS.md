# Workflow Rules & Branching Strategy

## Git Branch & PR Rules (MANDATORY)

1. **No Direct Pushes to Main**:
   - Direct pushing to `main` is strictly prohibited.
   - Every change, feature, or bugfix MUST be performed on a dedicated feature or fix branch branched off `main` (e.g. `feature/...` or `fix/...`).

2. **Pull Request (PR) Standard**:
   - Submit changes via Pull Requests (PR).

3. **No Merge Commits (Rebase Only)**:
   - Do NOT create merge commits when updating or integrating branches.
   - Always use `git rebase` (e.g., `git rebase main`) to maintain a clean, linear git history.
