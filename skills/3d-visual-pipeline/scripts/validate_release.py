#!/usr/bin/env python3
from __future__ import annotations
import re, subprocess
from validation_lib import Result, parse_args, read_json, repo_root, write_report
VERSION='1.0.0'; TAG='v1.0.0'
STATES={'candidate','tagged-validated','published'}
FULL_LOCAL_COMMAND=' && '.join([
    'python3 skills/3d-visual-pipeline/scripts/validate_repository.py',
    'python3 skills/3d-visual-pipeline/scripts/validate_runtime_contract.py',
    'python3 skills/3d-visual-pipeline/scripts/validate_asset_registry.py',
    'python3 skills/3d-visual-pipeline/scripts/validate_visual_regression.py',
    'python3 skills/3d-visual-pipeline/scripts/smoke_test_installation.py',
    'python3 skills/3d-visual-pipeline/scripts/validate_release.py',
    'python3 skills/3d-visual-pipeline/scripts/validate_debrand.py',
    'python3 -m unittest discover -s skills/3d-visual-pipeline/tests -p "test_*.py"',
])

def git(root,*args):
    return subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,check=False).stdout.strip()

def main():
    args=parse_args(__doc__ or 'release validator'); root=repo_root(); r=Result('release')
    plugin=read_json(root/'.codex-plugin/plugin.json'); manifest=read_json(root/f'release/{VERSION}/validation-manifest.json')
    head=git(root,'rev-parse','HEAD'); tag_sha=git(root,'rev-list','-n','1',TAG)
    if plugin.get('version')!=VERSION: r.error('plugin version not aligned')
    if manifest.get('version')!=VERSION or manifest.get('intended_tag')!=TAG: r.error('release manifest not aligned')
    for path in [f'release/{VERSION}/RELEASE_NOTES.md','CHANGELOG.md','README.md','RELEASE_CHECKLIST.md']:
        text=(root/path).read_text(encoding='utf-8')
        if VERSION not in text: r.error(f'version absent from {path}')
    status=manifest.get('status')
    if status not in STATES: r.error('release status must be candidate, tagged-validated, or published')
    evidence=manifest.get('evidence',{})
    if not isinstance(evidence,dict):
        r.error('release evidence must be an object'); evidence={}
    head_sha=evidence.get('head_sha'); tag_evidence=evidence.get('tag_sha')
    if head_sha is not None and not (isinstance(head_sha,str) and re.fullmatch(r'[0-9a-f]{40}',head_sha)): r.error('release evidence head_sha must be null or a 40-character sha')
    if isinstance(head_sha,str) and re.fullmatch(r'[0-9a-f]{40}',head_sha) and head_sha!=head: r.error('release evidence head_sha is stale')
    if tag_evidence is not None and not (isinstance(tag_evidence,str) and re.fullmatch(r'[0-9a-f]{40}',tag_evidence)): r.error('release evidence tag_sha must be null or a 40-character sha')
    if evidence.get('local_command')!=FULL_LOCAL_COMMAND: r.error('release evidence local_command must match the deterministic CI parity command')
    if evidence.get('reports_path')!='validation/runtime/': r.error('release evidence reports_path must be validation/runtime/')
    if head_sha is None and evidence.get('head_binding')!='runtime validator records git rev-parse HEAD in release report checks': r.error('release evidence head_binding must describe runtime exact HEAD binding')
    r.check(f'exact-head:{head}')
    if status=='candidate':
        if evidence.get('hosted_ci')!='not run': r.error('candidate hosted_ci must be not run')
        if manifest.get('published_at_utc'): r.error('candidate cannot be published')
    if status in {'tagged-validated','published'}:
        if not tag_sha: r.error(f'{status} requires local tag {TAG}')
        elif evidence.get('tag_sha')!=tag_sha: r.error('release evidence tag_sha is stale')
    if status=='published' and not manifest.get('published_at_utc'): r.error('published status requires published_at_utc')
    if manifest.get('legacy_immutable_tag')!='v0.2.0': r.error('legacy immutable tag v0.2.0 must be recorded')
    r.check('release-state-machine'); r.check('version-and-publication-contract'); return write_report(root,args,r)
if __name__=='__main__': raise SystemExit(main())
