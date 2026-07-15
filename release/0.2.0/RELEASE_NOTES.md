# Finuslugi 3D Visual Pipeline 0.2.0

`0.2.0` is the first governed public release candidate of the skill-only Codex plugin.

## Highlights

- Canonical reference-to-image orchestration from input validation to visible delivery.
- Versioned Modern Flat 2.1, Silver-Gold 3.1, and Obsidian Gold 1.0 style packs.
- Scene Specification as the source of truth.
- Capability-based routing for ChatGPT image generation, Nano Banana-style executors, and future runtimes.
- Explicit stop and fallback behavior for missing edit, mask edit, multi-reference, identity, transparency, upscale, dimensions, and delivery capabilities.
- Governed asset registry with provenance, rights, approval, role, collection, checksum, and history controls.
- Nine public deterministic SVG golden fixtures and five diagnostic anti-patterns.
- Repository, runtime, asset, visual, smoke, and release validators using the Python standard library.

## Breaking changes from 0.1.0

This is a backward-compatible minor release at plugin level. Output manifest version advances from `1.0` to `1.1` and adds mandatory runtime provenance and fallback fields. Consumers that parse output manifests must accept the new execution contract.

## Security and rights

- No MCP server, hook, package dependency, executable binary, or network-fetching runtime is bundled.
- Internal FDS source documents are not included.
- Finuslugi logos are owner-supplied and approved for this repository; downstream trademark rights are not granted.
- Golden and anti-pattern SVG fixtures are repository-authored and are not production illustrations.

## Known limitations

- Runtime capability profiles describe observed contracts; exact generator capabilities remain environment-dependent.
- Identity preservation is never guaranteed by the canonical skill.
- Hosted GitHub Actions runs were unavailable for several implementation PRs; deterministic exact-HEAD review evidence is retained in those PRs and validation files.
- Tag and GitHub Release publication require an external GitHub API operation after merge.

## Upgrade

Install from the `v0.2.0` tag when it is published. Before tag publication, use the exact release merge commit recorded in `validation-manifest.json`.
