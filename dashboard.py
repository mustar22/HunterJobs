import streamlit as st
import sqlite3
import subprocess
import pandas as pd
import json
import os

DB_PATH = "jobs.db"
SETTINGS_PATH = "settings.json"

# Default settings
DEFAULT_SETTINGS = {
    "gemma_api_key": "",
    "telegram_token": "",
    "telegram_chat_id": "",
    "profile": "",
    "search_terms": "AI engineer\nmachine learning engineer\ngenerative AI engineer",
    "hard_reject": "US citizenship required\nsecurity clearance\nDataAnnotation\nMindrift"
}

def load_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)

def get_conn():
    return sqlite3.connect(DB_PATH)

def get_jobs(verdict_filter=None):
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = get_conn()
    try:
        query = """
            SELECT job_url, title, company, verdict, score, date_seen,
                   description, green, red, reason
            FROM seen_jobs
            WHERE verdict != 'SKIP'
            ORDER BY score DESC, date_seen DESC
        """
        if verdict_filter and verdict_filter != "All":
            query = """
                SELECT job_url, title, company, verdict, score, date_seen,
                       description, green, red, reason
                FROM seen_jobs
                WHERE verdict = ?
                ORDER BY score DESC, date_seen DESC
            """
            df = pd.read_sql_query(query, conn, params=(verdict_filter,))
        else:
            df = pd.read_sql_query(query, conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def update_verdict(url, new_verdict):
    conn = get_conn()
    conn.execute("UPDATE seen_jobs SET verdict = ? WHERE job_url = ?", (new_verdict, url))
    conn.commit()
    conn.close()

def get_stats():
    if not os.path.exists(DB_PATH):
        return 0, 0, 0
    conn = get_conn()
    try:
        total = conn.execute("SELECT count(*) FROM seen_jobs").fetchone()[0]
        apply = conn.execute("SELECT count(*) FROM seen_jobs WHERE verdict = 'APPLY'").fetchone()[0]
        applied = conn.execute("SELECT count(*) FROM seen_jobs WHERE verdict = 'APPLIED'").fetchone()[0]
    except:
        total, apply, applied = 0, 0, 0
    conn.close()
    return total, apply, applied

# Page config
st.set_page_config(page_title="HunterJobsBot", page_icon="🎯", layout="wide")
st.title("🎯 HunterJobsBot")

# Tabs
tab1, tab2 = st.tabs(["🔍 Jobs", "⚙️ Setup"])

# ─── JOBS TAB ───
with tab1:
    settings = load_settings()

    # Stats row
    total, apply_count, applied_count = get_stats()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Scanned", total)
    col2.metric("Worth Applying", apply_count)
    col3.metric("Applied", applied_count)

    with col4:
        if st.button("🔍 Run Scan Now", type="primary"):
            if not settings.get("gemma_api_key"):
                st.error("Set your Gemma API key in Setup first!")
            else:
                with st.spinner("Scanning jobs... this takes a few minutes"):
                    subprocess.run(["python", "main.py"])
                st.success("Scan complete!")
                st.rerun()

    st.divider()

    # Filter
    verdict_filter = st.radio(
        "Filter:",
        ["All", "APPLY", "MAYBE", "APPLIED"],
        horizontal=True
    )

    # Job listings
    df = get_jobs(verdict_filter)

    if df.empty:
        st.info("No jobs yet. Run a scan or check your Setup tab.")
    else:
        st.markdown(f"**{len(df)} jobs found**")

        for _, row in df.iterrows():
            score = row["score"]
            verdict = row["verdict"]
            emoji = "🎯" if verdict == "APPLY" else "🤔" if verdict == "MAYBE" else "✅"

            with st.container():
                col1, col2, col3, col4 = st.columns([4, 1, 1, 1])

                with col1:
                    st.markdown(f"**{emoji} {row['title']}**")
                    st.caption(f"{row['company']} · Score: {score}/10 · {row['date_seen'][:10]}")
                    if row.get("green") or row.get("red"):
                        with st.expander("Details"):
                            if row.get("green"):
                                st.markdown(f"✅ {row['green']}")
                            if row.get("red"):
                                st.markdown(f"❌ {row['red']}")
                            if row.get("reason"):
                                st.markdown(f"_{row['reason']}_")
                            if row.get("description"):
                                st.markdown("**Description:**")
                                st.markdown(str(row["description"])[:500] + "...")

                with col2:
                    st.link_button("Apply", row["job_url"])

                with col3:
                    if st.button("✅ Applied", key=f"applied_{row['job_url']}"):
                        update_verdict(row["job_url"], "APPLIED")
                        st.rerun()

                with col4:
                    if st.button("🗑️ Skip", key=f"skip_{row['job_url']}"):
                        update_verdict(row["job_url"], "SKIP")
                        st.rerun()

                st.divider()

# ─── SETUP TAB ───
with tab2:
    st.header("⚙️ Setup")
    settings = load_settings()

    st.subheader("🔑 API Keys")
    gemma_key = st.text_input(
        "Gemma API Key (Google AI Studio)",
        value=settings.get("gemma_api_key", ""),
        type="password",
        help="Get your free key at aistudio.google.com/apikey"
    )

    st.subheader("👤 Your Profile")
    st.caption("Describe yourself — the more detail the better filtering")
    profile = st.text_area(
        "Profile",
        value=settings.get("profile", ""),
        height=300,
        label_visibility="collapsed"
    )

    st.subheader("🔍 Search Terms")
    st.caption("One search term per line")
    search_terms = st.text_area(
        "Search Terms",
        value=settings.get("search_terms", ""),
        height=150,
        label_visibility="collapsed"
    )

    st.subheader("🚫 Hard Reject Keywords")
    st.caption("Jobs containing these words will be auto-rejected without using API")
    hard_reject = st.text_area(
        "Hard Reject",
        value=settings.get("hard_reject", ""),
        height=200,
        label_visibility="collapsed"
    )

    st.subheader("⏱️ Search Settings")
    hours_old = st.slider("Only show jobs posted within (hours)",
                          min_value=24, max_value=168, value=int(settings.get("hours_old", 48)), step=24)

    if st.button("💾 Save Settings", type="primary"):
        new_settings = {
            "gemma_api_key": gemma_key,
            "profile": profile,
            "search_terms": search_terms,
            "hard_reject": hard_reject,
            "hours_old": hours_old,
        }
        save_settings(new_settings)
        st.success("✅ Settings saved!")