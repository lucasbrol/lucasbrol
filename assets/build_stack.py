"""Gera assets/stack.svg: o cartão "Tools & technologies" do perfil.

Os logos são baixados (devicon, MIT; simple-icons, CC0) e embutidos em base64,
porque um SVG exibido como <img> no GitHub não carrega recursos externos.

Para adicionar uma ferramenta, edite SECTIONS e rode:
    python assets/build_stack.py
"""

import base64
import pathlib
import urllib.request
from xml.sax.saxutils import escape

DEVICON = "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/{0}/{0}-{1}.svg"
SIMPLE = "https://cdn.simpleicons.org/{}"

# Projetos (cor do ponto embaixo de cada ferramenta).
PROJECTS = {
    "P": ("ParkFinder", "#a6e3a1"),
    "A": ("AlphaPulse", "#89b4fa"),
    "L": ("Leukemia", "#f38ba8"),
    "F": ("Portfolio", "#f9e2af"),
    "E": ("EventHub", "#fab387"),
    "D": ("E-commerce", "#cba6f7"),
    "U": ("Agenda UFV", "#94e2d5"),
    "R": ("RideFleet", "#74c7ec"),
}
# Só marca um projeto quando o repositório mostra a ferramenta em uso
# (planos futuros de um README não contam).


def dv(name, variant="original"):
    return DEVICON.format(name, variant)


def si(slug, color=None):
    return SIMPLE.format(slug + (f"/{color}" if color else ""))


# (título, subtítulo, cor, [(rótulo, url do logo, projetos)])
SECTIONS = [
    ("QA & Testing", "test design · bug reports · API & E2E automation", "#fab387", [
        ("Postman", dv("postman"), ""),
        ("Jira", dv("jira"), "E"),
        ("Playwright", dv("playwright"), "F"),
        ("Pytest", dv("pytest"), "PDR"),
        ("Vitest", dv("vitest"), "F"),
        ("Swagger", dv("swagger"), "PR"),
    ]),
    ("Languages", "", "#cba6f7", [
        ("Python", dv("python"), "PALDR"),
        ("TypeScript", dv("typescript"), "PF"),
        ("JavaScript", dv("javascript"), "UR"),
        ("C", dv("c"), ""),
        ("PHP", dv("php"), "U"),
        ("HTML5", dv("html5"), "DU"),
        ("CSS3", dv("css3"), "DU"),
    ]),
    ("AI & Machine Learning", "deep learning · NLP · computer vision · RAG", "#f38ba8", [
        ("PyTorch", dv("pytorch"), "AL"),
        ("Hugging Face", si("huggingface"), "A"),
        ("scikit-learn", dv("scikitlearn"), "AL"),
        ("pandas", si("pandas", "e70488"), "AL"),
        ("NumPy", dv("numpy"), "AL"),
        ("Matplotlib", dv("matplotlib"), "AL"),
        ("Jupyter", dv("jupyter"), "L"),
        ("Streamlit", dv("streamlit"), "A"),
        ("Gemini", si("googlegemini"), "F"),
        ("Kaggle", dv("kaggle"), "L"),
    ]),
    ("Back-end & Data", "REST APIs · async ORM · spatial queries with PostGIS", "#89b4fa", [
        ("FastAPI", dv("fastapi"), "PR"),
        ("Pydantic", si("pydantic"), "PR"),
        ("SQLAlchemy", si("sqlalchemy", "f38ba8"), "PR"),
        ("PostgreSQL", dv("postgresql"), "PR"),
        ("JWT", si("jsonwebtokens", "white"), "P"),
        ("SQLite", dv("sqlite"), "ADR"),
        ("MySQL", si("mysql", "6a9fd4"), "D"),
        ("Django", si("django", "44b78b"), "D"),
        ("Node.js", dv("nodejs"), ""),
        ("Redis", dv("redis"), "R"),
    ]),
    ("Mobile & Web", "", "#a6e3a1", [
        ("React Native", dv("react"), "P"),
        ("Expo", si("expo", "white"), "P"),
        ("OpenStreetMap", si("openstreetmap"), "P"),
        ("React", dv("react"), "FR"),
        ("Next.js", si("nextdotjs", "white"), "F"),
    ]),
    ("DevOps & Observability", "containers · load balancing · metrics", "#94e2d5", [
        ("Docker", dv("docker"), "PDR"),
        ("Nginx", dv("nginx"), "R"),
        ("Prometheus", dv("prometheus"), "R"),
        ("Grafana", dv("grafana"), "R"),
        ("Git", dv("git"), ""),
        ("GitHub", si("github", "white"), ""),
        ("Actions", si("githubactions", "2088ff"), "F"),
    ]),
]
# Última linha opcional com duas seções lado a lado (vazia por enquanto).
SPLIT_ROW = []

W = 840
PAD = 24
TILE_W = (W - 2 * PAD) / 10  # 10 ferramentas por linha
BOX = 50
ICON = 32
HEADER_H = 26
ROW_H = 96
TOP = 52

_cache = {}


def fetch(url):
    if url not in _cache:
        req = urllib.request.Request(url, headers={"User-Agent": "profile-readme-builder"})
        with urllib.request.urlopen(req, timeout=30) as r:
            _cache[url] = base64.b64encode(r.read()).decode()
    return _cache[url]


def tile(x, y, label, url, projects, delay):
    cx = x + TILE_W / 2
    out = [f'<g class="t" style="animation-delay:{delay:.2f}s">']
    out.append(f'<rect x="{cx - BOX / 2:.1f}" y="{y}" width="{BOX}" height="{BOX}" rx="12" class="box"/>')
    out.append(
        f'<image x="{cx - ICON / 2:.1f}" y="{y + (BOX - ICON) / 2}" width="{ICON}" height="{ICON}" '
        f'href="data:image/svg+xml;base64,{fetch(url)}"/>'
    )
    size = "" if len(label) < 11 else ' style="font-size:9.5px"'
    out.append(f'<text x="{cx:.1f}" y="{y + BOX + 16}" class="lbl"{size}>{escape(label)}</text>')
    n = len(projects)
    for i, p in enumerate(projects):
        dx = (i - (n - 1) / 2) * 9
        out.append(f'<circle cx="{cx + dx:.1f}" cy="{y + BOX + 26}" r="3" fill="{PROJECTS[p][1]}"/>')
    out.append("</g>")
    return "".join(out)


def header(x, y, title, subtitle, color):
    s = f'<text x="{x}" y="{y}" class="h" fill="{color}">▸ {escape(title)}</text>'
    if subtitle:
        s += f'<text x="{x + 9 * len(title) + 30}" y="{y}" class="sub">// {escape(subtitle)}</text>'
    return s


def build():
    parts = []
    y = TOP
    delay = 0.2
    for title, subtitle, color, tools in SECTIONS:
        parts.append(header(PAD + 4, y + 16, title, subtitle, color))
        for i, (label, url, prj) in enumerate(tools):
            parts.append(tile(PAD + i * TILE_W, y + HEADER_H, label, url, prj, delay))
            delay += 0.05
        y += HEADER_H + ROW_H
    col = 0
    for title, subtitle, color, tools in SPLIT_ROW:
        x0 = PAD + col * TILE_W
        parts.append(header(x0 + 4, y + 16, title, subtitle, color))
        for i, (label, url, prj) in enumerate(tools):
            parts.append(tile(x0 + i * TILE_W, y + HEADER_H, label, url, prj, delay))
            delay += 0.05
        col += len(tools) + 1
    if SPLIT_ROW:
        y += HEADER_H + ROW_H

    # Legenda
    legend = ['<text x="%d" y="%d" class="sub">used in →</text>' % (PAD + 4, y + 14)]
    lx = PAD + 104
    for name, color in PROJECTS.values():
        legend.append(f'<circle cx="{lx}" cy="{y + 10}" r="4" fill="{color}"/>')
        legend.append(f'<text x="{lx + 9}" y="{y + 14}" class="leg">{name}</text>')
        lx += 22 + 7.2 * len(name)
    H = y + 34

    return f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="'Fira Code','Cascadia Code',Consolas,'Courier New',monospace">
<style>
.box {{ fill:#313244; stroke:#45475a; stroke-width:1; }}
.lbl {{ fill:#bac2de; font-size:11px; text-anchor:middle; }}
.h {{ font-size:14px; font-weight:700; }}
.sub {{ fill:#6c7086; font-size:11.5px; }}
.leg {{ fill:#a6adc8; font-size:11.5px; }}
.t {{ animation: pop .5s ease-out both; transform-box: fill-box; transform-origin: center; }}
@keyframes pop {{ from {{ opacity:0; transform: translateY(8px) scale(.9); }} to {{ opacity:1; transform:none; }} }}
</style>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1e1e2e"/><stop offset="100%" stop-color="#181825"/></linearGradient>
<clipPath id="round"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#round)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="34" fill="#11111b"/>
<circle cx="20" cy="17" r="6" fill="#f38ba8"/><circle cx="40" cy="17" r="6" fill="#f9e2af"/><circle cx="60" cy="17" r="6" fill="#a6e3a1"/>
<text x="{W / 2}" y="21" fill="#6c7086" font-size="12" text-anchor="middle">lucas@ufv:~/stack $ ls ./used-in-projects</text>
{"".join(parts)}
{"".join(legend)}
</g>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="#313244"/>
</svg>
'''


if __name__ == "__main__":
    out = pathlib.Path(__file__).with_name("stack.svg")
    out.write_text(build(), encoding="utf-8")
    print(f"ok: {out} ({out.stat().st_size // 1024} KB)")
