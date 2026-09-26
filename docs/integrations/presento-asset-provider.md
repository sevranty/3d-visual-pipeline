# Presento asset-provider boundary

Issue: 3DP#38

3DP accepts the optional Presento request/result boundary for raster and 3D render results.

- Request: `presento.asset-provider.request.v1` / `1.0.0`
- Result: `presento.asset-provider.result.v1` / `1.0.0`
- 3DP retains provider runtime and rendering ownership.
- Result must include exact provider revision, canonical configuration SHA-256, asset path and checksum provenance.
- Failures must be machine-readable.
- Contract tests must not require paid calls or secrets.
- No runtime dependency 3DP -> Presento is introduced.
- Source: https://github.com/sevranty/presento/issues/31
- Source merge: `3ce75515783cc6c956d43eaaa6dc0600a434a1e4`.

This is contract adoption; adapter implementation and tests remain before terminal completion.