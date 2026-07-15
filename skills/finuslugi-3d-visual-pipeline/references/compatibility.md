# Compatibility Matrix

Release: `0.2.0`.

| Environment | Packaging | Status | Notes |
|---|---|---|---|
| Codex client with plugin support | `.codex-plugin/plugin.json` + `skills/` | supported | Install repository root through the available plugin-management interface. |
| Codex or agent harness with repository-scoped Agent Skills | `.agents/skills/<name>/SKILL.md` | supported fallback | Copy the canonical skill directory; plugin interface metadata is not loaded. |
| ChatGPT image generation runtime | capability profile `chatgpt-image-generation@1` | contract-supported | Actual generate/edit/reference/alpha capabilities must be observed at runtime. |
| Nano Banana-style external executor | capability profile `nano-banana-style@1` | contract-supported | Orchestration, QA, and delivery verification remain in ChatGPT. |
| Future image runtime | runtime-capabilities schema | supported by adapter | Requires a versioned profile, routing evidence, and eval update. |
| Python 3.10–3.13 | standard-library validators | supported | No third-party Python dependencies. |
| Python below 3.10 | validators | unsupported | Code uses modern type annotations. |
| Windows, macOS, Linux | repository files and validators | expected | Smoke test uses only portable Python filesystem operations. |

## Contract compatibility

- Plugin: `0.2.0`.
- Scene Specification: `1.0`.
- Output manifest: `1.1`.
- Runtime profile: `1.0`.
- Asset registry: `2.0`.
- Modern Flat: `2.1`.
- Silver-Gold: `3.1`.
- Obsidian Gold: `1.0`.

## Not guaranteed

Compatibility does not guarantee that a particular generator supports mask edit, exact identity, transparency, exact dimensions, seed control, or upscale. Those are runtime capability decisions.
