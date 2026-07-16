# 3D Visual Pipeline 1.0.0

This major release establishes the generic public package.

## Highlights

- Generic repository, plugin and skill identity
- Neutral repository-authored plugin assets
- Configurable accent color with a neutral default
- Versioned Modern Flat, Silver-Gold and Obsidian Gold visual contracts
- Capability-based runtime routing and explicit fallback rules
- Governed asset registry with checksums and public-distribution states
- Correct nested relative paths
- Dedicated debrand validation and regression tests
- Local project contract and WebFactoryOS orchestration boundary without runtime coupling
- One deterministic validation entrypoint for local and hosted checks
- Explicit candidate, tagged-validated and published lifecycle states

## Breaking changes

The plugin identifier and skill installation path changed. Install from `../../skills/3d-visual-pipeline` and invoke the `3d-visual-pipeline` skill.

## Validation

Run:

```bash
python3 skills/3d-visual-pipeline/scripts/validate_all.py --report-dir validation/runtime
```

Published state requires an annotated tag target, clean immutable-tag validation and the canonical GitHub Release URL.

## Legacy boundary

The deprecated pre-generic release remains an immutable historical record and is not recommended for installation.
