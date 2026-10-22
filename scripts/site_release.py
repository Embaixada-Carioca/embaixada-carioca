#!/usr/bin/env python3
"""Build-time provenance; never commit a guessed production SHA to the source tree."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess

CRITICAL_ASSETS = ('assets/conversion-tracking.js', 'assets/event-system-link.js',
                   'assets/css/ec-home-2026.css', 'assets/js/ec-a11y-guard.js')

def write_manifest(root: Path, output: Path) -> dict:
    sha = os.environ.get('GITHUB_SHA') or subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('A full, real Git commit SHA is required')
    manifest = {
        'schema_version': 1, 'site': 'Embaixada Carioca',
        'repository': 'Embaixada-Carioca/embaixada-carioca', 'branch': 'master',
        'deploy_sha': sha,
        'built_at': datetime.now(timezone.utc).isoformat(),
        'assets': {('/' + path): hashlib.sha256((output / path).read_bytes()).hexdigest()
                   for path in CRITICAL_ASSETS},
    }
    (output / 'version.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest
