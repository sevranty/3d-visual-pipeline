# Changelog

## Unreleased

### Changed

- Added the local WebFactoryOS orchestration boundary without a runtime or build dependency.
- Standardized active project metadata and validation identity on `3DP` and the native `Validate repository / validate` check.
- Added one deterministic validation entrypoint shared by local execution and GitHub Actions.
- Deduplicated task-branch and Pull Request validation, retained one read-only job and limited artifacts to failed or requested manual runs.
- Added explicit release lifecycle states, tag binding checks and negative tests.
- Added tool-agnostic public usage examples and a factual debt closure record.

## 1.0.0 - 2026-07-16

### Changed

- Renamed the repository, plugin, skill, paths, commands and validation context to the generic 3D Visual Pipeline contract.
- Removed organization-specific naming, fixed palette requirements, URLs, asset identifiers and visual branding from the active tree.
- Replaced legacy brand assets with neutral repository-authored cube assets.
- Made the Modern Flat accent configurable with a neutral default.
- Corrected nested repository-asset paths.
- Added a dedicated debrand validator and regression tests.

### Breaking

- Installation path changes to `skills/3d-visual-pipeline`.
- Plugin identifier changes to `3d-visual-pipeline`.

### Legacy

The deprecated pre-generic release remains immutable for historical reproducibility and is not the recommended installation target.
