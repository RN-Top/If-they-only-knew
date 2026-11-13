import itertools
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="If They Only Knew", layout="wide")
st.markdown("""<style>
.stApp {background:#0b0b12; color:#e8e6d9;}
.card {border-radius:12px; padding:16px; margin:8px 0; background:#15151f;}
.green {border:2px solid #3ddc84; box-shadow:0 0 14px #3ddc84;}
.amber {border:2px solid #f5b942; box-shadow:0 0 14px #f5b942;}
.red {border:2px solid #ff5c5c; box-shadow:0 0 14px #ff5c5c;}
</style>""", unsafe_allow_html=True)

def droot(n):
    """Digital root: keep adding digits until one digit is left."""
    return 0 if n == 0 else 1 + (n - 1) % 9

st.title("If They Only Knew")
st.caption("Testing the significance of 3, 6 and 9 through every lens, with proof.")

wall, fam, circuit, grid, earth = st.tabs(
    ["The Wall", "The Family", "Doubling Circuit", "Nine-Box Grid", "As Above, So Below"])

CLAIMS = [
    ("Every multiple of 3 reduces to 3, 6 or 9", "green", "Proven: theorem, see The Family"),
    ("Doubling from 1 never touches 3, 6 or 9", "green", "Proven: see Doubling Circuit"),
    ("A nine-box grid can be perfectly balanced", "green", "Proven: 8 magic squares, see Nine-Box Grid"),
    ("Earth and sky numbers favour 3, 6, 9 beyond chance", "amber", "Open: see As Above, So Below"),
]

with wall:
    cols = st.columns(2)
    for i, (claim, colour, verdict) in enumerate(CLAIMS):
        cols[i % 2].markdown(
            f"<div class='card {colour}'><h4>{claim}</h4><p>{verdict}</p></div>",
            unsafe_allow_html=True)

with fam:
    n = st.slider("Check multiples up to", 30, 100000, 1000)
    base = st.selectbox("Compare against multiples of (control)", [3, 4, 5, 7], index=0)
    roots = [droot(k) for k in range(base, n + 1, base)]
    counts = [roots.count(d) for d in range(1, 10)]
    fig = go.Figure(go.Bar(x=list(range(1, 10)), y=counts,
        marker_color=["#f5b942" if d in (3, 6, 9) else "#555" for d in range(1, 10)]))
    fig.update_layout(template="plotly_dark", xaxis_title="Digital root", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)
    st.write(f"Digital roots found for multiples of {base}: {sorted(set(roots))}")

with circuit:
    pos = {k: (__import__('math').cos(__import__('math').radians(90 - 40 * k)),
               __import__('math').sin(__import__('math').radians(90 - 40 * k))) for k in range(1, 10)}
    seq, v = [], 1
    for _ in range(7):
        seq.append(droot(v)); v *= 2
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[pos[d][0] for d in seq], y=[pos[d][1] for d in seq],
        mode="lines", line=dict(color="#4fa3ff", width=3), name="Doubling 1-2-4-8-7-5"))
    tri = [3, 6, 9, 3]
    fig.add_trace(go.Scatter(x=[pos[d][0] for d in tri], y=[pos[d][1] for d in tri],
        mode="lines", line=dict(color="#f5b942", width=3), name="3-6-9"))
    fig.add_trace(go.Scatter(x=[pos[k][0] for k in pos], y=[pos[k][1] for k in pos],
        mode="markers+text", text=[str(k) for k in pos], textposition="middle center",
        marker=dict(size=36, color="#15151f", line=dict(color="#e8e6d9", width=2)),
        textfont=dict(size=16, color="#e8e6d9"), showlegend=False))
    fig.update_layout(template="plotly_dark", height=600, xaxis_visible=False,
        yaxis_visible=False, yaxis_scaleanchor="x")
    st.plotly_chart(fig, use_container_width=True)
    st.write("Doubling sequence (digital roots):", seq)

@st.cache_data
def magic_squares():
    found = []
    for p in itertools.permutations(range(1, 10)):
        g = [p[0:3], p[3:6], p[6:9]]
        lines = g + [tuple(r[c] for r in g) for c in range(3)] + \
            [(g[0][0], g[1][1], g[2][2]), (g[0][2], g[1][1], g[2][0])]
        if all(sum(l) == 15 for l in lines):
            found.append(g)
    return found

with grid:
    squares = magic_squares()
    st.write(f"Out of 362,880 ways to fill a nine-box grid with 1 to 9, "
             f"exactly {len(squares)} have every row, column and diagonal summing to 15.")
    i = st.slider("Show square", 1, len(squares), 1)
    g = squares[i - 1]
    fig = go.Figure(go.Heatmap(z=g, text=g, texttemplate="%{text}",
        colorscale=[[0, "#15151f"], [1, "#f5b942"]], showscale=False))
    fig.update_layout(template="plotly_dark", height=450, yaxis_autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

with earth:
    data = {
        "Degrees in a circle": 360, "Minutes in a day": 1440,
        "Seconds in a day": 86400, "Precession, traditional years": 25920,
        "Hours in a day": 24, "Days in a year": 365,
        "Days in a week": 7, "Speed of light, km/s": 299792,
    }
    rows, hits = [], 0
    for name, val in data.items():
        r = droot(val); hit = r in (3, 6, 9); hits += hit
        rows.append({"Measure": name, "Value": val, "Digital root": r, "3-6-9?": "yes" if hit else ""})
    st.table(rows)
    st.write(f"{hits} of {len(data)} land on 3, 6 or 9 ({hits/len(data):.0%}). "
             f"Pure chance would give about 33%.")
    st.info("Honest note: several of these come from 360 or 24, so they are not independent. "
            "Add more measurements to make the test stronger.")
