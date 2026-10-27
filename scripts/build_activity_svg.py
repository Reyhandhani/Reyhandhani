"""Render the Persona activity card from live GitHub contribution data.

Pure standard library. Requires GITHUB_TOKEN (provided automatically in GitHub Actions).
"""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import html
import json
import os
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "persona-activity.svg"
QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""


def fetch_calendar(login, token):
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "persona-activity"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors") or not payload.get("data", {}).get("user"):
        raise SystemExit(f"GitHub GraphQL request failed: {payload.get('errors', payload)}")
    calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    counts = {
        date.fromisoformat(day["date"]): day["contributionCount"]
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    }
    return calendar["totalContributions"], counts


def summarize(counts, today):
    past = {day: count for day, count in counts.items() if day <= today}
    last_30 = sum(count for day, count in past.items() if day > today - timedelta(days=30))

    current_day = today if past.get(today, 0) else today - timedelta(days=1)
    current = 0
    while past.get(current_day, 0) > 0:
        current += 1
        current_day -= timedelta(days=1)

    longest = run = 0
    for day in sorted(past):
        run = run + 1 if past[day] > 0 else 0
        longest = max(longest, run)
    return last_30, current, longest


def render(total, last_30, current, longest, updated):
    stats = (
        (470, f"{total:,}", "LAST YEAR"),
        (640, f"{last_30:,}", "LAST 30 DAYS"),
        (810, f"{current:,}", "CURRENT STREAK"),
        (980, f"{longest:,}", "LONGEST STREAK"),
    )
    blocks = "\n".join(
        f'<text x="{x}" y="58" fill="#fff9ed" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="900">{value}</text>\n'
        f'<text x="{x}" y="80" fill="#b5b5b5" font-family="Arial, Helvetica, sans-serif" font-size="11" letter-spacing="1">{label}</text>'
        for x, value, label in stats
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="92" viewBox="0 0 1200 92">
  <title>{html.escape("ACTIVITY — THE CONTRIBUTION RECORD")}</title>
  <desc>{html.escape(f"{total} contributions in the last year. Updated {updated}.")}</desc>
  <path d="M5 26L406 5L425 72L18 88Z" fill="#e6162c"/>
  <path d="M0 14L384 23L368 84L11 65Z" fill="#111111"/>
  <text x="30" y="61" fill="#fff9ed" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="900" font-style="italic" transform="rotate(-2 30 61)">ACTIVITY</text>
  <path d="M421 56L1172 47" stroke="#e6162c" stroke-width="2"/>
  <text x="453" y="34" fill="#e6162c" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" letter-spacing="2">THE CONTRIBUTION RECORD</text>
  <text x="700" y="34" fill="#b5b5b5" font-family="Arial, Helvetica, sans-serif" font-size="11" letter-spacing="1">UPDATED {html.escape(updated)}</text>
  {blocks}
  <path d="M1182 27L1187 39L1200 38L1190 47L1194 60L1182 53L1171 61L1174 47L1164 39L1178 39Z" fill="#e6162c"/>
</svg>
'''


def main():
    token = os.environ.get("PROFILE_TOKEN")
    if not token:
        raise SystemExit("PROFILE_TOKEN is required")
    login = os.environ.get("GITHUB_REPOSITORY_OWNER", "Reyhandhani")
    today = datetime.now(timezone.utc).date()
    total, counts = fetch_calendar(login, token)
    last_30, current, longest = summarize(counts, today)
    OUTPUT.write_text(render(total, last_30, current, longest, today.isoformat()), encoding="utf-8")
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
