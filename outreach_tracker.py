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


st.set_page_config(page_title="Job Outreach Tracker", page_icon="\U0001F4EC", layout="wide")
init_db()

st.title("Job Search Outreach Tracker")
st.caption("Log every recruiter and alumni message, track replies, and never miss a follow-up.")

with st.expander("Log a new outreach", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("Recruiter or contact name")
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
                st.success("Logged " + name + " at " + company + ".")
            else:
                st.error("Name and company are required.")

df = load_contacts()
st.divider()

if not df.empty:
    total = len(df)
    replied = len(df[df["status"].isin(["Replied", "Interview"])])
    response_rate = round((replied / total) * 100, 1) if total else 0
    followups_due = sum(needs_followup(row) for _, row in df.iterrows())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total outreach", total)
    m2.metric("Replies", replied)
    m3.metric("Response rate", str(response_rate) + "%")
    m4.metric("Follow-ups due", followups_due, delta_color="inverse")

    if followups_due > 0:
        st.warning(str(followups_due) + " contact(s) need a follow-up. Check the flagged rows below.")

st.subheader("Your contacts")

if df.empty:
    st.info("No contacts logged yet. Add your first outreach above.")
else:
    for _, row in df.iterrows():
        flag = "FOLLOW UP" if needs_followup(row) else ""
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            with c1:
                st.markdown("**" + row["name"] + "** - " + row["company"] + " " + flag)
                if row["role"]:
                    st.caption("Role: " + row["role"])
                if row["notes"]:
                    st.caption(row["notes"])
            with c2:
                st.caption("Contacted: " + str(row["date_contacted"]))
                if row["last_followup"] and not pd.isna(row["last_followup"]):
                    st.caption("Last follow-up: " + str(row["last_followup"]))
            with c3:
                new_status = st.selectbox(
                    "Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(row["status"]), key="status_" + str(row["id"])
                )
                if new_status != row["status"]:
                    update_status(row["id"], new_status)
                    st.rerun()
            with c4:
                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    if st.button("Mark followed up", key="followup_" + str(row["id"])):
                        mark_followup(row["id"])
                        st.rerun()
                with bcol2:
                    if st.button("Delete", key="delete_" + str(row["id"])):
                        delete_contact(row["id"])
                        st.rerun()
