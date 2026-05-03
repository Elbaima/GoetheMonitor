import requests
from bs4 import BeautifulSoup
import hashlib
import os
import datetime

# ============================================================
TELEGRAM_BOT_TOKEN = "8589490725:AAFuxTEo3ZLFokwTZ6s8xmXXov_bbmwDj20"
TELEGRAM_CHAT_ID   = "-1003918637838"
# ============================================================

URL = "https://www.goethe.de/ins/rw/de/spr/prf/gzb1.cfm"
PARAMS = {"type": "ER", "page": "1"}
SNAPSHOT_FILE = "last_snapshot.txt"

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
            print(f"[{now()}] Telegram message sent!")
        else:
            print(f"[{now()}] Telegram error: {response.text}")
    except Exception as e:
        print(f"[{now()}] Could not send message: {e}")

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_page_hash():
    """Download the page and return a hash of its content."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(URL, params=PARAMS, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Get only the main content text, ignoring menus/headers
        text = soup.get_text(separator=" ").strip()
        return hashlib.md5(text.encode()).hexdigest(), text
    except Exception as e:
        print(f"[{now()}] Error fetching page: {e}")
        return None, None

def main():
    print(f"[{now()}] Checking Goethe B1 Rwanda page for any changes...")

    current_hash, current_text = get_page_hash()

    if current_hash is None:
        print(f"[{now()}] Could not reach the website. Will try again next run.")
        return

    # Load previous snapshot
    if os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE, "r") as f:
            last_hash = f.read().strip()

        if current_hash != last_hash:
            # Page has CHANGED — notify immediately!
            print(f"[{now()}] PAGE CHANGED! Sending notification...")
            send_telegram_message(
                "🚨 <b>GOETHE B1 PAGE HAS CHANGED!</b> 🚨\n\n"
                "Something on the registration page is different from before.\n"
                "Please check immediately — registration may be open!\n\n"
                "👉 https://www.goethe.de/ins/rw/de/spr/prf/gzb1.cfm?type=ER&page=1\n\n"
                "⏰ Don't wait — check now! 🎓"
            )
            # Save new snapshot
            with open(SNAPSHOT_FILE, "w") as f:
                f.write(current_hash)
        else:
            print(f"[{now()}] No change detected. Page looks the same.")

    else:
        # First time running — save the current snapshot
        print(f"[{now()}] First run — saving current page snapshot.")
        with open(SNAPSHOT_FILE, "w") as f:
            f.write(current_hash)
        send_telegram_message(
            "✅ <b>Goethe Monitor is now active!</b>\n\n"
            "I have saved today's page snapshot.\n"
            "I will notify you the moment ANYTHING changes on the registration page! 🎓"
        )

if __name__ == "__main__":
    main()
