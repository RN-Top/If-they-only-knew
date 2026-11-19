"""
If They Only Knew
Testing the significance of 3, 6 and 9 through every lens, with proof.
Author: Erin Rae Toppe
"""
import math
import random
import datetime as dt
import itertools
from collections import Counter

import numpy as np  # load numpy fully before plotly uses it (fixes the AttributeError on Streamlit Cloud)
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

st.set_page_config(page_title="If They Only Knew", page_icon="🔺", layout="wide")

GOLD, RED, GREEN, AMBER, BLUE, GREY = "#f2c14e", "#c8423b", "#5fbf77", "#e6a23c", "#5aa9e6", "#6b6658"
TARGETS = {3, 6, 9}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Inter:wght@400;600&display=swap');
.stApp {background: radial-gradient(ellipse at top left, #2a2418 0%, #12100c 55%, #0a0907 100%); color:#e8e2d0;}
h1, h2, h3 {font-family:'Special Elite', monospace !important; color:#f2c14e !important; letter-spacing:1px;}
.hero {font-family:'Special Elite', monospace; font-size:1.05rem; color:#cfc6ad;
       border-left:3px solid #c8423b; padding:6px 14px; margin-bottom:12px;}
.card {position:relative; background:#f3ecd8; color:#2a2418; padding:20px 16px 14px; margin:16px 6px;
       border-radius:3px; box-shadow:4px 6px 14px rgba(0,0,0,.65); transform:rotate(var(--r));
       border-top:6px solid var(--c); font-family:'Special Elite', monospace;}
.pin {position:absolute; top:-9px; left:50%; width:14px; height:14px; border-radius:50%;
      background:#c8423b; box-shadow:0 2px 3px rgba(0,0,0,.6); transform:translateX(-50%);}
.card-title {font-size:1.05rem; font-weight:bold; margin-bottom:6px;}
.card-body {font-size:.88rem; line-height:1.4; margin-bottom:10px;}
.badge {display:inline-block; color:#12100c; padding:2px 10px; border-radius:2px; font-size:.8rem; font-weight:bold;}
.finding {background:rgba(242,193,78,.08); border:1px solid rgba(242,193,78,.45); border-radius:6px;
          padding:10px 14px; margin:10px 0; font-family:'Special Elite', monospace; color:#efe6cc;}
.stTabs [data-baseweb="tab"] {font-family:'Special Elite', monospace;}
</style>
""", unsafe_allow_html=True)


# ======================= helpers =======================
def droot(n, base=10):
    """Digital root in any base: keep adding digits until one is left."""
    return 0 if n == 0 else 1 + (n - 1) % (base - 1)


def digit_root_of_text(text):
    total = sum(int(ch) for ch in str(text) if ch.isdigit())
    return droot(total) if total else 0


def prime_factors(n):
    out, d = [], 2
    while d * d <= n:
        while n % d == 0:
            out.append(d)
            n //= d
        d = 3 if d == 2 else d + 2
    if n > 1:
        out.append(n)
    return out


def binom_tail(k, n, p):
    """Chance of k or more hits out of n, if each hit has probability p."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def style(fig, h=420):
    fig.update_layout(template="plotly_dark", paper_bgcolor="#15120d", plot_bgcolor="rgba(0,0,0,0)",
                      height=h, margin=dict(l=10, r=10, t=40, b=10),
                      font=dict(family="Special Elite, monospace", color="#e8e2d0"))
    return fig


def show_chart(fig):
    """Draw a chart inside its own small web page, using plotly's own script from its CDN.
    This skips Streamlit's built-in chart loader, which failed on phones with
    'TypeError: Importing a module script failed'."""
    h = fig.layout.height or 420
    html = fig.to_html(full_html=False, include_plotlyjs="cdn",
                       config={"responsive": True, "displaylogo": False})
    components.html(
        '<style>html,body{margin:0;padding:0;background:#15120d;}</style>' + html,
        height=int(h) + 10, scrolling=False)


def finding(text):
    st.markdown(f'<div class="finding">{text}</div>', unsafe_allow_html=True)


def card(title, body, verdict, colour, tilt):
    return (f'<div class="card" style="--c:{colour};--r:{tilt}deg"><div class="pin"></div>'
            f'<div class="card-title">{title}</div><div class="card-body">{body}</div>'
            f'<div class="badge" style="background:{colour}">{verdict}</div></div>')


def lines_of(g):
    rows = [list(r) for r in g]
    cols = [[g[r][c] for r in range(3)] for c in range(3)]
    diags = [[g[i][i] for i in range(3)], [g[i][2 - i] for i in range(3)]]
    return rows + cols + diags


@st.cache_data
def magic_squares():
    found = []
    for p in itertools.permutations(range(1, 10)):
        if p[0] + p[1] + p[2] != 15:
            continue
        g = [list(p[0:3]), list(p[3:6]), list(p[6:9])]
        if all(sum(line) == 15 for line in lines_of(g)):
            found.append(g)
    return found


def no_shared_line(g):
    return all(len(TARGETS & set(line)) <= 1 for line in lines_of(g))


def field_vector(n, t_deg):
    """Magnetic field from n coils spaced evenly, each fed a current shifted by its own angle."""
    t, x, y = math.radians(t_deg), 0.0, 0.0
    for k in range(n):
        phi = 2 * math.pi * k / n
        i = math.cos(t - phi)
        x += i * math.cos(phi)
        y += i * math.sin(phi)
    return x, y


def field_range(n):
    mags = [math.hypot(*field_vector(n, t)) for t in range(360)]
    return min(mags), max(mags)


# Earth and sky measurements. independent = a natural measurement, not built from 360 or 24.
SKY = [
    ("Degrees in a circle", "360", "°", None, None, False),
    ("Hours in a day", "24", "h", None, None, False),
    ("Minutes in a day", "1440", "min", None, None, False),
    ("Seconds in a day", "86400", "s", None, None, False),
    ("Precession cycle (traditional)", "25920", "yr", None, None, False),
    ("Precession cycle (modern)", "25772", "yr", None, None, True),
    ("Days in a year", "365.2422", "days", None, None, True),
    ("Lunar month (synodic)", "29.53", "days", None, None, True),
    ("Earth's axial tilt", "23.44", "°", None, None, True),
    ("Earth's circumference", "40075", "km", "24901", "mi", True),
    ("Earth's diameter", "12742", "km", "7918", "mi", True),
    ("Moon's diameter", "3474", "km", "2159", "mi", True),
    ("Sun's diameter", "1392700", "km", "865370", "mi", True),
    ("Earth to Moon (average)", "384400", "km", "238855", "mi", True),
    ("Earth to Sun (average)", "149597871", "km", "92955807", "mi", True),
    ("Speed of light", "299792", "km/s", "186282", "mi/s", True),
    ("Surface gravity", "9.81", "m/s²", "32.17", "ft/s²", True),
    ("Schumann resonance", "7.83", "Hz", None, None, True),
]


# Ancient sites, approximate coordinates (degrees, 4 decimals)
SITES = [
    ("Great Pyramid of Giza", 29.9792, 31.1342), ("Stonehenge", 51.1789, -1.8262),
    ("Newgrange", 53.6947, -6.4755), ("Göbekli Tepe", 37.2231, 38.9225),
    ("Dendera Temple", 26.1419, 32.6703), ("Teotihuacan", 19.6925, -98.8438),
    ("Chichén Itzá", 20.6843, -88.5678), ("Machu Picchu", -13.1631, -72.5450),
    ("Angkor Wat", 13.4125, 103.8670), ("Easter Island (Ahu Tongariki)", -27.1258, -109.2769),
]


def coord_root(lat, lon):
    return digit_root_of_text(f"{abs(lat):.4f}{abs(lon):.4f}")


@st.cache_data
def random_coord_share(samples=5000):
    rng = random.Random(9)
    hits = sum(coord_root(rng.uniform(-90, 90), rng.uniform(-180, 180)) in TARGETS for _ in range(samples))
    return hits / samples


@st.cache_data
def geodesic(freq):
    phi = (1 + 5 ** 0.5) / 2
    base = [(0, s1, s2 * phi) for s1 in (-1, 1) for s2 in (-1, 1)] + \
           [(s1, s2 * phi, 0) for s1 in (-1, 1) for s2 in (-1, 1)] + \
           [(s2 * phi, 0, s1) for s1 in (-1, 1) for s2 in (-1, 1)]
    dist = lambda a, b: math.dist(base[a], base[b])
    faces = [f for f in itertools.combinations(range(12), 3)
             if all(abs(dist(a, b) - 2) < 1e-6 for a, b in itertools.combinations(f, 2))]

    def unit(p):
        n = math.sqrt(sum(c * c for c in p))
        return tuple(c / n for c in p)

    tris = []
    for a, b, c in faces:
        A, B, C = base[a], base[b], base[c]
        P = lambda i, j: unit(tuple(A[t] + (B[t] - A[t]) * i / freq + (C[t] - A[t]) * j / freq for t in range(3)))
        for i in range(freq):
            for j in range(freq - i):
                tris.append((P(i, j), P(i + 1, j), P(i, j + 1)))
                if i + j < freq - 1:
                    tris.append((P(i + 1, j), P(i + 1, j + 1), P(i, j + 1)))
    return tris


def sky_rows(imperial, independent_only, extra):
    rows = []
    for name, metric, mu, imp, iu, indep in SKY + extra:
        if independent_only and not indep:
            continue
        value, unit = (imp, iu) if (imperial and imp) else (metric, mu)
        r = digit_root_of_text(value)
        rows.append({"Measure": name, "Value": f"{value} {unit}", "Digital root": r,
                     "3·6·9": "✦" if r in TARGETS else "", "Natural?": "yes" if indep else "human-made"})
    return rows


@st.cache_data
def core_checks():
    family = all(droot(k) in TARGETS for k in range(3, 300001, 3))
    v, seen = 1, set()
    for _ in range(20):
        seen.add(v if v else 9)
        v = v * 2 % 9
    squares = magic_squares()
    grid = len(squares) == 8 and all(no_shared_line(s) for s in squares)
    lo, hi = field_range(3)
    rows = sky_rows(False, True, [])
    hits = sum(r["Digital root"] in TARGETS for r in rows)
    p = binom_tail(hits, len(rows), 1 / 3)
    tri = {droot(k * (k + 1) // 2) for k in range(1, 901)} <= {1, 3, 6, 9}
    s_hits = sum(coord_root(la, lo_) in TARGETS for _, la, lo_ in SITES)
    s_p = binom_tail(s_hits, len(SITES), random_coord_share())
    return (family, not (seen & TARGETS), grid, abs(hi - lo) < 1e-9, hits, len(rows), p,
            tri, s_hits, s_p)


# ======================= header =======================
st.title("If They Only Knew")
st.markdown('<div class="hero">“If you only knew the magnificence of the 3, 6 and 9…” — attributed to Nikola Tesla.<br>'
            'Working premise: the line points to something real. Every claim here is tested, '
            'run against a control, and given a verdict. Open ❓ Question Everything to scan the whole world at once.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Lens settings")
    BASE = st.number_input("Counting base", min_value=3, max_value=36, value=10,
                           help="We count in base 10. Change it and every number lens reruns. "
                                "If a pattern vanishes in another base, it belongs to our counting, not the universe.")
    st.caption("Base 10 is how we count. Try 9, 12 or 13 and watch what survives.")

if "extra_sky" not in st.session_state:
    st.session_state.extra_sky = []

tabs = st.tabs(["🧷 The Wall", "Ⅰ The Family", "Ⅱ The Vortex", "Ⅲ Sequence Lab", "Ⅳ Nine-Box Grid",
                "Ⅴ Tesla's Field", "Ⅵ Harmony", "Ⅶ As Above, So Below", "Ⅷ Triangles",
                "Ⅸ Spheres & Domes", "Ⅹ Maps", "Ⅺ Calendar Map", "Ⅻ Living Patterns", "🔎 Search Engine", "✝ Biblical Numbers", "🔢 Numerology",
                "⚡ Electricity", "❓ Question Everything"])

# ======================= THE WALL =======================
with tabs[0]:
    (fam_ok, vortex_ok, grid_ok, field_ok, sky_hits, sky_n, sky_p,
     tri_ok, site_hits, site_p) = core_checks()
    sky_status = (GREEN, "PROVEN") if sky_p < 0.05 else (AMBER, "NOT PROVEN YET")
    site_status = (GREEN, "PROVEN") if site_p < 0.05 else (AMBER, "NOT PROVEN YET")
    claims = [
        ("Triangles", "Triangular numbers (1, 3, 6, 10, 15…) only ever reduce to 1, 3, 6 or 9.", tri_ok),
        ("The Family", "Every multiple of 3 reduces to 3, 6 or 9.", fam_ok),
        ("The Vortex", "Doubling from 1 loops 1-2-4-8-7-5 and never touches 3, 6 or 9.", vortex_ok),
        ("Nine-Box Grid", "Only 8 of 362,880 grids balance. In all 8, 3, 6 and 9 never share a line.", grid_ok),
        ("Tesla's Field", "Three phases make a perfectly smooth rotating magnetic field.", field_ok),
        ("Harmony", "The 3rd and 6th harmonics ring as the same note. The 9th is 3's own fifth.", True),
        ("As Above, So Below", f"{sky_hits} of {sky_n} natural measurements land on 3, 6 or 9. Chance odds: {sky_p:.0%}.", None),
        ("Sacred Sites", f"{site_hits} of {len(SITES)} ancient sites have coordinates that reduce to 3, 6 or 9. "
                         f"Chance odds: {site_p:.0%}.", None),
        ("The Quote", "Tesla said it. No original letter, lecture or interview has been found yet.", None),
    ]

    # pattern wall graph
    fig = go.Figure()
    pts = []
    for i, (name, _, ok) in enumerate(claims):
        a = math.radians(90 - i * 360 / len(claims))
        pts.append((math.cos(a), math.sin(a)))
    def status_of(name, ok):
        if name.startswith("As Above"):
            return sky_status
        if name == "Sacred Sites":
            return site_status
        return (GREEN, "PROVEN") if ok else (AMBER, "UNVERIFIED")

    colours = [status_of(name, ok)[0] for name, _, ok in claims]
    proven = [i for i, (_, _, ok) in enumerate(claims) if ok]
    for i, (x, y) in enumerate(pts):
        fig.add_trace(go.Scatter(x=[0, x], y=[0, y], mode="lines", hoverinfo="skip", showlegend=False,
                                 line=dict(color=RED, width=1.5, dash="dot")))
    for a, b in zip(proven, proven[1:] + proven[:1]):
        fig.add_trace(go.Scatter(x=[pts[a][0], pts[b][0]], y=[pts[a][1], pts[b][1]], mode="lines",
                                 hoverinfo="skip", showlegend=False, line=dict(color=GOLD, width=3)))
    fig.add_trace(go.Scatter(x=[p[0] for p in pts], y=[p[1] for p in pts], mode="markers+text",
                             text=[c[0] for c in claims], textposition="bottom center", showlegend=False,
                             marker=dict(size=26, color=colours, line=dict(color="#f3ecd8", width=2))))
    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers+text", text=["3 · 6 · 9"], textposition="middle center",
                             showlegend=False, textfont=dict(size=18, color="#12100c"),
                             marker=dict(size=80, color=GOLD, line=dict(color="#f3ecd8", width=3))))
    fig.update_xaxes(visible=False, range=[-1.5, 1.5])
    fig.update_yaxes(visible=False, range=[-1.4, 1.4], scaleanchor="x")
    show_chart(style(fig, 520))
    st.caption("Gold threads join proven claims. Red string runs to every claim still under test.")

    cols = st.columns(3)
    tilts = [-1.5, 1, -0.5, 1.5, -1, 0.5, -1.2, 0.8, -0.3]
    for i, (name, body, ok) in enumerate(claims):
        colour, verdict = status_of(name, ok)
        cols[i % 3].markdown(card(name, body, verdict, colour, tilts[i]), unsafe_allow_html=True)

# ======================= I. THE FAMILY =======================
with tabs[1]:
    st.subheader("Ⅰ The Family")
    st.write("Add up a number's digits, and keep adding until one digit is left. That last digit is its digital root.")
    c1, c2 = st.columns(2)
    d = c1.number_input("Multiples of", min_value=1, max_value=BASE - 1, value=min(3, BASE - 1))
    N = c2.slider("Check every multiple up to", 100, 200000, 20000, step=100)
    counts = Counter(droot(k, BASE) for k in range(d, N + 1, d))
    reach = sorted(counts)
    fig = go.Figure(go.Bar(x=[str(r) for r in range(1, BASE)], y=[counts.get(r, 0) for r in range(1, BASE)],
                           marker_color=[GOLD if r in reach else GREY for r in range(1, BASE)]))
    fig.update_layout(xaxis_title="Digital root", yaxis_title="How many multiples land here")
    show_chart(style(fig))
    finding(f"In base {BASE}, every multiple of {d} collapses into {len(reach)} of the {BASE - 1} possible roots: "
            f"{', '.join(map(str, reach))}.")

    table = []
    for dd in range(1, BASE):
        fam = sorted({droot(k, BASE) for k in range(dd, dd * 2 * (BASE - 1) + 1, dd)})
        table.append({"Multiples of": dd, "Collapse into": ", ".join(map(str, fam)), "Family size": len(fam)})
    with st.expander("Every number's family, side by side (the control)"):
        st.dataframe(table, hide_index=True)
    if BASE == 10:
        finding("PROOF. 10 leaves a remainder of 1 when divided by 9, so every number has the same remainder as "
                "its digit sum. Multiples of 3 can only leave remainders 0, 3 or 6, so their roots are 9, 3 or 6. "
                "The secret of the family is 10 − 1 = 9.")
    else:
        finding(f"The small families belong to numbers that share a factor with {BASE} − 1 = {BASE - 1}. "
                f"Go back to base 10 and that number is 9.")

# ======================= II. THE VORTEX =======================
with tabs[2]:
    st.subheader("Ⅱ The Vortex")
    st.write("Keep multiplying, take the digital root each time, and trace the path around a circle.")
    m = st.number_input("Multiply by", min_value=2, max_value=50, value=2)
    M = BASE - 1
    path, v = [], 1 % M
    for _ in range(M + 2):
        r = v if v else M
        path.append(r)
        if path.count(r) > 1:
            break
        v = v * m % M
    never = sorted(set(range(1, M + 1)) - set(path))

    def pos(k):
        a = math.radians(90 - 360 * k / M)
        return math.cos(a), math.sin(a)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[pos(k)[0] for k in path], y=[pos(k)[1] for k in path], mode="lines",
                             line=dict(color=BLUE, width=3), name="Multiplying path"))
    if len(never) >= 2:
        loop = never + [never[0]]
        fig.add_trace(go.Scatter(x=[pos(k)[0] for k in loop], y=[pos(k)[1] for k in loop], mode="lines",
                                 line=dict(color=GOLD, width=3), name="Never touched"))
    fig.add_trace(go.Scatter(x=[pos(k)[0] for k in range(1, M + 1)], y=[pos(k)[1] for k in range(1, M + 1)],
                             mode="markers+text", text=[str(k) for k in range(1, M + 1)],
                             textposition="middle center", showlegend=False,
                             marker=dict(size=34, color=[GOLD if k in never else "#1b1813" for k in range(1, M + 1)],
                                         line=dict(color="#f3ecd8", width=2)),
                             textfont=dict(size=15, color="#f3ecd8")))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x")
    fig.update_layout(legend=dict(orientation="h", y=-0.05))
    show_chart(style(fig, 560))
    finding(f"Path: {' → '.join(map(str, path))}. "
            + (f"It never touches {', '.join(map(str, never))}." if never else "It touches every point."))
    if BASE == 10 and m == 2:
        finding("PROOF. A power of 2 is never a multiple of 3, so its digital root can never be 3, 6 or 9. "
                "The 1-2-4-8-7-5 loop runs forever, and 3, 6, 9 stand outside it as their own triangle.")

# ======================= III. SEQUENCE LAB =======================
with tabs[3]:
    st.subheader("Ⅲ Sequence Lab")
    st.write("Test any arrangement. Every result is compared with thousands of random sequences of the same length.")
    pick = st.selectbox("Start from", ["333666999", "369369369", "999666333", "369", "963", "123456789"])
    raw = st.text_input("…or type your own digits", value=pick)
    s = "".join(ch for ch in raw if ch.isdigit())
    if not s:
        st.warning("Type at least one digit.")
    else:
        n = int(s)
        chain = [n]
        while chain[-1] >= 10:
            chain.append(sum(int(c) for c in str(chain[-1])))
        c1, c2, c3 = st.columns(3)
        c1.metric("Digit sum", sum(int(c) for c in s))
        c2.metric("Digital root", chain[-1])
        c3.metric("Digits that are 3, 6 or 9", f"{round(100 * sum(c in '369' for c in s) / len(s))}%")
        finding("Collapse: " + " → ".join(map(str, chain)))

        random.seed(369)
        sims = ["".join(random.choice("0123456789") for _ in range(len(s))) for _ in range(4000)]
        sim_ints = [int(x) for x in sims]
        rows = [{"Test": "Digital root is 3, 6 or 9", "Yours": "✦" if chain[-1] in TARGETS else "—",
                 "Random sequences": f"{sum(digit_root_of_text(x) in TARGETS for x in sims) / 40:.1f}%"}]
        for div in (3, 9, 27, 37, 111):
            rows.append({"Test": f"Divisible by {div}", "Yours": "✦" if n % div == 0 else "—",
                         "Random sequences": f"{sum(x % div == 0 for x in sim_ints) / 40:.1f}%"})
        st.dataframe(rows, hide_index=True)
        if 1 < n and len(s) <= 12:
            finding(f"{n:,} = " + " × ".join(map(str, prime_factors(n))))
        if len(s) == 9:
            g = [[int(c) for c in s[i:i + 3]] for i in (0, 3, 6)]
            sums = [sum(line) for line in lines_of(g)]
            fig = go.Figure(go.Heatmap(z=g, text=g, texttemplate="%{text}", textfont=dict(size=30),
                                       colorscale=[[0, "#1b1813"], [1, GOLD]], showscale=False))
            fig.update_yaxes(autorange="reversed", visible=False)
            fig.update_xaxes(visible=False)
            show_chart(style(fig, 360))
            finding(f"As a nine-box grid. Rows: {sums[0:3]}, columns: {sums[3:6]}, diagonals: {sums[6:8]}. "
                    + ("Every line balances." if len(set(sums)) == 1 else "Not every line balances."))

# ======================= IV. NINE-BOX GRID =======================
with tabs[4]:
    st.subheader("Ⅳ Nine-Box Grid")
    squares = magic_squares()
    st.write(f"There are 362,880 ways to fill a 3 × 3 grid with the numbers 1 to 9. "
             f"Searching all of them, exactly {len(squares)} make every row, column and diagonal add to 15. "
             f"The oldest known is China's Lo Shu square.")
    i = st.slider("Show square", 1, len(squares), 1)
    g = squares[i - 1]
    z = [[1 if x in TARGETS else (0.5 if x == 5 else 0) for x in row] for row in g]
    fig = go.Figure(go.Heatmap(z=z, text=g, texttemplate="%{text}", textfont=dict(size=34),
                               colorscale=[[0, "#1b1813"], [0.5, "#4a3f2a"], [1, GOLD]], showscale=False, zmin=0, zmax=1))
    fig.update_yaxes(autorange="reversed", visible=False)
    fig.update_xaxes(visible=False)
    show_chart(style(fig, 380))
    centre5 = all(sq[1][1] == 5 for sq in squares)
    apart = all(no_shared_line(sq) for sq in squares)
    finding(f"Checked across all {len(squares)} squares: the centre is always 5 ({'true' if centre5 else 'false'}), "
            f"and 3, 6 and 9 never share a row, column or diagonal ({'true' if apart else 'false'}). "
            f"Each one sits on its own line, like three points of a triangle around the centre.")

# ======================= V. TESLA'S FIELD =======================
with tabs[5]:
    st.subheader("Ⅴ Tesla's Field")
    st.write("Tesla's alternating-current motor runs on a rotating magnetic field. "
             "Feed coils with currents that rise and fall a step apart, and the field spins.")
    c1, c2 = st.columns(2)
    phases = c1.slider("Number of phases (the control)", 2, 9, 3)
    angle = c2.slider("Moment in the cycle (degrees)", 0, 359, 0)
    ts = list(range(0, 361, 2))
    wave = go.Figure()
    for k in range(phases):
        wave.add_trace(go.Scatter(x=ts, y=[math.cos(math.radians(t) - 2 * math.pi * k / phases) for t in ts],
                                  mode="lines", name=f"Phase {k + 1}"))
    wave.add_vline(x=angle, line=dict(color=GOLD, dash="dot"))
    wave.update_layout(xaxis_title="Degrees through the cycle", yaxis_title="Current",
                       legend=dict(orientation="h", y=-0.25))
    show_chart(style(wave, 340))

    fx, fy = field_vector(phases, angle)
    trail = [field_vector(phases, t) for t in range(0, 361, 3)]
    vec = go.Figure()
    vec.add_trace(go.Scatter(x=[p[0] for p in trail], y=[p[1] for p in trail], mode="lines",
                             line=dict(color=GREY, dash="dot"), name="Path over one cycle"))
    vec.add_trace(go.Scatter(x=[0, fx], y=[0, fy], mode="lines+markers", line=dict(color=GOLD, width=5),
                             marker=dict(size=[0, 14]), name="Field right now"))
    lim = phases / 2 + 0.6
    vec.update_xaxes(range=[-lim - 0.5, lim + 0.5], visible=False)
    vec.update_yaxes(range=[-lim, lim], visible=False, scaleanchor="x")
    vec.update_layout(legend=dict(orientation="h", y=-0.05))
    show_chart(style(vec, 420))

    lo, hi = field_range(phases)
    if phases == 2:
        finding(f"Two phases set half a circle apart only pulse back and forth (strength {lo:.2f} to {hi:.2f}). No rotation.")
    else:
        finding(f"{phases} phases: a smooth spinning field with constant strength {hi:.2f}. "
                + ("Three is the smallest number of evenly spaced phases that does this, "
                   "and three-phase power, built on Tesla's work, runs the world's grid today."
                   if phases == 3 else "It works, but it needs more wires than three."))
    st.caption("Honest note: Tesla's first motor patents (1888) used two phases a quarter-cycle apart. "
               "Three-phase became the standard because it carries the most power for the least wire.")

# ======================= VI. HARMONY =======================
with tabs[6]:
    st.subheader("Ⅵ Harmony")
    st.write("Every vibrating string or air column sounds its fundamental plus harmonics at 2×, 3×, 4× that frequency.")
    NOTES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

    def note_name(f):
        semis = 12 * math.log2(f / 440)
        r = round(semis)
        return f"{NOTES[r % 12]}{4 + (r + 9) // 12}", round((semis - r) * 100)

    f0 = st.number_input("Fundamental frequency (Hz)", min_value=20.0, max_value=2000.0, value=110.0)
    harm = []
    for h in range(1, 10):
        name, cents = note_name(f0 * h)
        harm.append({"Harmonic": h, "Frequency (Hz)": round(f0 * h, 2), "Note": name, "Off by (cents)": cents})
    fig = go.Figure(go.Bar(x=[f"{r['Harmonic']}: {r['Note']}" for r in harm], y=[r["Frequency (Hz)"] for r in harm],
                           marker_color=[GOLD if r["Harmonic"] in TARGETS else GREY for r in harm]))
    fig.update_layout(yaxis_title="Hz")
    show_chart(style(fig, 360))
    st.dataframe(harm, hide_index=True)
    finding(f"The 3rd and 6th harmonics are the same note, an octave apart ({harm[2]['Note']} and {harm[5]['Note']}). "
            f"The 9th ({harm[8]['Note']}) is a perfect fifth above the 3rd, because 9 = 3 × 3. "
            f"The ratio 3:2, the perfect fifth, is the sweetest interval after the octave.")

# ======================= VII. AS ABOVE, SO BELOW =======================
with tabs[7]:
    st.subheader("Ⅶ As Above, So Below")
    st.write("Real measurements of the earth and sky. If 3, 6, 9 are built into the universe, they should beat chance "
             "and survive a change of units.")
    c1, c2 = st.columns(2)
    imperial = c1.checkbox("Use miles and feet instead of metric")
    indep = c2.checkbox("Only natural measurements (leave out ones built on 360 or 24)", value=True)
    rows = sky_rows(imperial, indep, st.session_state.extra_sky)
    st.dataframe(rows, hide_index=True)
    hits = sum(r["Digital root"] in TARGETS for r in rows)
    n_rows = len(rows)
    p = binom_tail(hits, n_rows, 1 / 3) if n_rows else 1
    dist = Counter(r["Digital root"] for r in rows)
    fig = go.Figure(go.Bar(x=[str(k) for k in range(1, 10)], y=[dist.get(k, 0) for k in range(1, 10)],
                           marker_color=[GOLD if k in TARGETS else GREY for k in range(1, 10)]))
    fig.add_hline(y=n_rows / 9, line=dict(color=RED, dash="dot"), annotation_text="chance")
    fig.update_layout(xaxis_title="Digital root", yaxis_title="Measurements")
    show_chart(style(fig, 340))
    verdict = "beats chance. Worth a closer look." if p < 0.05 else "is within what chance would give."
    finding(f"{hits} of {n_rows} land on 3, 6 or 9 ({hits / max(n_rows, 1):.0%}). Chance alone gives about 33%. "
            f"Odds of doing this well by luck: {p:.0%}. This {verdict}")
    st.caption("Tip: flip the units. Units like km and miles are human choices, so a true pattern of nature "
               "should hold in both.")

    with st.form("add_measure", clear_on_submit=True):
        st.write("Add your own measurement")
        a1, a2, a3 = st.columns(3)
        name = a1.text_input("Name")
        value = a2.text_input("Value")
        unit = a3.text_input("Unit")
        natural = st.checkbox("This is a natural measurement", value=True)
        if st.form_submit_button("Add to the board") and name and any(ch.isdigit() for ch in value):
            st.session_state.extra_sky.append((name, value, unit, None, None, natural))
            st.rerun()

# ======================= VIII. TRIANGLES =======================
with tabs[8]:
    st.subheader("Ⅷ Triangles")
    st.write("Stack dots into triangles: 1, 3, 6, 10, 15, 21, 28, 36, 45… These are the triangular numbers.")
    fig = go.Figure()
    off = 0.0
    for k in range(1, 10):
        t = k * (k + 1) // 2
        r = droot(t, BASE)
        xs, ys = [], []
        for row in range(k):
            for c in range(row + 1):
                xs.append(off + c - row / 2 + k / 2)
                ys.append(-row)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", showlegend=False, hoverinfo="skip",
                                 marker=dict(size=9, color=GOLD if r in TARGETS else GREY)))
        fig.add_annotation(x=off + k / 2, y=1.3, text=f"{t}<br>root {r}", showarrow=False)
        off += k + 1.5
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x")
    show_chart(style(fig, 320))
    tn = st.slider("Check this many triangular numbers", 9, 9000, 900, step=9)
    counts = Counter(droot(k * (k + 1) // 2, BASE) for k in range(1, tn + 1))
    fig = go.Figure(go.Bar(x=[str(r) for r in range(1, BASE)], y=[counts.get(r, 0) for r in range(1, BASE)],
                           marker_color=[GOLD if r in TARGETS else GREY for r in range(1, BASE)]))
    fig.update_layout(xaxis_title="Digital root", yaxis_title="Triangular numbers")
    show_chart(style(fig, 320))
    share = sum(v for r, v in counts.items() if r in TARGETS) / tn
    finding(f"Roots that ever appear: {', '.join(map(str, sorted(counts)))}. "
            f"Share landing on 3, 6 or 9: {share:.0%} (chance would be 33%).")
    if BASE == 10:
        finding("PROOF. Triangular roots repeat every 9 steps: 1, 3, 6, 1, 6, 3, 1, 9, 9. "
                "Only 1, 3, 6 and 9 can ever appear, and 3, 6, 9 fill six of every nine places.")

# ======================= IX. SPHERES & DOMES =======================
with tabs[9]:
    st.subheader("Ⅸ Spheres & Domes")
    st.write("A geodesic dome is a sphere built entirely from triangles. Split each face of a 20-sided "
             "icosahedron into smaller triangles and push them out onto a sphere.")
    c1, c2 = st.columns(2)
    freq = c1.slider("Frequency (how finely each face is split)", 1, 9, 3)
    half = c2.checkbox("Show as a dome (top half only)", value=False)
    tris = geodesic(freq)
    if half:
        tris = [t for t in tris if sum(p[2] for p in t) / 3 > 0]
    X, Y, Z, I, J, K = [], [], [], [], [], []
    ex, ey, ez = [], [], []
    for n_, (a, b, c) in enumerate(tris):
        for p in (a, b, c):
            X.append(p[0]); Y.append(p[1]); Z.append(p[2])
        I.append(3 * n_); J.append(3 * n_ + 1); K.append(3 * n_ + 2)
        for p in (a, b, c, a):
            ex.append(p[0]); ey.append(p[1]); ez.append(p[2])
        ex.append(None); ey.append(None); ez.append(None)
    fig = go.Figure([
        go.Mesh3d(x=X, y=Y, z=Z, i=I, j=J, k=K, intensity=Z, colorscale=[[0, "#2a2418"], [1, GOLD]],
                  showscale=False, flatshading=True, opacity=0.95),
        go.Scatter3d(x=ex, y=ey, z=ez, mode="lines", line=dict(color="#12100c", width=2),
                     hoverinfo="skip", showlegend=False),
    ])
    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
                                 aspectmode="data", bgcolor="rgba(0,0,0,0)"))
    show_chart(style(fig, 520))
    rows = []
    for f in range(1, 10):
        faces, edges, verts = 20 * f * f, 30 * f * f, 10 * f * f + 2
        rows.append({"Frequency": f, "Triangles": faces, "root": droot(faces),
                     "Edges": edges, "root ": droot(edges), "Corners": verts, "root  ": droot(verts)})
    st.dataframe(rows, hide_index=True)
    finding("Every full geodesic sphere has 30 × f² edges, and 30 is a multiple of 3, so the edge count "
            "always reduces to 3, 6 or 9. The triangle count lands on 9 exactly when the frequency is a "
            "multiple of 3. Drag the 3D model to spin it.")

# ======================= X. MAPS =======================
with tabs[10]:
    st.subheader("Ⅹ Maps")
    st.write("Ancient sites around the world. Add up the digits of each site's coordinates and see "
             "whether they lean toward 3, 6 or 9. The control is thousands of random points on Earth.")
    if "extra_sites" not in st.session_state:
        st.session_state.extra_sites = []
    sites = SITES + st.session_state.extra_sites
    c1, c2 = st.columns(2)
    flat = c1.checkbox("Flat map instead of globe")
    spin = c2.slider("Spin the globe", -180, 180, 20)
    roots = [coord_root(la, lo) for _, la, lo in sites]
    geo = go.Figure(go.Scattergeo(
        lat=[s[1] for s in sites], lon=[s[2] for s in sites], mode="markers+text",
        text=[s[0] for s in sites], textposition="top center", textfont=dict(color="#efe6cc", size=10),
        marker=dict(size=11, color=[GOLD if r in TARGETS else BLUE for r in roots],
                    line=dict(color="#f3ecd8", width=1))))
    geo.update_geos(projection_type="natural earth" if flat else "orthographic",
                    projection_rotation=dict(lon=spin, lat=20), showland=True, landcolor="#2a2418",
                    showocean=True, oceancolor="#0d1117", coastlinecolor=GREY, showcountries=False,
                    bgcolor="rgba(0,0,0,0)",
                    lataxis=dict(showgrid=True, dtick=9, gridcolor="rgba(242,193,78,.18)"),
                    lonaxis=dict(showgrid=True, dtick=9, gridcolor="rgba(242,193,78,.18)"))
    show_chart(style(geo, 520))
    st.caption("Grid lines every 9 degrees. Gold sites reduce to 3, 6 or 9.")
    st.dataframe([{"Site": s[0], "Latitude": s[1], "Longitude": s[2], "Digital root": r,
                   "3·6·9": "✦" if r in TARGETS else ""} for s, r in zip(sites, roots)], hide_index=True)
    chance = random_coord_share()
    hits = sum(r in TARGETS for r in roots)
    p = binom_tail(hits, len(sites), chance)
    finding(f"{hits} of {len(sites)} sites land on 3, 6 or 9. Random points on Earth do it {chance:.0%} of the time. "
            f"Odds of this many by luck: {p:.0%}.")
    with st.form("add_site", clear_on_submit=True):
        st.write("Add a place")
        a1, a2, a3 = st.columns(3)
        nm = a1.text_input("Place name")
        la = a2.number_input("Latitude", -90.0, 90.0, 0.0, format="%.4f")
        lo = a3.number_input("Longitude", -180.0, 180.0, 0.0, format="%.4f")
        if st.form_submit_button("Pin it") and nm:
            st.session_state.extra_sites.append((nm, la, lo))
            st.rerun()

# ======================= XI. CALENDAR MAP =======================
with tabs[11]:
    st.subheader("Ⅺ Calendar Map")
    st.write("Every day of the year on one wheel. Each ring is a digital root from 1 (centre) to 9 (outside).")
    c1, c2 = st.columns(2)
    year = c1.number_input("Year", 1, 9999, dt.date.today().year)
    mode = c2.radio("Read each day as", ["Full date (month, day, year)", "Day of the year (1–366)"])
    start = dt.date(year, 1, 1)
    ndays = (dt.date(year + 1, 1, 1) - start).days
    days, theta, rr = [], [], []
    for i in range(ndays):
        day = start + dt.timedelta(days=i)
        val = f"{day.month}{day.day}{day.year}" if mode.startswith("Full") else str(i + 1)
        r = digit_root_of_text(val)
        days.append((day, r))
        theta.append(360 * i / ndays)
        rr.append(r)
    wheel = go.Figure(go.Scatterpolar(
        r=rr, theta=theta, mode="markers", text=[d.strftime("%b %d") for d, _ in days],
        hovertemplate="%{text}: root %{r}<extra></extra>",
        marker=dict(size=6, color=[GOLD if r in TARGETS else GREY for r in rr])))
    month_starts = [360 * (dt.date(year, m, 1) - start).days / ndays for m in range(1, 13)]
    wheel.update_layout(polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(range=[0, 9.5], tickvals=list(range(1, 10)), gridcolor="rgba(242,193,78,.15)"),
        angularaxis=dict(direction="clockwise", rotation=90, tickvals=month_starts,
                         ticktext=[dt.date(2000, m, 1).strftime("%b") for m in range(1, 13)],
                         gridcolor="rgba(242,193,78,.15)")))
    show_chart(style(wheel, 560))
    hits = sum(r in TARGETS for r in rr)
    today = dt.date.today()
    finding(f"{hits} of {ndays} days in {year} reduce to 3, 6 or 9 ({hits / ndays:.0%}; chance is 33%). "
            f"Today, {today:%B %d, %Y}, reduces to {digit_root_of_text(f'{today.month}{today.day}{today.year}')}.")

# ======================= XII. LIVING PATTERNS =======================
with tabs[12]:
    st.subheader("Ⅻ Living Patterns")
    st.write("Numbers in everything. Simple rules, repeated, grow into living shapes.")
    pat = st.radio("Pattern", ["Times-Table Circle", "Vedic Square", "Pascal's Triangle", "Fibonacci Wheel"],
                   horizontal=True)

    if pat == "Times-Table Circle":
        npts = st.slider("Points around the circle", 9, 360, 180, step=9)
        ks = [2 + 0.5 * s for s in range(57)]

        def tt_lines(k):
            xs, ys = [], []
            for i in range(npts):
                a1 = 2 * math.pi * i / npts
                a2 = 2 * math.pi * (i * k % npts) / npts
                xs += [math.cos(a1), math.cos(a2), None]
                ys += [math.sin(a1), math.sin(a2), None]
            return xs, ys

        x0, y0 = tt_lines(2)
        fig = go.Figure(go.Scatter(x=x0, y=y0, mode="lines", line=dict(color=GOLD, width=1), hoverinfo="skip"),
                        frames=[go.Frame(data=[go.Scatter(x=tt_lines(k)[0], y=tt_lines(k)[1])], name=str(k))
                                for k in ks])
        fig.update_layout(
            updatemenus=[dict(type="buttons", x=0, y=1.08, buttons=[
                dict(label="▶ Bring it to life", method="animate",
                     args=[None, dict(frame=dict(duration=250, redraw=True), fromcurrent=True)])])],
            sliders=[dict(currentvalue=dict(prefix="Multiply by "), steps=[
                dict(label=str(k), method="animate", args=[[str(k)], dict(mode="immediate")]) for k in ks])])
        fig.update_xaxes(visible=False, range=[-1.1, 1.1])
        fig.update_yaxes(visible=False, range=[-1.1, 1.1], scaleanchor="x")
        show_chart(style(fig, 620))
        finding("Each point connects to the point at its number times the multiplier. "
                "×2 draws a heart shape (a cardioid), ×3 a two-lobed nephroid. "
                "With 9 points and ×2 you get the vortex from Lens Ⅱ.")

    elif pat == "Vedic Square":
        M = BASE - 1
        z = [[droot(i * j, BASE) for j in range(1, M + 1)] for i in range(1, M + 1)]
        fig = go.Figure(go.Heatmap(
            z=[[1 if v in TARGETS else 0 for v in row] for row in z], text=z, texttemplate="%{text}",
            colorscale=[[0, "#1b1813"], [1, GOLD]], showscale=False,
            x=list(range(1, M + 1)), y=list(range(1, M + 1))))
        fig.update_yaxes(autorange="reversed")
        show_chart(style(fig, 560))
        if BASE == 10:
            finding(f"The times table with every answer reduced to one digit. Row 9 is all 9s. "
                    f"Rows 3 and 6 use only {sorted(set(z[2]))} and {sorted(set(z[5]))}. "
                    f"Every other row runs through all nine digits.")

    elif pat == "Pascal's Triangle":
        c1, c2 = st.columns(2)
        nrows = c1.slider("Rows", 9, 243, 81, step=9)
        mod = c2.selectbox("Colour by remainder after dividing by", [3, 9, 2, 6], index=0)
        xs, ys, cs = [], [], []
        row = [1]
        for nr in range(nrows):
            for k, v in enumerate(row):
                if v % mod:
                    xs.append(k - nr / 2)
                    ys.append(-nr)
                    cs.append(v % mod)
            row = [1] + [(row[i] + row[i + 1]) % mod for i in range(len(row) - 1)] + [1]
        fig = go.Figure(go.Scatter(x=xs, y=ys, mode="markers", hoverinfo="skip",
                                   marker=dict(size=max(2, 300 // nrows), color=cs,
                                               colorscale=[[0, BLUE], [1, GOLD]])))
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False, scaleanchor="x")
        show_chart(style(fig, 560))
        finding(f"Every number is the sum of the two above it. Keep only the remainder after dividing by {mod} "
                f"and triangles appear inside triangles, forever.")

    else:
        M = BASE - 1
        seq, a, b = [], 1, 1
        while True:
            seq.append(a if a else M)
            a, b = b, (a + b) % M
            if (a, b) == (1, 1) or len(seq) > 500:
                break
        L = len(seq)
        wheel = go.Figure(go.Scatterpolar(
            r=seq + [seq[0]], theta=[360 * i / L for i in range(L + 1)], mode="lines+markers+text",
            text=[str(v) for v in seq] + [""], textposition="top center",
            line=dict(color=BLUE), marker=dict(size=12, color=[GOLD if v in TARGETS else GREY for v in seq + [seq[0]]])))
        wheel.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(range=[0, M + 1]),
                                       angularaxis=dict(direction="clockwise", rotation=90, showticklabels=False)))
        show_chart(style(wheel, 560))
        spots = [i + 1 for i, v in enumerate(seq) if v in TARGETS]
        finding(f"Fibonacci numbers (each the sum of the two before) reduce to a loop of {L}. "
                f"3, 6 and 9 appear at positions {spots}."
                + (" Every 4th one, because a Fibonacci number is divisible by 3 exactly when its position is "
                   "divisible by 4." if BASE == 10 else ""))

# ======================= SEARCH ENGINE =======================
with tabs[13]:
    st.subheader("🔎 Search Engine")
    st.write("Type any word, name, date or number. It's turned into numbers several ways, then checked "
             "against every lens in this app.")
    q = st.text_input("Search", value="Tesla")
    CIPHERS = {
        "English ordinal (A=1 … Z=26)": lambda ch: ord(ch) - 64,
        "Pythagorean (A=1 … I=9, then repeat)": lambda ch: (ord(ch) - 65) % 9 + 1,
        "Reverse ordinal (A=26 … Z=1)": lambda ch: 91 - ord(ch),
    }
    letters = [ch for ch in q.upper() if "A" <= ch <= "Z"]
    numbers = [int(x) for x in "".join(ch if ch.isdigit() else " " for ch in q).split()]
    values = {}
    if letters:
        for name, fn in CIPHERS.items():
            values[name] = sum(fn(ch) for ch in letters)
    if numbers:
        values["Number(s) typed"] = sum(numbers)
    if not values:
        st.info("Type a word or number to search.")
    else:
        rows = [{"Reading": k, "Value": v, "Digital root": droot(v), "3·6·9": "✦" if droot(v) in TARGETS else ""}
                for k, v in values.items()]
        st.dataframe(rows, hide_index=True)

        if letters:
            rng = random.Random(len(letters))
            sims = ["".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in letters) for _ in range(3000)]
            chance = {name: sum(droot(sum(fn(c) for c in w)) in TARGETS for w in sims) / 3000
                      for name, fn in CIPHERS.items()}
            hit_count = sum(droot(values[n]) in TARGETS for n in CIPHERS)
            finding(f"“{q}” lands on 3, 6 or 9 in {hit_count} of {len(CIPHERS)} ciphers. A random "
                    f"{len(letters)}-letter string does it about {sum(chance.values()) / len(chance):.0%} "
                    f"of the time in each.")

        # Look the values up across the lenses
        hits = []
        targets = set(values.values()) | set(numbers)
        tri_set = {k * (k + 1) // 2 for k in range(1, 3000)}
        fib, a, b = set(), 1, 1
        while a < 10 ** 12:
            fib.add(a)
            a, b = b, a + b
        for v in sorted(targets):
            if v in tri_set:
                hits.append(f"{v} is a triangular number (Lens Ⅷ)")
            if v in fib:
                hits.append(f"{v} is a Fibonacci number (Lens Ⅻ)")
            if v and v % 9 == 0:
                hits.append(f"{v} is a multiple of 9: it belongs to the family of 9 (Lens Ⅰ)")
            elif v and v % 3 == 0:
                hits.append(f"{v} is a multiple of 3: it belongs to the 3, 6, 9 family (Lens Ⅰ)")
            if v and 360 % v == 0:
                hits.append(f"{v} divides the 360° circle evenly")
            if v and v > 1 and v < 10 ** 12:
                pf = prime_factors(v)
                if len(pf) > 1:
                    hits.append(f"{v} = {' × '.join(map(str, pf))}")
            for name, metric, mu, imp, iu, _ in SKY + st.session_state.extra_sky:
                for val, unit in ((metric, mu), (imp, iu)):
                    if val and str(v) in val.replace(".", ""):
                        hits.append(f"{v} appears inside {name}: {val} {unit} (Lens Ⅶ)")
            for name, la, lo in SITES:
                if str(v) in f"{abs(la):.4f}{abs(lo):.4f}".replace(".", ""):
                    hits.append(f"{v} appears inside the coordinates of {name} (Lens Ⅹ)")
        st.markdown("**Connections found**")
        if hits:
            for h in dict.fromkeys(hits):
                st.markdown(f"- {h}")
        else:
            st.write("No connections found for this one.")
        st.caption("Honest note: short numbers turn up inside long ones by chance all the time. "
                   "A connection is a lead to test, not proof.")

def number_board(items, chance=1 / 3):
    """Table + chart + odds for a list of (name, value_text, unit, natural)."""
    rows = []
    for name, val, unit, natural in items:
        r = digit_root_of_text(val)
        rows.append({"What": name, "Number": f"{val} {unit}".strip(), "Digital root": r,
                     "3·6·9": "✦" if r in TARGETS else "", "Kind": natural})
    st.dataframe(rows, hide_index=True)
    dist = Counter(r["Digital root"] for r in rows)
    fig = go.Figure(go.Bar(x=[str(k) for k in range(1, 10)], y=[dist.get(k, 0) for k in range(1, 10)],
                           marker_color=[GOLD if k in TARGETS else GREY for k in range(1, 10)]))
    fig.add_hline(y=len(rows) / 9, line=dict(color=RED, dash="dot"), annotation_text="chance")
    fig.update_layout(xaxis_title="Digital root", yaxis_title="Count")
    show_chart(style(fig, 320))
    hits = sum(r["Digital root"] in TARGETS for r in rows)
    p = binom_tail(hits, len(rows), chance)
    finding(f"{hits} of {len(rows)} reduce to 3, 6 or 9 ({hits / len(rows):.0%}; chance is 33%). "
            f"Odds of this many by luck: {p:.0%}.")


# ======================= BIBLICAL NUMBERS =======================
with tabs[14]:
    st.subheader("✝ Biblical Numbers")
    st.write("Numbers that carry meaning in scripture, run through the same test as everything else.")
    BIBLE = [
        ("Days of creation", "6", "", "Genesis 1"), ("Day of rest", "7", "", "Genesis 2"),
        ("Days in the tomb", "3", "", "Gospels"), ("Persons of the Trinity", "3", "", "Tradition"),
        ("Tribes of Israel / apostles", "12", "", "Genesis, Gospels"), ("Commandments", "10", "", "Exodus 20"),
        ("Gospels", "4", "", "New Testament"), ("Days of the flood rains / Jesus' fast", "40", "", "Genesis 7, Matthew 4"),
        ("Fish in the net", "153", "", "John 21:11"), ("Number of the beast", "666", "", "Revelation 13:18"),
        ("The sealed", "144000", "", "Revelation 7:4"), ("Years of Methuselah", "969", "", "Genesis 5:27"),
        ("Ark length", "300", "cubits", "Genesis 6:15"), ("Ark width", "50", "cubits", "Genesis 6:15"),
        ("Ark height", "30", "cubits", "Genesis 6:15"), ("Fruits of the Spirit", "9", "", "Galatians 5:22–23"),
        ("Years of exile", "70", "", "Jeremiah 29:10"), ("Reign of the millennium", "1000", "years", "Revelation 20"),
        ("Jesus' age at the crucifixion (traditional)", "33", "", "Tradition"),
    ]
    st.caption("Source shown in the Kind column.")
    number_board([(n, v, u, src) for n, v, u, src in BIBLE])
    finding("Notice the family: creation 6, the tomb 3, the fruits 9, the beast 666, the fish 153 and "
            "the 144,000 all reduce to 3, 6 or 9. Whether that beats chance is in the odds line above.")

# ======================= NUMEROLOGY =======================
with tabs[15]:
    st.subheader("🔢 Numerology")
    st.write("Classic Pythagorean numerology. Your life path comes from your birth date; your expression "
             "number from your name (A=1 … I=9, then J starts again at 1).")

    def reduce_keep_master(n):
        steps = [n]
        while n > 9 and n not in (11, 22, 33):
            n = sum(int(c) for c in str(n))
            steps.append(n)
        return n, steps

    c1, c2 = st.columns(2)
    born = c1.date_input("Birth date", value=dt.date(1856, 7, 10),
                         min_value=dt.date(1, 1, 1), max_value=dt.date(9999, 12, 31))
    nm = c2.text_input("Full name", value="Nikola Tesla")
    lp, lp_steps = reduce_keep_master(sum(int(c) for c in born.strftime("%m%d%Y")))
    letters = [ch for ch in nm.upper() if "A" <= ch <= "Z"]
    ex, ex_steps = reduce_keep_master(sum((ord(ch) - 65) % 9 + 1 for ch in letters)) if letters else (0, [0])
    m1, m2 = st.columns(2)
    m1.metric("Life path", lp)
    m2.metric("Expression", ex)
    finding(f"Life path: {' → '.join(map(str, lp_steps))}. Expression: {' → '.join(map(str, ex_steps))}. "
            "11, 22 and 33 are kept as master numbers, as numerology tradition does.")

    st.markdown("**The control: how life paths spread across a century**")
    counts = Counter(reduce_keep_master(sum(int(c) for c in (dt.date(1900, 1, 1) + dt.timedelta(days=i))
                                            .strftime("%m%d%Y")))[0] for i in range(36525))
    keys = sorted(counts)
    fig = go.Figure(go.Bar(x=[str(k) for k in keys], y=[counts[k] for k in keys],
                           marker_color=[GOLD if k in TARGETS or k == 33 else GREY for k in keys]))
    fig.update_layout(xaxis_title="Life path", yaxis_title="Birthdays 1900–1999")
    show_chart(style(fig, 320))
    finding("Life paths aren't spread evenly: some numbers are more common simply because of how dates add up. "
            "That's why every claim here needs a control.")

# ======================= ELECTRICITY =======================
with tabs[16]:
    st.subheader("⚡ Electricity")
    st.write("The numbers of electric power, Tesla's world. Some are nature's, some are human choices.")
    ELEC = [
        ("Phase spacing in three-phase power", "120", "°", "geometry"),
        ("Phases in the power grid", "3", "", "engineering"),
        ("US mains frequency", "60", "Hz", "human choice"), ("Europe mains frequency", "50", "Hz", "human choice"),
        ("US household voltage", "120", "V", "human choice"), ("Europe household voltage", "230", "V", "human choice"),
        ("US commercial three-phase", "208", "V", "human choice"), ("Industrial three-phase", "480", "V", "human choice"),
        ("Niagara Falls plant, Tesla's AC system (1895)", "25", "Hz", "human choice"),
        ("Charge of one electron", "1.602176634", "× 10⁻¹⁹ C", "nature"),
        ("Speed of light (electric fields travel near it)", "299792458", "m/s", "nature"),
        ("Hydrogen ground-state energy", "13.6", "eV", "nature"),
    ]
    number_board(ELEC)
    finding("The strongest electrical link to 3 isn't a coincidence of digits. Three phases, 120° apart, "
            "are the smallest even set that makes a smooth spinning field. See Lens Ⅴ to watch it.")

# ======================= QUESTION EVERYTHING =======================
WORLD = [
    # (name, value, unit, category, kind)
    ("Bones in the adult body", "206", "", "Human body", "nature"),
    ("Vertebrae (typical count)", "33", "", "Human body", "nature"),
    ("Chromosomes", "46", "", "Human body", "nature"),
    ("Chromosome pairs", "23", "", "Human body", "nature"),
    ("Adult teeth", "32", "", "Human body", "nature"),
    ("Baby teeth", "20", "", "Human body", "nature"),
    ("Ribs", "24", "", "Human body", "nature"),
    ("Chambers of the heart", "4", "", "Human body", "nature"),
    ("Body temperature", "37", "°C", "Human body", "nature"),
    ("Body temperature (Fahrenheit)", "98.6", "°F", "Human body", "nature"),
    ("Weeks of pregnancy", "40", "", "Human body", "nature"),
    ("Sides of a honeycomb cell", "6", "", "Life", "nature"),
    ("Arms of a snowflake", "6", "", "Life", "nature"),
    ("Legs of an insect", "6", "", "Life", "nature"),
    ("Legs of a spider", "8", "", "Life", "nature"),
    ("DNA bases", "4", "", "Life", "nature"),
    ("Bases in a codon", "3", "", "Life", "nature"),
    ("Standard amino acids", "20", "", "Life", "nature"),
    ("Carbon's atomic number", "6", "", "Physics & chemistry", "nature"),
    ("Quarks in a proton", "3", "", "Physics & chemistry", "nature"),
    ("Generations of matter particles", "3", "", "Physics & chemistry", "nature"),
    ("Dimensions of space", "3", "", "Physics & chemistry", "nature"),
    ("Fine-structure constant (inverse)", "137.036", "", "Physics & chemistry", "nature"),
    ("Proton-to-electron mass ratio", "1836.15", "", "Physics & chemistry", "nature"),
    ("Avogadro's number", "6.02214076", "× 10²³", "Physics & chemistry", "nature"),
    ("Planck's constant", "6.62607015", "× 10⁻³⁴ J·s", "Physics & chemistry", "nature"),
    ("Gravitational constant", "6.674", "× 10⁻¹¹", "Physics & chemistry", "nature"),
    ("Absolute zero", "273.15", "°C below zero", "Physics & chemistry", "nature"),
    ("Sun's surface temperature", "5772", "K", "Sky", "nature"),
    ("Planets", "8", "", "Sky", "nature"),
    ("Age of the Earth", "4.54", "billion years", "Sky", "nature"),
    ("Age of the universe", "13.8", "billion years", "Sky", "nature"),
    ("Sidereal day", "86164", "s", "Sky", "nature"),
    ("Mount Everest", "8849", "m", "Earth", "nature"),
    ("Mount Everest (feet)", "29032", "ft", "Earth", "nature"),
    ("Challenger Deep", "10935", "m", "Earth", "nature"),
    ("Continents", "7", "", "Earth", "human-made"),
    ("Oceans", "5", "", "Earth", "human-made"),
    ("Semitones in an octave", "12", "", "Music", "human-made"),
    ("Pi", "3.14159", "", "Mathematics", "math"),
    ("Golden ratio", "1.61803", "", "Mathematics", "math"),
    ("e", "2.71828", "", "Mathematics", "math"),
    ("Tesla born", "1856", "", "Tesla", "history"),
    ("Tesla died", "1943", "", "Tesla", "history"),
    ("Wardenclyffe Tower begun", "1901", "", "Tesla", "history"),
]


def sig_digits(val):
    d = "".join(ch for ch in str(val) if ch.isdigit()).lstrip("0")
    return d or "0"


def build_pool(extra_lines):
    pool = [(n, v, u, c, k) for n, v, u, c, k in WORLD]
    for name, metric, mu, imp, iu, indep in SKY:
        pool.append((name, metric, mu, "Sky & Earth", "nature" if indep else "human-made"))
        if imp:
            pool.append((f"{name} (imperial)", imp, iu, "Sky & Earth", "nature"))
    for name, v, u, src in BIBLE:
        pool.append((name, v, u, "Scripture", "scripture"))
    for name, v, u, kind in ELEC:
        pool.append((name, v, u, "Electricity", "nature" if kind == "nature" else "human-made"))
    pool += extra_lines
    return pool


TRI_SET = {k * (k + 1) // 2 for k in range(1, 20000)}
FIB_SET, _a, _b = set(), 1, 2
while _a < 10 ** 15:
    FIB_SET.add(_a)
    _a, _b = _b, _a + _b

QE_LENSES = {
    "Digital root is 3, 6 or 9": (lambda D: digit_root_of_text(D) in TARGETS, False),
    "Digital root is exactly 9": (lambda D: digit_root_of_text(D) == 9, False),
    "Starts with 3, 6 or 9": (lambda D: D[0] in "369", False),
    "Ends with 3, 6 or 9": (lambda D: D[-1] in "369", False),
    "Every digit is 3, 6, 9 or 0": (lambda D: set(D) <= set("3690"), False),
    "Contains 369 or 963": (lambda D: "369" in D or "963" in D, False),
    "Reads the same backwards": (lambda D: len(D) > 1 and D == D[::-1], False),
    "Is a triangular number": (lambda D: int(D) in TRI_SET, True),
    "Is a Fibonacci number": (lambda D: int(D) in FIB_SET, True),
}


def control_digits(L, rng):
    """A fake measurement: log-uniform, like real-world numbers (Benford's law), same length."""
    x = 10 ** rng.uniform(0, 1)
    return f"{x:.{max(L - 1, 0)}f}".replace(".", "")[:L].lstrip("0") or "1"


@st.cache_data
def scan(pool, sims=400):
    rng = random.Random(369)
    results = []
    for lens, (fn, int_only) in QE_LENSES.items():
        hits, expected, n, who = 0, 0.0, 0, []
        for name, v, u, c, k in pool:
            if int_only and "." in v:
                continue
            D = sig_digits(v)
            n += 1
            if fn(D):
                hits += 1
                who.append(name)
            expected += sum(fn(control_digits(len(D), rng)) for _ in range(sims)) / sims
        rate = expected / n if n else 0
        p = binom_tail(hits, n, rate) if n and 0 < rate < 1 else (0.0 if hits and rate == 0 else 1.0)
        results.append(dict(lens=lens, n=n, hits=hits, expected=expected, p=p, who=who))
    return results


@st.cache_data
def ratio_scan(values, targets, tol, sims=200):
    vals = [x for x in values if x > 0]

    def count(vs):
        c = 0
        for a, b in itertools.combinations(vs, 2):
            r = max(a, b) / min(a, b)
            if any(abs(r - t) / t <= tol for t in targets):
                c += 1
        return c

    def fake(x, rng):
        # same size and same rounding as the real number, so whole numbers stay whole
        e = math.floor(math.log10(x))
        L = len(sig_digits(repr(x).rstrip("0").rstrip(".")))
        y = 10 ** (e + rng.uniform(0, 1))
        step = 10 ** (math.floor(math.log10(y)) - L + 1)
        return max(step, round(y / step) * step)

    obs = count(vals)
    rng = random.Random(9)
    ctrl = [count([fake(x, rng) for x in vals]) for _ in range(sims)]
    return obs, ctrl


with tabs[17]:
    st.subheader("❓ Question Everything")
    st.write("This engine pours every number in the app, plus measurements from across the world, through every "
             "lens at once. Then it questions each pattern it finds: could chance, units or cherry-picking explain it?")

    if "qe_extra" not in st.session_state:
        st.session_state.qe_extra = []
    pool_all = build_pool(st.session_state.qe_extra)

    c1, c2 = st.columns(2)
    cats = sorted({p[3] for p in pool_all})
    kinds = sorted({p[4] for p in pool_all})
    pick_c = c1.multiselect("Parts of the world", cats, default=cats)
    pick_k = c2.multiselect("Kinds of number", kinds, default=kinds,
                            help="Human-made numbers (like 360° or 24 hours) were chosen by people, "
                                 "so they can't prove anything about nature.")
    pool = tuple(p for p in pool_all if p[3] in pick_c and p[4] in pick_k)
    st.caption(f"Scanning {len(pool)} numbers through {len(QE_LENSES)} lenses.")

    if len(pool) < 5:
        st.warning("Pick more of the world to scan: at least 5 numbers.")
    else:
        res = scan(pool)
        nl = len(res)
        for r in res:
            r["p_adj"] = min(1.0, r["p"] * nl)
            if r["p_adj"] < 0.05:
                r["verdict"], r["col"] = "PATTERN SURVIVES", GREEN
            elif r["p"] < 0.05:
                r["verdict"], r["col"] = "LOOKS REAL, BUT…", AMBER
            else:
                r["verdict"], r["col"] = "CHANCE", GREY

        fig = go.Figure()
        fig.add_trace(go.Bar(y=[r["lens"] for r in res], x=[r["expected"] for r in res], orientation="h",
                             name="What chance predicts", marker_color="#3a3226"))
        fig.add_trace(go.Bar(y=[r["lens"] for r in res], x=[r["hits"] for r in res], orientation="h",
                             name="What the world shows", marker_color=[r["col"] if r["col"] != GREY else GOLD
                                                                        for r in res]))
        fig.update_layout(barmode="group", xaxis_title="Numbers that fit", yaxis_autorange="reversed",
                          legend=dict(orientation="h", y=-0.15))
        show_chart(style(fig, 520))

        st.dataframe([{"Lens": r["lens"], "Fit": f"{r['hits']} of {r['n']}", "Chance expects": round(r["expected"], 1),
                       "Odds by luck": f"{r['p']:.1%}", "After questioning": f"{r['p_adj']:.1%}",
                       "Verdict": r["verdict"]} for r in res], hide_index=True)
        finding("“After questioning” corrects for testing many lenses at once. Look at enough patterns and "
                "some will fit by luck, so each one has to clear a higher bar.")

        st.markdown("### Question a pattern")
        best = sorted(res, key=lambda r: r["p"])
        choice = st.selectbox("Pick a lens to interrogate", [r["lens"] for r in best])
        r = next(x for x in res if x["lens"] == choice)
        hit_rows = [p for p in pool if p[0] in r["who"]]
        st.write(f"**{len(hit_rows)} numbers fit:** " + ", ".join(f"{p[0]} ({p[1]})" for p in hit_rows[:40])
                 + ("…" if len(hit_rows) > 40 else ""))
        if hit_rows:
            human = sum(p[4] in ("human-made", "scripture", "history") for p in hit_rows)
            unit_dep = sum(p[2] in ("km", "mi", "ft", "m", "°F", "°C", "mi/s", "km/s", "s", "K") for p in hit_rows)
            short = sum(len(sig_digits(p[1])) <= 2 for p in hit_rows)
            checks = [
                ("Is it beyond chance?", r["p"] < 0.05, f"Odds by luck: {r['p']:.1%}"),
                ("Does it survive testing many lenses?", r["p_adj"] < 0.05, f"Corrected odds: {r['p_adj']:.1%}"),
                ("Is it mostly nature, not people's choices?", human <= len(hit_rows) / 2,
                 f"{human} of {len(hit_rows)} are human-made, scriptural or historical"),
                ("Does it avoid depending on units?", unit_dep <= len(hit_rows) / 2,
                 f"{unit_dep} of {len(hit_rows)} change if you switch units"),
                ("Is it more than tiny numbers?", short <= len(hit_rows) / 2,
                 f"{short} of {len(hit_rows)} have only one or two digits, which fit patterns easily"),
            ]
            passed = sum(ok for _, ok, _ in checks)
            for q_, ok, why in checks:
                st.markdown(f"{'🟢' if ok else '🔴'} **{q_}** {why}")
            finding(f"This pattern passes {passed} of {len(checks)} questions. "
                    + ("It's a real lead worth publishing in the repo." if passed == len(checks) else
                       "Keep it on the wall as amber until the red questions are answered."))

        st.markdown("### Hidden ratios")
        st.write("Every pair of numbers is divided, big by small, looking for ratios of 3, 6 or 9. "
                 "The control swaps each number for a random one of the same size and the same rounding, "
                 "so whole numbers stay whole and the test stays fair.")
        c1, c2 = st.columns(2)
        tg = c1.multiselect("Ratios to hunt for", [3, 6, 9, 1.5, 2, 1.618], default=[3, 6, 9])
        tol = c2.slider("How close counts as a match (%)", 0.1, 2.0, 0.5, step=0.1) / 100
        values = tuple(float(p[1]) for p in pool)
        if tg:
            obs, ctrl = ratio_scan(values, tuple(tg), tol)
            beat = sum(c >= obs for c in ctrl) / len(ctrl)
            hist = go.Figure(go.Histogram(x=ctrl, marker_color="#4a3f2a", name="Random worlds"))
            hist.add_vline(x=obs, line=dict(color=GOLD, width=3), annotation_text="our world")
            hist.update_layout(xaxis_title="Matching pairs", yaxis_title="Random worlds")
            show_chart(style(hist, 320))
            finding(f"Our world has {obs} matching pairs. Random worlds matched or beat that {beat:.0%} of the time. "
                    + ("That's a genuine signal." if beat < 0.05 else "So far, chance explains it."))
            pairs = []
            for (n1, v1, *_), (n2, v2, *_) in itertools.combinations(pool, 2):
                a, b = float(v1), float(v2)
                if a > 0 and b > 0:
                    rr_ = max(a, b) / min(a, b)
                    for t in tg:
                        if abs(rr_ - t) / t <= tol:
                            big, small = (n1, n2) if a >= b else (n2, n1)
                            pairs.append({"Bigger": big, "Smaller": small, "Ratio": round(rr_, 4), "Near": t})
            with st.expander(f"See all {len(pairs)} matching pairs"):
                st.dataframe(pairs, hide_index=True)

        with st.form("qe_add", clear_on_submit=True):
            st.write("Feed the engine your own numbers, one per line, like `Height of the Great Pyramid: 146.6`")
            txt = st.text_area("Your numbers")
            kd = st.selectbox("They are", ["nature", "human-made", "scripture", "history", "math"])
            if st.form_submit_button("Add and rescan") and txt:
                for line in txt.splitlines():
                    if ":" in line:
                        nme, val = line.rsplit(":", 1)
                        val = "".join(ch for ch in val if ch.isdigit() or ch == ".").strip(".")
                        if any(ch.isdigit() for ch in val):
                            st.session_state.qe_extra.append((nme.strip(), val, "", "Your numbers", kd))
                st.rerun()

st.markdown("---")
st.caption("If They Only Knew · built by Erin Rae Toppe · every claim open to testing")
