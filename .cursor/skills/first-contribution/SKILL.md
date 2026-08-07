---
name: first-contribution
description: >-
  Guided first contribution for a Dagster public-API change. Takes an issue
  description and runs Plan → Implement → Test → Verify without skipping ahead.
  Use when the user invokes /first-contribution or asks to walk a first
  contribution through the public-API fan-out.
---

# First contribution

Input: the issue description (and any linked issue URL/number) supplied after `/first-contribution`.

Run **exactly four phases in order**. Do not start a later phase until the current one is complete. After Plan, **stop and wait for explicit user approval** before Implement.

The skill ends after Phase 4. Do **not** write `docs/dossier/` or produce plan / test-plan / deploy-notes files — the cloud agent posts that content as a PR comment when the PR is opened.

Read and obey these rules while working:

- `.cursor/rules/public-api-exports.mdc`
- `.cursor/rules/api-stability-annotations.mdc`
- `.cursor/rules/sphinx-api-docs.mdc`
- `.cursor/rules/public-api-tests.mdc`

---

## Phase 1 — Plan

1. Restate the **fan-out for this specific change** (which of these apply, and why):
   - private implementation module
   - `@public` on the definition
   - root `__init__.py` export (`import X as X`)
   - stability / lifecycle annotation (`@preview` / `@beta` / `@deprecated` / …)
   - Sphinx rST entry under `docs/sphinx/sections/`
   - behavioral tests under the matching `*_tests/` tree
2. List **every file** you will create or edit, in the order you will touch them.
3. Call out whether this is a new top-level symbol vs a new `@public` member on an existing public class (different fan-out).
4. **Stop.** Ask for approval. Do not edit files until the user approves the plan.

---

## Phase 2 — Implement

**Before touching any files**, derive a branch name from the issue description and create it.

Format: `feat/<library>-<short-kebab-case-description>`

Example: for "add retry_delay property to RetryPolicy in dagster-core" → `feat/dagster-retry-delay-property`

Then run:

```bash
git checkout -b <derived-branch-name>
```

If the command fails because the branch already exists locally, **stop** and tell the user:

> Branch `<name>` already exists locally. Run `git branch -D <name>` and then re-invoke the skill.

Do **not** delete or recreate the branch automatically.

State the derived branch name clearly at the **top** of the Phase 2 output so the user can use it in `git push` and the PR URL later.

Then apply changes in this reviewer-expected order (skip a step only if Plan marked it N/A):

1. **Private implementation** — code under `dagster._…` / library internals
2. **Public export** — root `from …defining_module… import X as X` when adding a top-level symbol
3. **Stability annotation** — `@public` plus any `@preview` / `@beta` / `@deprecated(breaking_version=…)` / param variants from `dagster._annotations`
4. **Docs rST entry** — matching `.. autoclass::` / `.. autofunction::` / `.. autodecorator::` with correct `.. currentmodule::`

Do not invent exports “just in case.” Do not grow `exclude_lists.py`.

---

## Phase 3 — Test

Write tests in the correct location per `.cursor/rules/public-api-tests.mdc`.

- Behavioral API tests: package `*_tests/` tree; import the public path when asserting user-facing behavior.
- Annotation mechanics only: extend `dagster_tests/utils_tests/test_annotations.py`.

---

## Phase 4 — Verify

1. Run a **scoped** test selection with `python -m pytest` (not bare `pytest` — a system Python 3.14 on PATH can shadow the venv):

   ```bash
   python -m pytest path/to/tests/… -q
   ```

2. From `$DAGSTER_GIT_REPO_DIR` / repo root:

   ```bash
   make ruff
   make quick_ty
   ```

Pre-existing failures: if `make ruff` fails on a file you did not write but that file is inside the hook allowlist, fix it in the same commit and include it in the files-changed summary.
Do not revert and re-apply repeatedly. One fix, move on. If the failing file is outside the allowlist, report it and stop — do not touch it."

3. Docs validators — **only if they exist as Makefile targets**. Before the demo / any docs-check step, run:

   ```bash
   grep -n "dagster-docs" Makefile
   ```

   - If matches exist: run the corresponding `make` / `dagster-docs check …` targets for exports, `@public`, docstrings, or RST changes.
   - If **no matches** (current repo): do **not** invoke `dagster-docs` directly. Rely on `make ruff` and `make quick_ty` from step 2 only.

4. On any failure: fix, then re-run the failing command. Repeat until green.

5. **Allowlist gate** — before reporting success, confirm every changed path is under the pre-tool-use hook allowlist in `.cursor/hooks/restrict-writes.py` (`ALLOWLIST` / `ALLOWED_LIBRARY`):

   ```bash
   git diff --name-only
   ```

   Every listed path must fall under that allowlist (and not under `js_modules/` or another library package). If any path is outside the allowlist, fix or revert it and re-check. Do **not** report success while out-of-allowlist files remain.

6. **Never report success on a red suite.** If something is still failing, say what failed and stop.

7. When Phase 4 is green, output a **single completion summary** containing only:
   - **Files changed** (paths only)
   - **Test result** (pass count, command used)
   - **Ruff and pyright status**

---

## Progress checklist

Copy and update as you go:

```
- [ ] Phase 1 Plan — approved
- [ ] Phase 2 Implement
- [ ] Phase 3 Test
- [ ] Phase 4 Verify — green
```
