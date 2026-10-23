#!/usr/bin/env python3
"""3DP#38: offline Presento v1 boundary for already accepted local renders.

The caller owns 3DP generation and QA and supplies an existing file, its
expected SHA-256, and the exact provider revision. This module does not
generate images, contact Presento, write files, or read credentials.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

VERSION = "1.0.0"
REQUEST_CONTRACT = "presento.asset-provider.request.v1"
RESULT_CONTRACT = "presento.asset-provider.result.v1"
PROJECT_ID = "3D_VISUAL_PIPELINE"
PROVIDER_ID = "3dp"
ASSET_KINDS = frozenset({"raster-image", "3d-render"})
_REQUEST_FIELDS = frozenset({
    "schema_version", "request_id", "provider_id", "asset_kind",
    "prompt_profile", "requirements", "config",
})
_HEX = frozenset("0123456789abcdef")
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class PresentoAdapterError(ValueError):
    """A refusal whose code is stable and machine-readable."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def validate_request(request: dict[str, Any]) -> None:
    if not isinstance(request, dict) or set(request) != _REQUEST_FIELDS:
        raise PresentoAdapterError("invalid_request", "unexpected request fields")
    if request["schema_version"] != VERSION:
        raise PresentoAdapterError("unsupported_version", "expected 1.0.0")
    if request["provider_id"] != PROVIDER_ID:
        raise PresentoAdapterError("unsupported_provider", "expected 3dp")
    if request["asset_kind"] not in ASSET_KINDS:
        raise PresentoAdapterError("unsupported_capability", "raster-image or 3d-render required")
    if not isinstance(request["request_id"], str) or not request["request_id"].strip():
        raise PresentoAdapterError("invalid_request", "request_id is required")
    if request["prompt_profile"] is not None and not isinstance(request["prompt_profile"], str):
        raise PresentoAdapterError("invalid_request", "prompt_profile must be string or null")
    if not isinstance(request["requirements"], dict) or not isinstance(request["config"], dict):
        raise PresentoAdapterError("invalid_request", "requirements and config must be objects")


def _sha256(value: str) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in _HEX for ch in value)


def _canonical_config(request: dict[str, Any]) -> str:
    try:
        encoded = json.dumps(
            request["config"], ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise PresentoAdapterError("invalid_config", "config is not canonical JSON") from exc
    return hashlib.sha256(encoded).hexdigest()


def _asset(
    *,
    asset_root: Path,
    asset_path: Path,
    expected_sha256: str,
) -> tuple[bytes, str, dict[str, int] | None, Path]:
    if not _sha256(expected_sha256):
        raise PresentoAdapterError("missing_asset_provenance", "expected sha256 is required")
    try:
        root = Path(asset_root).resolve(strict=True)
        candidate = Path(asset_path)
        resolved = (candidate if candidate.is_absolute() else root / candidate).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PresentoAdapterError("missing_asset", "local asset cannot be resolved") from exc
    if not root.is_dir() or root not in resolved.parents or not resolved.is_file():
        raise PresentoAdapterError("asset_outside_root", "asset must be a file inside the 3DP root")
    try:
        payload = resolved.read_bytes()
    except OSError as exc:
        raise PresentoAdapterError("missing_asset", "local asset cannot be read") from exc
    if not payload:
        raise PresentoAdapterError("empty_asset", "local asset is empty")
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise PresentoAdapterError("asset_checksum_mismatch", "bytes differ from accepted checksum")

    if payload.startswith(_PNG_MAGIC):
        if len(payload) < 33 or payload[12:16] != b"IHDR":
            raise PresentoAdapterError("invalid_asset", "PNG has no IHDR")
        width = int.from_bytes(payload[16:20], "big")
        height = int.from_bytes(payload[20:24], "big")
        if width <= 0 or height <= 0:
            raise PresentoAdapterError("invalid_asset", "PNG dimensions are invalid")
        mime_type = "image/png"
        dimensions: dict[str, int] | None = {"width_px": width, "height_px": height}
    elif payload.startswith(b"\xff\xd8") and payload.endswith(b"\xff\xd9"):
        mime_type = "image/jpeg"
        dimensions = None
    else:
        raise PresentoAdapterError("unsupported_mime", "only local PNG/JPEG renders are supported")
    return payload, mime_type, dimensions, resolved


def _checked(
    request: dict[str, Any],
    *,
    asset_root: Path,
    asset_path: Path,
    expected_sha256: str,
) -> tuple[bytes, str, dict[str, int] | None, Path]:
    validate_request(request)
    payload, mime_type, dimensions, resolved = _asset(
        asset_root=asset_root, asset_path=asset_path, expected_sha256=expected_sha256,
    )
    required_mime = request["requirements"].get("mime_type")
    if required_mime is not None and required_mime != mime_type:
        raise PresentoAdapterError("mime_mismatch", "asset does not satisfy requested mime_type")
    return payload, mime_type, dimensions, resolved


def make_executor(
    *,
    asset_root: Path,
    asset_path: Path,
    expected_sha256: str,
) -> Callable[[dict[str, Any], Path], tuple[bytes, str, dict[str, int] | None]]:
    """Explicit executor for Presento's external-local-runtime provider.

    The output directory is owned by Presento; this adapter never writes it.
    """
    def execute(
        request: dict[str, Any], output_dir: Path,
    ) -> tuple[bytes, str, dict[str, int] | None]:
        payload, mime_type, dimensions, _ = _checked(
            request, asset_root=asset_root, asset_path=asset_path,
            expected_sha256=expected_sha256,
        )
        return payload, mime_type, dimensions

    return execute


def result_from_local_asset(
    request: dict[str, Any],
    *,
    asset_root: Path,
    asset_path: Path,
    expected_sha256: str,
    provider_revision: str,
) -> dict[str, Any]:
    """Build Presento result v1 from a verified, pre-existing 3DP output."""
    validate_request(request)
    if not isinstance(provider_revision, str) or not provider_revision.strip():
        raise PresentoAdapterError("missing_provider_revision", "exact 3DP revision is required")
    payload, mime_type, dimensions, resolved = _checked(
        request, asset_root=asset_root, asset_path=asset_path,
        expected_sha256=expected_sha256,
    )
    return {
        "schema_version": VERSION,
        "request_id": request["request_id"],
        "provider_id": PROVIDER_ID,
        "provider_project_id": PROJECT_ID,
        "provider_revision": provider_revision,
        "config_sha256": _canonical_config(request),
        "asset_kind": request["asset_kind"],
        "materialization": "local-file",
        "mime_type": mime_type,
        "path": resolved.as_posix(),
        "checksum": hashlib.sha256(payload).hexdigest(),
        "dimensions": dimensions,
        "diagnostics": [],
    }
