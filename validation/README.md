# Validation Evidence

Each local validation run writes a JSON report to `validation/<run-id>/report.json`.

A report is evidence only when it records:

- exact command;
- UTC timestamp;
- repository HEAD SHA;
- passed checks;
- warnings;
- errors;
- final `pass` or `fail` status.

Connector-level file inspection is not equivalent to executing the validator. Do not create a passing report without running:

```bash
python3 skills/finuslugi-3d-visual-pipeline/scripts/validate_repository.py
```

Visual QA and golden-image regression remain separate from this deterministic validation directory.
