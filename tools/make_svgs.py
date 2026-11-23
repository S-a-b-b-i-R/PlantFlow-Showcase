"""Builds the animated SVGs for the README, one light and one dark copy of each.

    python tools/make_svgs.py

Animations are SMIL, which GitHub renders inside <img>. No scripts, no web fonts.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

THEMES = {
    "light": dict(bg="#f2f3f0", fg="#1b2a31", muted="#556268", border="#c6cbc5",
                  track="#d5d9d4", signal="#f4c20d", ok="#2f7d5c", late="#a8392b", ink="#1b2a31"),
    "dark": dict(bg="#1a2328", fg="#e6e9e5", muted="#93a0a5", border="#2b383f",
                 track="#33424a", signal="#f4c20d", ok="#4fb58a", late="#e0705f", ink="#1b2a31"),
}


def f(x):
    return f"{x:.4f}".rstrip("0").rstrip(".")


def steps(dur, changes, attr="opacity"):
    """A value that jumps at given seconds: changes = [(0, a), (t1, b), ...]."""
    times = ";".join(f(t / dur) for t, _ in changes)
    values = ";".join(str(v) for _, v in changes)
    return (f'<animate attributeName="{attr}" values="{values}" keyTimes="{times}" '
            f'calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>')


def glide(dur, points, attr):
    """A value that moves linearly between (seconds, value) points."""
    if points[0][0] > 0:
        points = [(0, points[0][1])] + points
    if points[-1][0] < dur:
        points = points + [(dur, points[-1][1])]
    times = ";".join(f(t / dur) for t, _ in points)
    values = ";".join(str(v) for _, v in points)
    return (f'<animate attributeName="{attr}" values="{values}" keyTimes="{times}" '
            f'dur="{dur}s" repeatCount="indefinite"/>')


def shown(dur, start, end):
    """Visible from start to end seconds, hidden otherwise."""
    changes = [(0, 0)] if start > 0 else []
    changes.append((start, 1))
    if end < dur:
        changes.append((end, 0))
    return steps(dur, changes)


def svg(w, h, c, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}" role="img" aria-label="{title}">\n<title>{title}</title>\n'
            f'<rect width="{w}" height="{h}" rx="14" fill="{c["bg"]}" stroke="{c["border"]}"/>\n{body}\n</svg>\n')


# 1. Banner: a mixer truck runs an order through the whole flow.
def hero(c):
    w, h, dur = 1200, 330, 11.0
    stations = [("Order", "lines, VAT, charges"), ("Approve", "floor price checked"),
                ("Plan", "pours, pumps, crews"), ("Batch", "one tap per step"),
                ("Deliver", "poured minus returned"), ("Invoice", "PDF, Mushak 6.3")]
    x0, x1, y = 110, 1090, 246
    xs = [x0 + i * (x1 - x0) / (len(stations) - 1) for i in range(len(stations))]
    stay, move = 0.7, 1.0
    arrive = [i * (stay + move) for i in range(len(xs))]
    leave = [a + stay for a in arrive]
    route = []
    for i, x in enumerate(xs):
        route += [(arrive[i], f(x)), (leave[i], f(x))]

    parts = [
        f'<rect x="56" y="58" width="14" height="52" rx="3" fill="{c["signal"]}"/>',
        f'<text x="86" y="100" font-size="50" font-weight="800" fill="{c["fg"]}" letter-spacing="-1">PlantFlow</text>',
        f'<text x="58" y="142" font-size="21" fill="{c["muted"]}">Operations software for ready-mix concrete companies, '
        f'from the first quote to the invoice.</text>',
        f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{c["track"]}" stroke-width="6" stroke-linecap="round"/>',
        f'<line x1="{x0}" y1="{y}" x2="{x0}" y2="{y}" stroke="{c["ok"]}" stroke-width="6" stroke-linecap="round">'
        f'{glide(dur, route, "x2")}</line>',
    ]
    for i, (x, (name, note)) in enumerate(zip(xs, stations)):
        fill = [(0, c["bg"])] if arrive[i] > 0 else []
        fill += [(arrive[i], c["signal"]), (leave[i] if i < len(xs) - 1 else leave[i] + 0.6, c["ok"])]
        parts += [
            f'<circle cx="{f(x)}" cy="{y}" r="11" fill="{c["bg"]}" stroke="{c["fg"]}" stroke-width="3">'
            f'{steps(dur, fill, "fill")}</circle>',
            f'<text x="{f(x)}" y="{y + 42}" text-anchor="middle" font-size="19" font-weight="700" fill="{c["fg"]}">{name}</text>',
            f'<text x="{f(x)}" y="{y + 66}" text-anchor="middle" font-size="15" fill="{c["muted"]}">{note}</text>',
        ]
    # The truck faces right: drum behind, cab in front. Its origin sits over the station.
    truck = f'''<g>
  <animateTransform attributeName="transform" type="translate" values="{";".join(f"{v},{y - 22}" for _, v in route)};{f(xs[-1])},{y - 22}"
    keyTimes="{";".join(f(t / dur) for t, _ in route)};1" dur="{dur}s" repeatCount="indefinite"/>
  <rect x="-52" y="-12" width="92" height="7" rx="2" fill="{c["fg"]}"/>
  <g transform="rotate(-10 -16 -30)">
    <ellipse cx="-16" cy="-30" rx="31" ry="17" fill="{c["signal"]}" stroke="{c["fg"]}" stroke-width="2.5"/>
    <line x1="-44" y1="-30" x2="12" y2="-30" stroke="{c["ink"]}" stroke-width="3" stroke-dasharray="7 7">
      <animate attributeName="stroke-dashoffset" values="0;-28" dur="0.7s" repeatCount="indefinite"/></line>
  </g>
  <path d="M18 -12 V-42 H33 L42 -27 V-12 Z" fill="{c["fg"]}"/>
  <path d="M22 -38 H31 L37 -28 H22 Z" fill="{c["bg"]}"/>
  <circle cx="-38" cy="-4" r="7.5" fill="{c["fg"]}"/><circle cx="-38" cy="-4" r="2.5" fill="{c["bg"]}"/>
  <circle cx="-18" cy="-4" r="7.5" fill="{c["fg"]}"/><circle cx="-18" cy="-4" r="2.5" fill="{c["bg"]}"/>
  <circle cx="30" cy="-4" r="7.5" fill="{c["fg"]}"/><circle cx="30" cy="-4" r="2.5" fill="{c["bg"]}"/>
</g>'''
    parts.append(truck)
    return svg(w, h, c, "\n".join(parts), "PlantFlow: an order moves from order to approval, plan, batching, delivery and invoice")


# 2. One load on the live board: plan rings, actual dots, a late step, and the next button changing.
def load_cycle(c):
    w, h = 1200, 410
    sweep, dur = 10.0, 12.5
    t0, t1 = 8 * 60 + 55, 10 * 60 + 55  # minutes since midnight shown on the axis
    gx0, gx1 = 300, 1150
    late_after = 15

    def x(m):
        return gx0 + (m - t0) * (gx1 - gx0) / (t1 - t0)

    def at(m):  # seconds into the loop when Now reaches minute m
        return (m - t0) / (t1 - t0) * sweep

    def hm(m):
        return f"{m // 60:02d}:{m % 60:02d}"

    rows = [("Load made", 540, 540, "Send out"), ("Sent out", 545, 547, "Truck arrived"),
            ("Arrived on site", 575, 596, "Pouring started"), ("Pouring started", 590, 601, "Pouring ended"),
            ("Pouring ended", 610, 618, "Truck is back"), ("Back at plant", 645, 648, None)]
    top, gap = 128, 40

    parts = [
        f'<text x="40" y="54" font-size="25" font-weight="800" fill="{c["fg"]}">One load, from plant to pour and back</text>',
        f'<text x="40" y="84" font-size="16" fill="{c["muted"]}">A ring is the plan, a dot is what happened. '
        f'More than {late_after} minutes behind plan turns red.</text>',
    ]
    for m in range(9 * 60, t1 + 1, 30):
        parts += [f'<line x1="{f(x(m))}" y1="{top - 18}" x2="{f(x(m))}" y2="{top + gap * 5 + 18}" stroke="{c["track"]}" stroke-width="1.5"/>',
                  f'<text x="{f(x(m))}" y="{top + gap * 5 + 42}" text-anchor="middle" font-size="14" fill="{c["muted"]}">{hm(m)}</text>']

    for i, (name, plan, actual, _) in enumerate(rows):
        y = top + i * gap
        late_at = plan + late_after
        is_late = actual - plan > late_after
        colour = [(0, c["ok"])] + ([(at(late_at), c["late"])] if is_late else [])
        line_end = [(at(plan), f(x(plan))), (at(actual), f(x(actual)))]
        dash = [(0, "5 5"), (at(actual), "none")]
        parts += [
            f'<text x="40" y="{y + 6}" font-size="17" font-weight="600" fill="{c["fg"]}">{name}</text>',
            f'<line x1="{f(x(plan))}" y1="{y}" x2="{f(x(plan))}" y2="{y}" stroke="{c["ok"]}" stroke-width="4" stroke-linecap="round">'
            f'{glide(dur, line_end, "x2")}{steps(dur, colour, "stroke")}{steps(dur, dash, "stroke-dasharray")}</line>',
            f'<circle cx="{f(x(plan))}" cy="{y}" r="8" fill="{c["bg"]}" stroke="{c["muted"]}" stroke-width="2.5"/>',
            f'<circle cx="{f(x(actual))}" cy="{y}" r="7" fill="{c["late"] if is_late else c["ok"]}" opacity="0">'
            f'{shown(dur, at(actual), dur)}</circle>',
            f'<text x="200" y="{y + 6}" font-size="15" fill="{c["late"] if is_late else c["muted"]}" '
            f'font-weight="{700 if is_late else 400}" opacity="0">{hm(actual)}{f" · {actual - plan} min late" if is_late else ""}'
            f'{shown(dur, at(actual), dur)}</text>',
        ]

    # The Now marker sweeps across the shift.
    ny0, ny1 = top - 30, top + gap * 5 + 20
    parts.append(f'''<g>
  <animateTransform attributeName="transform" type="translate" values="{f(x(t0))},0;{f(x(t1))},0;{f(x(t1))},0"
    keyTimes="0;{f(sweep / dur)};1" dur="{dur}s" repeatCount="indefinite"/>
  <line x1="0" y1="{ny0}" x2="0" y2="{ny1}" stroke="{c["fg"]}" stroke-width="2" stroke-dasharray="3 4"/>
  <rect x="-24" y="{ny0 - 22}" width="48" height="22" rx="4" fill="{c["fg"]}"/>
  <text x="0" y="{ny0 - 6}" text-anchor="middle" font-size="13" font-weight="700" fill="{c["bg"]}">Now</text>
</g>''')

    # The batching console's next action: the only yellow thing on screen.
    bx, by = 860, 30
    labels = [(0, "Make load")] + [(at(actual), nxt or "Done") for _, _, actual, nxt in rows]
    parts.append(f'<text x="{bx - 14}" y="{by + 30}" text-anchor="end" font-size="15" fill="{c["muted"]}">Next on the console</text>')
    parts.append(f'<rect x="{bx}" y="{by}" width="300" height="48" rx="8" fill="{c["signal"]}">'
                 f'{steps(dur, [(0, c["signal"]), (at(rows[-1][2]), c["ok"])], "fill")}</rect>')
    for k, (start, text) in enumerate(labels):
        end = labels[k + 1][0] if k + 1 < len(labels) else dur
        colour = c["ink"] if text != "Done" else "#ffffff"
        parts.append(f'<text x="{bx + 150}" y="{by + 31}" text-anchor="middle" font-size="19" font-weight="700" '
                     f'fill="{colour}" opacity="0">{text}{shown(dur, start, end)}</text>')
    return svg(w, h, c, "\n".join(parts), "A load's steps on the live board: planned against actual time, with one late arrival")


# 3. Three requests meet the API's guards: one served, one refused by permission, one by company isolation.
def architecture(c):
    w, h, dur = 1200, 400, 14.6
    boxes = [("React app", "Google sign-in", 40), (".NET 10 API", "checks the Firebase token", 270),
             ("Permissions", "deny beats grant", 500), ("Company filter", "one rule, every query", 730),
             ("SQL Server", "shared database", 960)]
    bw, by, bh = 200, 150, 84
    cy = by + bh / 2
    scenes = [
        dict(start=0.0, stop=5.2, to=960, back=True, code="200 OK", tone="ok",
             text="A dispatcher at Company A opens one of their orders."),
        dict(start=5.5, stop=9.7, to=500, back=False, code="403", tone="late",
             text="A sales rep without the billing permission tries to issue an invoice."),
        dict(start=10.0, stop=14.2, to=730, back=False, code="404", tone="late",
             text="Someone at Company B guesses the id of Company A's order. To them it doesn't exist."),
    ]

    parts = [f'<text x="40" y="54" font-size="25" font-weight="800" fill="{c["fg"]}">Every request passes the same guards</text>',
             f'<text x="40" y="84" font-size="16" fill="{c["muted"]}">Access is decided by the API in one place, '
             f'never by the screen and never per controller.</text>']
    for i, (name, note, bx) in enumerate(boxes):
        stroke = [(0, c["border"])]
        for s in scenes:
            if not s["back"] and s["to"] == bx:
                hit = s["start"] + 1.9
                stroke += [(hit, c["late"]), (s["stop"], c["border"])]
        parts += [
            f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="3">'
            f'{steps(dur, stroke, "stroke")}</rect>',
            f'<text x="{bx + bw / 2}" y="{by + 36}" text-anchor="middle" font-size="19" font-weight="700" fill="{c["fg"]}">{name}</text>',
            f'<text x="{bx + bw / 2}" y="{by + 62}" text-anchor="middle" font-size="14" fill="{c["muted"]}">{note}</text>',
        ]
        if i < len(boxes) - 1:
            ax0, ax1 = bx + bw + 4, boxes[i + 1][2] - 6
            parts.append(f'<path d="M{ax0} {cy} H{ax1} m-8 -6 l8 6 l-8 6" fill="none" stroke="{c["muted"]}" stroke-width="2"/>')

    for s in scenes:
        start, stop, tone = s["start"], s["stop"], c[s["tone"]]
        fly = 1.6 * (s["to"] - 240) / 720 if s["back"] else 1.6
        target = s["to"] - 12 if not s["back"] else s["to"] + 30
        badge = 140 if s["back"] else s["to"] + bw / 2
        path = [(start, 240), (start + 0.3, 240), (start + 0.3 + fly, target)]
        if s["back"]:
            path += [(start + 0.6 + fly, target), (start + 0.6 + 2 * fly, 240)]
        path += [(stop, path[-1][1])]
        arrived = path[-2][0]
        parts += [
            f'<circle cx="240" cy="{cy}" r="10" fill="{c["signal"]}" stroke="{c["fg"]}" stroke-width="2" opacity="0">'
            f'{glide(dur, [(t, f(v)) for t, v in path], "cx")}{shown(dur, start, stop)}'
            f'{steps(dur, [(0, c["signal"]), (arrived, tone)], "fill")}</circle>',
            f'<g opacity="0">{shown(dur, arrived, stop)}'
            f'<rect x="{badge - 52}" y="{by - 46}" width="104" height="30" rx="6" fill="{tone}"/>'
            f'<text x="{badge}" y="{by - 25}" text-anchor="middle" font-size="16" font-weight="700" fill="#ffffff">{s["code"]}</text></g>',
            f'<text x="40" y="{by + bh + 72}" font-size="18" fill="{c["fg"]}" opacity="0">{s["text"]}{shown(dur, start, stop)}</text>',
        ]
    parts.append(f'<text x="40" y="{by + bh + 108}" font-size="15" fill="{c["muted"]}">Each refusal is covered by an '
                 f'integration test against a real SQL Server.</text>')
    return svg(w, h, c, "\n".join(parts), "Three requests: one served, one refused by permissions, one refused by company isolation")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, build in [("hero", hero), ("load-cycle", load_cycle), ("guards", architecture)]:
        for theme, colours in THEMES.items():
            (OUT / f"{name}-{theme}.svg").write_text(build(colours), encoding="utf-8")
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("*.svg"))))
