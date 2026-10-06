"""Build crisp, self-contained Persona cards and smooth SVG wing animation.

Uses the unmodified official PNG inside native SVG composition. No raster
quantization, generated illustration, or external image dependency is involved.
"""

from pathlib import Path
import base64
import html

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
RED, BLACK, WHITE = "#e6162c", "#111111", "#fff9ed"
ART = "data:image/png;base64," + base64.b64encode((ASSETS / "arsene-official.png").read_bytes()).decode()
PROFILE_ART = "data:image/png;base64," + base64.b64encode((ASSETS / "arsene-strikers-official.png").read_bytes()).decode()


def write(name, width, height, title, content, description=""):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">
<title>{html.escape(title)}</title><desc>{html.escape(description or title)}</desc>
{content}
</svg>'''
    (ASSETS / name).write_text(svg, encoding="utf-8")


def text(x, y, value, size=24, color=WHITE, bold=False, italic=False, family="Arial, Helvetica, sans-serif"):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}" font-weight="{900 if bold else 400}" font-style="{"italic" if italic else "normal"}">{html.escape(value)}</text>'


def label(x, y, width, value, size=25, paper=RED, ink=WHITE, angle=-2):
    return f'''<g transform="translate({x} {y}) rotate({angle})">
<path d="M4 3L{width} 0L{width-6} 43L0 47Z" fill="{paper}"/>
{text(15, 33, value, size, ink, True, True)}</g>'''


def star(x, y, scale=1, color=WHITE):
    return f'<path transform="translate({x} {y}) scale({scale})" d="M0-22L6-6L23-4L10 7L14 24L0 14L-16 24L-10 6L-24-5L-7-7Z" fill="{color}"/>'


banner = f'''
<defs>
  <clipPath id="banner-edge"><path d="M0 0H1200V460H0Z"/></clipPath>
  <pattern id="halftone" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="1.6" fill="#8f0e1d"/></pattern>
  <clipPath id="wing-left-cut"><path d="M0 0H180V350H0Z"/></clipPath>
  <clipPath id="wing-right-cut"><path d="M690 0H1348V660H690Z"/></clipPath>
  <mask id="body" maskUnits="userSpaceOnUse" x="0" y="0" width="1348" height="1305">
    <path d="M0 0H1348V1305H0Z" fill="white"/>
    <path d="M0 0H160V330H0ZM710 0H1348V640H710Z" fill="black"/>
  </mask>
</defs>
<style>
  .idle {{ animation: idle 6s ease-in-out infinite; }}
  .left-wing {{ transform-origin:180px 300px; animation: left-wing 6s ease-in-out infinite; }}
  .right-wing {{ transform-origin:690px 400px; animation: right-wing 6s ease-in-out infinite; }}
  .paper-float {{ animation: paper-float 6s ease-in-out infinite; }}
  @keyframes idle {{ 0%,100% {{transform:translate(0,0)}} 50% {{transform:translate(-1.5px,-3px)}} }}
  @keyframes left-wing {{ 0%,100% {{transform:rotate(0deg)}} 50% {{transform:rotate(-1.5deg)}} }}
  @keyframes right-wing {{ 0%,100% {{transform:rotate(0deg)}} 50% {{transform:rotate(1.2deg)}} }}
  @keyframes paper-float {{ 0%,100% {{transform:translate(0,0)}} 50% {{transform:translate(-3px,-7px)}} }}
  @media (prefers-reduced-motion:reduce) {{ .idle,.left-wing,.right-wing,.paper-float {{animation:none}} }}
</style>
<g clip-path="url(#banner-edge)">
<path d="M0 0H1200V460H0Z" fill="{RED}"/>
<path d="M0 0H792L657 460H0Z" fill="{BLACK}"/>
<path d="M856-20L1200 37V115L731 265Z" fill="{WHITE}"/>
<path d="M828 270L1200 189V286L719 422Z" fill="#b90d20"/>
<path d="M1042-5H1082L885 460H857Z" fill="{BLACK}"/>
<path d="M868 72H1200V430H868Z" fill="url(#halftone)"/>
<path d="M22 384L511 408L455 438L0 410ZM0 11L275 0H330L0 28Z" fill="{WHITE}"/>
<path d="M46 350L557 338" stroke="{RED}" stroke-width="3"/>
{star(576,68,1,WHITE)}{star(550,389,.72,RED)}
{label(49,63,188,"MUHAMMAD",23,angle=-3)}
<g transform="translate(43 131) rotate(3)">
<path d="M5 0H566L573 97L0 104Z" fill="{WHITE}"/>
<text x="14" y="79" fill="{BLACK}" font-family="Impact, 'Arial Narrow', Arial, sans-serif" font-size="71" font-weight="900" textLength="536" lengthAdjust="spacingAndGlyphs">REYHANDHANI</text>
</g>
{label(63,259,362,"FULL STACK DEVELOPER",22,angle=-2)}
<g class="paper-float"><path d="M1065 333L1073 348L1062 359L1057 344Z" fill="{WHITE}"/></g>
<g transform="translate(650 -9) scale(.48961)">
  <g class="idle">
    <g class="left-wing"><image href="{ART}" width="1348" height="1305" clip-path="url(#wing-left-cut)"/></g>
    <g class="right-wing"><image href="{ART}" width="1348" height="1305" clip-path="url(#wing-right-cut)"/></g>
    <image href="{ART}" width="1348" height="1305" mask="url(#body)"/>
  </g>
</g>
{label(971,417,207,"PERSONA 5 ROYAL",14,BLACK,WHITE,angle=-3)}
</g>'''
# One image definition instead of repeating base64 data in each animated layer.
banner = banner.replace(f'<image href="{ART}" width="1348" height="1305"', '<use href="#arsene-art"')
banner = banner.replace('<defs>', f'<defs><image id="arsene-art" href="{ART}" width="1348" height="1305"/>', 1)
write("persona-banner.svg",1200,460,"Muhammad Reyhandhani — full stack developer",banner,
      "Persona 5 Royal calling card. Official Arsène artwork with smoothly animated wing tips and a gentle breathing motion.")

profile = f'''
<defs>
<clipPath id="portrait"><path d="M804 32L1185 17V584L788 630V183Z"/></clipPath>
<pattern id="profile-dots" width="19" height="19" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="1.6" fill="#9f0c1d"/></pattern>
</defs>
<path d="M0 16L758 0L775 612L15 641Z" fill="{RED}"/>
<path d="M12 0L768 26L751 631L0 608Z" fill="{BLACK}"/>
<path d="M804 32L1185 17V584L788 630V183Z" fill="{RED}"/>
<path d="M774 146L1185 75L1149 235L788 491Z" fill="{WHITE}"/>
<path d="M1003 326H1185V588H1003Z" fill="url(#profile-dots)"/>
<image href="{PROFILE_ART}" x="718" y="42" width="830" height="556" clip-path="url(#portrait)"/>
{label(43,37,636,"MUHAMMAD REYHANDHANI",36,WHITE,BLACK,angle=-2)}
{text(55,151,"I build web applications and APIs. Backend work",23)}
{text(55,183,"is where I spend most of my time, but I also",23)}
{text(55,215,"work on the frontend.",23)}
{text(55,272,"I like digging into how an application works,",23)}
{text(55,304,"from the interface to the database, and making",23)}
{text(55,336,"the code easier to maintain along the way.",23)}
{label(42,369,371,"CURRENTLY LEARNING",24,angle=1)}
<path d="M56 449L64 441L72 449L64 457ZM56 484L64 476L72 484L64 492Z" fill="{RED}"/>
{text(87,457,"System design / scalable architecture",23)}
{text(87,492,"DevOps / CI/CD",23)}
{label(42,529,359,"OPEN TO COLLABORATION",23,WHITE,BLACK,angle=-1)}
{text(55,603,"Full stack projects and open source.",22)}
{label(990,565,172,"ARSÈNE",36,WHITE,BLACK,angle=-4)}
{star(1150,64,.65,BLACK)}'''
write("persona-about.svg",1200,650,"About Muhammad Reyhandhani",profile,
      "I build web applications and APIs, primarily backend and also frontend. Currently learning system design, scalable architecture, DevOps, and CI/CD. Open to full stack projects and open source collaboration. Official Arsène artwork from Persona 5 Strikers accompanies the profile in a different pose from the banner.")

repo = f'''<path d="M4 8L442 0L450 62L0 72Z" fill="{RED}"/>
{text(23,46,"BROWSE REPOSITORIES",24,WHITE,True,True)}
<path d="M398 37H425M414 26L425 37L414 48" stroke="{WHITE}" stroke-width="3"/>'''
write("persona-repositories.svg",450,74,"Browse my repositories",repo)

for filename, title, subtitle, icon in (
    ("persona-email.svg","EMAIL","reyhandhani11@gmail.com","mail"),
    ("persona-linkedin.svg","LINKEDIN","Muhammad Reyhandhani","linkedin"),
):
    symbol = (f'<path d="M36 46H94V86H36Z M36 46L65 67L94 46" stroke="{WHITE}" stroke-width="3"/>'
              if icon == "mail" else
              f'<path d="M35 40H94V98H35Z" stroke="{WHITE}" stroke-width="3"/>{text(46,85,"in",39,WHITE,True)}')
    content = f'''<path d="M6 12L555 0L570 138L0 153Z" fill="{RED}"/>
<path d="M10 0L570 16L554 153L0 133Z" fill="{BLACK}"/>
<path d="M126 21L480 15L489 66L121 72Z" fill="{WHITE}"/>
{symbol}{text(143,56,title,31,BLACK,True,True)}
{text(139,111,subtitle,20,WHITE)}
<path d="M505 53L536 25M517 25H536V44" stroke="{RED}" stroke-width="4"/>'''
    write(filename,570,155,f"{title} — {subtitle}",content)

print("Built animated SVG banner, profile card with alternate Arsène artwork, repositories button, and contact cards")
