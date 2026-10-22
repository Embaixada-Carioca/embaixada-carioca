"""Read-only regression checks for the public event-system handoff."""
import json
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[1]
PAGES = [f'{prefix}{name}.html' for prefix in ('', 'en/', 'es/')
         for name in ('index', 'eventos', 'eventos-corporativos', 'contato')]


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links, self.forms, self.scripts = [], [], []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            self.links.append(attrs)
        elif tag == 'form':
            self.forms.append(attrs)
        elif tag == 'script':
            self.scripts.append(attrs)


class EventSystemLinks(unittest.TestCase):
    def test_destinations_and_tracking(self):
        for path in PAGES:
            with self.subTest(page=path):
                page = Page((ROOT / path).read_text(encoding='utf-8'))
                links = [a for a in page.links if 'data-event-system-link' in a]
                self.assertTrue(links)
                for link in links:
                    url = urlsplit(link['href'])
                    self.assertEqual((url.scheme, url.netloc, url.path),
                                     ('https', 'leorangel22.github.io', '/main/formulario.html'))
                    query = parse_qs(url.query)
                    self.assertEqual(set(query), {'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'lang'})
                    language = 'en' if path.startswith('en/') else 'es' if path.startswith('es/') else 'pt'
                    self.assertEqual(query['lang'], [language])
                    self.assertEqual(query['utm_source'], ['embaixadacarioca'])
                    self.assertEqual(query['utm_medium'], ['website'])
                    self.assertEqual(query['utm_campaign'], ['eventos'])
                    expected = path.replace('/', '-').removesuffix('.html')
                    if path.endswith('index.html'): expected = 'index' + ('_' + language if language != 'pt' else '')
                    if path.endswith('/eventos.html'): expected = 'eventos'
                    self.assertEqual(query['utm_content'], [expected])
                    self.assertNotIn('onclick', link)
                scripts = [s.get('src', '') for s in page.scripts]
                self.assertEqual(sum('/assets/event-system-link.js' in s for s in scripts), 1)
                self.assertFalse(any('event-lead-funnel.js' in s for s in scripts))

    def test_no_duplicate_contact_entry(self):
        for prefix in ('', 'en/', 'es/'):
            source = (ROOT / f'{prefix}eventos.html').read_text(encoding='utf-8')
            page = Page(source)
            self.assertFalse(any(f.get('id', '').startswith('ec-event-lead-form') for f in page.forms))
            self.assertIn('data-position="form"', source)
            self.assertNotIn('confirma o envio pelo WhatsApp', source)
            self.assertTrue(any(a.get('href', '').startswith('mailto:') for a in page.links))
            self.assertTrue(any('wa.me/' in a.get('href', '') for a in page.links))

    def test_bridge_does_not_copy_arbitrary_queries(self):
        source = (ROOT / 'formulario.html').read_text(encoding='utf-8')
        self.assertNotIn('window.location.search', source)
        self.assertIn('https://leorangel22.github.io/main/formulario.html', source)
        self.assertIn('noindex, follow', source)

    def test_event_mobile_action_keeps_the_quote_journey(self):
        for prefix in ('', 'en/', 'es/'):
            for name in ('eventos', 'eventos-corporativos'):
                with self.subTest(page=prefix+name):
                    source = (ROOT / f'{prefix}{name}.html').read_text(encoding='utf-8')
                    page = Page(source)
                    mobile = [a for a in page.links if a.get('class') == 'mobile-reserve']
                    self.assertEqual(len(mobile), 1)
                    self.assertIn('data-event-system-link', mobile[0])
                    self.assertEqual(mobile[0].get('data-intent'), 'eventos')
                    self.assertIn('leorangel22.github.io/main/formulario.html', mobile[0]['href'])
                    self.assertNotIn('tagme', mobile[0]['href'])
                    self.assertEqual(source.count('<h1>'), 1)
                    self.assertIn('class="visit-hero-actions"', source)
                    self.assertTrue(any('tagme' in a.get('href', '') and 'data-event-system-link' not in a for a in page.links))

    def test_regular_reservations_are_not_event_leads(self):
        for prefix in ('', 'en/', 'es/'):
            page = Page((ROOT / f'{prefix}index.html').read_text(encoding='utf-8'))
            reservations = [a for a in page.links if 'go.tagme.com.br' in a.get('href', '')]
            self.assertTrue(reservations)
            self.assertTrue(all('data-event-system-link' not in a for a in reservations))


if __name__ == '__main__':
    unittest.main()
