
# 🎯 HunterJobsBot

Automated job hunting pipeline. Scrapes LinkedIn and Indeed, filters listings using Gemma AI against your profile, and shows results in a clean dashboard.

## How it works

1. JobSpy scrapes remote job listings for your search terms
2. Gemma 4 scores each listing 1-10 against your profile
3. Results appear in a Streamlit dashboard — apply, skip, or mark as applied

## Setup

1. Install dependencies:
```
pip install streamlit python-jobspy google-genai pandas
```

2. Run the dashboard:
```
streamlit run dashboard.py
```

3. Open the **Setup tab**, enter your:
   - Gemma API key (free at [aistudio.google.com](https://aistudio.google.com/apikey))
   - Your profile (skills, experience, target salary)
   - Search terms
   - Hard reject keywords

4. Go to **Jobs tab** and hit **Run Scan Now**

## Stack

Python · JobSpy · Gemma 4 26B · Streamlit · SQLite

---

*Built this because I was spending a lot of time manually filtering job boards full of US-only roles, agency spam, and senior positions. Automated the boring part so I can focus on actually applying :)*

## Credits

- [JobSpy](https://github.com/speedyapply/JobSpy) — job scraping library