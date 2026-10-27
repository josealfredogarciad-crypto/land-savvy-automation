"""Human-reviewed public booking preview. Does not click Submit or checkout."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from extract import Booking


def preview(booking: Booking, url: str, output: str):
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 950})
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        page.screenshot(path=str(out / 'homepage.png'), full_page=True)
        # Inspectable proof of form structure without inventing selectors.
        fields = page.locator('input, select, textarea, button').evaluate_all('''els => els.map(e => ({
            tag: e.tagName, type: e.type || null, name: e.name || null,
            id: e.id || null, text: (e.innerText || '').trim().slice(0,80),
            placeholder: e.placeholder || null
        }))''')
        import json
        (out / 'fields.json').write_text(json.dumps(fields, indent=2, ensure_ascii=False))
        (out / 'booking.json').write_text(booking.model_dump_json(indent=2))
        browser.close()
    return str(out)
