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
| `tools/create_meet_event.py` | Creates a Google Calendar event with a unique Meet link |
| `tools/send_email.py` | Sends follow-up and reminder emails via Gmail API |
| `tools/scheduler.py` | Persists and fires reminder jobs via APScheduler + SQLite |

## Execution Sequence
1. User submits form at `http://localhost:5000`
2. `create_meet_event` → new Calendar event created, unique Meet URL returned
3. `send_followup_email` → follow-up email sent immediately via Gmail
4. `schedule_reminder` → one reminder job written to `.tmp/jobs.sqlite`
5. APScheduler fires the reminder at the calculated time (see logic below)

## Reminder Scheduling Logic
| Time until meeting (at time of booking) | Reminder sent |
|------------------------------------------|---------------|
| 24+ hours away | Day before at 9:00 AM |
| 2–24 hours away | 1 hour before |
| Under 2 hours | 30 minutes before |
| Reminder time already passed | No reminder sent |

## Edge Cases
- **Meet link missing**: Google occasionally delays generating the link. If `meet_link` is None, the submit will fail with a clear error. Retry after a few seconds.
- **Reminder fires while app is offline**: APScheduler uses `misfire_grace_time=3600` — if the app restarts within 1 hour of a missed reminder, it fires immediately on startup.
- **Duplicate submissions**: Scheduler uses `replace_existing=True` keyed on `client_email + meeting_dt`, so resubmitting the same client/time overwrites the old job without duplicating.
- **OAuth expiry**: `token.json` refresh tokens are long-lived. If auth fails, delete `token.json` and restart — the browser auth flow runs again.

## Configuration (`.env`)
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
