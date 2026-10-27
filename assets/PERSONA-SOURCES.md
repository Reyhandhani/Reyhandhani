# Persona 5 Royal profile assets

The Arsène illustration is the official ATLUS / SEGA artwork, downloaded from:
https://p5r.jp/resources/img/character/hero/persona_aa0c6566c4bd27dd93fc4f7a5444bc7b.png

Banner character page: https://p5r.jp/character/hero/

The profile card uses a separate official Arsène artwork from Persona 5 Strikers:
https://p5s.jp/resources/img/character/hero/persona_e5d42eb6355fe4f95f71a084ce3c4c95.png

Profile character page: https://p5s.jp/character/hero/

The current profile uses native SVG compositions with the original PNG embedded
as a data URI. The character illustration was not generated or repainted.

## Rebuild

No Python dependencies are needed for the current SVG assets:

    python scripts/build_persona_svg.py

The contribution trail and activity card need PROFILE_TOKEN (see below):

    PROFILE_TOKEN=... python scripts/build_activity_svg.py
    PROFILE_TOKEN=... python scripts/build_contribution_svg.py

The banner's geometry and lettering remain vector graphics. The unmodified
Arsène image is shared between independently animated wing-tip layers and the
body, with overlap at the joins. Continuous CSS keyframes replace the older
palette-compressed GIF and integer-position frames. Reduced-motion preferences
stop the banner and contribution animations.

## Active assets

- persona-banner.svg: self-contained 1200 × 460 animated banner
- persona-about.svg: profile, learning, collaboration, and Arsène composition
- persona-repositories.svg: repositories button
- persona-email.svg / persona-linkedin.svg: individual linked contact cards
- persona-contributions.svg: actual contribution animation in a Persona frame
- persona-profile.svg / persona-stack.svg / persona-activity.svg: section strips
- persona-footer.svg: contact section title
- arsene-official.png: original banner artwork
- arsene-strikers-official.png: alternate profile artwork

The workflow reads the full GitHub contribution calendar on schedule and renders
persona-activity.svg (scripts/build_activity_svg.py) and persona-contributions.svg
(scripts/build_contribution_svg.py) from it. Both scripts read PROFILE_TOKEN and
fall back to GITHUB_TOKEN; a PROFILE_TOKEN with read:user is needed to include
private contributions, which the default token cannot see. Only per-day totals
are drawn, so no repository or event details reach the public README. The bot
commits those files and README.md to main with [skip ci] to avoid a push-triggered loop. The asset URLs in README.md get ?v=<hash of the files> so
GitHub's image cache fetches new content when it changes. No output branch is kept.

The section strips and contact section title are standalone editable SVG files.
Only active profile assets, their original artwork, and the two current build
scripts are retained in this repository.
