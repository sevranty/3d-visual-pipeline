# Presento asset-provider contract fixtures

Issue: 3DP#38

Repository-only cases for the optional Presento boundary covering raster and 3D render results. They require no paid calls or secrets.

## Successful raster or 3D result

Required provenance:

- exact provider revision;
- canonical configuration SHA-256 as 64 lowercase hexadecimal characters;
- materialized raster/render asset path owned by 3DP;
- asset checksum as `sha256:` plus 64 lowercase hexadecimal characters.

Expected outcome: `accepted`.

## Missing provider revision

Expected outcome: `rejected` with machine-readable reason `missing_provider_revision`.

## Invalid configuration digest

Expected outcome: `rejected` with machine-readable reason `invalid_config_sha256`.

## Missing asset provenance

Path or checksum is absent for the materialized result.

Expected outcome: `rejected` with machine-readable reason `missing_asset_provenance`.

## Provider failure

Provider fails before a raster/render asset exists.

Expected outcome: machine-readable failure with a stable error code and no fabricated path/checksum.

## Ownership invariant

3DP retains render-generation and runtime ownership. Presento remains an optional integration caller and does not become a runtime dependency of 3DP.

Source contract: https://github.com/sevranty/presento/issues/31
Source merge: `3ce75515783cc6c956d43eaaa6dc0600a434a1e4`.
