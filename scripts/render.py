"""Render the profile README card (dark + light) in the style of pscl.dev.

Age and service uptimes are computed at render time; the daily workflow re-runs
this script and commits only when the output changes.
"""
import base64
import datetime as dt
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets'
ICONS = OUT / 'icons'

BORN = dt.date(2000, 10, 25)
STACK = 'TypeScript · Go · Nuxt · NestJS'
FOCUS = 'side projects, self-hosting, cycling & the outdoors'
UNITS = [
    ('side-projects', 'Side Projects', dt.date(2018, 5, 18)),
    ('self-hosting', 'Self-Hosting', dt.date(2020, 2, 2)),
    ('cycling', 'Cycling', dt.date(2025, 5, 12)),
    ('outdoors', 'Outdoors', dt.date(2021, 3, 26)),
]
TREE = [
    ('languages', [('typescript', 'TypeScript'), ('go', 'Go'), ('csharp', 'C#')]),
    ('frameworks', [('nuxtjs', 'Nuxt.js'), ('nestjs', 'NestJS'), ('tailwindcss', 'Tailwind')]),
    ('tools', [('apple', 'macOS'), ('postgresql', 'PostgreSQL'), ('docker', 'Docker'), ('claude', 'Claude Code')]),
]
ASCII = """\
██████  ███████  ██████  ██
██   ██ ██      ██       ██
██████  ███████ ██       ██
██           ██ ██       ██
██      ███████  ██████  ███████"""

# same tokens as pscl.dev/assets/style.css
THEMES = {
    'dark': dict(bg='#0a0c10', bg2='#0e1117', bg3='#151a22', fg='#c9d1d9', dim='#b8c1cc', faint='#8b95a4',
                 line='#1e252f', accent='#00dc82', accent2='#b07bff', warn='#ffb86b', grid=.2, dark=True),
    'light': dict(bg='#f6f4ee', bg2='#fffdf7', bg3='#efece3', fg='#1f2328', dim='#5b6472', faint='#6f7887',
                  line='#e0dbd0', accent='#0a8f58', accent2='#6715db', warn='#b26a00', grid=.3, dark=False),
}

W = 880
G = 34          # background grid pitch
FS = 14         # body font size
CW = FS * .6    # monospace advance
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"


def months_since(d, today):
    return (today.year - d.year) * 12 + today.month - d.month - (today.day < d.day)


def uptime(d, today):
    mo = months_since(d, today)
    return (f'{mo // 12}y ' if mo >= 12 else '') + f'{mo % 12}mo'


def icon(name, t):
    src = (ICONS / f'{name}.svg').read_text()
    if name == 'apple' and t['dark']:
        src = src.replace('<path ', f'<path fill="{t["fg"]}" ', 1)
    return 'data:image/svg+xml;base64,' + base64.b64encode(src.encode()).decode()


def canvas(t, h, body):
    """Rounded background with the dot grid and a few packets routed along the grid lines."""
    packets = [
        (f'M0 {G*2} H{G*9} V{G*5} H{W}', t['accent'], 11),
        (f'M{G*23} {h} V{G*3} H{G*14} V0', t['accent2'], 14),
        (f'M{W} {G*7} H{G*19} V{h}', t['accent'], 9),
        (f'M{G*4} {h} V{G*8} H0', t['warn'], 12),
        (f'M0 {G*13} H{G*12} V{G*17} H{W}', t['accent2'], 13),
        (f'M{W} {G*20} H{G*8} V0', t['accent'], 15),
    ]
    trail = []
    glow = ' filter="url(#glow)"'
    for path, c, dur in packets:
        for i in range(8):
            trail.append(
                f'<rect x="-1.75" y="-1.75" width="3.5" height="3.5" fill="{c}" opacity="{(.9 if t["dark"] else .7) * (1 - i / 8):.2f}"'
                f'{glow if i == 0 else ""}>'
                f'<animateMotion path="{path}" dur="{dur}s" begin="-{i * .09 + dur * .37:.2f}s" repeatCount="indefinite"/></rect>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" font-family="{MONO}" font-size="{FS}">
<defs>
  <pattern id="grid" width="{G}" height="{G}" patternUnits="userSpaceOnUse"><rect x="-.7" y="-.7" width="1.4" height="1.4" fill="{t['faint']}" opacity="{t['grid']}"/><rect x="{G - .7}" y="-.7" width="1.4" height="1.4" fill="{t['faint']}" opacity="{t['grid']}"/><rect x="-.7" y="{G - .7}" width="1.4" height="1.4" fill="{t['faint']}" opacity="{t['grid']}"/></pattern>
  <filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="{3 if t['dark'] else 1.5}"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="frame"><rect width="{W}" height="{h}" rx="12"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{h}" fill="{t['bg']}"/>
  <rect width="{W}" height="{h}" fill="url(#grid)"/>
  {''.join(trail)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="12" fill="none" stroke="{t['line']}"/>
{body}
</svg>
'''


def hero(t, today):
    age = today.year - BORN.year - ((today.month, today.day) < (BORN.month, BORN.day))
    x0, y0, w = 36, 36, W - 72
    px, cell_w, cell_h = x0 + 30, 9, 15
    ay = y0 + 36 + 30

    blocks = ''.join(
        f'<rect x="{px + c * cell_w}" y="{ay + r * cell_h}" width="{cell_w + .3}" height="{cell_h + .3}"/>'
        for r, row in enumerate(ASCII.splitlines()) for c, ch in enumerate(row) if ch == '█')
    if t['dark']:
        ascii_art = (f'<g fill="{t["accent"]}" opacity=".45" filter="url(#bloom)">{blocks}</g>'
                     f'<g fill="{t["accent"]}">{blocks}</g>')
    else:  # paper: a hard, slightly misregistered print offset instead of a glow
        ascii_art = (f'<g fill="{t["accent2"]}" opacity=".22" transform="translate(3 3)">{blocks}</g>'
                     f'<g fill="{t["accent"]}">{blocks}</g>')

    py = ay + 5 * cell_h + 42
    cmd = 'whoami --verbose'
    cx = px + CW * 20
    # SMIL starts at 0s and holds the empty prompt for a beat; the base attribute values are the final
    # state, so a renderer without animation still shows the full card
    steps = [0] * 9 + list(range(len(cmd) + 1))
    typing = len(steps) * .07
    widths = ';'.join(f'{i * CW:.1f}' for i in steps)
    xs = ';'.join(f'{cx + i * CW:.1f}' for i in steps)
    oy = py + 32
    kv = [('stack', STACK, t['fg']), ('focus', FOCUS, t['fg']), ('status', None, None)]
    kv_svg = ''
    for i, (k, v, c) in enumerate(kv):
        y = oy + 36 + i * 25
        val = (f'<tspan fill="{t["accent"]}">● available</tspan><tspan fill="{t["fg"]}"> for interesting problems</tspan>'
               if v is None else f'<tspan fill="{c}">{escape(v)}</tspan>')
        kv_svg += (f'<text x="{px}" y="{y}" fill="{t["faint"]}">{k}</text>'
                   f'<text x="{px + CW * 8}" y="{y}">{val}</text>')
    foot = oy + 36 + 2 * 25 + 34
    h = foot + 46 + y0

    body = f'''<defs>
  <filter id="bloom" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
  <clipPath id="typed"><rect x="{cx}" y="{py - 16}" height="22" width="{len(cmd) * CW + 2:.1f}"><animate attributeName="width" values="{widths}" calcMode="discrete" dur="{typing:.2f}s" fill="freeze"/></rect></clipPath>
</defs>
<rect x="{x0 + .5}" y="{y0 + .5}" width="{w - 1}" height="{h - 2 * y0 - 1}" rx="10" fill="{t['bg2']}" stroke="{t['line']}"/>
<path d="M{x0 + .5} {y0 + 36} V{y0 + 10.5} a10 10 0 0 1 10 -10 H{x0 + w - 10.5} a10 10 0 0 1 10 10 V{y0 + 36} Z" fill="{t['bg3']}"/>
<line x1="{x0 + 1}" x2="{x0 + w - 1}" y1="{y0 + 36.5}" y2="{y0 + 36.5}" stroke="{t['line']}"/>
<circle cx="{x0 + 20}" cy="{y0 + 18}" r="5.5" fill="#ff5f57"/><circle cx="{x0 + 38}" cy="{y0 + 18}" r="5.5" fill="#febc2e"/><circle cx="{x0 + 56}" cy="{y0 + 18}" r="5.5" fill="#28c840"/>
<text x="{x0 + 76}" y="{y0 + 22.5}" font-size="12.5" fill="{t['faint']}">pascal@basecamp — zsh — 92×28</text>
{ascii_art}
<text x="{px}" y="{py}" font-weight="500"><tspan fill="{t['accent2']}">pascal@basecamp </tspan><tspan fill="{t['warn']}">~</tspan><tspan fill="{t['accent2']}"> ❯</tspan></text>
<text x="{cx}" y="{py}" fill="{t['fg']}" clip-path="url(#typed)">{cmd}</text>
<rect x="{cx + len(cmd) * CW:.1f}" y="{py - 12}" width="{CW}" height="{FS * 1.05:.1f}" fill="{t['accent']}">
  <animate attributeName="x" values="{xs}" calcMode="discrete" dur="{typing:.2f}s" fill="freeze"/>
  <animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1.1s" repeatCount="indefinite"/>
</rect>
<g>
  <animate attributeName="opacity" values="0;0;1" keyTimes="0;{(typing + .2) / (typing + .6):.3f};1" dur="{typing + .6:.2f}s" fill="freeze"/>
  <text x="{px}" y="{oy}"><tspan fill="{t['fg']}" font-weight="600">Pascal Johann</tspan><tspan fill="{t['dim']}"> — full-stack developer, {age} yrs, Germany</tspan></text>
  {kv_svg}
</g>
<line x1="{px}" x2="{x0 + w - 30}" y1="{foot}" y2="{foot}" stroke="{t['line']}" stroke-dasharray="4 4"/>
<text x="{px}" y="{foot + 26}" font-size="13" fill="{t['faint']}">more at <tspan fill="{t['accent']}">pscl.dev</tspan>  ·  say hi at <tspan fill="{t['dim']}">me@pscl.dev</tspan></text>'''
    return body, h


def cmdline(t, x, y, w, cmd, arg, flag, ret):
    return (f'<text x="{x}" y="{y}"><tspan fill="{t["accent"]}">❯ </tspan><tspan fill="{t["fg"]}">{cmd} </tspan>'
            f'<tspan fill="{t["fg"]}" font-weight="500" font-size="16">{arg}</tspan><tspan fill="{t["faint"]}"> {flag}</tspan></text>'
            f'<text x="{x + w}" y="{y}" text-anchor="end" font-size="12.5" fill="{t["faint"]}">{ret}</text>'
            f'<line x1="{x}" x2="{x + w}" y1="{y + 14.5}" y2="{y + 14.5}" stroke="{t["line"]}" stroke-dasharray="4 4"/>')


def panel(t, today):
    x0, y0 = 36, 36
    lx, lw = x0 + 30, 440
    rx, rw = lx + lw + 40, W - 2 * x0 - 30 - lw - 40 - 30
    top = y0 + 44

    cards, cy, ch = '', top + 40, 78
    for i, (slug, name, since) in enumerate(UNITS):
        y = cy + i * (ch + 12)
        dx = lx + 16 + CW * 8.5
        cards += f'''<rect x="{lx + .5}" y="{y + .5}" width="{lw - 1}" height="{ch - 1}" rx="8" fill="{t['bg2']}" stroke="{t['line']}"/>
<circle cx="{lx + 20}" cy="{y + 21}" r="4" fill="{t['accent']}"{' filter="url(#glow)"' if t['dark'] else ''}><animate attributeName="opacity" values="1;.35;1" dur="2.4s" begin="-{i * .6}s" repeatCount="indefinite"/></circle>
<text x="{lx + 32}" y="{y + 26}"><tspan fill="{t['fg']}" font-weight="500">{slug}.service</tspan><tspan fill="{t['faint']}"> — {name}</tspan></text>
<text x="{dx - CW}" y="{y + 47}" text-anchor="end" fill="{t['faint']}">Active:</text><text x="{dx}" y="{y + 47}" fill="{t['accent']}">active (running)</text>
<text x="{dx - CW}" y="{y + 67}" text-anchor="end" fill="{t['faint']}">Since:</text><text x="{dx}" y="{y + 67}" fill="{t['dim']}">{since.isoformat()} · {uptime(since, today)} ago</text>
'''
    left_h = 40 + len(UNITS) * (ch + 12) - 12

    tree, ty = '', top + 40 + 4
    files = 0
    for gi, (node, leaves) in enumerate(TREE):
        last_node = gi == len(TREE) - 1
        tree += f'<text x="{rx}" y="{ty + 14}" fill="{t["warn"]}">{"└" if last_node else "├"}── {node}/</text>'
        ty += 24
        for li, (ic, label) in enumerate(leaves):
            pipe = ('    ' if last_node else '│   ') + ('└──' if li == len(leaves) - 1 else '├──')
            tree += (f'<text x="{rx}" y="{ty + 14}" fill="{t["faint"]}" xml:space="preserve">{pipe}</text>'
                     f'<image x="{rx + CW * 7.6:.1f}" y="{ty + 2}" width="15" height="15" href="{icon(ic, t)}"/>'
                     f'<text x="{rx + CW * 7.6 + 23:.1f}" y="{ty + 14}" fill="{t["fg"]}">{label}</text>')
            ty += 24
            files += 1
        ty += 12

    h = top + max(left_h, ty - top) + 30 + y0
    body = f'''<rect x="{x0 + .5}" y="{y0 + .5}" width="{W - 2 * x0 - 1}" height="{h - 2 * y0 - 1}" rx="12" fill="{t['bg']}" stroke="{t['line']}"/>
{cmdline(t, lx, top, lw, 'systemctl', 'status', '--user', f'{len(UNITS)} units · all running')}
{cards}
{cmdline(t, rx, top, rw, 'tree', '~/.stack', '', f'{len(TREE)} dirs, {files} files')}
{tree}'''
    return body, h


def main():
    today = dt.date.today()
    for name, t in THEMES.items():
        top, top_h = hero(t, today)
        bottom, bottom_h = panel(t, today)
        dy = top_h - 44  # the panel's own top margin shrinks to a 28px gap below the window
        body = f'{top}\n<g transform="translate(0 {dy})">\n{bottom}\n</g>'
        (OUT / f'profile-{name}.svg').write_text(canvas(t, dy + bottom_h, body))


if __name__ == '__main__':
    main()
