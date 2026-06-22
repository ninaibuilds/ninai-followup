import logging
from datetime import datetime, timedelta, timezone

from tools.google_auth import get_calendar_service
from tools.send_email import send_reminder_email


def check_and_send_reminders() -> int:
    service = get_calendar_service()
    now = datetime.now()
    sent = 0

    result = service.events().list(
        calendarId='primary',
        timeMin=(now - timedelta(hours=2)).isoformat() + 'Z',
        timeMax=(now + timedelta(days=8)).isoformat() + 'Z',
        privateExtendedProperty='ninai_app=true',
        singleEvents=True,
    ).execute()

    for event in result.get('items', []):
        props = event.get('extendedProperties', {}).get('private', {})

        if props.get('reminder_sent') == 'true':
            continue

        reminder_at_str = props.get('reminder_at', '')
        if not reminder_at_str:
            continue

        reminder_at = datetime.fromisoformat(reminder_at_str)
        if reminder_at > now:
            continue

        client_name = props.get('client_name', '')
        client_email = props.get('client_email', '')
        meeting_local = props.get('meeting_local', '')

        meet_link = None
        for ep in event.get('conferenceData', {}).get('entryPoints', []):
            if ep.get('entryPointType') == 'video':
                meet_link = ep['uri']
                break

        meeting_dt = datetime.fromisoformat(meeting_local) if meeting_local else None

        if client_email and meeting_dt and meet_link:
            send_reminder_email(client_name, client_email, meeting_dt, meet_link)
            event.setdefault('extendedProperties', {}).setdefault('private', {})['reminder_sent'] = 'true'
            service.events().update(
                calendarId='primary',
                eventId=event['id'],
                body=event,
            ).execute()
            logging.info(f'Reminder sent to {client_email}')
            sent += 1

    return sent
