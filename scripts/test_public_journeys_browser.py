"""Read-only local browser QA for the existing site. External requests are blocked."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'browser-qa'
ROUTES = [('index.html','pt'),('en/index.html','en'),('es/index.html','es'),
          ('eventos.html','pt'),('en/eventos.html','en'),('es/eventos.html','es')]

def assert_mobile_menu(page, opened, timeout=3000):
    toggle=page.locator('#menu-toggle'); navigation=page.locator('#primary-links')
    expect(toggle).to_have_attribute('aria-expanded',str(opened).lower(),timeout=timeout)
    links=navigation.locator('a[href]')
    assert links.count()>0, 'mobile navigation has no links'
    if opened:
        expect(navigation).to_be_visible(timeout=timeout)
        expect(navigation).to_be_in_viewport(timeout=timeout)
        for link in links.all():
            expect(link).to_be_visible(timeout=timeout)
            expect(link).to_be_in_viewport(timeout=timeout)
    else:
        expect(navigation).to_be_hidden(timeout=timeout)
        for link in links.all(): expect(link).to_be_hidden(timeout=timeout)

def expect_broken_menu_detected(page):
    # The old aria-only assertion still passes for these intentional mutations.
    assert page.locator('#menu-toggle').get_attribute('aria-expanded')=='true'
    try: assert_mobile_menu(page,True,timeout=100)
    except AssertionError: return
    raise AssertionError('menu visibility regression was not detected')

def audit_accessibility(page):
    audit=page.evaluate("async () => await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})")
    return [{'id':v['id'],'impact':v['impact'],'nodes':len(v['nodes'])} for v in audit['violations']]

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
                        page.add_style_tag(content='html { scroll-behavior: auto !important; }')
                        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                        page.wait_for_timeout(300)
                        page.evaluate('window.scrollTo(0, 0)')
                        assert page.locator('html').get_attribute('lang').startswith(language)
                        assert page.locator('h1').count()==1
                        assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), 'horizontal overflow'
                        page.add_script_tag(path=str(ROOT/'node_modules/axe-core/axe.min.js'))
                        if width==375:
                            toggle=page.locator('#menu-toggle')
                            assert_mobile_menu(page,False)
                            toggle.click(); assert_mobile_menu(page,True)
                            row['open_menu_violations']=audit_accessibility(page)
                            assert not row['open_menu_violations'], 'open menu accessibility violations'
                            page.screenshot(path=str(OUT/(path.replace('/','-')+f'-{width}-menu-open.png')))
                            if path=='index.html':
                                page.locator('#primary-links').evaluate("node => node.classList.remove('is-open')")
                                try: expect_broken_menu_detected(page)
                                finally: page.locator('#primary-links').evaluate("node => node.classList.add('is-open')")
                                style=page.add_style_tag(content='#primary-links { display: none !important; }')
                                try: expect_broken_menu_detected(page)
                                finally: style.evaluate('node => node.remove()')
                                link=page.locator('#primary-links a').first
                                link.evaluate("node => node.style.display='none'")
                                try: expect_broken_menu_detected(page)
                                finally: link.evaluate("node => node.style.removeProperty('display')")
                                row['negative_menu_checks']=['missing_open_class','hidden_navigation','hidden_link']
                            toggle.click(); assert_mobile_menu(page,False)
                            toggle.press('Enter'); assert_mobile_menu(page,True)
                            toggle.press('Enter'); assert_mobile_menu(page,False)
                        assert page.locator('a[href*="leorangel22.github.io/main/formulario.html"]').count()>0, 'missing central form'
                        row['violations']=audit_accessibility(page)
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
