"""3DP#38: offline contract tests for the optional Presento adapter."""
from __future__ import annotations

import hashlib
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from presento_adapter import (  # noqa: E402
    PresentoAdapterError,
    make_executor,
    result_from_local_asset,
)


def png_1x1() -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    pixel = zlib.compress(b"\x00\xff\x00\x00")
    return (
        b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", pixel) + chunk(b"IEND", b"")
    )


def request(kind: str = "raster-image") -> dict:
    return {
        "schema_version": "1.0.0",
        "request_id": "3dp-38-offline-1",
        "provider_id": "3dp",
        "asset_kind": kind,
        "prompt_profile": None,
        "requirements": {"mime_type": "image/png"},
        "config": {"style": "local", "seed": 42},
    }


class PresentoAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="3dp-presento-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "accepted.png"
        self.payload = png_1x1()
        self.path.write_bytes(self.payload)
        self.digest = hashlib.sha256(self.payload).hexdigest()

    def result(self, data: dict | None = None, **kwargs) -> dict:
        return result_from_local_asset(
            request() if data is None else data,
            asset_root=self.root,
            asset_path=kwargs.get("asset_path", Path("accepted.png")),
            expected_sha256=kwargs.get("expected_sha256", self.digest),
            provider_revision=kwargs.get("provider_revision", "3dp-reviewed-sha"),
        )

    def assert_code(self, code: str, data: dict | None = None, **kwargs) -> None:
        with self.assertRaises(PresentoAdapterError) as caught:
            self.result(data, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def test_raster_result_has_exact_provenance_and_no_writes(self) -> None:
        before = self.path.read_bytes()
        result = self.result()
        self.assertEqual(set(result), {
            "schema_version", "request_id", "provider_id", "provider_project_id",
            "provider_revision", "config_sha256", "asset_kind", "materialization",
            "mime_type", "path", "checksum", "dimensions", "diagnostics",
        })
        self.assertEqual(result["schema_version"], "1.0.0")
        self.assertEqual(result["provider_project_id"], "3D_VISUAL_PIPELINE")
        self.assertEqual(result["provider_revision"], "3dp-reviewed-sha")
        self.assertEqual(result["checksum"], self.digest)
        self.assertEqual(result["path"], self.path.resolve().as_posix())
        self.assertEqual(result["dimensions"], {"width_px": 1, "height_px": 1})
        self.assertEqual(result["diagnostics"], [])
        self.assertEqual(self.path.read_bytes(), before)

    def test_3d_render_uses_same_local_result_contract(self) -> None:
        result = self.result(request("3d-render"))
        self.assertEqual(result["asset_kind"], "3d-render")
        self.assertEqual(result["mime_type"], "image/png")
        self.assertEqual(result["materialization"], "local-file")

    def test_config_sha_is_canonical(self) -> None:
        first = request()
        second = request()
        second["config"] = {"seed": 42, "style": "local"}
        a = self.result(first)["config_sha256"]
        b = self.result(second)["config_sha256"]
        self.assertEqual(a, b)
        expected = hashlib.sha256(
            json.dumps(first["config"], ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        self.assertEqual(a, expected)

    def test_missing_revision_refuses_to_invent_provenance(self) -> None:
        self.assert_code("missing_provider_revision", provider_revision="")

    def test_wrong_or_missing_checksum_is_rejected(self) -> None:
        self.assert_code("asset_checksum_mismatch", expected_sha256="0" * 64)
        self.assert_code("missing_asset_provenance", expected_sha256="unknown")

    def test_outside_root_and_missing_file_are_rejected(self) -> None:
        other = self.root.parent / (self.root.name + "-external.png")
        other.write_bytes(self.payload)
        self.addCleanup(other.unlink)
        self.assert_code("asset_outside_root", asset_path=other)
        self.assert_code("missing_asset", asset_path=Path("missing.png"))

    def test_symlink_cannot_escape_root(self) -> None:
        other = self.root.parent / (self.root.name + "-external.png")
        other.write_bytes(self.payload)
        self.addCleanup(other.unlink)
        (self.root / "escape.png").symlink_to(other)
        self.assert_code("asset_outside_root", asset_path=Path("escape.png"))

    def test_version_provider_and_capability_are_strict(self) -> None:
        data = request()
        data["schema_version"] = "2.0.0"
        self.assert_code("unsupported_version", data)
        data = request()
        data["provider_id"] = "ogp"
        self.assert_code("unsupported_provider", data)
        data = request()
        data["asset_kind"] = "vector-image"
        self.assert_code("unsupported_capability", data)

    def test_mime_mismatch_and_unsupported_bytes(self) -> None:
        data = request()
        data["requirements"]["mime_type"] = "image/jpeg"
        self.assert_code("mime_mismatch", data)
        self.path.write_bytes(b"not a valid image")
        self.assert_code(
            "unsupported_mime",
            expected_sha256=hashlib.sha256(self.path.read_bytes()).hexdigest(),
        )

    def test_executor_is_explicit_and_never_writes_output_directory(self) -> None:
        output = self.root / "presento-output"
        executor = make_executor(
            asset_root=self.root, asset_path=self.path, expected_sha256=self.digest,
        )
        payload, mime_type, dimensions = executor(request("3d-render"), output)
        self.assertEqual(payload, self.payload)
        self.assertEqual(mime_type, "image/png")
        self.assertEqual(dimensions, {"width_px": 1, "height_px": 1})
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
