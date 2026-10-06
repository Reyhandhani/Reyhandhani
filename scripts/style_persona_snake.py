"""Frame a real Platane contribution animation as a Persona 5 Royal card.

Pure standard library; also used by the scheduled GitHub Actions job.
"""
from pathlib import Path
import argparse
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--source", type=Path, default=ROOT / "assets/contribution-source.svg")
parser.add_argument("--output", type=Path, default=ROOT / "assets/persona-contributions.svg")
args = parser.parse_args()

ET.register_namespace("", "http://www.w3.org/2000/svg")
source = args.source.read_text(encoding="utf-8-sig")
root = ET.fromstring(source)
assert root.tag == "{http://www.w3.org/2000/svg}svg"
palette = ":root{--cb:#333333;--cs:#fff9ed;--ce:#242424;--c0:#242424;--c1:#64131e;--c2:#a51528;--c3:#e6162c;--c4:#fff9ed}"
for style in root.findall("{http://www.w3.org/2000/svg}style"):
    style.text = re.sub(r":root\{[^}]+\}", lambda _: palette, style.text or "")
    style.text += "@media(prefers-reduced-motion:reduce){.c,.s,.u{animation:none!important}}"
root.attrib.update(x="65", y="88", width="1070", height="235")
inner = ET.tostring(root, encoding="unicode")
output = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="365" viewBox="0 0 1200 365">
<title>Contribution trail — Persona 5 Royal snake animation</title>
<desc>Actual GitHub contribution data, framed in red, black, and white. A white snake clears the contribution grid.</desc>
<path d="M0 27L1183 0L1200 340L22 365Z" fill="#e6162c"/>
<path d="M13 0L1200 20L1181 365L0 335Z" fill="#111111"/>
<path d="M30 32L472 20L478 68L25 77Z" fill="#fff9ed"/>
<text x="47" y="59" fill="#111111" font-family="Arial, Helvetica, sans-serif" font-size="26" font-weight="900" font-style="italic" transform="rotate(-1 47 59)">CONTRIBUTION TRAIL</text>
<path d="M1098 23L1105 40L1123 40L1109 51L1114 69L1098 58L1083 69L1088 51L1073 40L1092 40Z" fill="#e6162c"/>
{inner}
<text x="917" y="337" fill="#b5b5b5" font-family="Arial, Helvetica, sans-serif" font-size="13">LESS</text>
<path d="M961 324H973V336H961Z" fill="#242424"/><path d="M979 324H991V336H979Z" fill="#64131e"/>
<path d="M997 324H1009V336H997Z" fill="#a51528"/><path d="M1015 324H1027V336H1015Z" fill="#e6162c"/>
<path d="M1033 324H1045V336H1033Z" fill="#fff9ed"/>
<text x="1054" y="337" fill="#b5b5b5" font-family="Arial, Helvetica, sans-serif" font-size="13">MORE</text>
</svg>'''
ET.fromstring(output)
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(output, encoding="utf-8")
print(f"Saved {args.output}")
