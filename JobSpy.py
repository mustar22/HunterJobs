from jobspy import scrape_jobs

jobs = scrape_jobs(
    site_name=["linkedin", "indeed"],
    search_term=term,
    is_remote=True,
    results_wanted=20,
    hours_old=48,
    linkedin_fetch_description=True,
    location="Worldwide",
    country_indeed="worldwide"
)

print(jobs[["title", "company", "description"]].to_string())