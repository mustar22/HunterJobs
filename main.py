import sqlite3
import time
from jobspy import scrape_jobs
from filter import filter_job
from telegram_sender import send_telegram
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, SEARCH_TERMS

# Setup SQLite to track seen jobs
def init_db():
    conn = sqlite3.connect("jobs.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_jobs (
            job_url TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            verdict TEXT,
            score INTEGER,
            date_seen TEXT,
            description TEXT,
            green TEXT,
            red TEXT,
            reason TEXT
        )
    """)
    conn.commit()
    return conn

def is_seen(conn, url):
    cursor = conn.execute("SELECT 1 FROM seen_jobs WHERE job_url = ?", (url,))
    return cursor.fetchone() is not None

def mark_seen(conn, url, title, company, verdict, score, description="", green="", red="", reason=""):
    conn.execute(
        "INSERT OR IGNORE INTO seen_jobs VALUES (?, ?, ?, ?, ?, datetime('now'), ?, ?, ?, ?)",
        (url, title, company, verdict, score, description[:1000], green, red, reason)
    )
    conn.commit()

def format_message(title, company, score, verdict, green, red, reason, url, date_posted="Unknown", freshness="❓ Unknown"):
    emoji = "🎯" if verdict == "APPLY" else "🤔"
    return f"""
{emoji} *{verdict}* — Score: {score}/10
*{title}*
Company: {company}
📅 Posted: {date_posted}

✅ {green}
❌ {red}

_{reason}_

[Apply Here]({url})
""".strip()

def run_hunt():
    conn = init_db()
    send_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, "🔍 HunterJobsBot starting scan...")
    
    total_apply = 0
    
    for term in SEARCH_TERMS:
        print(f"Searching: {term}")
        try:
            jobs = scrape_jobs(
                site_name=["linkedin", "indeed"],
                search_term=term,
                is_remote=True,
                results_wanted=20,
                hours_old=48,
                linkedin_fetch_description=True,
                country_indeed="worldwide"
            )
        except Exception as e:
            print(f"Scrape error: {e}")
            continue

        for _, job in jobs.iterrows():
            url = str(job.get("job_url", ""))
            title = str(job.get("title", ""))
            company = str(job.get("company", ""))
            description = str(job.get("description", ""))

            if not url or is_seen(conn, url):
                continue

            if not description or len(description) < 100:
                mark_seen(conn, url, title, company, "SKIP", 0)
                continue

            print(f"Filtering: {title} @ {company}")
            date_posted = str(job.get("date_posted", "Unknown"))
            result = filter_job(title, company, description, date_posted)

            mark_seen(conn, url, title, company, result["verdict"], result["score"],
                      description, result["green"], result["red"], result["reason"])
            
            if result["verdict"] in ["APPLY", "MAYBE"]:
                msg = format_message(
                    title, company,
                    result["score"], result["verdict"],
                    result["green"], result["red"],
                    result["reason"], url,
                    date_posted,
                    result["freshness"]
                )
                send_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, msg)
                total_apply += 1
                time.sleep(1)

            time.sleep(2)  # be polite to APIs

    send_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, f"✅ Scan complete. {total_apply} jobs worth reviewing.")
    conn.close()

if __name__ == "__main__":
    run_hunt()