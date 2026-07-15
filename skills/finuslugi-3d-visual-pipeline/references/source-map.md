# Source Map

This repository stores normalized production rules and source metadata. It does not publish the internal source DOCX/PDF files.

## Source registry

| source_id | source document | version or date | canonical responsibility |
|---|---|---|---|
| `SRC-PIPELINE-001` | `3D Иллюстрации Финуслуг.pdf` | Pipeline 1.0, 2026 | Designer-first sequence, metaphor search, reference roles, composition lock, technical brief, diagnostic first generation, staged correction, complex-scene order, and final upscale. |
| `SRC-ARCH-001` | `FDS [visual-architecture] Архитектура визуальных стилей Финуслуг v2 (август 2025).docx` | v2, August 2025 | Visual-layer positioning, style status, product/marketing/AI responsibilities, and the style-pack model of prompts, negatives, anchors, QA, and versioning. |
| `SRC-STYLE-MF-001` | `FDS [visual-style] Стиль Modern Flat v2.1 (2026-02-24).docx` | v2.1, 2026-02-24 | Modern Flat geometry, light, palette, composition, safe areas, prohibitions, prompt markers, and QA. |
| `SRC-STYLE-SG-001` | `FDS [visual-style] Стиль Silver-Gold v3.1 (2026-02-24).docx` | v3.1, 2026-02-24 | Silver/Gold semantics and ratio, matte/satin materials, controlled reflections, light, prohibitions, governance, and QA. |
| `SRC-STYLE-OG-001` | `FDS [visual-style] Стиль Obsidian Gold v1.0 (2026-02-24).docx` | v1.0, 2026-02-24 | Obsidian/Gold tokens, isolated-object composition, pure-black background, prompt requirements, prohibitions, conflict resolutions, and QA. |
| `DEC-F3D-006` | GitHub Issue #6 and owner execution instruction | 2026-07-15 | Tool-agnostic capability vocabulary, runtime routing, explicit fallback rules, execution provenance, and delivery failure semantics. |
| `DEC-F3D-007` | GitHub Issue #7 and owner execution instruction | 2026-07-15 | Stable asset identities, rights and approval states, collection boundaries, checksum policy, history, and public golden eligibility. |
| `DEC-F3D-004` | GitHub Issue #4 and owner execution instruction | 2026-07-15 | Deterministic public regression goldens, anti-pattern diagnostics, flow coverage, repeatability evidence, and golden replacement policy. |

## Canonical destination map

| normalized topic | canonical repository file |
|---|---|
| runtime orchestration order | `../SKILL.md` |
| workflow states | `workflow.md` |
| input and reference requirements | `input-contract.md`, `reference-analysis.md` |
| transformation modes | `transformation-modes.md` |
| Scene Specification | `scene-specification.md`, `../assets/schemas/scene-spec.schema.json` |
| prompt compilation and staged execution | `prompt-architecture.md`, `generation-sequence.md` |
| runtime capability vocabulary and profiles | `runtime-capabilities.md`, `../assets/schemas/runtime-capabilities.schema.json` |
| runtime route selection and reference mapping | `runtime-routing.md` |
| runtime fallbacks and stop rules | `runtime-fallbacks.md` |
| runtime behavior regression | `../evals/runtime-cases.json` |
| governed asset policy | `asset-governance.md`, `../../../assets/manifest.json` |
| asset registry schema and history | `../assets/schemas/asset-manifest.schema.json`, `../../../assets/manifest-history.json` |
| asset governance regression | `../evals/asset-cases.json` |
| visual golden and anti-pattern cases | `../evals/visual-cases.json` |
| visual regression evidence | `../evals/results/` |
| deterministic visual validation | `../scripts/validate_visual_regression.py` |
| diagnostic correction | `diagnostic-codes.md`, `iteration-rules.md` |
| weighted visual QA | `quality-gates.md` |
| final delivery and execution manifest | `output-delivery.md`, `../assets/schemas/output-manifest.schema.json` |
| style selection and governance status | `style-selection.md` |
| Modern Flat | `style-modern-flat.md` |
| Silver-Gold | `style-silver-gold.md` |
| Obsidian Gold | `style-obsidian-gold.md` |
| conflicting source statements | `style-conflict-log.md` |

## Normalization decisions

- The pipeline PDF defines the production method but not a complete installable skill contract.
- The Scene Specification is the source of truth; natural-language prompts are compiled outputs.
- Every reference receives an explicit role plus `take` and `do_not_take` constraints.
- Style details are separated into independently versioned style packs.
- Visual-architecture rollout status is preserved even when a detailed style document is technically complete.
- Exact text and Finuslugi logos are post-generation assets by default.
- Tool names do not imply capabilities; every route uses an observed capability profile.
- `unknown` is treated as unsupported for mandatory capabilities.
- Requested and selected execution modes may differ only through a recorded fallback.
- Unregistered visual files and generated logos are rejected.
- Exploratory references are quarantine-only and cannot become style sources implicitly.
- Public golden assets require approved status, cleared rights, and public distribution approval.
- Repository SVG goldens test contracts and invariants; they do not claim production-art or model-quality equivalence.
- Every anti-pattern is linked to one primary diagnostic code.
- Tool success and user-visible delivery are separate states.
- Tool success without a visible image is `DELIVERY_MISSING`.
- A critical defect overrides the weighted QA score.

## Traceability rule

Every normative rule added to the repository must be supported by one of:

1. a registered source ID;
2. an accepted ADR in `../../../docs/decisions/`;
3. an explicit owner decision recorded in an Issue or PR.

A normalization decision that changes behavior must also update the relevant eval case.

## Version policy

When a source document or owner decision changes behavior:

1. record the new source version, date, or decision ID;
2. update only the affected canonical file;
3. add a conflict-log entry when sources disagree;
4. increment the style, schema, registry, or plugin version when required;
5. update `CHANGELOG.md`;
6. add or update an eval case;
7. run the repository, runtime, asset, and visual regression validators;
8. keep this source map synchronized.
