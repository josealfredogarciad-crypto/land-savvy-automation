"""Thread-aware eligibility analysis. FAIL CLOSED: no reservation submission."""
import hashlib
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from extract import extract_booking
from policy import assess
from gmail_client import service, conversations
from booking_browser import preview


def run():
    load_dotenv()
    if os.getenv('BOT_MODE', 'preview_only') != 'preview_only':
        raise RuntimeError('Live submission is disabled until website selectors and confirmation behavior are verified.')
    output = Path('output')
    output.mkdir(exist_ok=True)
    demo = os.getenv('SAMPLE_EMAIL_FILE')
    if demo:
        samples = [('sample', Path(demo).read_text())]
    else:
        samples = conversations(service(),os.getenv('GMAIL_QUERY','newer_than:7d'),int(os.getenv('MAX_MESSAGES','10')))
    client = OpenAI()
    for thread_id, text in samples:
        safe_id = hashlib.sha256(thread_id.encode()).hexdigest()[:16]
        b = extract_booking(text,client,os.getenv('OPENAI_MODEL','gpt-4.1-mini'))
        issues = assess(b)
        d = output / safe_id
        d.mkdir(exist_ok=True)
        # Personal data intentionally omitted from persistent output and logs.
        report = {'thread_hash':safe_id,'eligible':not issues,'issues':issues,
                  'route_known':bool(b.origin and b.destination),
                  'travel_type':b.travel_type,'vehicle_known':bool(b.vehicle_type),
                  'duplicate_or_existing':b.existing_reservation,
                  'review_required':bool(issues),'submitted':False}
        (d/'assessment.json').write_text(json.dumps(report,indent=2))
        print(json.dumps(report))
        if not issues and os.getenv('INSPECT_SITE','0') == '1':
            preview(b,os.getenv('LAND_SAVVY_URL','https://www.land-savvy.com/'),str(d))
    print('DRY RUN COMPLETE. No reservations submitted or Gmail messages changed.')

if __name__ == '__main__':
    run()
