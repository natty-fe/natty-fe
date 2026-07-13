import html

FONT = "SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
FONT_SIZE = 13
CHAR_W = FONT_SIZE * 0.6
LINE_H = FONT_SIZE * 1.35

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "text": "#c9d1d9",
        "accent": "#79c0ff",
        "label": "#ffa657",
        "value": "#a5d6ff",
        "ascii": "#58a6ff",
    },
    "light": {
        "bg": "#ffffff",
        "border": "#d0d7de",
        "text": "#24292f",
        "accent": "#0969da",
        "label": "#953800",
        "value": "#0969da",
        "ascii": "#0969da",
    },
}

def esc(s):
    return html.escape(str(s), quote=True)

def render_card(ascii_lines, stat_lines, theme="dark", title="andrew@grant"):
    t = THEMES[theme]
    has_ascii = bool(ascii_lines)
    ascii_w = max((len(l) for l in ascii_lines), default=0)
    left_px_w = ascii_w * CHAR_W
    left_col_x = 24
    right_col_x = (left_col_x + left_px_w + 40) if has_ascii else left_col_x

    rows = max(len(ascii_lines), len(stat_lines))
    height = int((rows + 3) * LINE_H + 40)
    width = int(right_col_x + 560)

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    svg.append(f'<rect width="100%" height="100%" rx="12" fill="{t["bg"]}" stroke="{t["border"]}" stroke-width="1"/>')
    svg.append(f'<text x="24" y="34" font-family="{FONT}" font-size="{FONT_SIZE+2}" fill="{t["accent"]}" font-weight="bold">{esc(title)}</text>')
    svg.append(f'<line x1="24" y1="46" x2="{width-24}" y2="46" stroke="{t["border"]}" stroke-width="1"/>')

    y0 = 46 + LINE_H
    svg.append(f'<g font-family="{FONT}" font-size="{FONT_SIZE}" xml:space="preserve">')

    for i, line in enumerate(ascii_lines):
        y = y0 + i * LINE_H
        svg.append(f'<text x="{left_col_x}" y="{y:.1f}" fill="{t["ascii"]}">{esc(line)}</text>')

    for i, line in enumerate(stat_lines):
        y = y0 + i * LINE_H
        if line is None:
            continue
        if line.startswith("---"):
            svg.append(f'<text x="{right_col_x}" y="{y:.1f}" fill="{t["border"]}">{esc(line)}</text>')
        elif ":" in line and not line.startswith(" "):
            label, _, value = line.partition(":")
            svg.append(
                f'<text x="{right_col_x}" y="{y:.1f}">'
                f'<tspan fill="{t["label"]}">{esc(label)}:</tspan>'
                f'<tspan fill="{t["value"]}">{esc(value)}</tspan>'
                f'</text>'
            )
        else:
            svg.append(f'<text x="{right_col_x}" y="{y:.1f}" fill="{t["text"]}">{esc(line)}</text>')

    svg.append('</g>')
    svg.append('</svg>')
    return "\n".join(svg)
