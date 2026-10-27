# Land Savvy email-to-booking automation — SAFE PROTOTYPE

This project **does NOT submit reservations**. It extracts booking requests from Gmail using the OpenAI API, checks completeness, and captures a screenshot/field inventory of the public Land Savvy booking page. The complete workflow past the public site's first screen must be mapped and tested before submission automation can be added.

## What is verified / not verified
- The public homepage at https://www.land-savvy.com/ shows Travel Type, From, To, Arrival and Passengers, then “Let's Travel Savvy!”.
- Exact HTML selectors and subsequent checkout steps are NOT VERIFIED.
- Gmail consent and OpenAI API keys are NOT yet connected.
- GitHub scheduled trigger is intentionally disabled to avoid repeats or unintended costs.

## Local setup
1. Install Python 3.11+.
2. `python3 -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `python -m playwright install chromium`
5. Copy `.env.example` to `.env` and enter `OPENAI_API_KEY` (never share it in chat).
6. For testing without Gmail, create `sample_email.txt` (anonymized), and run `SAMPLE_EMAIL_FILE=sample_email.txt python main.py`.
7. For Gmail, create a Google Cloud project, enable Gmail API, configure OAuth consent and create a *Desktop* OAuth client. Download its OAuth JSON as `credentials.json`; then run `python main.py` and authorize in your own browser. OAuth scope is `gmail.modify` so that a processed label can be used in the later live phase. **The current preview version never labels or alters messages.** Consider a dedicated mailbox/label for least-privilege testing.
8. See results under `output/<gmail-message-id>/`: `booking.json`, `fields.json` and `homepage.png`.

## Inspect the full booking flow locally
`python -m playwright codegen https://www.land-savvy.com/`
Record each step using fictional data and DO NOT submit/charge a real booking. Share only sanitized generated selectors, never credentials or customer info. A public form can include price, payment, and service agreements; these need explicit business rules and a safe staging or manual approval before any final submit.

## GitHub Actions (manual-only prototype)
Push this project to a **private** repository. Add `OPENAI_API_KEY` and `GMAIL_TOKEN_JSON` to Settings -> Secrets and variables -> Actions. Use workflow_dispatch from Actions tab. Never store `credentials.json`, `token.json`, email text, secrets, or customer booking data in the repo. **Important:** workflow artifacts contain customer data; ensure suitable access permissions/retention or disable artifact uploads in production. Current workflow artifacts expire after 3 days. A real scheduler needs durable idempotency: apply the `LS_BOT_PROCESSED` label only after confirmed successful submission, and implement concurrency controls and an error/review queue. GitHub schedules are polling, not instant email arrival triggers.

## Safety concerns
- AI extraction may err. Never assume missing dates, locations or passenger counts.
- Dates/times must be verified in Cancún local time; timezone normalization is not yet implemented.
- False-positive emails, forwarded chains and cancellations require explicit handling.
- The public form may not support all passenger, flight and service variations; do not fake values.
- A live system must verify a success confirmation and use a stable message ID to avoid double bookings.
- The Gmail token might need refreshed authorization; workflows require a valid refresh token.
- OpenAI API and GitHub usage may incur charges; no guaranteed free unlimited tier.

## Automatic-booking decision (27 Oct 2026)
The owner selected **automatic submission only for explicit, complete reservations**.
A fail-closed eligibility policy now lives in `policy.py`. It rejects quotations,
modifications/cancellations, ambiguous requests, missing contact information,
and dates in the past. Unit tests cover these gates.

**Crucial**: live submission remains **disabled**. A production implementation must
first verify the booking path and form selectors, vehicle choice, payment flow,
final confirmation state, and persistence of message IDs. Do not enable by merely
changing BOT_MODE. `main.py` intentionally refuses any non-preview mode.

For idempotency, store completed Gmail message IDs in a persistent database with
atomic locking before booking, and reconcile uncertain outcomes against Land Savvy
confirmation references; email labels alone are insufficient to guarantee exactly-once
submission. Confirm capacity, cutoff windows and booking authorization in the
real business workflow. Keep secrets out of GitHub logs and repository files.

## Updated thread-aware version (27 October 2026)
- `gmail_client.py` uses **read-only** OAuth and reads full conversations, not isolated messages. Old `gmail.modify` tokens must be reauthorized for the new readonly scope; never paste credentials into ChatGPT.
- `extract.py` uses AI to interpret the latest customer intent with earlier context. It flags existing reservations, conflicting details and missing vehicle selection.
- `policy.py` blocks those cases and requires explicit confirmation, valid routing, dates, passenger counts and contact information.
- `main.py` writes a **redacted eligibility assessment**, not raw private email content or customer contact details.
- GitHub workflow runs tests **on demand only**; it does not access Gmail, upload customer data, or submit anything.
- Default website inspection is off. Set `INSPECT_SITE=1` locally after Playwright/Chromium is installed; captured homepage screenshots must be kept private.
- Confirmed prerequisite for live submission: manually map actual page selectors and every booking step, ensure chosen vehicle/price match customer intent, inspect order confirmation, and maintain durable database of successfully submitted reservations. The website's public form may create duplicate bookings or send notifications; these cannot be safely assumed away. There is **no production live-submit** in this ZIP.
- Connected Gmail inside ChatGPT **does not automatically grant a Python script or GitHub Actions access to Gmail**. The script needs its own explicit OAuth credentials, and the OpenAI API has separate usage-based billing.

## Website mapping without installing anything on your Mac (27 Oct 2026)
A new GitHub workflow `.github/workflows/inspect-website.yml` opens the **public homepage only** in headless Chromium and saves a screenshot plus `inventory.json` of visible form controls. It does **not click any controls, enter customer information, or submit a reservation**. This is the next real step toward mapping the booking form; it does not yet inspect subsequent checkout screens.

1. Create a **private** GitHub repository and upload these project files preserving their folder structure (including `.github/workflows`). Never upload credentials, OAuth tokens, `.env`, or private client data.
2. Go to GitHub → your repository → **Actions** → **Inspect Land Savvy public form (no booking)** → **Run workflow**.
3. When the run finishes, download the `land-savvy-public-form-inspection` artifact (screenshot and `inventory.json`). Share that ZIP in chat for mapping field selectors.
4. After mapping initial page, record the subsequent form screens with synthetic test data, without clicking payment/submit, and adapt Playwright to fill the booking form.

Note: Here, outbound network access from the Python container to the website was unavailable; the Playwright website inspection has not yet been run. GitHub Actions should be able to access it unless the site blocks cloud hosts. Github workflow is **manual only** and cannot create bookings.
