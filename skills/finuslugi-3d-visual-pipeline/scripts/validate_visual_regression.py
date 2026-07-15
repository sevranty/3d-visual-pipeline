#!/usr/bin/env python3
"""Validate visual golden fixtures, anti-pattern mappings, and eval evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

STYLE_REQUIREMENTS = {
    "modern-flat@2.1": {"count": 3, "collection": "anchors-modern-flat"},
    "silver-gold@3.1": {"count": 3, "collection": "anchors-silver-gold"},
    "obsidian-gold@1.0": {"count": 3, "collection": "anchors-obsidian-gold"},
}
REQUIRED_FLOWS = {"simple", "complex", "local-correction"}
REQUIRED_DIAGNOSTICS = {"PALETTE_ERROR", "MATERIAL_ERROR", "BACKGROUND_ERROR", "LOGO_ERROR", "COMPOSITION_DRIFT", "DELIVERY_MISSING"}


def args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=root)
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args()


def read_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"Missing file: {path}")
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON: {path}: {exc}")
    return None


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def head(root: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"


def validate(root: Path) -> tuple[list[str], list[str]]:
    checks: list[str] = []
    errors: list[str] = []
    skill = root / "skills/finuslugi-3d-visual-pipeline"
    cases = read_json(skill / "evals/visual-cases.json", errors)
    registry = read_json(root / "assets/manifest.json", errors)
    if not isinstance(cases, dict) or not isinstance(cases.get("cases"), list):
        errors.append("visual-cases.json must contain cases")
        return checks, errors
    if not isinstance(registry, dict) or not isinstance(registry.get("assets"), list):
        errors.append("asset registry must contain assets")
        return checks, errors

    assets = {item.get("asset_id"): item for item in registry["assets"] if isinstance(item, dict)}
    seen: set[str] = set()
    style_counts = {style: 0 for style in STYLE_REQUIREMENTS}
    flows: set[str] = set()
    diagnostics: set[str] = set()

    for case in cases["cases"]:
        if not isinstance(case, dict):
            errors.append("Visual case must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or re.fullmatch(r"V[GAR]-[0-9]{3}", case_id) is None:
            errors.append(f"Invalid visual case ID: {case_id!r}")
            continue
        if case_id in seen:
            errors.append(f"Duplicate visual case ID: {case_id}")
        seen.add(case_id)
        kind = case.get("kind")
        if kind not in {"positive", "negative"}:
            errors.append(f"{case_id}: invalid kind")
        assertions = case.get("assertions")
        if not isinstance(assertions, list) or not assertions or not all(isinstance(item, str) and item for item in assertions):
            errors.append(f"{case_id}: assertions must be a non-empty string array")
        flow = case.get("flow")
        if isinstance(flow, str):
            flows.add(flow)
        diagnostic = case.get("diagnostic_code")
        if isinstance(diagnostic, str):
            diagnostics.add(diagnostic)

        asset_id = case.get("asset_id")
        if asset_id is None:
            continue
        asset = assets.get(asset_id)
        if asset is None:
            errors.append(f"{case_id}: unknown asset_id {asset_id}")
            continue
        path = root / str(asset.get("path"))
        if not path.is_file():
            errors.append(f"{case_id}: missing asset file {path}")
            continue
        if file_sha(path) != asset.get("sha256"):
            errors.append(f"{case_id}: checksum mismatch for {asset_id}")
        if asset.get("approval_status") != "approved" or asset.get("rights_status") != "cleared" or asset.get("public_distribution_status") != "approved":
            errors.append(f"{case_id}: fixture is not eligible for public regression")
        if path.suffix.lower() != ".svg":
            errors.append(f"{case_id}: deterministic golden fixture must be SVG")
        else:
            try:
                ET.fromstring(path.read_text(encoding="utf-8"))
            except (ET.ParseError, UnicodeDecodeError) as exc:
                errors.append(f"{case_id}: invalid SVG: {exc}")

        style = case.get("style")
        if kind == "positive":
            if style not in STYLE_REQUIREMENTS:
                errors.append(f"{case_id}: missing canonical style")
            else:
                style_counts[style] += 1
                if asset.get("collection_id") != STYLE_REQUIREMENTS[style]["collection"]:
                    errors.append(f"{case_id}: asset collection does not match style")
                text = path.read_text(encoding="utf-8")
                if style == "modern-flat@2.1" and "#FF0508" not in text:
                    errors.append(f"{case_id}: Modern Flat fixture lacks controlled brand-red marker")
                if style == "silver-gold@3.1" and ("silver" not in text or "gold" not in text):
                    errors.append(f"{case_id}: Silver-Gold fixture lacks named material gradients")
                if style == "obsidian-gold@1.0" and 'fill="#000000"' not in text:
                    errors.append(f"{case_id}: Obsidian Gold fixture lacks pure-black background")
        elif asset.get("type") != "anti-pattern" or asset.get("collection_id") != "anti-patterns":
            errors.append(f"{case_id}: negative visual fixture is not registered as anti-pattern")

    for style, requirement in STYLE_REQUIREMENTS.items():
        if style_counts[style] < requirement["count"]:
            errors.append(f"{style} has {style_counts[style]} positive cases; requires {requirement['count']}")
    if not REQUIRED_FLOWS.issubset(flows):
        errors.append(f"Missing flows: {', '.join(sorted(REQUIRED_FLOWS - flows))}")
    if not REQUIRED_DIAGNOSTICS.issubset(diagnostics):
        errors.append(f"Missing diagnostic regressions: {', '.join(sorted(REQUIRED_DIAGNOSTICS - diagnostics))}")
    repeatability = cases.get("repeatability")
    if not isinstance(repeatability, dict) or repeatability.get("attempts", 0) < 3 or repeatability.get("minimum_style_passes", 0) < 2:
        errors.append("Repeatability contract must require at least 3 attempts and 2 style passes")

    checks.extend(["visual-case-ids", "golden-style-coverage", "flow-coverage", "diagnostic-coverage", "asset-provenance", "svg-integrity", "repeatability-contract"])
    return checks, errors


def main() -> int:
    ns = args()
    root = ns.repo_root.resolve()
    checks, errors = validate(root)
    commit = head(root)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    report = ns.report or root / "validation/runtime/visual-report.json"
    if not report.is_absolute():
        report = root / report
    report.parent.mkdir(parents=True, exist_ok=True)
    payload = {"report_version":"1.0","run_id":f"{now.strftime('%Y%m%dT%H%M%SZ')}-{commit[:8] if commit != 'unknown' else 'nogit'}-visual","timestamp":now.isoformat().replace("+00:00","Z"),"head_sha":commit,"status":"pass" if not errors else "fail","passed_checks":checks,"errors":errors}
    report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[{'PASS' if not errors else 'FAIL'}] Visual regression validation")
    print(f"HEAD: {commit}\nChecks: {len(checks)}\nErrors: {len(errors)}\nReport: {report}")
    for error in errors:
        print(f"ERROR: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
