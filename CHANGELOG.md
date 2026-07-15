# Changelog

All notable changes to this repository are documented here.

## Unreleased

### Added

- Tool-agnostic runtime capability vocabulary and versioned capability profiles.
- Explicit routing from Scene Specification roles to generator operations.
- Fallback and stop rules for missing edit, mask edit, multi-reference, identity preservation, transparency, exact dimensions, upscale, and delivery capabilities.
- Runtime capability JSON Schema with valid and invalid fixtures.
- Runtime behavior cases for ChatGPT image generation and Nano Banana-style execution.

### Changed

- Output manifest version `1.1` records runtime profile, adapter, requested and selected modes, required capabilities, fallback decision, and limitations.
- Canonical skill now routes through a capability gate before execution.

### Governance

- Unknown capabilities are treated as unsupported when mandatory.
- Hidden execution degradation is prohibited.
- Tool success without visible user delivery is `DELIVERY_MISSING`.

## 0.1.0 - 2026-07-15

Status: draft architecture and canonical-skill baseline.

### Added

- Skill-only Codex plugin manifest.
- Canonical orchestration skill with mandatory reference-to-image workflow.
- Reference analysis, transformation modes, semantic/identity/composition/style locks.
- Scene Specification as the source of truth.
- Prompt planning, staged generation, diagnostic iteration, weighted QA, and delivery contracts.
- Stable diagnostic codes including `DELIVERY_MISSING`.
- Versioned Modern Flat 2.1, Silver-Gold 3.1, and Obsidian Gold 1.0 style packs.
- Style-selection policy and conflict log.
- Machine-readable Scene Specification and output manifest schemas.
- Positive and negative eval cases and fixtures.
- Python stdlib-only repository validator.
- Brand asset manifest and SHA-256 checksums.
- ADRs for plugin packaging, Scene Specification, runtime independence, and public asset policy.
- Source map with stable source IDs and canonical destination mapping.

### Governance

- Exact text and Finuslugi logos are post-generation assets by default.
- Code licensing and brand-asset rights are separated.
- Silver-Gold and Obsidian Gold remain controlled-rollout specifications.
- A critical visual defect overrides the weighted QA score.
- Tool success without visible user delivery is not completion.

### Known limitations

- No approved visual golden set is included yet.
- Visual regression evidence has not been produced yet.
- Runtime capability adapters are not implemented yet.
- Public-distribution rights for binary brand assets remain pending review.
- Installation smoke testing and first release gates remain pending.
