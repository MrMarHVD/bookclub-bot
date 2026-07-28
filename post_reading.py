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
# The workflow polls every 15 minutes, so scheduled times are matched to the
# 15-minute window they fall in rather than the exact minute.
WINDOW_MINUTES = 15
BOOKS_DIR = os.path.join(os.path.dirname(__file__), "books")


def floor_to_window(dt):
    floored_minute = (dt.minute // WINDOW_MINUTES) * WINDOW_MINUTES
    return dt.replace(minute=floored_minute, second=0, microsecond=0)


def load_books():
    books = []
    for path in sorted(glob.glob(os.path.join(BOOKS_DIR, "*.yaml"))):
        with open(path, "r") as f:
            books.append((path, yaml.safe_load(f)))
    return books


def find_current_entry(books, window_start):
    matches = []
    for path, book in books:
        for raw_time, message in book.get("schedule", {}).items():
            entry_dt = datetime.strptime(raw_time, SCHEDULE_TIME_FORMAT).replace(
                tzinfo=TIMEZONE
            )
            if floor_to_window(entry_dt) == window_start:
                matches.append((path, raw_time, message))

    if len(matches) > 1:
        details = ", ".join(f"{path} ({raw_time})" for path, raw_time, _ in matches)
        raise RuntimeError(
            f"Multiple schedule entries fall in the same window: {details}"
        )

    return matches[0] if matches else None


def post_to_discord(webhook_url, message):
    body = json.dumps({"content": message}).encode()
    request = urllib.request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        if response.status >= 300:
            raise RuntimeError(f"Discord webhook returned status {response.status}")


def main():
    now = datetime.now(TIMEZONE)
    window_start = floor_to_window(now)

    books = load_books()
    match = find_current_entry(books, window_start)
    if match is None:
        print(f"No reading scheduled for window {window_start}, skipping.")
        return

    _, raw_time, message = match
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    post_to_discord(webhook_url, message)
    print(f"Posted (scheduled for {raw_time}): {message}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
