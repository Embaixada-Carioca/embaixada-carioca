"""Read-only local browser QA for the existing site. External requests are blocked."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'browser-qa'
ROUTES = [(prefix + name + '.html', language)
          for prefix, language in (('', 'pt'), ('en/', 'en'), ('es/', 'es'))
          for name in ('index', 'eventos', 'eventos-corporativos', 'contato')]

def main():
    OUT.mkdir(exist_ok=True)
    handler=functools.partial(SimpleHTTPRequestHandler,directory=str(ROOT))
    server=ThreadingHTTPServer(('127.0.0.1',0),handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}'
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            for width in (375,1440):
                for path,language in ROUTES:
                    row={'path':path,'width':width,'status':'pass'}
                    page=browser.new_page(viewport={'width':width,'height':900})
                    page.route('**/*',lambda route: route.continue_() if urlparse(route.request.url).netloc==urlparse(origin).netloc else route.abort())
                    try:
                        page.goto(origin+'/'+path+'?email=synthetic@example.test&utm_source=untrusted',wait_until='networkidle')
                        page.evaluate('document.fonts.ready')
                        page.add_style_tag(content='html { scroll-behavior: auto !important; }')
                        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                        page.wait_for_timeout(300)
                        page.evaluate('window.scrollTo(0, 0)')
                        assert page.locator('html').get_attribute('lang').startswith(language)
                        assert page.locator('h1').count()==1
                        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), 'horizontal overflow'
                        if width==375:
                            toggle=page.locator('#menu-toggle')
                            toggle.click(); assert toggle.get_attribute('aria-expanded')=='true', 'menu did not open'
                            toggle.click(); assert toggle.get_attribute('aria-expanded')=='false', 'menu did not close'
                        handoffs = page.locator('a[href*="leorangel22.github.io/main/formulario.html"]')
                        assert handoffs.count() > 0, 'missing central form'
                        for link in handoffs.all():
                            target = urlparse(link.get_attribute('href'))
                            query = parse_qs(target.query)
                            assert target.netloc == 'leorangel22.github.io' and target.path == '/main/formulario.html'
                            assert set(query) == {'lang','utm_source','utm_medium','utm_campaign','utm_content'}
                            assert query['lang'] == [language], 'handoff lost page language'
                            assert query['utm_source'] == ['embaixadacarioca']
                            assert query['utm_medium'] == ['website'] and query['utm_campaign'] == ['eventos']
                            assert not any('synthetic' in value or 'untrusted' in value for values in query.values() for value in values)
                            assert link.get_attribute('data-event-system-link') is not None
                        if path.endswith(('eventos.html','eventos-corporativos.html')):
                            primary = page.locator('.mobile-actions .mobile-reserve')
                            assert primary.get_attribute('data-intent') == 'eventos'
                            assert 'leorangel22.github.io/main/formulario.html' in primary.get_attribute('href')
                        page.add_script_tag(path=str(ROOT/'node_modules/axe-core/axe.min.js'))
                        audit=page.evaluate("async () => await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})")
                        row['violations']=[{'id':v['id'],'impact':v['impact'],'nodes':len(v['nodes'])} for v in audit['violations']]
                        assert not row['violations'], 'accessibility violations'
                    except Exception as error:
                        row['status']='fail';row['reason']=str(error)
                    finally:
                        page.evaluate('document.activeElement?.blur(); window.scrollTo(0, 0)')
                        page.wait_for_function('window.scrollY === 0')
                        page.screenshot(path=str(OUT/(path.replace('/','-')+f'-{width}.png')),full_page=True)
                        results.append(row);page.close()
        finally:
            browser.close();server.shutdown()
    (OUT/'results.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))
    raise SystemExit(any(row['status']!='pass' for row in results))
if __name__=='__main__':main()
