#!/usr/bin/env python3
"""Independent, read-only public smoke checks. No forms or messages are submitted."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
import re
import time
from urllib.request import Request, urlopen
from urllib.parse import urlparse

BASE = 'https://www.embaixadacarioca.com'
PAGES = {'/': 'pt', '/en/': 'en', '/es/': 'es', '/almoco': 'pt',
         '/cafe-da-manha': 'pt', '/eventos': 'pt', '/en/eventos': 'en', '/es/eventos': 'es'}
BAD = ('BondinhSugarloaf', 'Bondinhel', 'Private events up to 300', 'Quando Every day',
       'Harmonização', 'Roteiros & grupos')

class Page(HTMLParser):
    def __init__(self, content):
        super().__init__(); self.lang = ''; self.h1 = 0; self.links = []; self.canonical = ''
        self.feed(content)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = a.get('lang', '')
        if tag == 'h1': self.h1 += 1
        if tag == 'a': self.links.append(a.get('href', ''))
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a.get('href', '')

def normalized_public_path(path):
    # Public extensionless routes and their .html redirects are the same journey.
    if path.endswith('/index.html'):
        path = path[:-len('index.html')]
    elif path.endswith('.html'):
        path = path[:-len('.html')]
    return path.rstrip('/') or '/'

def validate_page(body, path, language):
    text = body.decode('utf-8'); page = Page(text)
    assert page.lang.lower().startswith(language), 'wrong document language'
    assert page.h1 == 1, 'expected one H1'
    canonical = urlparse(page.canonical)
    assert canonical.scheme == 'https' and canonical.netloc == urlparse(BASE).netloc, 'wrong canonical origin'
    assert not canonical.query and not canonical.fragment, 'canonical must not contain query or fragment'
    assert normalized_public_path(canonical.path) == normalized_public_path(path), 'wrong canonical journey'
    assert any('tagme.com.br' in link for link in page.links), 'missing reservation link'
    assert 'Bondinho' in text, 'missing park identity'
    if language in ('en', 'es'):
        assert not any(word in text for word in BAD), 'known stale/corrupt translation'
    if language == 'es':
        assert 'PRÊMIO' not in text and 'Quando' not in text, 'known stale ES translation'
    if path in ('/', '/en/', '/es/', '/eventos', '/en/eventos', '/es/eventos'):
        assert any(urlparse(link).netloc == 'leorangel22.github.io' and
                   urlparse(link).path == '/main/formulario.html' for link in page.links), 'missing central event form'

def validate_manifest(body, expected_sha=''):
    data = json.loads(body)
    assert data.get('schema_version') == 1, 'unsupported manifest schema'
    assert data.get('repository') == 'Embaixada-Carioca/embaixada-carioca', 'wrong repository'
    assert re.fullmatch('[0-9a-f]{40}', data.get('deploy_sha', '')), 'missing real commit SHA'
    if expected_sha:
        assert data['deploy_sha'] == expected_sha, 'deployed SHA differs from completed deployment'
    assert data.get('built_at'), 'missing build timestamp'
    from site_release import CRITICAL_ASSETS
    assert set(data.get('assets', {})) == {'/' + p for p in CRITICAL_ASSETS}, 'critical asset set differs'
    for path, digest in data['assets'].items():
        assert re.fullmatch('[0-9a-f]{64}', digest), 'invalid asset digest'
    return data

def fetch(path):
    request = Request(BASE + path + ('&' if '?' in path else '?') + 'health=' + str(time.time_ns()),
                      headers={'User-Agent': 'EmbaixadaSiteHealth/1.0', 'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=25) as response:
        assert response.status == 200, 'unexpected HTTP status'
        assert urlparse(response.url).netloc == urlparse(BASE).netloc, 'unexpected cross-domain redirect'
        assert normalized_public_path(urlparse(response.url).path) == normalized_public_path(path), 'unexpected redirect to another journey'
        return response.read(4 * 1024 * 1024)

def run(fetcher=fetch, expected_sha=''):
    results = []
    def check(name, operation):
        try: operation(); results.append({'check': name, 'status': 'pass'})
        except Exception as error: results.append({'check': name, 'status': 'fail', 'reason': str(error)})
    manifest = {}
    check('release_manifest', lambda: manifest.update(validate_manifest(fetcher('/version.json'), expected_sha)))
    for path, language in PAGES.items():
        check('page:' + path, lambda path=path, language=language: validate_page(fetcher(path), path, language))
    # Never skip page checks after a broken release marker or another language.
    for path, digest in manifest.get('assets', {}).items():
        def asset(path=path, digest=digest):
            assert hashlib.sha256(fetcher(path)).hexdigest() == digest, 'published asset differs from build'
        check('asset:' + path, asset)
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--expected-sha', default='')
    parser.add_argument('--output', default='site-health.json'); args = parser.parse_args()
    results = run(expected_sha=args.expected_sha)
    report = {'checked_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'results': results}
    with open(args.output, 'w') as file: json.dump(report, file, indent=2)
    print(json.dumps(report, indent=2))
    raise SystemExit(any(row['status'] != 'pass' for row in results))
