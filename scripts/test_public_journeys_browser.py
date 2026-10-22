"""Read-only local browser QA for the existing site. External requests are blocked."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'browser-qa'
ROUTES = [('index.html','pt'),('en/index.html','en'),('es/index.html','es'),
          ('eventos.html','pt'),('en/eventos.html','en'),('es/eventos.html','es')]

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
                        page.goto(origin+'/'+path,wait_until='networkidle')
                        page.evaluate('document.fonts.ready')
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
                        assert page.locator('a[href*="leorangel22.github.io/main/formulario.html"]').count()>0, 'missing central form'
                        page.add_script_tag(path=str(ROOT/'node_modules/axe-core/axe.min.js'))
                        audit=page.evaluate("async () => await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})")
                        row['violations']=[{'id':v['id'],'impact':v['impact'],'nodes':len(v['nodes'])} for v in audit['violations']]
                        assert not row['violations'], 'accessibility violations'
                    except Exception as error:
                        row['status']='fail';row['reason']=str(error)
                    finally:
                        page.screenshot(path=str(OUT/(path.replace('/','-')+f'-{width}.png')),full_page=True)
                        results.append(row);page.close()
        finally:
            browser.close();server.shutdown()
    (OUT/'results.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))
    raise SystemExit(any(row['status']!='pass' for row in results))
if __name__=='__main__':main()
