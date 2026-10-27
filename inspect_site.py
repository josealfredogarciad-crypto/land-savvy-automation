"""Public website reconnaissance: no customer data, no clicks, no submissions."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

DEFAULT_URL = 'https://www.land-savvy.com/'


def inspect(url=DEFAULT_URL, destination='site-inspection'):
    parts = urlparse(url)
    if parts.scheme != 'https' or parts.hostname not in ('land-savvy.com', 'www.land-savvy.com'):
        raise ValueError('Only official HTTPS Land Savvy website is allowed')
    out = Path(destination)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, locale='en-US')
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=60000)
            page.wait_for_timeout(2500)
            page.screenshot(path=str(out/'homepage.png'), full_page=True, animations='disabled')
            inventory = page.evaluate('''() => ({
              title: document.title,
              url: location.href,
              headings: [...document.querySelectorAll('h1,h2,h3')].map(x => x.innerText.trim()).filter(Boolean).slice(0,25),
              forms: [...document.forms].map(f => ({id:f.id, action:f.getAttribute('action'), method:f.method})),
              controls: [...document.querySelectorAll('input,select,textarea,button,[role=combobox]')].map(x => ({
                tag:x.tagName.toLowerCase(), type:x.getAttribute('type'), name:x.getAttribute('name'),
                id:x.id, placeholder:x.getAttribute('placeholder'), required:x.required || false,
                ariaLabel:x.getAttribute('aria-label'), text:(x.innerText||'').trim().slice(0,100),
                options:x.tagName==='SELECT' ? [...x.options].map(o=>o.textContent.trim()).slice(0,40) : undefined
              })),
              links: [...document.querySelectorAll('a[href]')].map(a=>({text:a.innerText.trim().slice(0,80),href:a.href})).filter(x=>x.text && /book|transfer|reserv|travel|quote/i.test(x.text)).slice(0,30)
            })''')
            (out/'inventory.json').write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding='utf-8')
            print('Public page inspected. Controls:', len(inventory['controls']))
            return inventory
        finally:
            browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Inspect public booking page without submitting forms')
    parser.add_argument('--url', default=DEFAULT_URL)
    parser.add_argument('--output', default='site-inspection')
    args = parser.parse_args()
    inspect(args.url,args.output)
