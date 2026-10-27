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
LIGHT = "#fff9ed"
CELL, PITCH = 14, 18
GRID_X, GRID_Y = 110, 110
DURATION = 12
SNAKE_LENGTH = 0.06


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

    slots = {}
    for day, count in counts.items():
        offset = (day - start).days
        slots[(offset // 7, offset % 7)] = count

    weeks = max(col for col, _ in slots) + 1
    order = []
    for col in range(weeks):
        rows = range(7) if col % 2 == 0 else range(6, -1, -1)
        order += [(col, row) for row in rows if (col, row) in slots]

    total_steps = len(order) - 1
    cells, css = [], []
    for index, (col, row) in enumerate(order):
        x = GRID_X + col * PITCH
        y = GRID_Y + row * PITCH
        count = slots[(col, row)]
        base = LEVELS[level(count)]
        if count <= 0:
            cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{base}"/>')
            continue
        name = f"k{index}"
        passed = index / total_steps - SNAKE_LENGTH
        pct = max(0.0, passed) * 100
        flash_end = min(pct + 3, 100)
        css.append(
            f"@keyframes {name} {{ 0%, {pct:.3f}% {{ fill: {base}; }} {min(pct + 0.4, 100):.3f}% {{ fill: {LIGHT}; }} {flash_end:.3f}%, 100% {{ fill: {base}; }} }}"
        )
        css.append(f".{name} {{ animation-name: {name}; }}")
        cells.append(f'<rect class="c {name}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{base}"/>')

    points = " L".join(f"{GRID_X + col * PITCH + CELL / 2:g} {GRID_Y + row * PITCH + CELL / 2:g}" for col, row in order)
    trail = f'<path class="trail" pathLength="1" d="M{points}"/>'

    legend = "".join(
        f'<rect x="{948 + index * 16}" y="326" width="12" height="12" rx="2" fill="{color}"/>'
        for index, color in enumerate(LEVELS)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="365" viewBox="0 0 1200 365">
<title>Contribution trail — Persona 5 Royal snake animation</title>
<desc>{html.escape(f"{total} contributions in the last year, including private contributions. Updated {updated}.")}</desc>
<style>
  .c {{ animation-duration: {DURATION}s; animation-timing-function: linear; animation-iteration-count: infinite; }}
  .trail {{ fill: none; stroke: {LIGHT}; stroke-width: 4; stroke-linejoin: round; stroke-linecap: round; stroke-dasharray: {SNAKE_LENGTH} 1; animation: move {DURATION}s linear infinite; }}
  @keyframes move {{ 0% {{ stroke-dashoffset: 0; }} 100% {{ stroke-dashoffset: -1; }} }}
  {" ".join(css)}
  @media (prefers-reduced-motion: reduce) {{ .c {{ animation: none !important; }} .trail {{ display: none; }} }}
</style>
<path d="M0 27L1183 0L1200 340L22 365Z" fill="#e6162c"/>
<path d="M13 0L1200 20L1181 365L0 335Z" fill="#111111"/>
<path d="M30 32L472 20L478 68L25 77Z" fill="#fff9ed"/>
<text x="47" y="59" fill="#111111" font-family="Arial, Helvetica, sans-serif" font-size="26" font-weight="900" font-style="italic" transform="rotate(-1 47 59)">CONTRIBUTION TRAIL</text>
<text x="{GRID_X}" y="96" fill="#fff9ed" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700">{total:,} CONTRIBUTIONS IN THE LAST YEAR</text>
<text x="800" y="59" fill="#b5b5b5" font-family="Arial, Helvetica, sans-serif" font-size="13">UPDATED {html.escape(updated)}</text>
{"".join(cells)}
{trail}
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
