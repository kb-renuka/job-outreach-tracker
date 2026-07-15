"""
Tests for outreach_tracker.py core logic (DB-independent parts).
Run: pip install pytest pandas && pytest test_tracker.py -v
"""

from datetime import date, timedelta
import pandas as pd
from outreach_tracker import needs_followup, FOLLOWUP_DAYS


def make_row(status, date_contacted, last_followup=None):
    return pd.Series(
        {
            "status": status,
            "date_contacted": date_contacted.isoformat(),
            "last_followup": last_followup.isoformat() if last_followup else None,
        }
    )


def test_needs_followup_true_after_threshold_days():
    old_date = date.today() - timedelta(days=FOLLOWUP_DAYS + 1)
    row = make_row("Sent", old_date)
    assert needs_followup(row) is True


def test_needs_followup_false_within_threshold():
    recent_date = date.today() - timedelta(days=1)
    row = make_row("Sent", recent_date)
    assert needs_followup(row) is False


def test_needs_followup_false_for_replied_status():
    old_date = date.today() - timedelta(days=10)
    row = make_row("Replied", old_date)
    assert needs_followup(row) is False


def test_needs_followup_false_for_interview_status():
    old_date = date.today() - timedelta(days=10)
    row = make_row("Interview", old_date)
    assert needs_followup(row) is False


def test_needs_followup_respects_last_followup_date():
    old_contact_date = date.today() - timedelta(days=10)
    recent_followup = date.today() - timedelta(days=1)
    row = make_row("Connected", old_contact_date, last_followup=recent_followup)
    assert needs_followup(row) is False
