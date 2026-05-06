from google import genai
from config import GEMMA_API_KEY, PROFILE, HARD_REJECT, SCORING_RUBRIC
from datetime import datetime

client = genai.Client(api_key=GEMMA_API_KEY)

def is_too_old(date_posted_str: str, max_days: int = 14) -> bool:
    try:
        date = datetime.strptime(str(date_posted_str), "%Y-%m-%d")
        return (datetime.now() - date).days > max_days
    except:
        return False

def get_freshness(date_posted_str: str) -> str:
    try:
        date = datetime.strptime(str(date_posted_str), "%Y-%m-%d")
        days = (datetime.now() - date).days
        if days == 0: return "🟢 Today"
        if days == 1: return "🟢 Yesterday"
        if days <= 7: return "🟡 This week"
        return "🔴 Older"
    except:
        return "❓ Unknown"

def filter_job(title: str, company: str, description: str, date_posted: str = "") -> dict:
    # Age check
    if is_too_old(date_posted):
        return {"verdict": "SKIP", "score": 0, "reason": "Too old", "green": "", "red": "", "freshness": "🔴 Older"}

    # Hard reject check
    description_lower = description.lower()
    for reject in HARD_REJECT:
        if reject.lower() in description_lower or reject.lower() in company.lower():
            return {"verdict": "SKIP", "score": 0, "reason": f"Hard reject: {reject}", "green": "", "red": "", "freshness": get_freshness(date_posted)}

    prompt = f"""
You are a job filter for a specific candidate. Evaluate this job posting.

CANDIDATE PROFILE:
{PROFILE}

JOB POSTING:
Title: {title}
Company: {company}
Description: {description[:3000]}

Score this job 1-10 and give a verdict based on the candidate profile above.

{SCORING_RUBRIC}

Respond in this exact format:
SCORE: X
VERDICT: APPLY/MAYBE/SKIP
GREEN: [2-3 green flags]
RED: [2-3 red flags]
REASON: [one sentence]
"""

    try:
        response = client.models.generate_content(
            model="gemma-4-26b-a4b-it",
            contents=prompt
        )
        text = response.text
    except Exception as e:
        print(f"Gemma API error: {e}")
        return {"verdict": "SKIP", "score": 0, "reason": "API error",
                "green": "", "red": "", "freshness": get_freshness(date_posted)}

    result = {
        "raw": text,
        "score": 0,
        "verdict": "SKIP",
        "green": "",
        "red": "",
        "reason": "",
        "freshness": get_freshness(date_posted)
    }

    for line in text.split("\n"):
        if line.startswith("SCORE:"):
            try:
                result["score"] = int(line.split(":")[1].strip())
            except:
                pass
        elif line.startswith("VERDICT:"):
            result["verdict"] = line.split(":")[1].strip()
        elif line.startswith("GREEN:"):
            result["green"] = line.split(":", 1)[1].strip()
        elif line.startswith("RED:"):
            result["red"] = line.split(":", 1)[1].strip()
        elif line.startswith("REASON:"):
            result["reason"] = line.split(":", 1)[1].strip()

    return result