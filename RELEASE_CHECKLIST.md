# Release Checklist - 1.0.0

## Identity

- [x] Repository, plugin, skill and commands use `3d-visual-pipeline`
- [x] Skill path is `skills/3d-visual-pipeline`
- [x] Project SHORT_ID is `3DP`
- [x] Plugin version is `1.0.0`
- [x] Native validation check is `Validate repository / validate`; no duplicate custom commit status is published

## Governance

- [x] `TASK.md` defines the local execution contract
- [x] ADR 0002 defines the WebFactoryOS orchestration boundary
- [x] One repository-local execution Issue Form remains
- [x] No runtime, package, workflow or network dependency on WebFactoryOS exists

## Debrand

- [x] Active tracked tree contains no blocked organization identifiers, URLs, filenames, asset IDs or fixed palette marker
- [x] Generic repository-authored visual assets are registered and checksummed
- [x] Style contracts are organization-neutral
- [x] New active previous project IDs are rejected outside narrow historical evidence

## Validation

Run one local command matching CI:

```bash
python3 skills/3d-visual-pipeline/scripts/validate_all.py --report-dir validation/runtime
```

- [x] Exact approved release commit validation passes
- [x] Hosted GitHub Actions result for immutable-tag validation is recorded factually as `not_run`
- [x] Closure PR full diff review has no P0-P2 findings
- [x] Closure PR unresolved review threads are zero

Immutable-tag validation evidence:

- annotated tag object SHA: `158aa30c4fa7e17ae587c288b619df1ff824f62d`
- peeled commit: `eea9b34403d05b32393e118883334e75f0d76170`
- validation timestamp: `2026-07-22T19:42:40.666580+00:00`
- result: eight validation groups passed, including 52 unit tests

## Publication

Current factual state: `published`

- [x] Annotated tag `v1.0.0` created on the approved release commit
- [x] Full validation repeated from a clean immutable-tag checkout
- [x] Manifest records exact annotated-tag object, target and checkout evidence
- [x] Public non-draft, non-prerelease GitHub Release published from checked-in notes
- [x] Manifest moved to `published` with canonical Release URL
- [ ] Closure evidence merged

Release: https://github.com/sevranty/3d-visual-pipeline/releases/tag/v1.0.0

The historical `v0.2.0` tag and Release remain immutable and continue to peel to `3d2cdea9f651f7641ec1f805519a777f013dd6ec`.
