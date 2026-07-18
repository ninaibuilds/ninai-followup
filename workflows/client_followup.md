# Workflow: Client Follow-up Email

## Objective
After a discovery call, generate a unique Google Meet link for the scheduled meeting and immediately send a personalised follow-up email. Schedule one automated reminder based on how far away the meeting is.

## Inputs
| Field | Required | Notes |
|-------|----------|-------|
| Client first name | Yes | Used in greeting and subject |
| Client email | Yes | Follow-up and reminder destination |
| Meeting date & time | Yes | Used to create Calendar event and Meet link |
| Discussion note | No | 1 sentence max — personalises the email body |

## Tools Used
| Tool | Purpose |
|------|---------|
| `tools/google_auth.py` | OAuth 2.0 — shared credential manager for Calendar + Gmail |
| `tools/create_meet_event.py` | Creates a Google Calendar event with a unique Meet link, and stores the calculated reminder time on the event itself |
| `tools/send_email.py` | Sends follow-up and reminder emails via Gmail API |
| `tools/reminders.py` | Scans upcoming Calendar events and fires any reminder that's due |

## Execution Sequence
1. User submits form at the deployed URL (or `http://localhost:8080` for local dev)
2. `create_meet_event` → new Calendar event created, unique Meet URL returned, reminder time stored as a private extended property on the event
3. `send_followup_email` → follow-up email sent immediately via Gmail, in the same request
4. A GitHub Actions cron job (`.github/workflows/cron.yml`) pings the app's `/cron` endpoint every 10 minutes
5. `check_and_send_reminders` (in `tools/reminders.py`) finds any event whose reminder time has passed and hasn't been sent yet, sends the reminder email, and flags the event so it won't send twice

## Reminder Scheduling Logic
| Time until meeting (at time of booking) | Reminder sent |
|------------------------------------------|---------------|
| 24+ hours away | Day before at 9:00 AM |
| 2–24 hours away | 1 hour before |
| Under 2 hours | 30 minutes before |
| Reminder time already passed | No reminder sent |

## Edge Cases
- **Meet link missing**: Google occasionally delays generating the link. If `meet_link` is None, the submit will fail with a clear error. Retry after a few seconds.
- **Reminder fires late**: the cron job only runs every 10 minutes, so a reminder can fire up to ~10 minutes after its calculated time.
- **Duplicate reminders**: each Calendar event stores a `reminder_sent` flag, so a reminder is never sent twice even if the cron job overlaps or retries.
- **OAuth expiry (local dev)**: `token.json` refresh tokens are long-lived. If auth fails, delete `token.json` and restart — the browser auth flow runs again.
- **OAuth expiry (deployed)**: the deployed app reads credentials from the `TOKEN_JSON_B64` env var (base64-encoded `token.json`) instead of a file — see `tools/google_auth.py`. If this env var is missing or corrupted, Calendar/Gmail calls fail.

## Configuration (`.env` for local dev; same keys as env vars on the host for deployed use)
```
SENDER_EMAIL=your.gmail@gmail.com
WEBSITE_URL=https://ninaiagencyandconsulting.netlify.app/
TIMEZONE=America/New_York
```

## Running the Tool
```bash
python app.py
```
First run opens a browser for Google OAuth. Subsequent runs use `token.json` automatically.
