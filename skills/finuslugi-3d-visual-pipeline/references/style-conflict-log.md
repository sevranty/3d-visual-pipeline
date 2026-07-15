# Style Conflict Log

This file records conflicts between source documents and the normalization decision used by the canonical skill. Do not silently resolve future conflicts inside prompt text.

## CL-001: Architecture status versus technical completeness

**Sources**

- Visual Architecture v2 lists Modern Flat as the main style.
- The same architecture lists Obsidian Gold and Silver-Gold as concept or controlled premium directions.
- Dedicated style documents provide detailed production rules for all three packs.

**Decision**

The repository treats all three documents as canonical technical specifications, but preserves governance status:

- `modern-flat@2.1`: canonical, primary;
- `silver-gold@3.1`: canonical specification, controlled rollout;
- `obsidian-gold@1.0`: canonical specification, controlled rollout.

A technically valid prompt does not imply automatic product approval.

## CL-002: Obsidian background

**Conflict**

Some expanded descriptions allow black or deep graphite. Other production specifications require pure black.

**Decision**

Production background is `#000000`. Deep graphite is exploratory only and is invalid for `obsidian-gold@1.0` production output.

## CL-003: Obsidian environment

**Conflict**

Marketing descriptions imply broader campaign contexts, while the production specification requires one isolated object without an environment.

**Decision**

The canonical pack requires one isolated object. Any environment-based scene is a derivative style and must receive a new ID, version, source decision, and eval set.

## CL-004: Obsidian material wording

**Conflict**

The word `obsidian` can cause natural stone texture drift.

**Decision**

Use `matte obsidian-black` or `faceted obsidian-black`. Reject `obsidian stone`, rock, mineral, and realistic stone texture.

## CL-005: Obsidian production effort

**Conflict**

Source snapshots describe both hour-scale production and multi-day board-ready work.

**Decision**

Treat them as different quality tiers:

- icon-grade: compact isolated asset, hour-scale effort;
- board-ready hero: higher detail and manual refinement, multi-day effort.

Both must satisfy the same style invariants.

## CL-006: Silver-Gold background semantics

**Conflict**

The detailed style guide allows dark or neutral backgrounds, while the visual architecture notes a light-theme rollout risk.

**Decision**

Rendering may use a dark or neutral background according to the detailed technical specification. Product placement in a theme remains a governance decision and must be recorded in the output manifest.

## CL-007: Modern Flat naming and master snapshots

**Conflict**

The source document contains multiple embedded historical snapshots with version numbers that differ from the document-level version `2.1`.

**Decision**

The repository style ID remains `modern-flat@2.1`. Embedded snapshots are treated as source history. Canonical rules are the normalized common invariants and explicit document-level controls: non-photorealistic output, volumetric gradients, heroic light, clean shadows, safe areas, and red limited to 10% visual weight.

## Change rule

A new conflict entry must include:

1. stable conflict ID;
2. affected sources;
3. user-visible or production impact;
4. normalization decision;
5. files and evals affected;
6. required version change, when behavior changes.
