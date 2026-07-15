# Style Selection

Select exactly one primary style pack before prompt compilation. A style pack is a versioned production contract, not a mood label.

## Available packs

| style_id | version | repository status | intended use |
|---|---:|---|---|
| `modern-flat` | `2.1` | canonical | Main Finuslugi illustration language for brand, product, marketing, and AI-assisted scenes. |
| `silver-gold` | `3.1` | canonical specification; controlled rollout | Premium value, increased yield, status levels, awards, and selected hero objects. |
| `obsidian-gold` | `1.0` | canonical specification; controlled rollout | High-value, private, investment, security, and exclusive-service scenarios on a black background. |

Repository status describes the normalized contract in this plugin. Product or campaign approval remains a separate governance decision.

## Selection rules

1. Choose `modern-flat` for human-centered scenes, lifestyle narratives, digital work, mobility, growth, or broad product communication.
2. Choose `silver-gold` for a premium object where technological stability is the base and gold is a limited value accent.
3. Choose `obsidian-gold` for one isolated premium object whose meaning depends on status, security, exclusivity, or controlled value.
4. Do not mix primary material, lighting, background, or palette invariants from different packs.
5. A hybrid is invalid until it has a unique `style_id`, version, source decision, prompt vocabulary, rejection criteria, and regression cases.

## Required Scene Specification values

```yaml
locks:
  style:
    id: "modern-flat | silver-gold | obsidian-gold"
    version: "exact version"
```

The style selection must also record:

- why the pack matches the communication task;
- which channel and background are intended;
- whether the pack requires additional design review;
- which approved anchor images were used;
- any documented deviation.

## Conflict handling

When the visual architecture status and a detailed style specification differ, do not hide the conflict. Use the detailed document as the technical source for rendering rules, keep the rollout status explicit, and record the normalization in `style-conflict-log.md`.
