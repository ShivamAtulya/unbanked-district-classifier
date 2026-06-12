import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import base64

# Page Config
st.set_page_config(
    page_title="Indian Unbanked District Classifier",
    page_icon="🏦",
    layout="wide"
)

# ── Minimal CSS (only overrides that Streamlit respects) ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body {
    font-family: 'Inter', sans-serif;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {display: none !important;}

/* Remove top padding */
.block-container {
    padding-top: 1rem !important;
}
[data-testid="stAppViewContainer"] {
    padding-top: 0 !important;
}

/* Hide anchor link icons on headers */
a.header-anchor, .stMarkdown a[href^="#"], h1 a, h2 a, h3 a,
[data-testid="stHeaderActionElements"] {
    display: none !important;
}

/* Streamlit metric card styling */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(30,32,44,0.9), rgba(22,24,34,0.95));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
}
div[data-testid="stMetric"] label {
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: rgba(255,255,255,0.45) !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #818cf8 !important;
}

/* Selectbox styling */
div[data-baseweb="select"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ── Load Data ──
df = pd.read_csv("final_clustered_dataset.csv")
# Strip whitespace from all string columns
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].str.strip()


# ── Navbar ──
st.markdown("""
<table style="width:100%; background:transparent; border-radius:14px; padding:12px 28px; border:none; margin-bottom:20px; border-collapse:separate; border-spacing:0;">
<tr>
<td style="border:none; padding:12px 16px;">
    <span style="font-size:2.5rem; font-weight:800; color:#38bdf8; white-space:nowrap;">🏦 Indian Unbanked District Classifier</span>
</td>
<td style="border:none; text-align:right; padding:6px 14px; white-space:nowrap; background:#1e2030; border-radius:10px; border:1px solid rgba(255,255,255,0.06);">
    <span class="nav-item" data-target="dashboard" style="color:#e2e8f0; font-size:1.6rem; font-weight:600; cursor:pointer;">🏠 Dashboard</span>
    <span class="nav-item" data-target="explorer" style="color:#e2e8f0; font-size:1.6rem; font-weight:600; margin-left:20px; cursor:pointer;">🔍 Explorer</span>
    <span class="nav-item" data-target="analytics" style="color:#e2e8f0; font-size:1.6rem; font-weight:600; margin-left:20px; cursor:pointer;">📊 Analytics</span>
</td>
</tr>
</table>
""", unsafe_allow_html=True)

# Hidden JS to wire up navbar click → scroll
components.html("""
<script>
(function() {
  const doc = window.parent.document;
  const items = doc.querySelectorAll('.nav-item');
  items.forEach(function(item) {
    item.addEventListener('click', function() {
      const target = item.getAttribute('data-target');
      const el = doc.getElementById(target);
      if (el) el.scrollIntoView({behavior: 'smooth', block: 'start'});
    });
  });
})();
</script>
""", height=0)


# ══════════════════════════════════════════════
# SECTION 1 — DASHBOARD
# ══════════════════════════════════════════════

st.markdown('<div id="dashboard"></div>', unsafe_allow_html=True)

# Metrics — using Streamlit native components
total_districts = len(df)
total_pop = f"{df['Population'].sum():,.0f}"
total_branches = f"{int(df['num_branches'].sum()):,}"
total_csp = f"{int(df['num_csp'].sum()):,}"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Districts Analyzed", total_districts)
col2.metric("Total Population", total_pop)
col3.metric("Bank Branches", total_branches)
col4.metric("CSPs", total_csp)

st.markdown("---")


# ══════════════════════════════════════════════
# SECTION 2 — DISTRICT EXPLORER
# ══════════════════════════════════════════════

st.markdown('<div id="explorer"></div>', unsafe_allow_html=True)
st.header("🔍 District Explorer")
st.caption("Select a state and district to explore detailed banking data")

col_s, col_d = st.columns(2)

with col_s:
    selected_state = st.selectbox(
        "Select State",
        sorted(df["State"].unique()),
        key="state_select"
    )

with col_d:
    districts = sorted(
        df[df["State"] == selected_state]["District"].unique()
    )
    selected_district = st.selectbox(
        "Select District",
        districts,
        key="district_select"
    )

district_data = df[
    (df["State"] == selected_state) &
    (df["District"] == selected_district)
]

if not district_data.empty:
    row = district_data.iloc[0]

    # Priority badge with inline style
    priority = row["Priority_Level"]
    badge_colors = {
        "Critical Priority": ("#f87171", "rgba(239,68,68,0.15)", "rgba(239,68,68,0.3)"),
        "Moderate Priority": ("#fbbf24", "rgba(251,191,36,0.12)", "rgba(251,191,36,0.25)"),
        "Well Served": ("#34d399", "rgba(52,211,153,0.12)", "rgba(52,211,153,0.25)"),
        "Highly Served": ("#10b981", "rgba(16,185,129,0.15)", "rgba(16,185,129,0.3)")
    }
    text_c, bg_c, border_c = badge_colors.get(priority, ("#34d399", "rgba(52,211,153,0.12)", "rgba(52,211,153,0.25)"))

    st.markdown(f"""
    <span style="
        display:inline-block; padding:6px 18px; border-radius:20px;
        font-size:0.9rem; font-weight:600; letter-spacing:0.4px;
        color:{text_c}; background:{bg_c}; border:1px solid {border_c};
    ">{priority}</span>
    """, unsafe_allow_html=True)

    st.write("")

    # District info in 2-column layout
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown(f"**State:** {row['State']}")
        st.markdown(f"**District:** {row['District']}")
        st.markdown(f"**Population:** {row['Population']:,}")
        st.markdown(f"**Area (km²):** {row['Area_km2']:,.0f}")

    with info_col2:
        st.markdown(f"**Bank Branches:** {row['num_branches']}")
        st.markdown(f"**CSPs:** {row['num_csp']}")
        st.markdown(f"**Branches per 100k:** {row['branches_per_100k']:.2f}")
        st.markdown(f"**CSP per 100k:** {row['csp_per_100k']:.2f}")

st.markdown("---")


# ══════════════════════════════════════════════
# SECTION 3 — ANALYTICS
# ══════════════════════════════════════════════

st.markdown('<div id="analytics"></div>', unsafe_allow_html=True)
st.header("📊 Analytics Dashboard")
st.caption("Comprehensive banking accessibility analysis")

# Priority count cards
critical_count = len(df[df["Priority_Level"] == "Critical Priority"])
moderate_count = len(df[df["Priority_Level"] == "Moderate Priority"])
well_count = len(df[df["Priority_Level"] == "Well Served"])
highly_count = len(df[df["Priority_Level"] == "Highly Served"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("🚨 Critical", critical_count)
c2.metric("⚠️ Moderate", moderate_count)
c3.metric("✅ Well Served", well_count)
c4.metric("🌟 Highly Served", highly_count)

st.write("")

# ── Population by Priority Level ──
st.subheader("👥 Population by Priority Level")
pop_summary = (
    df.groupby("Priority_Level")["Population"]
    .sum()
    .reset_index()
)

import plotly.graph_objects as go

color_map = {
    "Critical Priority": "#f87171",
    "Moderate Priority": "#fbbf24",
    "Well Served": "#34d399",
    "Highly Served": "#10b981"
}
colors = [color_map.get(p, "#888") for p in pop_summary["Priority_Level"]]

fig_pop = go.Figure(data=[go.Pie(
    labels=pop_summary["Priority_Level"].tolist(),
    values=pop_summary["Population"].tolist(),
    hole=0.45,
    marker=dict(colors=colors),
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Population: %{value:,.0f}<br>Share: %{percent}<extra></extra>"
)])
fig_pop.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="rgba(255,255,255,0.7)",
    margin=dict(l=20, r=20, t=20, b=20),
    legend=dict(font=dict(size=11))
)
st.plotly_chart(fig_pop, use_container_width=True)

st.write("")

# ── Top States by Banking Accessibility ──
st.subheader("🏆 Top 10 States by Banking Accessibility")

state_score = (
    df.groupby("State")["branches_per_100k"]
    .mean()
    .reset_index()
    .sort_values(by="branches_per_100k", ascending=False)
    .head(10)
)

fig_state = px.bar(
    x=state_score["State"].tolist(),
    y=state_score["branches_per_100k"].tolist(),
    color=state_score["branches_per_100k"].tolist(),
    color_continuous_scale=["#6366f1", "#a78bfa", "#c4b5fd"],
    labels={"x": "State", "y": "Branches per 100k", "color": "Branches per 100k"}
)
fig_state.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="rgba(255,255,255,0.7)",
    margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
)
st.plotly_chart(fig_state, use_container_width=True)

st.write("")

# ── State-wise Banking Accessibility Table ──
st.subheader("🏛️ State-wise Banking Accessibility")
state_summary = (
    df.groupby("State")["Priority_Level"]
    .value_counts()
    .unstack(fill_value=0)
)
st.dataframe(state_summary, use_container_width=True)

st.write("")

# ── Top 10 Critical Districts ──
st.subheader("🚨 Top 10 Critical Districts by Population")
critical_df = df[df["Priority_Level"] == "Critical Priority"]
top10 = critical_df.nlargest(10, "Population")[
    ["State", "District", "Population", "num_branches", "num_csp"]
]
st.dataframe(top10, use_container_width=True)

st.markdown("---")

# Footer
st.markdown("""
<p style="text-align:center; padding:40px 0 24px; color:rgba(255,255,255,0.3); font-size:0.8rem;">
    Built with Streamlit & Plotly · Indian Unbanked District Classifier
</p>
""", unsafe_allow_html=True)