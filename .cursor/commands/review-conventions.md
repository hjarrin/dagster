# Review conventions

When invoked with a file reference (e.g. `/review-conventions @path/to/file.py`), do **exactly** the following steps **in order**. Read-only: do **not** touch any files. Do **not** suggest fixes beyond naming the correct pattern.

## 1. Attach rules

Read the referenced file with the Read tool so glob-scoped `.cursor/rules/*.mdc` rules attach.

## 2. List attached rules

List every rule now in context and the **glob that attached it**.

If **no** glob-scoped rules attached, **stop** and say so. Do not continue to later steps.

## 3. Review against attached rules

Review the file against every attached rule.

For each violation:

- Quote the specific line(s)
- Name the rule it violates
- State the correct pattern (name it only — do not rewrite the code)
- Classify as **BLOCKER** (reviewer will reject) or **WARNING** (judgment call)

## 4. Check exports

If the file defines any symbol decorated with `@public`, verify each appears in the package root `__init__.py` (`dagster`, `dagster_pipes`, or the relevant `dagster_*` library).

Flag any `@public` symbols that are missing from the root export. (New `@public` methods/properties on an already-exported class do not need a new root export — only flag top-level classes/functions that should be re-exported.)

## 5. Check tests

If the file is an **implementation** module (not already under a `*_tests/` tree), confirm a corresponding test file exists in the matching `*_tests/` tree per `.cursor/rules/public-api-tests.mdc`.

If none exists, name the **expected path**.

## 6. Structured report

Output **one** structured report with these sections only:

```
## BLOCKERS
…

## WARNINGS
…

## MISSING
…   # missing root exports and/or missing expected test paths

## CLEAN
…   # attached rules / checks with no findings, or "none"
```

Empty sections may say `(none)`.
