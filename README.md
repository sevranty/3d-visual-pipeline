<p align="center"><img src="assets/plugin-logo.png" alt="Abstract 3D cube" width="320"></p>

# 3D Visual Pipeline

Skill-only Codex plugin for controlled reference-to-image production: from task framing and reference mapping to a validated, visibly delivered three-dimensional visual.

**Version:** `1.0.0`  
**Status:** generic public release candidate

## Workflow

1. validate inputs and rights
2. define task, metaphor and subject
3. map each reference to one declared role
4. lock semantics, identity, composition and style
5. compile the Scene Specification
6. choose one versioned style pack
7. route through observed runtime capabilities
8. generate or edit without hidden degradation
9. diagnose and repair local defects
10. validate, record provenance and deliver visibly

## Installation

Canonical instructions: `skills/3d-visual-pipeline/references/installation.md`.

From a repository checkout:

```bash
mkdir -p .agents/skills
cp -R skills/3d-visual-pipeline .agents/skills/3d-visual-pipeline
python3 skills/3d-visual-pipeline/scripts/smoke_test_installation.py
```

For a published release, check out the immutable release tag before running the same commands. Do not treat a branch name as immutable release evidence.

## Usage

Tool-agnostic examples for style transfer, reinterpretation and local correction: `docs/examples.md`.

Every request must declare inputs, reference roles, locks, stop conditions and visible delivery evidence.

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

One local command matches the GitHub Actions validation set:

```bash
python3 skills/3d-visual-pipeline/scripts/validate_all.py --report-dir validation/runtime
```

The workflow publishes the `3dp/validation` status and uploads one compact JSON evidence artifact. When a hosted run does not exist, report `not run`; do not replace it with a local-CI claim.

## Governance

- local execution contract: `TASK.md`
- orchestration boundary: `docs/decisions/0002-web-factory-os-orchestration.md`
- debt closure record: `docs/debt/3dp-018.md`
- runtime source: `skills/3d-visual-pipeline/SKILL.md`

WebFactoryOS supplies routing and relation context only. This repository has no runtime, build, package, workflow or network dependency on it.

## License and rights

MIT covers repository code and original documentation. Visual assets in `assets/` are repository-authored unless their manifest entry states otherwise. No trademark or third-party usage right is implied.
