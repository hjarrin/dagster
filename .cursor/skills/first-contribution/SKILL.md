---
name: first-contribution
description: >-
  Guided first contribution for a Dagster public-API change. Takes an issue
  description and runs Plan → Implement → Test → Verify → Dossier without
  skipping ahead. Use when the user invokes /first-contribution or asks to
  walk a first contribution through the public-API fan-out.
---

# First contribution

Input: the issue description (and any linked issue URL/number) supplied after `/first-contribution`.

Run **exactly five phases in order**. Do not start a later phase until the current one is complete. After Plan, **stop and wait for explicit user approval** before Implement.

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

Apply changes in this reviewer-expected order (skip a step only if Plan marked it N/A):

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
   make quick_pyright
   ```

3. Docs validators — **only if they exist as Makefile targets**. Before the demo / any docs-check step, run:

   ```bash
   grep -n "dagster-docs" Makefile
   ```

   - If matches exist: run the corresponding `make` / `dagster-docs check …` targets for exports, `@public`, docstrings, or RST changes.
   - If **no matches** (current repo): do **not** invoke `dagster-docs` directly. Rely on `make ruff` and `make quick_pyright` from step 2 only.

4. On any failure: fix, then re-run the failing command. Repeat until green.

5. **Allowlist gate** — before reporting success, confirm every changed path is under the pre-tool-use hook allowlist in `.cursor/hooks/restrict-writes.py` (`ALLOWLIST` / `ALLOWED_LIBRARY`):

   ```bash
   git diff --name-only
   ```

   Every listed path must fall under that allowlist (and not under `js_modules/` or another library package). If any path is outside the allowlist, fix or revert it and re-check. Do **not** report success while out-of-allowlist files remain.

6. **Never report success on a red suite.** If something is still failing, say what failed and stop.

---

## Phase 5 — Dossier

Write these three files (create `docs/dossier/` if needed):

### `docs/dossier/plan.md` — for a PM

- Scope
- Behavior change
- Breaking change? (yes/no + one-line why)
- Rollback

**No file paths.**

### `docs/dossier/test-plan.md` — for QA

- Coverage by tier (unit / integration / docs validators)
- What a human must verify by hand

### `docs/dossier/deploy-notes.md` — for DevOps and release

- Public API surface added or changed
- Stability level (`public` / `preview` / `beta` / `deprecated` / …)
- Deprecation timeline (or N/A)
- Docs rebuild required? (yes/no)
- Breaking-change flag for the PR template (yes/no)

---

## Progress checklist

Copy and update as you go:

```
- [ ] Phase 1 Plan — approved
- [ ] Phase 2 Implement
- [ ] Phase 3 Test
- [ ] Phase 4 Verify — green
- [ ] Phase 5 Dossier
```
