# Job Search Outreach Tracker

A personal CRM for tracking recruiter/alumni outreach during a job search — logs every contact, tracks reply status, and auto-flags anyone who needs a follow-up.

**🔗 Live Demo:** https://kbrenuka-outreach-tracker.streamlit.app/

## Why I built this

During my own job search, I had no system for tracking who I'd messaged, who replied, and who needed a follow-up — messages were getting lost across LinkedIn threads. This tool solves that directly: log once, get automatically reminded.

## Features

- Log recruiter/alumni contacts with company, role, status, and notes
- Status pipeline: Sent → Connected → Replied → Interview → Rejected/Ghosted
- Auto-flags contacts needing a follow-up after 3 days of no movement
- Live dashboard: total outreach, response rate, follow-ups due
- Mark-as-followed-up and delete actions per contact

## Tech stack

Python · Streamlit · SQLite · pandas · pytest

## Setup

```bash
pip install -r requirements.txt
streamlit run outreach_tracker.py
```

## Run tests

```bash
pip install pytest pandas
pytest test_tracker.py -v
```

## Run with Docker

```bash
docker build -t job-outreach-tracker .
docker run -p 8501:8501 job-outreach-tracker
```

## Deployment

Deployed free on [Streamlit Community Cloud](https://share.streamlit.io).
