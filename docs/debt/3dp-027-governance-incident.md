# 3DP#27 governance incident record

## Scope

This record documents the post-merge defects, duplicate Pull Requests and unsupported release-state incident discovered after the 3DP completion wave. It defines preventive controls without changing runtime semantics, style contracts, governed assets, historical tags or Releases.

## Baseline

```text
repository: sevranty/3d-visual-pipeline
candidate main before 3DP#27: b00c5c87189fb84203aed94de94b17a8e9ae0e80
release state: candidate
hosted workflow for candidate main: not run
legacy release: v0.2.0
legacy target: 3d2cdea9f651f7641ec1f805519a777f013dd6ec
```

## Timeline

| Item | Exact record | Finding | Resolution |
|---|---|---|---|
| PR #19 | merge `28f842210cf15a78d5d72fa599a0aa8b37c53162` | Consolidated WFO adapter, naming and release hardening were merged before complete reconstructed-tree validation finished | Full post-merge validation was completed and defects were isolated |
| PR #23 | historical merge `e4f3d25e07e7b1336c7df0183b808ced24293ad2` | Corrected a broken nested release link and stale checksum records | Candidate validation tree repaired without runtime, style or binary changes |
| PR #24 | merge `74670a91ee9931f1ee7a32255616cc5274f9825c` | Completed the repository execution Issue Form and contract coverage | Task intake contract completed |
| PR #20 | head `3ea4df6842d4d52e570055f4a2889dfb00e5ab42` | Parallel duplicate of release hardening work | Closed without merge and marked superseded |
| PR #21 | head `bfa2a1e1dedb96441b67f503ad9c3b873079c59c` | Parallel duplicate of SHORT_ID and validation identity work | Closed without merge and marked superseded |
| PR #22 | head `63e7c49889336e8a467915003d2370fa3e405dbe` | Parallel duplicate of repository routing and Issue Form work | Closed without merge and marked superseded |
| PR #25 | merge `8a1c673ba4a5653e89beb305d4c3e23f7774f77b`, defect commit `3975f92207d65d8f018959a86ab6c7aa175f7f1f` | Changed release status from `candidate` to unsupported `pass` without annotated tag, immutable-tag validation, Release URL or hosted CI evidence | Classified as an incident, not validation evidence |
| PR #26 | merge `b00c5c87189fb84203aed94de94b17a8e9ae0e80` | Restored factual release state | Candidate state and validated file-level equivalence restored |

## Root causes

- Release lifecycle values were documented but the complete evidence matrix was not enforced
- PR prose and commit messages could appear to claim facts that were absent from the release manifest
- A task could produce several open implementation PRs without a deterministic duplicate gate
- Replacement relations were not required in machine-checkable PR metadata
- Full reconstructed-tree validation was completed after a merge instead of before it

## Preventive controls

### Release lifecycle

- Accept only `candidate`, `tagged-validated` and `published`
- Reject `pass` and every unrecognized value
- Require exact hosted CI URL and commit when hosted CI is claimed
- Require annotated tag object, intended tag, peeled commit, exact checkout SHA, command, report and timestamp for `tagged-validated`
- Require canonical Release URL, intended tag, non-draft state, non-prerelease state and publication timestamp for `published`
- Keep all publication fields null for `candidate`
- Preserve `v0.2.0` and its target as immutable historical evidence

### Pull Request governance

- Require exact `TASK_ID`, canonical Issue and `Supersedes` metadata in every implementation PR body
- Permit one open implementation PR per `TASK_ID`
- Permit replacement only after the prior PR is closed
- Require every replacement link in the form `PR #N (closed)`
- Run the duplicate check with read-only repository and Pull Request permissions
- Keep CI unable to write branches, Issues or Pull Requests

### Review and merge

- Validate the exact current HEAD
- Review the full diff and changed-file allowlist
- Resolve every P0-P2 finding in the same branch
- Require zero unresolved review threads
- Merge only the reviewed expected HEAD SHA
- Verify the resulting `main` after merge

## Cross-links

- Publication task - https://github.com/sevranty/3d-visual-pipeline/issues/8
- Consolidation task - https://github.com/sevranty/3d-visual-pipeline/issues/18
- Governance task - https://github.com/sevranty/3d-visual-pipeline/issues/27
- Canonical consolidation - https://github.com/sevranty/3d-visual-pipeline/pull/19
- Corrective PRs - https://github.com/sevranty/3d-visual-pipeline/pull/23, https://github.com/sevranty/3d-visual-pipeline/pull/24 and https://github.com/sevranty/3d-visual-pipeline/pull/26
- Superseded PRs - https://github.com/sevranty/3d-visual-pipeline/pull/20, https://github.com/sevranty/3d-visual-pipeline/pull/21 and https://github.com/sevranty/3d-visual-pipeline/pull/22
- Release-state incident - https://github.com/sevranty/3d-visual-pipeline/pull/25
