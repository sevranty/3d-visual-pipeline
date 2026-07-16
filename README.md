<p align="center"><img src="assets/plugin-logo.png" alt="Abstract 3D cube" width="320"></p>

# 3D Visual Pipeline

Skill-only Codex plugin for controlled reference-to-image production: from task framing and reference mapping to a validated, visibly delivered three-dimensional visual.

**Version:** `1.0.0`  
**Status:** candidate (local validation only; hosted CI evidence is `not run` until a workflow run exists)

## Workflow

1. validate inputs and rights
2. define task, metaphor, and subject
3. map each reference to one declared role
4. lock semantics, identity, composition, and style
5. compile the Scene Specification
6. choose one versioned style pack
7. route through observed runtime capabilities
8. generate or edit without hidden degradation
9. diagnose and repair local defects
10. validate, record provenance, and deliver visibly

## Installation

Canonical instructions: `skills/3d-visual-pipeline/references/installation.md`. Minimal examples: `docs/examples.md`. Debt register: `docs/debt-register-3dp-018.md`.

```bash
mkdir -p .agents/skills
cp -R skills/3d-visual-pipeline .agents/skills/3d-visual-pipeline
python3 skills/3d-visual-pipeline/scripts/smoke_test_installation.py
```

## Canonical contracts

- skill: `skills/3d-visual-pipeline/SKILL.md`
- Scene Specification: `skills/3d-visual-pipeline/references/scene-specification.md`
- runtime capabilities: `skills/3d-visual-pipeline/references/runtime-capabilities.md`
- asset governance: `skills/3d-visual-pipeline/references/asset-governance.md`
- diagnostics: `skills/3d-visual-pipeline/references/diagnostic-codes.md`
- release policy: `skills/3d-visual-pipeline/references/versioning-and-release.md`

## Style packs

| Style pack | Version | Contract |
|---|---:|---|
| Modern Flat | 2.1 | geometric volume, configurable accent, low visual noise |
| Silver-Gold | 3.1 | silver-dominant satin materials with restrained gold |
| Obsidian Gold | 1.0 | one isolated matte dark object with restrained gold |

## Validation

```bash
python3 skills/3d-visual-pipeline/scripts/validate_repository.py
python3 skills/3d-visual-pipeline/scripts/validate_runtime_contract.py
python3 skills/3d-visual-pipeline/scripts/validate_asset_registry.py
python3 skills/3d-visual-pipeline/scripts/validate_visual_regression.py
python3 skills/3d-visual-pipeline/scripts/smoke_test_installation.py
python3 skills/3d-visual-pipeline/scripts/validate_release.py
python3 skills/3d-visual-pipeline/scripts/validate_debrand.py
python3 -m unittest discover -s skills/3d-visual-pipeline/tests -p "test_*.py"
```

All runtime validators use only the Python standard library.

## License and rights

MIT covers repository code and original documentation. Visual assets in `assets/` are repository-authored unless their manifest entry states otherwise. No trademark or third-party usage right is implied.
