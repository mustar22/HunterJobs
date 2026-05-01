import requests

def send_telegram(token: str, chat_id: str, message: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

# Test it
if __name__ == "__main__":
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    result = send_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, "🎯 HunterJobsBot is alive!")
    print(result)