import os
import uuid
from datetime import datetime, timedelta

from tools.google_auth import get_calendar_service

TIMEZONE = os.getenv('TIMEZONE', 'Europe/London')


def _reminder_time(meeting_dt: datetime) -> datetime | None:
    now = datetime.now()
    delta = meeting_dt - now
    if delta >= timedelta(hours=24):
        reminder = (meeting_dt - timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    elif delta >= timedelta(hours=2):
        reminder = meeting_dt - timedelta(hours=1)
    elif delta > timedelta(minutes=0):
        reminder = meeting_dt - timedelta(minutes=30)
    else:
        return None
    return reminder if reminder > now else None


def create_meet_event(client_name: str, client_email: str, meeting_dt: datetime) -> dict:
    service = get_calendar_service()
    reminder_dt = _reminder_time(meeting_dt)

    event = {
        'summary': f'Meeting with {client_name}',
        'start': {'dateTime': meeting_dt.isoformat(), 'timeZone': TIMEZONE},
        'end': {'dateTime': (meeting_dt + timedelta(hours=1)).isoformat(), 'timeZone': TIMEZONE},
        'attendees': [{'email': client_email}],
        'conferenceData': {
            'createRequest': {
                'requestId': str(uuid.uuid4()),
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
            }
        },
        'reminders': {'useDefault': False, 'overrides': []},
        'extendedProperties': {
            'private': {
                'ninai_app': 'true',
                'client_name': client_name,
                'client_email': client_email,
                'meeting_local': meeting_dt.isoformat(),
                'reminder_at': reminder_dt.isoformat() if reminder_dt else '',
                'reminder_sent': 'false',
            }
        },
        'guestsCanModifyEvent': False,
    }

    created = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1,
        sendUpdates='none',
    ).execute()

    meet_link = None
    for ep in created.get('conferenceData', {}).get('entryPoints', []):
        if ep.get('entryPointType') == 'video':
            meet_link = ep['uri']
            break

    return {
        'event_id': created['id'],
        'meet_link': meet_link,
        'reminder_at': reminder_dt,
    }
