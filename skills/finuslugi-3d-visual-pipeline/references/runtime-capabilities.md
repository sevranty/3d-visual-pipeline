# Runtime Capabilities

The canonical skill is independent from any single image generator. Runtime selection is based on an explicit capability profile rather than a tool name.

## Capability vocabulary

| capability | meaning |
|---|---|
| `generate` | Create a new image from a Scene Specification and prompt plan. |
| `reference-conditioned` | Use input images as conditioning references without directly editing their pixels. |
| `edit` | Modify a supplied image while preserving approved regions. |
| `mask-edit` | Restrict an edit to an explicit mask or region. |
| `multi-reference` | Accept more than one image reference in one execution step. |
| `identity-preservation` | Preserve a person, product, or recognizable object with declared fidelity. |
| `transparent-output` | Produce a usable alpha channel. |
| `upscale` | Increase resolution while preserving geometry and style. |
| `exact-dimensions` | Produce requested pixel dimensions without later resampling. |
| `deliver` | Return the generated image visibly in the user-facing response. |
| `seed-control` | Accept a repeatable seed or equivalent deterministic control. |

Each capability state is `supported`, `unsupported`, or `unknown`. `unknown` is never treated as support.

## Canonical profiles

### `chatgpt-image-generation@1`

Expected baseline:

- `generate`: supported;
- `reference-conditioned`: supported when usable conversation images are present;
- `edit`: supported only when the exact target image is present in the current conversation;
- `mask-edit`: unknown unless the active tool exposes an explicit mask operation;
- `multi-reference`: supported subject to the active tool limit;
- `identity-preservation`: conditional and never guaranteed;
- `transparent-output`: supported only when exposed by the active tool;
- `upscale`: unsupported unless a dedicated upscale operation is exposed;
- `exact-dimensions`: tool-dependent;
- `deliver`: mandatory and supported by the image-generation response path;
- `seed-control`: unknown unless explicitly exposed.

### `nano-banana-style@1`

Expected baseline for an external executor controlled by ChatGPT:

- `generate`: supported;
- `reference-conditioned`: supported;
- `edit`: supported when an editable source is accepted;
- `mask-edit`: tool/version-dependent;
- `multi-reference`: supported within executor limits;
- `identity-preservation`: conditional;
- `transparent-output`: tool/version-dependent;
- `upscale`: may require a separate stage;
- `exact-dimensions`: tool/version-dependent;
- `deliver`: not implied by generator success and must be verified separately;
- `seed-control`: tool/version-dependent.

The actual run records observed capabilities, not only the expected baseline.

## Profile contract

A runtime profile contains:

- stable `profile_id` and `profile_version`;
- tool family, adapter ID, and observed model ID;
- capability states;
- quantitative limits such as maximum references;
- known limitations;
- evidence source and observation timestamp.

Machine contract: `../assets/schemas/runtime-capabilities.schema.json`.

## Rules

1. Tool names never override capability facts.
2. `unknown` is handled as `unsupported` for mandatory requirements.
3. A route may execute only when every mandatory capability is `supported`.
4. A fallback must be explicit, preserve all locks, and be recorded in the output manifest.
5. Hidden quality degradation is prohibited.
6. Generator success without visible delivery is `DELIVERY_MISSING`.
7. Profile changes affecting routing require a changelog entry and runtime eval update.
