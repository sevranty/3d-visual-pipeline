## Task

- TASK_ID: 3DP-000
- Canonical Issue: #0
- Supersedes: none
- Base SHA: 0000000000000000000000000000000000000000
- Exact HEAD: 0000000000000000000000000000000000000000

Replace the sentinel values above with the exact task facts before review. `Supersedes` must be `none` or a comma-separated list in the exact form `PR #20 (closed)`.

## Changes

- Describe every changed contract and file group

## Validation evidence

```text
command: python3 skills/3d-visual-pipeline/scripts/validate_all.py --report-dir validation/runtime
status: not-run
report: validation/runtime/summary.json
```

## Review

- [ ] Full diff matches the canonical Issue WRITE_SCOPE
- [ ] Only one active implementation PR exists for this TASK_ID
- [ ] Any replaced PR is closed and listed in `Supersedes`
- [ ] Canonical contracts remain consistent
- [ ] Validators and tests pass on exact HEAD
- [ ] Relative links, manifests, checksums and release metadata are valid
- [ ] Workflow permissions remain least-privilege and do not write branches, Issues or PRs
- [ ] No secrets, temporary files, unresolved review threads or hidden scope expansion remain

## Lifecycle

Keep the PR in Draft until exact-HEAD validation and technical review are complete. Merge only the reviewed HEAD SHA. After merge, verify the new `main` and synchronize the Issue and PR digital trace.
