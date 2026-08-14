# Comparative scan

When invoked with a git ref (branch name or commit SHA, e.g. `/comparative-scan feat/foo`), do **exactly** the following steps **in order**. Read-only: do **not** touch any files. Do **not** suggest fixes beyond naming the correct pattern.

Reuse the same rule-evaluation logic as `/review-conventions` for each changed file (attach rules → list attached → review against rules → check exports → check tests). Do **not** reimplement per-file checks; apply that command's criteria, then aggregate into counts.

## 1. Resolve the changed files

Run:

```bash
git rev-parse --verify <ref>
git diff --name-only master...<ref>
git diff --shortstat master...<ref>
```

- If `<ref>` does not resolve, **stop** and say so.
- Filter changed paths to **Python files under `python_modules/`** (`.py` only).
- Record `files_changed` = count of those filtered paths.
- Record `lines_changed` = total lines added **plus** removed from `git diff --shortstat` (the sum of the insertions and deletions numbers). Use the shortstat for the same `master...<ref>` range (not filtered to Python-only); if you need a Python-only line count, use `git diff --shortstat master...<ref> -- 'python_modules/**/*.py'`.

## 2. Attach rules per file

For **each** changed Python file:

1. Read it with the Read tool so glob-scoped `.cursor/rules/*.mdc` rules attach.
2. List every rule now in context and the **glob that attached it**.

If **no** glob-scoped rules attached to **any** changed file, **stop** and say so. Do not continue to later steps.

## 3. Evaluate violations

For each changed file that has attached rules, evaluate it using the **same reject-only criteria** as `/review-conventions` (and the attached `.mdc` rules themselves):

- Review against every attached rule
- Check `@public` root exports
- Check corresponding tests for implementation modules

For each violation record:

| Field | Value |
|-------|--------|
| file | path relative to repo root |
| line(s) | quoted line(s) or line numbers |
| rule name | rule / check name |
| category | one of: `visibility-annotation`, `export`, `stability`, `test-location`, `docs` |
| classification | `BLOCKER` or `WARNING` |

Category mapping:

| Category | Maps to |
|----------|---------|
| `visibility-annotation` | missing/incorrect `@public` (and related visibility decorator issues from public-api-exports) |
| `export` | root `__init__.py` re-export requirements |
| `stability` | api-stability-annotations (`@preview`/`@beta`, `breaking_version=`, `param=`, etc.) |
| `test-location` | public-api-tests path / tier placement |
| `docs` | sphinx-api-docs RST / docstring requirements |

Do not suggest fixes beyond naming the correct pattern.

## 4. Test-tier check

For each changed **implementation** module (not already under a `*_tests/` tree):

1. Determine whether a corresponding **behavioral** test file exists anywhere in the matching `*_tests/` tree per `.cursor/rules/public-api-tests.mdc`. Existence under that tree is the blocker-grade requirement; do not treat sub-tier placement as missing.
2. If a test exists, determine whether it is in the **domain-matching sub-tier** (e.g. core Dagster decorators → `dagster_tests/definitions_tests/decorators_tests/`; dagster-dbt core-domain symbols such as translator, asset specs, asset checks, decorators → `dagster_dbt_tests/core/`; annotation mechanics → `dagster_tests/utils_tests/test_annotations.py`). A test under the package `*_tests/` tree but **not** in that sub-tier (for a core-domain symbol: not under `core/`) is `present_wrong_tier`.
3. Record `test_tier_status` per module as one of:
   - `present_correct_tier` — test exists in the domain-matching sub-tier (no finding)
   - `present_wrong_tier` — test exists under the package `*_tests/` tree but not in the domain-matching sub-tier
   - `missing` — no corresponding test under the package `*_tests/` tree
4. Classification:
   - `missing` remains BLOCKER-eligible per the existing public-api-tests existence rule. Count it under `blocker_count`.
   - `present_wrong_tier` **must** produce a **WARNING** (category `test-location`) in the human-readable report and increment `warning_count`, **not** `blocker_count`. Count that placement once (do not also add a separate step-3 finding for the same sub-tier miss).
   - `present_correct_tier` is clean.
5. If tests exist and can be scoped, run:

```bash
python -m pytest <scoped path> -q
```

Use `python -m pytest` — **never** bare `pytest`. Record aggregate `tests_passed` and `tests_failed` from the run(s). If no scoped tests were run, use `0` for both.

Aggregate `test_tier_status` for the JSON summary as an object mapping each checked implementation path to its status (or a compact list of `{file, status}` entries).

## 5. Structured report

Emit **one** report with **two** parts, in this order.

### Part A — Human-readable (same shape as `/review-conventions`)

```
## BLOCKERS
…

## WARNINGS
…

## MISSING
…   # missing root exports and/or missing expected test paths (not wrong-tier; that is a WARNING)

## CLEAN
…   # attached rules / checks with no findings, or "none"
```

Empty sections may say `(none)`.

### Part B — Machine-countable JSON summary

Emit a single JSON object with **exactly** these fields:

```json
{
  "ref": "<ref>",
  "files_changed": 0,
  "lines_changed": 0,
  "violation_count_total": 0,
  "violation_count_by_category": {
    "visibility-annotation": 0,
    "export": 0,
    "stability": 0,
    "test-location": 0,
    "docs": 0
  },
  "violation_density": {
    "per_file": 0.0,
    "per_100_lines": 0.0
  },
  "blocker_count": 0,
  "warning_count": 0,
  "blocker_to_warning_ratio": null,
  "test_tier_status": [],
  "tests_passed": 0,
  "tests_failed": 0,
  "follow_up_pr_count": null,
  "review_round_trips": null
}
```

Field rules:

- `violation_density.per_file` = `violation_count_total / files_changed` (null if `files_changed` is 0)
- `violation_density.per_100_lines` = `(violation_count_total / lines_changed) * 100` (null if `lines_changed` is 0)
- `blocker_to_warning_ratio` = `blocker_count / warning_count` (null if `warning_count` is 0)
- `follow_up_pr_count` and `review_round_trips` are always `null` in this command

After the JSON, add a short note: `follow_up_pr_count` and `review_round_trips` are populated by the instrumented cloud agent from PR history and are not computable from a single ref.

## 6. Constraints

- Do **not** modify any files.
- Do **not** suggest fixes beyond naming the correct pattern.
- Do **not** reimplement `/review-conventions` checks — reuse that logic and aggregate.
