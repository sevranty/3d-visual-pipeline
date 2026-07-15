# ADR-0004: Separate code licensing from brand-asset rights

- Status: accepted
- Date: 2026-07-15
- Issues: #1, #7, #8

## Context

The repository is public and uses Finuslugi logos and future approved visual anchors. An MIT license can cover repository code and documentation, but it must not be interpreted as granting rights to trademarks, logos, internal source documents, or third-party references.

## Decision

- Keep code and original repository documentation under MIT.
- Record each binary asset in `../../assets/manifest.json` with a stable ID, checksum, source note, owner, approval status, allowed roles, and public-distribution status.
- Do not place internal FDS source documents in the public repository.
- Store normalized rules and source metadata instead of source DOCX/PDF files.
- Treat brand assets as post-production inputs, never as generative targets.
- Block the first public release until rights review confirms every public binary asset and golden reference.

## Consequences

- The repository may be technically public before it is release-ready.
- `pending-rights-review` is a release blocker, not a validator error during architectural development.
- New binary assets require manifest and checksum changes in the same PR.
- Removing an asset requires manifest history and changelog evidence.
