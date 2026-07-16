# 3D Visual Pipeline 1.0.0

This major release establishes the generic public package.

## Highlights

- Generic repository, plugin, and skill identity.
- Neutral repository-authored plugin assets.
- Configurable accent color with a neutral default.
- Versioned Modern Flat, Silver-Gold, and Obsidian Gold visual contracts.
- Capability-based runtime routing and explicit fallback rules.
- Governed asset registry with checksums and public-distribution states.
- Correct nested relative paths.
- Dedicated debrand validation and regression tests.

## Breaking changes

The plugin identifier and skill installation path changed. Install from the skills/3d-visual-pipeline directory and invoke the `3d-visual-pipeline` skill.

## Legacy boundary

The deprecated pre-generic release remains an immutable historical record and is not recommended for installation.

## Release lifecycle

The `candidate` state means local exact-HEAD validation is available and hosted CI may be `not run`. `tagged-validated` requires `v1.0.0` to resolve to the recorded tag SHA. `published` additionally requires a publication timestamp.
