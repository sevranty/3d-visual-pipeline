# Release Checklist — 1.0.0

## Identity

- [x] Repository, plugin, skill, and commands use `3d-visual-pipeline`.
- [x] Skill path is `skills/3d-visual-pipeline`.
- [x] Plugin version is `1.0.0`.
- [x] Validation context is `dvp/validation`.

## Debrand

- [x] Active tracked tree contains no blocked legacy identifiers, URLs, filenames, asset IDs, or fixed palette marker.
- [x] Legacy logo binaries are absent from the active tracked tree.
- [x] Generic repository-authored visual assets are registered and checksummed.
- [x] Style contracts are organization-neutral.

## Validation

- [x] Repository validator passes.
- [x] Runtime contract validator passes.
- [x] Asset registry validator passes.
- [x] Visual regression validator passes.
- [x] Installation smoke test passes.
- [x] Release validator passes.
- [x] Debrand validator passes.
- [x] Unit tests pass.

## Publication

- [ ] Annotated tag `v1.0.0` created on the release merge commit.
- [ ] Public GitHub Release published from checked-in notes.
- [ ] Full validation repeated from immutable tag.
- [ ] Closure evidence merged.

## Evidence lifecycle

- [x] Candidate state records local exact-HEAD evidence and does not claim hosted CI success.
- [ ] Tagged-validated state records immutable `v1.0.0` tag binding.
- [ ] Published state records release publication timestamp.
- [x] Hosted Actions unavailable evidence is recorded as `not run`.
