# ADR-0003: Keep orchestration independent from the generator

- Status: accepted
- Date: 2026-07-15
- Issues: #2, #6

## Context

The source production method names ChatGPT and Nano Banana, while the repository must remain usable with different image-generation capabilities. Hard-coding one generator into the canonical workflow would mix design rules with execution syntax and make future adapters expensive.

## Decision

The canonical skill owns analysis, specification, prompt planning, QA, iteration control, and delivery. The available image-generation tool owns generation or edit execution.

Runtime adapters must declare capabilities such as:

- text-to-image generation;
- reference-conditioned generation;
- image edit;
- mask edit;
- multi-reference handling;
- transparent output;
- upscale;
- visible user delivery.

The adapter may translate the Scene Specification into tool-specific calls, but it may not weaken locks or style invariants silently.

## Consequences

- Generator names do not appear as normative dependencies in style packs.
- Missing capabilities cause a documented fallback or a precise stop reason.
- Tool, model, execution mode, and limitations are recorded in the output manifest.
- Tool success without visible delivery is `DELIVERY_MISSING`.
