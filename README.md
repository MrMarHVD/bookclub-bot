# bookclubbot

Posts book club reading updates to a Discord channel automatically, at whatever date and time each schedule entry specifies (Europe/Oslo time). No always-on bot or server required — a GitHub Actions workflow polls every 15 minutes and the script decides whether anything is scheduled for the current window.

## Setup

1. **Create a Discord webhook**: in the target channel, go to Edit Channel → Integrations → Webhooks → New Webhook, then copy the webhook URL.
2. **Add it as a GitHub secret**: in this repo on GitHub, go to Settings → Secrets and variables → Actions → New repository secret, name it `DISCORD_WEBHOOK_URL`, and paste the URL.
3. Push this repo to GitHub. The `daily-post.yml` workflow will start running automatically on its 15-minute schedule.

## Starting a new book

Each reading period is its own file under `books/`. To start a new book, add a new YAML file (e.g. `books/2026-09-my-new-book.yaml`) with its own date/time entries and push — no code changes or edits to existing files needed:

```yaml
book: "New Book Title"
schedule:
  "2026-09-01 08:00": "Today we are reading Chapter 1."
  "2026-09-02 20:30": "Today we are reading Chapter 2."
```

Schedule keys are `"YYYY-MM-DD HH:MM"` in Europe/Oslo time (quotes required — otherwise YAML parses the colon oddly). To reschedule or change what's said on a given day, just edit the entry's time or message and push; no code changes needed.

Every file in `books/` is scanned each run. Because the workflow only polls every 15 minutes (see below), each entry is matched to the 15-minute window it falls into rather than its exact minute — e.g. an entry at `08:07` posts on the run covering `08:00`–`08:14`. Windows with no entry in any file are silently skipped. If two files both have an entry in the same window, the run fails loudly (visible as a red X in the Actions tab) instead of guessing which one to post — fix the overlap and it'll pick back up on the next run.

## Testing locally

```bash
pip install -r requirements.txt
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." python post_reading.py
```

The script posts only if some entry's 15-minute window matches right now — set a schedule entry a few minutes in the future (rounded down to the current quarter-hour) to test.

## Testing the GitHub Actions workflow

Use the "Run workflow" button on the Actions tab (enabled via `workflow_dispatch`) to trigger a manual run without waiting for the schedule.

## Note on timing precision

GitHub Actions' `schedule` trigger is best-effort — runs can be delayed several minutes during high load, and every-15-minutes polling only checks in quarter-hour windows. This is fine for a daily book club post but isn't a guarantee of exact-minute delivery.
