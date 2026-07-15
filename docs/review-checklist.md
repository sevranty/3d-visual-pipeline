# Owner Review Checklist

Review the exact Draft PR HEAD. Any new commit invalidates the review evidence and requires a new validation and review pass.

## Architecture

- [ ] Plugin manifest points to `./skills/`.
- [ ] Runtime rules live in one canonical `SKILL.md`.
- [ ] Detailed rules live in canonical reference files.
- [ ] Machine contracts live in schemas.
- [ ] Source documents are not copied into the public repository.
- [ ] ADRs explain the main architecture decisions.

## Canonical skill

- [ ] Input validation happens before prompt generation.
- [ ] Exactly one transformation mode is selected.
- [ ] Every reference has roles, `take`, and `do_not_take` rules.
- [ ] Semantic, identity, composition, and style locks are explicit.
- [ ] Scene Specification is the source of truth.
- [ ] One versioned style pack is selected.
- [ ] Complex generation is staged.
- [ ] Local correction changes one scene layer.
- [ ] Critical defects override weighted QA.
- [ ] Visible user delivery is mandatory.

## Style packs

- [ ] Modern Flat red is limited to 10% visual weight.
- [ ] Silver-Gold uses 70-85% Silver and 15-30% Gold.
- [ ] Obsidian Gold uses pure black background and no more than 25% Gold.
- [ ] Rollout status is not confused with technical completeness.
- [ ] Source conflicts are recorded.

## Evidence

- [ ] Validator executed on exact HEAD.
- [ ] Validation report records command, run ID, and HEAD SHA.
- [ ] Valid fixtures pass.
- [ ] Invalid fixtures fail.
- [ ] Asset checksums pass.
- [ ] Open limitations are listed.

## Lifecycle

- [ ] PR remains Draft.
- [ ] PR is not merged.
- [ ] Ready or merge requires a separate owner instruction.
