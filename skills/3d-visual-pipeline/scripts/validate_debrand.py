#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from validation_lib import Result, parse_args, read_json, repo_root, tracked_files, write_report


def blocked_brand_tokens() -> list[str]:
    cyr = lambda seq: "".join(chr(x) for x in seq)
    return [
        "".join(["fin", "us", "lugi"]),
        cyr([1092, 1080, 1085, 1091, 1089, 1083, 1091, 1075, 1080]),
        "".join(["mo", "ex"]),
        cyr([1084, 1086, 1089, 1082, 1086, 1074, 1089, 1082, 1072, 1103, 32, 1073, 1080, 1088, 1078, 1072]),
        "".join(["f", "d", "s"]),
        "".join(["ff", "05", "08"]),
    ]


def legacy_short_ids() -> list[str]:
    return ["".join(["d", "v", "p"]), "".join(["f", "3", "d"])]


HISTORICAL_TEXT_ALLOWLIST = {
    "CHANGELOG.md",
    "release/1.0.0/RELEASE_NOTES.md",
    "docs/debt/3dp-027-governance-incident.md",
}
HISTORICAL_MARKERS = ("legacy", "historical", "deprecated")


def historical_short_id_allowed(rel: str, text: str, token: str) -> bool:
    if rel not in HISTORICAL_TEXT_ALLOWLIST:
        return False
    matching = [line for line in text.splitlines() if token in line]
    return bool(matching) and all(any(marker in line for marker in HISTORICAL_MARKERS) for line in matching)


def scan(root: Path) -> list[str]:
    errors: list[str] = []
    brand_tokens = blocked_brand_tokens()
    short_ids = legacy_short_ids()
    text_suffix = {".md", ".json", ".yaml", ".yml", ".py", ".svg", ".txt"}

    for path in tracked_files(root):
        rel = path.relative_to(root).as_posix()
        low_rel = rel.lower()
        for token in brand_tokens + short_ids:
            if token in low_rel:
                errors.append(f"blocked path token in {rel}")

        if path.suffix.lower() not in text_suffix:
            continue
        try:
            text = path.read_text(encoding="utf-8").lower()
        except UnicodeDecodeError:
            continue

        for token in brand_tokens:
            if token in text:
                errors.append(f"blocked text token in {rel}")
        for token in short_ids:
            if token in text and not historical_short_id_allowed(rel, text, token):
                errors.append(f"blocked active short id in {rel}")

    return sorted(set(errors))


def main() -> int:
    args = parse_args(__doc__ or "debrand validator")
    root = repo_root()
    result = Result("debrand")
    for error in scan(root):
        result.error(error)

    plugin = read_json(root / ".codex-plugin/plugin.json")
    if plugin.get("name") != "3d-visual-pipeline":
        result.error("generic plugin identity missing")
    if plugin.get("interface", {}).get("brandColor") != "#6B7280":
        result.error("neutral interface color missing")
    if not (root / "skills/3d-visual-pipeline").exists():
        result.error("generic skill path missing")

    result.check("active-tree-scan")
    return write_report(root, args, result)


if __name__ == "__main__":
    raise SystemExit(main())
