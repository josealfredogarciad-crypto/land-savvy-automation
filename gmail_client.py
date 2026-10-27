"""Read-only Gmail conversations. No writes, labels, or message status changes."""
import base64
import json
import os
import re
from email import policy
from email.parser import BytesParser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def service():
    token = os.environ.get('GMAIL_TOKEN_JSON')
    if token:
        creds = Credentials.from_authorized_user_info(json.loads(token), SCOPES)
    elif os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        if not token:
            with open('token.json', 'w') as f:
                f.write(creds.to_json())
            os.chmod('token.json', 0o600)
    return build('gmail', 'v1', credentials=creds, cache_discovery=False)

def _decode(raw):
    parsed = BytesParser(policy=policy.default).parsebytes(base64.urlsafe_b64decode(raw))
    body = parsed.get_body(preferencelist=('plain', 'html'))
    content = body.get_content() if body else ''
    if body and body.get_content_type() == 'text/html':
        content = re.sub(r'<[^>]+>', ' ', content)
    return parsed, content

def _is_system_confirmation(subject):
    s = subject.lower().strip()
    return s == 'new reservation!' or 'land savvy - booking id:' in s

def conversations(svc, query, max_results=10):
    """Search candidate conversations, read up to 30 chronological messages per thread.

    No attempt is made to bypass Gmail permissions; content is used locally only.
    """
    q = f'({query}) -in:trash -in:spam'
    refs = svc.users().messages().list(userId='me', q=q, maxResults=max_results).execute().get('messages', [])
    seen = set()
    for ref in refs:
        msg = svc.users().messages().get(userId='me', id=ref['id'], format='minimal').execute()
        tid = msg['threadId']
        if tid in seen:
            continue
        seen.add(tid)
        thread = svc.users().threads().get(userId='me', id=tid, format='raw').execute()
        entries = []
        for item in thread.get('messages', [])[-30:]:
            parsed, content = _decode(item['raw'])
            if _is_system_confirmation(str(parsed.get('Subject',''))):
                continue
            entries.append((int(item.get('internalDate','0')), {
                'from': str(parsed.get('From','')),
                'date': str(parsed.get('Date','')),
                'subject': str(parsed.get('Subject','')),
                'body': content[:12000],
            }))
        if not entries:
            continue
        entries.sort(key=lambda x:x[0])
        # Print only analysis later, no raw email bodies in CI artifacts.
        yield tid, json.dumps([e for _,e in entries],ensure_ascii=False)
