# Agent Permissions — Standing Approvals

This file records approval the repository owner granted in-session
(2026-10-23) so agents do not need to wait for per-action confirmation.
It is referenced by `AGENTS.md` (Guardrails & Boundaries).

## Standing approvals (pre-authorized)

- Creating/deleting **agent-created feature branches** (`<type>/<issue#>-<slug>`).
  Deleting `dev`, `stag`, or `prod` — including by merging a promotion-hop
  PR with `--delete-branch` (which deletes the head branch) — is **not**
  pre-authorized; merge integration hops without it and clean up feature
  branches manually.
- Commits, pushes to agent-created branches, and `origin` remote operations.
- Creating/updating/closing GitHub issues and comments.
- Creating PRs targeting `prod` and **merging own PRs** (`gh pr merge --merge --delete-branch`)
  once PR checklist gates pass (tests pass, black/isort/mypy/flake8 clean,
  no secrets, AC met, docs updated).
- Running: git, gh, python/pip in `venv/`, pytest, black, isort, mypy, flake8,
  alembic, uvicorn, docker build / `docker compose up --build`.
- Installing declared dependencies into the local venv.
- Creating/editing/deleting any file inside the workspace needed for an
  accepted issue, including v1 legacy removal (`app/` v1 code, old
  requirements) once the corresponding issue is merged.
- DB schema changes and Alembic migrations as specified by the approved v2
  design (docs/superpowers/specs/). Local disposable test DBs may be created
  and dropped freely.
- Temporary network access to GitHub endpoints and package installs.

## Explicitly NOT pre-authorized (still require live user approval)

- `git push --force` (including to `prod`/`stag`/`dev` or agent-created
  branches with history).
- Publishing, releasing, or deploying to any external host.
- Committing real secrets or editing `.env` with real credentials.
- Disabling or bypassing test/lint/type gates or Git hooks.
- Operations on repos other than `mramitdas/RapidNotifyBot`.
- PRs that break the merge chain: from a feature branch into `stag`/`prod`
  directly, or from `stag` into `prod` directly. Promotion is `dev` →
  `stag` → `prod`, one hop per PR (see AGENTS.md).

Rule: if an action is on the NOT list, stop and ask; everything else on the
standing list may proceed autonomously.
