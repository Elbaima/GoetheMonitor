import requests
from bs4 import BeautifulSoup
import datetime

# ============================================================
#  CONFIGURATION — already filled in for you!
# ============================================================
TELEGRAM_BOT_TOKEN = "8589490725:AAFuxTEo3ZLFokwTZ6s8xmXXov_bbmwDj20"
TELEGRAM_CHAT_ID   = "-1003918637838"
# ============================================================

URL = "https://www.goethe.de/ins/rw/de/spr/prf/gzb1.cfm"
PARAMS = {"type": "ER", "page": "1"}

# Keywords that suggest registration is OPEN
OPEN_KEYWORDS = [
    "anmelden",
    "registrieren",
    "buchen",
    "jetzt anmelden",
    "register now",
    "book now",
    "sign up",
]

def send_telegram_message(message: str):
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(api_url, data=payload, timeout=10)
        if response.status_code == 200:
            print(f"[{now()}] Telegram message sent successfully!")
        else:
            print(f"[{now()}] Telegram error: {response.text}")
    except Exception as e:
        print(f"[{now()}] Could not send Telegram message: {e}")

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def is_registration_open():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(URL, params=PARAMS, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text(separator=" ").lower()
        for keyword in OPEN_KEYWORDS:
            if keyword.lower() in page_text:
                return True
        return False
    except requests.exceptions.RequestException as e:
        print(f"[{now()}] Network error: {e}")
        return False

def main():
    print(f"[{now()}] Checking Goethe B1 Rwanda registration page...")

    if is_registration_open():
        print(f"[{now()}] OPEN! Sending Telegram notification...")
        send_telegram_message(
            "🚨 <b>GOETHE B1 REGISTRATION IS NOW OPEN!</b> 🚨\n\n"
            "📝 Register immediately here:\n"
            "https://www.goethe.de/ins/rw/de/spr/prf/gzb1.cfm?type=ER&page=1\n\n"
            "⏰ Hurry — slots fill up very fast!\n\n"
            "Good luck everyone! 🎓"
        )
    else:
        print(f"[{now()}] Not open yet. No notification sent.")

if __name__ == "__main__":
    main()
