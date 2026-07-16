# Installation

Use repository tag `v1.0.0` after publication. For repository scope:

```bash
mkdir -p .agents/skills
cp -R skills/3d-visual-pipeline .agents/skills/3d-visual-pipeline
python3 skills/3d-visual-pipeline/scripts/smoke_test_installation.py
```

## Immutable tag install

After `v1.0.0` is created and validated, install from the immutable tag with:

```bash
git clone --branch v1.0.0 --depth 1 <repository-url> 3d-visual-pipeline
cd 3d-visual-pipeline
python3 skills/3d-visual-pipeline/scripts/smoke_test_installation.py
```

If hosted Actions are unavailable, record hosted CI as `not run` and attach local validation reports from `validation/runtime/`.
