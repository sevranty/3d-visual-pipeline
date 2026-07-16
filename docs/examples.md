# Minimal examples

These examples are tool-agnostic prompts for exercising the runtime contract. Each example stops if required rights, references, runtime capability, or visible delivery are unavailable.

## Style transfer

Input: one owned subject reference and permission to transform it. Select exactly one versioned style pack, preserve the subject silhouette, and deliver a visible image plus output manifest.

Stop conditions: missing rights, missing subject reference, or no visible delivery channel.

## Reinterpretation

Input: a text brief for a three-dimensional metaphor and optional palette reference. Map references to roles, compile the Scene Specification, select one style pack, and generate a new visual without claiming identity preservation.

Stop conditions: ambiguous subject, conflicting style packs, or unsupported runtime capability.

## Local correction

Input: a generated image with one diagnosed defect. Repair only the failing dimension, keep semantic and composition locks, and record the before/after evidence in the output manifest.

Stop conditions: defect requires changing locked meaning, rights are unclear, or repair cannot be visibly delivered.
