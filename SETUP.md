# Setup Guide

## Step 1 — Google Cloud Console (10 minutes, one-time)

### 1.1 Create a project
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click the project dropdown (top left) → **New Project**
3. Name it `ninai-followup` → **Create**

### 1.2 Enable the APIs
With your new project selected:
1. Go to **APIs & Services → Library**
2. Search **Google Calendar API** → click it → **Enable**
3. Search **Gmail API** → click it → **Enable**

### 1.3 Configure the OAuth consent screen
1. Go to **APIs & Services → OAuth consent screen**
2. Select **External** → **Create**
3. Fill in:
   - App name: `NINAI Follow-up`
   - User support email: your Gmail
   - Developer contact: your Gmail
4. Click through Scopes and Test users without changing anything → **Save and Continue**
5. On the Summary page, click **Back to Dashboard**
6. Click **Publish App** → **Confirm** (required so the token doesn't expire every 7 days)

### 1.4 Create OAuth credentials
1. Go to **APIs & Services → Credentials**
2. Click **+ Create Credentials → OAuth client ID**
3. Application type: **Desktop app**
4. Name: `ninai-followup-desktop`
5. Click **Create**
6. Click **Download JSON** → rename the file to `credentials.json`
7. Move `credentials.json` into this project folder (same level as `app.py`)

---

## Step 2 — Configure your environment

```bash
cp .env.example .env
```

Edit `.env`:
```
SENDER_EMAIL=your.gmail@gmail.com        # the Gmail account you just set up
WEBSITE_URL=https://ninaiagencyandconsulting.netlify.app/
TIMEZONE=America/New_York                # adjust to your timezone
```

---

## Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4 — Run

```bash
python app.py
```

The first time you run this, a browser window will open asking you to sign into your Google account and grant access. After you approve, a `token.json` file is saved. You won't need to do this again.

Once authenticated, open **http://localhost:5000** in your browser.

---

## Keep the app running for reminders

Reminder emails are fired by the scheduler running inside `app.py`. The app needs to be running at the scheduled reminder time for the email to send.

If the app was off and comes back online within 1 hour of a missed reminder, it fires immediately on startup.
