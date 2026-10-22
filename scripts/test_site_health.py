import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from site_release import write_manifest, CRITICAL_ASSETS
from verify_live_site import run, validate_manifest, validate_page, PAGES

ROOT = Path(__file__).resolve().parents[1]
class SiteHealthTests(unittest.TestCase):
    def test_current_pages_pass_without_obsolete_tagline(self):
        for path, language in PAGES.items():
            name = 'index.html' if path == '/' else path.strip('/') + ('/index.html' if path.endswith('/') else '.html')
            with self.subTest(path=path): validate_page((ROOT/name).read_bytes(), path, language)
    def test_corrupt_translation_fails(self):
        body = (ROOT/'en/index.html').read_bytes() + b'Bondinhel'
        with self.assertRaises(AssertionError): validate_page(body, '/en/', 'en')
    def test_missing_conversion_fails(self):
        body = (ROOT/'en/index.html').read_bytes().replace(b'leorangel22.github.io', b'invalid.example')
        with self.assertRaises(AssertionError): validate_page(body, '/en/', 'en')
    def test_wrong_language_fails(self):
        with self.assertRaises(AssertionError): validate_page((ROOT/'index.html').read_bytes(), '/en/', 'en')
    def test_all_pages_run_even_after_failures(self):
        calls = []
        def failure(path): calls.append(path); raise OSError('offline')
        results = run(failure)
        self.assertEqual(len(results), len(PAGES) + 1)
        self.assertEqual(calls, ['/version.json', *PAGES])
        self.assertTrue(all(row['status'] == 'fail' for row in results))
    def test_build_manifest_and_exact_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            for path in CRITICAL_ASSETS:
                (out/path).parent.mkdir(parents=True, exist_ok=True); (out/path).write_text(path)
            with patch.dict('os.environ', {'GITHUB_SHA':'a'*40}): data=write_manifest(ROOT,out)
            body=(out/'version.json').read_bytes()
            self.assertEqual(validate_manifest(body, 'a'*40), data)
            self.assertEqual(data['assets']['/'+CRITICAL_ASSETS[0]],hashlib.sha256(CRITICAL_ASSETS[0].encode()).hexdigest())
            with self.assertRaises(AssertionError): validate_manifest(body, 'b'*40)
            self.assertNotIn('expected_commit_contains',data)
    def test_legacy_manifest_rejected(self):
        with self.assertRaises(AssertionError): validate_manifest((ROOT/'version.json').read_bytes())
    def test_invalid_sha_rejected(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict('os.environ', {'GITHUB_SHA':'not-a-sha'}):
            with self.assertRaises(ValueError): write_manifest(ROOT,Path(tmp))
    def test_runtime_hash_mismatch_fails(self):
        data={'schema_version':1,'repository':'Embaixada-Carioca/embaixada-carioca','deploy_sha':'a'*40,'built_at':'2026-10-22',
              'assets':{'/'+p:hashlib.sha256(b'ok').hexdigest() for p in CRITICAL_ASSETS}}
        def fake(path):
            if path=='/version.json': return json.dumps(data).encode()
            if path.startswith('/assets/'): return b'changed'
            name='index.html' if path=='/' else path.strip('/')+('/index.html' if path.endswith('/') else '.html')
            return (ROOT/name).read_bytes()
        results=run(fake)
        self.assertEqual(len(results),len(PAGES) + 5)
        self.assertEqual(sum(row['status']=='fail' for row in results),4)
if __name__=='__main__': unittest.main()
