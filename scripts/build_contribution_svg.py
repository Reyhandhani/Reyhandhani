"""Render the Persona contribution trail from the full GitHub contribution calendar.

Uses PROFILE_TOKEN (falls back to GITHUB_TOKEN), so private contribution counts are
included. Only per-day totals are drawn; no repository or event details are used.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import html
import os
import build_activity_svg as activity

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "persona-contributions.svg"
LEVELS = ["#242424", "#64131e", "#a51528", "#e6162c", "#fff9ed"]
CELL, PITCH = 14, 18
GRID_X, GRID_Y = 110, 110


def level_for(counts):
    values = sorted(count for count in counts.values() if count > 0)
    if not values:
        return lambda count: 0
    cuts = [values[min(len(values) - 1, int(share * len(values)))] for share in (0.25, 0.5, 0.75)]

    def level(count):
        if count <= 0:
            return 0
        for index, cut in enumerate(cuts, start=1):
            if count <= cut:
                return index
        return 4

    return level


def render(counts, total, updated):
    level = level_for(counts)
    first = min(counts)
    start = first - timedelta(days=first.isoweekday() % 7)

    cells, trail = [], []
    for day in sorted(counts):
        offset = (day - start).days
        x = GRID_X + (offset // 7) * PITCH
        y = GRID_Y + (offset % 7) * PITCH
        cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{LEVELS[level(counts[day])]}"/>')
        if counts[day] > 0:
            trail.append(f"{x + CELL / 2:g} {y + CELL / 2:g}")
    path = f'<path class="trail" pathLength="1" d="M{" L".join(trail)}"/>' if trail else ""

    legend = "".join(
        f'<rect x="{948 + index * 16}" y="326" width="12" height="12" rx="2" fill="{color}"/>'
        for index, color in enumerate(LEVELS)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="365" viewBox="0 0 1200 365">
<title>Contribution trail — Persona 5 Royal snake animation</title>
<desc>{html.escape(f"{total} contributions in the last year, including private contributions. Updated {updated}.")}</desc>
<style>
  .trail {{ fill: none; stroke: #fff9ed; stroke-width: 3; stroke-linejoin: round; stroke-linecap: round; stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 12s linear infinite; }}
  @keyframes draw {{ 0% {{ stroke-dashoffset: 1; }} 70%, 100% {{ stroke-dashoffset: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .trail {{ animation: none; stroke-dashoffset: 0; }} }}
</style>
<path d="M0 27L1183 0L1200 340L22 365Z" fill="#e6162c"/>
<path d="M13 0L1200 20L1181 365L0 335Z" fill="#111111"/>
<path d="M30 32L472 20L478 68L25 77Z" fill="#fff9ed"/>
<text x="47" y="59" fill="#111111" font-family="Arial, Helvetica, sans-serif" font-size="26" font-weight="900" font-style="italic" transform="rotate(-1 47 59)">CONTRIBUTION TRAIL</text>
<text x="{GRID_X}" y="96" fill="#fff9ed" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700">{total:,} CONTRIBUTIONS IN THE LAST YEAR</text>
<text x="800" y="59" fill="#b5b5b5" font-family="Arial, Helvetica, sans-serif" font-size="13">UPDATED {html.escape(updated)}</text>
{"".join(cells)}
{path}
<text x="880" y="337" fill="#b5b5b5" font-family="Arial, Helvetica, sans-serif" font-size="13">LESS</text>
{legend}
<text x="1030" y="337" fill="#b5b5b5" font-family="Arial, Helvetica, sans-serif" font-size="13">MORE</text>
</svg>
'''


def main():
    token = os.environ.get("PROFILE_TOKEN")
    if not token:
        raise SystemExit("PROFILE_TOKEN is required")
    login = os.environ.get("GITHUB_REPOSITORY_OWNER", "Reyhandhani")
    today = datetime.now(timezone.utc).date()
    total, counts = activity.fetch_calendar(login, token)
    OUTPUT.write_text(render(counts, total, today.isoformat()), encoding="utf-8")
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
