import glob
import json
import os
import sys
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

import yaml

TIMEZONE = ZoneInfo("Europe/Oslo")
SCHEDULE_TIME_FORMAT = "%Y-%m-%d %H:%M"
BOOKS_DIR = os.path.join(os.path.dirname(__file__), "books")
STATE_PATH = os.path.join(os.path.dirname(__file__), "state", "posted.json")


def load_books():
    books = []
    for path in sorted(glob.glob(os.path.join(BOOKS_DIR, "*.yaml"))):
        with open(path, "r") as f:
            books.append((path, yaml.safe_load(f)))
    return books


def load_state():
    if not os.path.exists(STATE_PATH):
        return set()
    with open(STATE_PATH, "r") as f:
        return set(json.load(f))


def save_state(posted_keys):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(sorted(posted_keys), f, indent=2)
        f.write("\n")


def find_due_entries(books, now, posted_keys):
    due = []
    for path, book in books:
        for raw_time, message in book.get("schedule", {}).items():
            entry_dt = datetime.strptime(raw_time, SCHEDULE_TIME_FORMAT).replace(
                tzinfo=TIMEZONE
            )
            key = f"{os.path.basename(path)}::{raw_time}"
            if entry_dt <= now and key not in posted_keys:
                due.append((entry_dt, key, message))

    due.sort(key=lambda item: item[0])
    return due


def post_to_discord(webhook_url, message):
    body = json.dumps({"content": message}).encode()
    request = urllib.request.Request(
        webhook_url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "bookclubbot (https://github.com, 1.0)",
        },
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        if response.status >= 300:
            raise RuntimeError(f"Discord webhook returned status {response.status}")


def main():
    now = datetime.now(TIMEZONE)
    books = load_books()
    posted_keys = load_state()

    due = find_due_entries(books, now, posted_keys)
    if not due:
        print("No newly due reading entries, skipping.")
        return

    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    for entry_dt, key, message in due:
        post_to_discord(webhook_url, message)
        posted_keys.add(key)
        save_state(posted_keys)
        print(f"Posted (scheduled for {entry_dt}): {message}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
