import logging
import os
import sys
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from tools.create_meet_event import create_meet_event
from tools.reminders import check_and_send_reminders
from tools.send_email import send_followup_email

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')

ACCESS_PASSWORD = os.getenv('ACCESS_PASSWORD', '')
CRON_SECRET = os.getenv('CRON_SECRET', '')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if ACCESS_PASSWORD and not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == ACCESS_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        error = 'Incorrect password.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
@login_required
def submit():
    try:
        client_name = request.form['client_name'].strip()
        client_email = request.form['client_email'].strip()
        meeting_datetime_str = request.form['meeting_datetime']
        note = request.form.get('note', '').strip()

        meeting_dt = datetime.fromisoformat(meeting_datetime_str)

        result = create_meet_event(client_name, client_email, meeting_dt)
        meet_link = result['meet_link']
        reminder_dt = result['reminder_at']

        send_followup_email(client_name, client_email, meeting_dt, meet_link, note)

        return jsonify({
            'success': True,
            'meet_link': meet_link,
            'reminder_scheduled_at': reminder_dt.strftime('%-d %b at %-I:%M %p') if reminder_dt else None,
        })

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logging.error('Submit failed:\n' + tb)
        return jsonify({'success': False, 'error': str(e), 'detail': tb}), 500


@app.route('/cron')
def cron():
    if CRON_SECRET and request.args.get('secret') != CRON_SECRET:
        return jsonify({'error': 'Unauthorized'}), 401
    sent = check_and_send_reminders()
    return jsonify({'sent': sent})


if __name__ == '__main__':
    from tools.google_auth import get_credentials
    get_credentials()
    port = int(os.getenv('PORT', 8080))
    print(f'\n✓ Google authenticated')
    print(f'✓ Open http://localhost:{port}\n')
    app.run(debug=False, port=port, host='0.0.0.0', use_reloader=False)
