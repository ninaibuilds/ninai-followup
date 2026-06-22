import base64
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tools.google_auth import get_gmail_service

SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
WEBSITE_URL = os.getenv('WEBSITE_URL', '[YOUR WEBSITE URL]')
CREDIBILITY_LINE = os.getenv('CREDIBILITY_LINE', '[CREDIBILITY LINE]')

SENDER_NAME = 'Ishan Pattnaik'
SENDER_TITLE = 'Chief Growth Strategist'
SENDER_ORG = 'NINAI Builds'


def _raw(msg: MIMEMultipart) -> dict:
    return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}


def _build_msg(subject: str, to: str, body: str) -> MIMEMultipart:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f'{SENDER_NAME} <{SENDER_EMAIL}>'
    msg['To'] = to
    msg.attach(MIMEText(body, 'plain'))
    return msg


def send_followup_email(
    client_name: str,
    client_email: str,
    meeting_dt: datetime,
    meet_link: str,
    note: str = '',
) -> None:
    service = get_gmail_service()
    meeting_str = meeting_dt.strftime('%A, %B %-d at %-I:%M %p')

    if note:
        overview = (
            f"Based on our conversation about {note}, "
            f"in our session we'll map out exactly how NINAI Builds can help you move forward. "
            f"You'll leave with total clarity on what's possible and a concrete next step."
        )
    else:
        overview = (
            "In our session, we'll dig into your goals and walk through exactly how NINAI Builds "
            "can help you get there. You'll leave with a clear picture of what's possible and a concrete next step."
        )

    body = f"""Hi {client_name},

Great connecting — looking forward to our call on {meeting_str}.

{overview}

{CREDIBILITY_LINE}

Your dedicated Google Meet link:
{meet_link}

Learn more: {WEBSITE_URL}

Kind regards,

{SENDER_NAME}
{SENDER_TITLE}
{SENDER_ORG}"""

    msg = _build_msg(f"Looking forward to our call, {client_name}", client_email, body)
    service.users().messages().send(userId='me', body=_raw(msg)).execute()


def send_reminder_email(
    client_name: str,
    client_email: str,
    meeting_dt: datetime,
    meet_link: str,
) -> None:
    service = get_gmail_service()
    meeting_str = meeting_dt.strftime('%A, %B %-d at %-I:%M %p')

    body = f"""Hi {client_name},

Quick reminder — we have a call on {meeting_str}.

Join here: {meet_link}

See you soon,
{SENDER_NAME}"""

    msg = _build_msg(f"Reminder: Our call on {meeting_str}", client_email, body)
    service.users().messages().send(userId='me', body=_raw(msg)).execute()
