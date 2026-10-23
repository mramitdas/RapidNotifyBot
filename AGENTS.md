# AGENTS.md

Rules every AI agent (and human contributor) must follow when working in this
repository. Sections `Technical Stack`, `Commands`, and `Architecture & Code
Style` are project-specific. `Guardrails & Boundaries` is generic — it must be
carried over unchanged when this file is reused in another project, and only
the first three sections are rewritten.

---

## Technical Stack

<!-- PROJECT SPECIFIC — regenerate when reusing this file in another project -->

- **Language/Runtime:** Python 3.12+
- **Web framework:** FastAPI (latest)
- **Database:** PostgreSQL 16, SQLAlchemy 2.x (async) + asyncpg, Alembic migrations
- **Validation/config:** Pydantic v2 + pydantic-settings
- **Telegram:** python-telegram-bot (long polling, separate process)
- **Outbound HTTP:** httpx (async)
- **Logging:** structlog
- **Testing:** pytest + pytest-asyncio
- **Quality gates:** black, isort, mypy, flake8
- **Packaging/deploy:** Docker (multi-stage), docker-compose (api, bot, postgres)
- **License:** Apache 2.0

### Branch layout

- `prod` — default/protected branch. **Can be merged only from `stag`.**
- `stag` — staging. **Can be merged only from `dev`.**
- `dev` — integration branch. **Can be merged from any other branch.**
- Feature/issue branches (`<type>/<issue#>-<slug>`) target `dev`. Promotion
  through the chain happens via PRs only, one hop at a time.

---

## Commands

<!-- PROJECT SPECIFIC — regenerate when reusing this file in another project -->

Run all commands from the repository root unless stated otherwise.

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env   # then fill in real values

# Run
uvicorn app.main:app --reload          # API
python -m app.bot.rapidNotifyBot       # Telegram bot (separate terminal)

# Test
pytest                                  # all tests
pytest -k name                          # single test
pytest --cov=app                        # with coverage

# Quality gates (must be clean before every PR)
black . && isort .
mypy app
flake8 app

# Database
alembic upgrade head                     # apply migrations
alembic revision --autogenerate -m "..." # create migration

# Docker
docker compose up --build                # full local stack
```

**Rule:** never invent commands. Use these verbatim. If a required command is
missing, check the CI workflow config first; if not defined anywhere, stop and
ask instead of guessing.

---

## Architecture & Code Style

<!-- PROJECT SPECIFIC — regenerate when reusing this file in another project -->

### Architecture (v2 target)

- `app/api/` — FastAPI routers and endpoints (`POST /api/v1/notify`, key
  management, channel registration pages).
- `app/bot/` — Telegram bot process: `/start`, `/help`, `/subscribe`.
- `app/channels/` — channel adapters (telegram, slack, discord, webhook) behind
  a common interface; email is a documented extension point, not in v1.
- `app/db/` — SQLAlchemy models, Alembic migrations. Tables: `users`
  (telegram id, hashed API key, timestamps, rate-limit tier), `channels`
  (user_id, type, config JSON, enabled).
- `app/core/` — config (pydantic-settings), security (API key hashing, webhook
  URL SSRF validation, private-IP blocking), rate limiting (per-key sliding
  window stored in Postgres — no Redis).
- API auth: `X-API-Key` header or `Authorization: Bearer`. API keys shown once
  at subscribe, stored hashed.

### Code style

- Follow the existing pattern of the file/module you touch. Read neighboring
  code before writing anything new.
- Formatted by black + isort; type-hinted for mypy strictness over `app/`.
- Every behavior change ships with tests in the same PR; test names describe
  the behavior, not the implementation.
- Documentation (README, `docs/`) is updated in the same PR whenever setup,
  behavior, or the API contract changes.
- No TODO markers, commented-out code, or dead files left behind.

---

## Guardrails & Boundaries

<!-- GENERIC — do not modify when reusing this file in another project -->

### 1. Anti-hallucination

- **Cite, never guess.** Every file, function, command, or config an agent
  references must exist in the repo right now — verify by reading before
  acting. No "it should probably be in…" reasoning.
- **No invented APIs.** Never use a library method from memory; read the
  installed package for the pinned version in use. Versions come from the
  manifests, not from recollection.
- **Read before edit.** A file must be fully read (not just grepped) before it
  is edited.
- **Verify before claiming.** Never say "done", "passing", or "fixed" without
  having run the actual command and seen real output.
- **Acknowledge unknowns.** Unsure about an env value, expected behavior, or
  secret? Stop and ask. Never invent credentials, URLs, or DB values.
- **No silent fallbacks.** If a step fails, report the real error verbatim.
  Do not work around it by editing unrelated files.
- **Diff-check after edits.** After every edit, review `git diff` to confirm
  only intended changes.

### 2. Scope discipline (no overreach)

- One issue = one PR = one logical change. Strictly implement only what the
  accepted issue defines (its AC).
- No drive-by refactors, renames, or formatting-only edits; no "while I'm in
  here" changes. Spotted problems → create a new issue, do not fix inline.
- No unrequested suggestions at the end of a task. Finish, report, stop.
  Ideas belong in GitHub issues.
- One-way decisions (schema changes, API contracts, migrations) are proposed
  in 1–3 lines and approved before applying.
- Never create `v2`, `copy`, `.new`, `backup`, or `-final` variants of files;
  edit in place.

### 3. Issue → branch → PR workflow

- Every task/feature starts as a GitHub issue before any code.
- Branch naming: `<type>/<issue#>-<slug>` (e.g. `feat/12-rate-limiting`).
- One task = one commit: conventional commits (`feat:`, `fix:`, `chore:`,
  `docs:`, `test:`), subject ≤ 50 chars, commit body ends with `refs #N`.
- Work happens on the issue branch; the PR targets `dev`. Promotion is
  sequential and PR-only: `dev` → `stag` → `prod`. Never skip or reorder
  a hop; PRs into `prod` must come from `stag` only, PRs into `stag` from
  `dev` only.
- **PR checklist gates (all required before merge):**
  - tests pass (real command output),
  - black/isort/mypy/flake8 clean,
  - no secrets and no `.env` in the diff,
  - acceptance criteria demonstrably met,
  - docs updated if behavior/setup changed,
  - PR targets the correct branch in the chain (`dev` ← branch,
    `stag` ← `dev`, `prod` ← `stag`).
- Issue is closed **only** after its PR is merged. Never close otherwise.
- Never commit or PR directly to protected branches (`prod`, `stag`, `main`),
  even for docs. No skip-hooks (`--no-verify`), no force-pushing.
- **Never head-delete integration branches.** Merging a PR with
  `gh pr merge --delete-branch` deletes the PR's head branch, so use it
  only for feature/issue branches. PRs whose head is `dev`, `stag`, or
  `prod` (promotion hops) must be merged without `--delete-branch`.
  Feature-branch cleanup is manual or guarded by GitHub branch protection.

### 4. Task granularity & tracking

- One task = ≤ 30 minutes of work = one commit = one checkbox in its issue.
- A task exceeding 30 minutes is split into subtasks within the issue.
- Every task has executable acceptance criteria (a test, a command, or a
  demonstrable behavior). Done = AC passes — nothing more, nothing less.
- Feature issues are parents with a task checklist; each item is its own
  branch/PR and ≤ 30 minutes.
- Status is communicated through issue/PR comments, not memory or chat-only.

### 5. Security

- Never commit secrets, tokens, API keys, or `.env`; `.env` is git-ignored.
  Real secrets live only in the local `.env` / deployment secret store.
- Dependencies are added/changed only through the requirement manifests
  (`requirements/*.txt`); lockfile or pin updates are separate commits.
- Never disable lint, typecheck, or test gates to make something pass.

### 6. Destructive & irreversible operations

- The following require explicit, current-session user approval before
  running: `git push --force`, branch deletion (including of integration
  branches `dev`, `stag`, `prod`), dropping/updating-down DB
  migrations, deleting files beyond the current task's scope, publishing or
  releasing, and anything modifying `main`/`prod` history.
- Never touch files outside the workspace directory.

### 7. On session start

- Read this file first.
- Check open issues and PRs to resume context; rely on issue/PR comments, not
  memory of a previous session.
- Confirm the target branch and issue number before the first action.
