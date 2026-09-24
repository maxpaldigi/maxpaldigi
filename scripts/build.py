"""Generate the SVG assets used by the profile README.

Run locally or from the daily workflow:
    GITHUB_TOKEN=... python3 scripts/build.py
Without a token, the stats card is skipped and the other assets are rebuilt.
"""
import json
import os
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
USER = "maxpaldigi"

# Design tokens
BG = "#0F172A"
SURFACE = "#111C33"
BORDER = "#1E293B"
FG = "#F8FAFC"
MUTED = "#94A3B8"
ACCENT = "#22C55E"
SANS = "'Space Grotesk','Segoe UI',system-ui,-apple-system,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

# Lucide icon paths (ISC licence), drawn at 24x24
ICONS = {
    "card": '<rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/>',
    "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "chart": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "book": '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>',
}

CARDS = [
    ("digital-loyalty-card", "card", "Digital Loyalty Card", "digitalloyaltycard.io",
     ["Apple &amp; Google Wallet loyalty cards for shops,", "cafés and restaurants. No app download."],
     ["Laravel", "Wallet passes", "SaaS"]),
    ("healthyme", "heart", "HealthyMe", "healthyme.fit",
     ["Blood pressure &amp; glucose tracker. Log a", "reading in seconds, no Bluetooth needed."],
     ["Laravel", "PWA", "Health"]),
    ("gmb-planet", "pin", "GMB Planet", "gmbplanet.com",
     ["Google Business Profile management and", "local SEO for small businesses."],
     ["Local SEO", "GBP", "SaaS"]),
    ("seo-planet", "chart", "SEO Planet", "github.com/maxpaldigi/seo-planet",
     ["An affordable, SEMrush-style SEO platform", "for agencies and small teams."],
     ["Laravel", "React", "Open source"]),
    ("monetization-checker", "shield", "AdSense Eligibility Checker", "WordPress plugin",
     ["Scores your site on 12 approval factors", "before you apply. Runs 100% locally."],
     ["WordPress", "PHP", "Open source"]),
    ("laravel-saas-playbook", "book", "Laravel SaaS Playbook", "github.com/maxpaldigi/laravel-saas-playbook",
     ["Bite-sized, production-tested tips from", "building real Laravel SaaS products."],
     ["Laravel", "Tips", "Open source"]),
]


def chip_row(chips, x, y):
    out, cx = [], x
    for c in chips:
        w = 16 + len(c.replace("&amp;", "&")) * 7.6
        out.append(
            f'<rect x="{cx}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="{BORDER}"/>'
            f'<text x="{cx + w / 2:.0f}" y="{y + 17.5}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="12.5" fill="{MUTED}">{c}</text>'
        )
        cx += w + 8
    return "".join(out)


def card(icon, title, sub, desc, chips):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="230" viewBox="0 0 600 230" role="img" aria-label="{title}: {' '.join(desc)}">
<title>{title}</title>
<rect x="1" y="1" width="598" height="228" rx="16" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>
<rect x="28" y="28" width="56" height="56" rx="14" fill="{ACCENT}" fill-opacity="0.12"/>
<g transform="translate(40 40)" fill="none" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[icon]}</g>
<text x="104" y="54" font-family="{SANS}" font-size="25" font-weight="700" fill="{FG}">{title}</text>
<text x="104" y="78" font-family="{MONO}" font-size="13.5" fill="{ACCENT}">{sub}</text>
<text font-family="{SANS}" font-size="16.5" fill="{MUTED}"><tspan x="28" y="122">{desc[0]}</tspan><tspan x="28" y="146">{desc[1]}</tspan></text>
{chip_row(chips, 28, 176)}
<g transform="translate(552 32)" fill="none" stroke="{MUTED}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17 17 7"/><path d="M7 7h10v10"/></g>
</svg>
'''


def hero():
    lines = [
        ("cmd", "whoami"),
        ("big", "Max Pal"),
        ("out", "Founder @ Digigurkhas &amp; Byte Media · UK / Portugal"),
        ("cmd", "cat focus.txt"),
        ("out", "SaaS for local businesses: wallet loyalty, local SEO, health tracking"),
        ("cmd", "echo $STACK"),
        ("acc", "Laravel  ·  React  ·  TypeScript  ·  WordPress  ·  PostgreSQL"),
    ]
    y, rows, delay = 118, [], 0.0
    for kind, text in lines:
        if kind == "cmd":
            y += 12
            rows.append(f'<g class="l" style="animation-delay:{delay:.1f}s"><text x="48" y="{y}" font-family="{MONO}" font-size="18" fill="{ACCENT}">$</text>'
                        f'<text x="70" y="{y}" font-family="{MONO}" font-size="18" fill="{FG}">{text}</text></g>')
            y += 34
        elif kind == "big":
            y += 12
            rows.append(f'<text class="l" style="animation-delay:{delay:.1f}s" x="48" y="{y}" font-family="{SANS}" font-size="46" font-weight="700" fill="{FG}">{text}</text>')
            y += 34
        else:
            fill = ACCENT if kind == "acc" else MUTED
            rows.append(f'<text class="l" style="animation-delay:{delay:.1f}s" x="48" y="{y}" font-family="{MONO}" font-size="17" fill="{fill}">{text}</text>')
            y += 34
        delay += 0.35
    cursor_y = y + 12
    height = cursor_y + 40
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-label="Max Pal. Founder at Digigurkhas and Byte Media, UK and Portugal. Building SaaS for local businesses with Laravel, React, TypeScript, WordPress and PostgreSQL.">
<title>Max Pal</title>
<style>
.l{{opacity:0;animation:in .4s ease-out forwards}}
.c{{animation:blink 1.1s steps(1) infinite {delay:.1f}s;opacity:0}}
@keyframes in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.l{{animation:none;opacity:1}}.c{{animation:none;opacity:1}}}}
</style>
<rect x="1" y="1" width="1198" height="{height - 2}" rx="18" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>
<path d="M1 19a18 18 0 0 1 18-18h1162a18 18 0 0 1 18 18v33H1z" fill="{SURFACE}"/>
<line x1="1" y1="52" x2="1199" y2="52" stroke="{BORDER}" stroke-width="2"/>
<circle cx="32" cy="27" r="7" fill="#EF4444"/><circle cx="56" cy="27" r="7" fill="#F59E0B"/><circle cx="80" cy="27" r="7" fill="{ACCENT}"/>
<text x="600" y="32" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{MUTED}">max@digigurkhas: ~</text>
{"".join(rows)}
<g><text x="48" y="{cursor_y}" font-family="{MONO}" font-size="18" fill="{ACCENT}">$</text><rect class="c" x="70" y="{cursor_y - 16}" width="11" height="20" fill="{FG}"/></g>
</svg>
'''


def gql(query, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]


def stats(token):
    d = gql(f'''{{user(login:"{USER}"){{
      contributionsCollection{{contributionCalendar{{totalContributions}} totalCommitContributions restrictedContributionsCount}}
      pullRequests(states:MERGED){{totalCount}}
      repositories(ownerAffiliations:OWNER, privacy:PUBLIC){{totalCount}}
      followers{{totalCount}}
    }}}}''', token)["user"]
    c = d["contributionsCollection"]
    items = [
        ("Contributions", c["contributionCalendar"]["totalContributions"], "last 12 months"),
        ("Commits", c["totalCommitContributions"] + c["restrictedContributionsCount"], "incl. private"),
        ("Merged PRs", d["pullRequests"]["totalCount"], "all time"),
        ("Public repos", d["repositories"]["totalCount"], "and counting"),
    ]
    cells = []
    for i, (label, value, note) in enumerate(items):
        x = 28 + i * 286
        cells.append(
            f'<rect x="{x}" y="28" width="266" height="124" rx="12" fill="{SURFACE}" stroke="{BORDER}" stroke-width="1.5"/>'
            f'<text x="{x + 22}" y="62" font-family="{MONO}" font-size="13" fill="{MUTED}">{escape(label.upper())}</text>'
            f'<text x="{x + 22}" y="112" font-family="{SANS}" font-size="44" font-weight="700" fill="{FG}">{value:,}</text>'
            f'<text x="{x + 22}" y="136" font-family="{MONO}" font-size="12.5" fill="{ACCENT}">{note}</text>'
        )
    label = ", ".join(f"{l}: {v}" for l, v, _ in items)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="180" viewBox="0 0 1200 180" role="img" aria-label="GitHub stats. {label}">
<title>GitHub stats</title>
<rect x="1" y="1" width="1198" height="178" rx="16" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>
{"".join(cells)}
</svg>
'''


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "hero.svg").write_text(hero())
    for slug, icon, title, sub, desc, chips in CARDS:
        (OUT / f"card-{slug}.svg").write_text(card(icon, title, sub, desc, chips))
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        (OUT / "stats.svg").write_text(stats(token))
    print("built", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
