# 3DP-018 debt register

This register closes residual hardening debt for `1.0.0` without duplicating publication ownership, local WFO ownership, or legacy SHORT_ID migration work.

## P0 release integrity

- Explicit lifecycle states are `candidate`, `tagged-validated`, and `published`; `pass` is intentionally invalid.
- `candidate` may record local evidence and `hosted_ci: not run`, but must not claim hosted CI success or publication.
- `tagged-validated` requires immutable tag `v1.0.0` and matching `evidence.tag_sha`.
- `published` additionally requires `published_at_utc`.
- Historical `v0.2.0` is recorded as immutable legacy history and must not be moved.

## P1 CI evidence

- Workflow permissions are read-only except `statuses: write` for `dvp/validation` status publication.
- Pull requests check out exact PR HEAD with stale run cancellation.
- The local deterministic parity command is:

```bash
python3 skills/3d-visual-pipeline/scripts/validate_repository.py && python3 skills/3d-visual-pipeline/scripts/validate_runtime_contract.py && python3 skills/3d-visual-pipeline/scripts/validate_asset_registry.py && python3 skills/3d-visual-pipeline/scripts/validate_visual_regression.py && python3 skills/3d-visual-pipeline/scripts/smoke_test_installation.py && python3 skills/3d-visual-pipeline/scripts/validate_release.py && python3 skills/3d-visual-pipeline/scripts/validate_debrand.py && python3 -m unittest discover -s skills/3d-visual-pipeline/tests -p "test_*.py"
```

When hosted Actions are unavailable, evidence must say `not run`; local reports in `validation/runtime/` are the fallback evidence. The release report records `exact-head:<sha>` from `git rev-parse HEAD`.

## P1 public adoption

- Root install and immutable-tag install are documented in `../skills/3d-visual-pipeline/references/installation.md`.
- Minimal tool-agnostic examples are documented in `examples.md`.
- Identity limitations remain explicit: exact identity preservation is not guaranteed.

## P2 repository hygiene

- Branch deletion is a separate destructive action and requires explicit human confirmation outside a merge commit.
- Paths must remain ASCII, relative links valid, JSON parseable, assets registered, and checksums current. Asset registry updates are limited to checksum reconciliation for already tracked governed assets; rights metadata and history are unchanged.
- No new `SECURITY.md` or `SUPPORT.md` is added because no concrete security/support policy is in scope.
