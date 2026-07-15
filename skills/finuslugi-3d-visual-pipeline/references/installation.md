# Installation

Release: `0.2.0`.

## Plugin installation

Use the repository root as the plugin source. The installer must detect:

```text
.codex-plugin/plugin.json
skills/finuslugi-3d-visual-pipeline/SKILL.md
```

Add the public repository `sevranty/finuslugi-3d-visual-pipeline` through the Codex plugin-management interface available in the active client. Select release `0.2.0` or the immutable release commit when version selection is available. Do not install from an unreviewed feature branch.

Plugin-management wording and controls may differ by Codex client. The repository contract does not depend on a specific UI label.

## Repository-scoped fallback

For a local project that supports Agent Skills discovery, copy or link the skill directory into the project:

```bash
mkdir -p .agents/skills
cp -R skills/finuslugi-3d-visual-pipeline .agents/skills/finuslugi-3d-visual-pipeline
```

The resulting path must be:

```text
.agents/skills/finuslugi-3d-visual-pipeline/SKILL.md
```

This fallback installs the skill only. Plugin-level interface metadata remains in the repository root.

## Verification

From the repository root run:

```bash
python3 skills/finuslugi-3d-visual-pipeline/scripts/smoke_test_installation.py
```

Then run the complete deterministic suite:

```bash
python3 skills/finuslugi-3d-visual-pipeline/scripts/validate_repository.py --no-report
python3 skills/finuslugi-3d-visual-pipeline/scripts/validate_runtime_contract.py
python3 skills/finuslugi-3d-visual-pipeline/scripts/validate_asset_registry.py
python3 skills/finuslugi-3d-visual-pipeline/scripts/validate_visual_regression.py
python3 skills/finuslugi-3d-visual-pipeline/scripts/validate_release.py
```

## Expected discovery

A successful installation exposes one skill named `finuslugi-3d-visual-pipeline`. Its description must mention reference analysis, image generation or editing, runtime routing, and validated delivery.

## Removal

- Plugin installation: remove the plugin through the same plugin-management interface.
- Repository-scoped installation: delete `.agents/skills/finuslugi-3d-visual-pipeline`.

Do not delete source assets or manifests from a working repository to disable the skill.

## Security

Review `SKILL.md`, scripts, manifests, and plugin metadata before installation. The release contains no MCP servers, hooks, network-execution scripts, secrets, or package-manager dependencies. Validation scripts use the Python standard library only.
