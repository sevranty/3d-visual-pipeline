#!/usr/bin/env python3
"""Smoke-test plugin and repository-scoped skill installation using stdlib only."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=root)
    return parser.parse_args()


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"Missing file: {path}")
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON: {path}: {exc}")
    return None


def verify_frontmatter(path: Path, errors: list[str]) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        errors.append(f"Missing skill file: {path}")
        return
    if len(lines) < 4 or lines[0] != "---":
        errors.append(f"Invalid SKILL.md frontmatter start: {path}")
        return
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        errors.append(f"Unclosed SKILL.md frontmatter: {path}")
        return
    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    if metadata.get("name") != "finuslugi-3d-visual-pipeline":
        errors.append("Installed skill name is incorrect")
    description = metadata.get("description", "").lower()
    for marker in ("reference", "image", "runtime", "deliver"):
        if marker not in description:
            errors.append(f"Installed skill description lacks marker: {marker}")


def main() -> int:
    args = parse_args()
    root = args.repo_root.resolve()
    errors: list[str] = []
    checks: list[str] = []

    manifest = load_json(root / ".codex-plugin/plugin.json", errors)
    if isinstance(manifest, dict):
        if manifest.get("name") != "finuslugi-3d-visual-pipeline":
            errors.append("Plugin name mismatch")
        if manifest.get("version") != "0.2.0":
            errors.append("Plugin version must be 0.2.0")
        if manifest.get("skills") != "./skills/":
            errors.append("Plugin skills path must be ./skills/")
    checks.append("source-plugin-manifest")

    source_skill = root / "skills/finuslugi-3d-visual-pipeline"
    verify_frontmatter(source_skill / "SKILL.md", errors)
    checks.append("source-skill-frontmatter")

    with tempfile.TemporaryDirectory(prefix="f3d-install-") as temporary:
        target = Path(temporary) / "plugin"
        (target / ".codex-plugin").mkdir(parents=True)
        shutil.copy2(root / ".codex-plugin/plugin.json", target / ".codex-plugin/plugin.json")
        shutil.copytree(root / "skills", target / "skills")
        (target / "assets").mkdir()
        shutil.copy2(root / "assets/finuslugi-base.png", target / "assets/finuslugi-base.png")
        shutil.copy2(root / "assets/finuslugi-inverted.png", target / "assets/finuslugi-inverted.png")

        installed = load_json(target / ".codex-plugin/plugin.json", errors)
        if isinstance(installed, dict):
            skills_path = installed.get("skills")
            if not isinstance(skills_path, str) or not skills_path.startswith("./"):
                errors.append("Installed plugin skills path is not repository-relative")
            elif not (target / skills_path[2:]).is_dir():
                errors.append("Installed plugin skills directory does not exist")
            interface = installed.get("interface")
            if not isinstance(interface, dict):
                errors.append("Installed plugin interface is missing")
            else:
                for key in ("composerIcon", "logo"):
                    value = interface.get(key)
                    if not isinstance(value, str) or not value.startswith("./") or not (target / value[2:]).is_file():
                        errors.append(f"Installed plugin interface asset is missing: {key}")
        verify_frontmatter(target / "skills/finuslugi-3d-visual-pipeline/SKILL.md", errors)
        checks.append("plugin-install-copy")

        project = Path(temporary) / "project"
        fallback = project / ".agents/skills/finuslugi-3d-visual-pipeline"
        fallback.parent.mkdir(parents=True)
        shutil.copytree(source_skill, fallback)
        verify_frontmatter(fallback / "SKILL.md", errors)
        if (fallback / "agents/openai.yaml").is_file() is False:
            errors.append("Repository-scoped fallback lacks agents/openai.yaml")
        checks.append("repository-scoped-skill-copy")

    print(f"[{'PASS' if not errors else 'FAIL'}] Installation smoke test")
    print(f"Checks: {len(checks)}")
    print(f"Errors: {len(errors)}")
    for error in errors:
        print(f"ERROR: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
