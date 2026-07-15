import sqlite3
from datetime import date, datetime, timedelta
import pandas as pd
import streamlit as st

DB_PATH = "outreach.db"
FOLLOWUP_DAYS = 3
STATUS_OPTIONS = ["Sent", "Connected", "Replied", "Interview", "Rejected", "Ghosted"]


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT NOT NULL,
            role TEXT,
            status TEXT NOT NULL,
            date_contacted TEXT NOT NULL,
            last_followup TEXT,
            notes TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def add_contact(name, company, role, status, date_contacted, notes):
    conn = get_conn()
    conn.execute(
        "INSERT INTO contacts (name, company, role, status, date_contacted, last_followup, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, company, role, status, date_contacted.isoformat(), None, notes),
    )
    conn.commit()
    conn.close()


def update_status(contact_id, new_status):
    conn = get_conn()
    conn.execute("UPDATE contacts SET status = ? WHERE id = ?", (new_status, contact_id))
    conn.commit()
    conn.close()


def mark_followup(contact_id):
    conn = get_conn()
    conn.execute("UPDATE contacts SET last_followup = ? WHERE id = ?", (date.today().isoformat(), contact_id))
    conn.commit()
    conn.close()


def delete_contact(contact_id):
    conn = get_conn()
    conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()
    conn.close()


def load_contacts() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM contacts ORDER BY date_contacted DESC", conn)
    conn.close()
    return df


def needs_followup(row) -> bool:
    if row["status"] not in ("Sent", "Connected"):
        return False
    last_followup = row["last_followup"]
    last_action_str = row["date_contacted"] if pd.isna(last_followup) else last_followup
    last_action = datetime.fromisoformat(last_action_str).date()
    return (date.today() - last_action) >= timedelta(days=FOLLOWUP_DAYS)


st.set_page_config(page_title="Job Outreach Tracker", page_icon="📬", layout="wide")
init_db()

st.title("📬 Job Search Outreach Tracker")
st.caption("Log every recruiter/alumni message, track replies, and never miss a follow-up.")

with st.expander("➕ Log a new outreach", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("Recruiter/contact name")
        with c2:
            company = st.text_input("Company")
        with c3:
            role = st.text_input("Role applied for")
        c4, c5 = st.columns(2)
        with c4:
            status = st.selectbox("Status", STATUS_OPTIONS)
        with c5:
            date_contacted = st.date_input("Date contacted", value=date.today())
        notes = st.text_area("Notes", height=70)
        submitted = st.form_submit_button("Add contact")
        if submitted:
            if name and company:
                add_contact(name, company, role, status, date_contacted, notes)
                st.success(f"Logged {name} at {company}.")
            else:
                st.error("Name and company are
