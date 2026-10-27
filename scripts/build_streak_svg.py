"""Render the streak card from the full GitHub contribution history.

Same layout as the streak-stats card, fed with private-inclusive data through
PROFILE_TOKEN. Only aggregate numbers and dates are drawn.
"""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import html
import json
import os
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "persona-streak.svg"
QUERY = """query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    createdAt
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def graphql(token, login, start, end):
    body = json.dumps({"query": QUERY, "variables": {"login": login, "from": start, "to": end}}).encode()
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "persona-streak"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors") or not payload.get("data", {}).get("user"):
        raise SystemExit(f"GitHub GraphQL request failed: {payload.get('errors', payload)}")
    return payload["data"]["user"]


def collect(user, counts):
    for week in user["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for day in week["contributionDays"]:
            counts[date.fromisoformat(day["date"])] = day["contributionCount"]


def fetch_history(login, token, today):
    current = graphql(token, login, f"{today.year}-01-01T00:00:00Z", f"{today.isoformat()}T23:59:59Z")
    counts = {}
    collect(current, counts)
    created = date.fromisoformat(current["createdAt"][:10])
    for year in range(created.year, today.year):
        collect(graphql(token, login, f"{year}-01-01T00:00:00Z", f"{year}-12-31T23:59:59Z"), counts)
    return counts


def summarize(counts, today):
    past = {day: count for day, count in counts.items() if day <= today}
    total = sum(past.values())
    active = sorted(day for day, count in past.items() if count > 0)
    first = active[0]

    longest_len, longest_start, longest_end = 0, None, None
    run_len, run_start, last = 0, None, None
    for day in sorted(past):
        if past[day] > 0:
            if run_len and (day - last).days == 1:
                run_len += 1
            else:
                run_len, run_start = 1, day
            last = day
            if run_len > longest_len:
                longest_len, longest_start, longest_end = run_len, run_start, day
        else:
            run_len = 0

    end = today if past.get(today, 0) else today - timedelta(days=1)
    current_len, day = 0, end
    while past.get(day, 0) > 0:
        current_len += 1
        day -= timedelta(days=1)
    current_start = day + timedelta(days=1)

    return {
        "total": total,
        "first": first,
        "current": current_len,
        "current_start": current_start if current_len else None,
        "current_end": end if current_len else None,
        "longest": longest_len,
        "longest_start": longest_start,
        "longest_end": longest_end,
    }


def short(day):
    return f"{day:%b} {day.day}"


def full(day):
    return f"{day:%b} {day.day}, {day.year}"


def render(stats, today):
    if stats["current"]:
        current_range = short(stats["current_start"]) if stats["current_start"] == stats["current_end"] else f"{short(stats['current_start'])} - {short(stats['current_end'])}"
    else:
        current_range = short(today)
    longest_range = full(stats["longest_start"]) if stats["longest_start"] == stats["longest_end"] else f"{full(stats['longest_start'])} - {full(stats['longest_end'])}"
    total_range = f"{full(stats['first'])} - Present"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195" fill="none">
<title>{html.escape(f"Contribution streak — {stats['total']:,} total contributions")}</title>
<defs>
  <clipPath id="outer_rectangle"><rect width="495" height="195" rx="4.5"/></clipPath>
  <mask id="mask_out_ring_behind_fire">
    <rect width="495" height="195" fill="white"/>
    <ellipse cx="247.5" cy="32" rx="13" ry="18" fill="black"/>
  </mask>
</defs>
<g clip-path="url(#outer_rectangle)">
  <rect stroke="#000000" stroke-opacity="0" fill="#111111" rx="4.5" x="0.5" y="0.5" width="494" height="194"/>
  <line x1="165" y1="28" x2="165" y2="170" stroke-width="1" stroke="#333333"/>
  <line x1="330" y1="28" x2="330" y2="170" stroke-width="1" stroke="#333333"/>
  <g transform="translate(82.5, 48)"><text x="0" y="32" text-anchor="middle" fill="#ffffff" font-family='"Segoe UI", Ubuntu, sans-serif' font-weight="700" font-size="28px">{stats['total']:,}</text></g>
  <g transform="translate(82.5, 84)"><text x="0" y="32" text-anchor="middle" fill="#ffffff" font-family='"Segoe UI", Ubuntu, sans-serif' font-weight="400" font-size="14px">Total Contributions</text></g>
  <g transform="translate(82.5, 114)"><text x="0" y="32" text-anchor="middle" fill="#b5b5b5" font-family='"Segoe UI", Ubuntu, sans-serif' font-weight="400" font-size="12px">{html.escape(total_range)}</text></g>
  <g transform="translate(247.5, 108)"><text x="0" y="32" text-anchor="middle" fill="#e6162c" font-family='"Segoe UI", Ubuntu, sans-serif' font-weight="700" font-size="14px">Current Streak</text></g>
  <g transform="translate(247.5, 145)"><text x="0" y="21" text-anchor="middle" fill="#b5b5b5" font-family='"Segoe UI", Ubuntu, sans-serif' font-weight="400" font-size="12px">{html.escape(current_range)}</text></g>
  <g mask="url(#mask_out_ring_behind_fire)"><circle cx="247.5" cy="71" r="40" fill="none" stroke="#e6162c" stroke-width="5"/></g>
  <g transform="translate(247.5, 19.5)">
    <path d="M -12 -0.5 L 15 -0.5 L 15 23.5 L -12 23.5 L -12 -0.5 Z" fill="none"/>
    <path d="M 1.5 0.67 C 1.5 0.67 2.24 3.32 2.24 5.47 C 2.24 7.53 0.89 9.2 -1.17 9.2 C -3.23 9.2 -4.79 7.53 -4.79 5.47 L -4.76 5.11 C -6.78 7.51 -8 10.62 -8 13.99 C -8 18.41 -4.42 22 0 22 C 4.42 22 8 18.41 8 13.99 C 8 8.6 5.41 3.79 1.5 0.67 Z M -0.29 19 C -2.07 19 -3.51 17.6 -3.51 15.86 C -3.51 14.24 -2.46 13.1 -0.7 12.74 C 1.07 12.38 2.9 11.53 3.92 10.16 C 4.31 11.45 4.51 12.81 4.51 14.2 C 4.51 16.85 2.36 19 -0.29 19 Z" fill="#e6162c"/>
  </g>
  <g transform="translate(247.5, 48)"><text x="0" y="32" text-anchor="middle" fill="#ffffff" font-family='"Segoe UI", Ubuntu, sans-serif' font-weight="700" font-size="28px">{stats['current']:,}</text></g>
  <g transform="translate(412.5, 48)"><text x="0" y="32" text-anchor="middle" fill="#ffffff" font-family='"Segoe UI", Ubuntu, sans-serif' font-weight="700" font-size="28px">{stats['longest']:,}</text></g>
  <g transform="translate(412.5, 84)"><text x="0" y="32" text-anchor="middle" fill="#ffffff" font-family='"Segoe UI", Ubuntu, sans-serif' font-weight="400" font-size="14px">Longest Streak</text></g>
  <g transform="translate(412.5, 114)"><text x="0" y="32" text-anchor="middle" fill="#b5b5b5" font-family='"Segoe UI", Ubuntu, sans-serif' font-weight="400" font-size="12px">{html.escape(longest_range)}</text></g>
</g>
</svg>
'''


def main():
    token = os.environ.get("PROFILE_TOKEN")
    if not token:
        raise SystemExit("PROFILE_TOKEN is required")
    login = os.environ.get("GITHUB_REPOSITORY_OWNER", "Reyhandhani")
    today = datetime.now(timezone.utc).date()
    stats = summarize(fetch_history(login, token, today), today)
    OUTPUT.write_text(render(stats, today), encoding="utf-8")
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
