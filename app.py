import math
from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Motion-Based Labor Scheduling",
    page_icon="⚙️",
    layout="wide",
)

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .main {background: #0b1020;}
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    h1, h2, h3, p, li, label, div {font-family: Inter, Arial, sans-serif;}
    h1 {font-size: 3rem !important; line-height: 1.05;}
    .hero {
        padding: 2rem;
        border-radius: 26px;
        background: linear-gradient(135deg, #101936 0%, #18284f 55%, #1f355f 100%);
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 18px 45px rgba(0,0,0,0.30);
    }
    .card {
        padding: 1.25rem;
        border-radius: 20px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        height: 100%;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 18px;
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.10);
        text-align: center;
    }
    .big-number {font-size: 2rem; font-weight: 800; color: #ffffff;}
    .muted {color: rgba(255,255,255,0.72);}
    .step-pill {
        display:inline-block;
        padding: .3rem .7rem;
        border-radius: 99px;
        background: rgba(255,255,255,.12);
        border: 1px solid rgba(255,255,255,.16);
        margin-bottom: .4rem;
        font-size: .85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Data model
# -----------------------------
@dataclass
class Motion:
    name: str
    description: str
    seconds: float
    icon: str

DEFAULT_MOTIONS = [
    Motion("Reach", "Extend arm to pick item", 1.2, "↗"),
    Motion("Grasp", "Secure the item", 0.7, "✋"),
    Motion("Move", "Move item to target location", 1.8, "➡"),
    Motion("Place", "Release item accurately", 0.9, "⬇"),
    Motion("Walk", "Walk to next work position", 4.5, "🚶"),
    Motion("Scan", "Confirm item or location", 1.5, "▣"),
]


def ceil_to_increment(minutes: float, increment: int) -> int:
    return int(math.ceil(minutes / increment) * increment)


def avatar_svg(selected_motion: str) -> str:
    arm_angle = {
        "Reach": "rotate(-35 160 120)",
        "Grasp": "rotate(-10 160 120)",
        "Move": "rotate(20 160 120)",
        "Place": "rotate(45 160 120)",
        "Walk": "rotate(-5 160 120)",
        "Scan": "rotate(-20 160 120)",
    }.get(selected_motion, "rotate(-25 160 120)")

    arrow = {
        "Reach": ("M250 78 L325 42", "Extend arm"),
        "Grasp": ("M260 105 L330 105", "Secure item"),
        "Move": ("M250 145 L345 145", "Move item"),
        "Place": ("M255 155 L310 220", "Place down"),
        "Walk": ("M130 260 L235 260", "Walk path"),
        "Scan": ("M250 90 L330 65", "Scan"),
    }.get(selected_motion, ("M250 78 L325 42", "Motion"))

    return f"""
    <svg viewBox="0 0 520 330" width="100%" height="330" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="5" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L6,3 z" fill="#77d4ff" />
        </marker>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#000" flood-opacity=".35"/>
        </filter>
      </defs>
      <rect x="20" y="20" width="480" height="290" rx="28" fill="#111a33" stroke="rgba(255,255,255,.18)"/>
      <line x1="80" y1="270" x2="440" y2="270" stroke="rgba(255,255,255,.25)" stroke-width="3"/>
      <circle cx="160" cy="78" r="28" fill="#f3c79b" filter="url(#shadow)"/>
      <rect x="130" y="108" width="60" height="92" rx="24" fill="#4f8cff" filter="url(#shadow)"/>
      <line x1="148" y1="198" x2="125" y2="260" stroke="#d7e2ff" stroke-width="13" stroke-linecap="round"/>
      <line x1="176" y1="198" x2="210" y2="260" stroke="#d7e2ff" stroke-width="13" stroke-linecap="round"/>
      <line x1="125" y1="260" x2="105" y2="267" stroke="#d7e2ff" stroke-width="10" stroke-linecap="round"/>
      <line x1="210" y1="260" x2="236" y2="267" stroke="#d7e2ff" stroke-width="10" stroke-linecap="round"/>
      <g transform="{arm_angle}">
        <line x1="185" y1="125" x2="255" y2="110" stroke="#d7e2ff" stroke-width="13" stroke-linecap="round"/>
        <circle cx="263" cy="108" r="9" fill="#f3c79b"/>
      </g>
      <line x1="136" y1="125" x2="92" y2="158" stroke="#d7e2ff" stroke-width="13" stroke-linecap="round"/>
      <rect x="310" y="165" width="68" height="52" rx="8" fill="#ffc857" stroke="#fff" stroke-opacity=".35"/>
      <path d="{arrow[0]}" stroke="#77d4ff" stroke-width="5" fill="none" marker-end="url(#arrow)"/>
      <text x="340" y="55" fill="#ffffff" font-size="20" font-weight="700">{selected_motion}</text>
      <text x="340" y="82" fill="rgba(255,255,255,.72)" font-size="15">{arrow[1]}</text>
      <text x="65" y="52" fill="rgba(255,255,255,.72)" font-size="15">MOST motion breakdown</text>
    </svg>
    """

# -----------------------------
# Hero
# -----------------------------
st.markdown(
    """
    <div class="hero">
      <div class="step-pill">Motion-based scheduling demo</div>
      <h1>We build schedules from the work itself, not just sales history.</h1>
      <p class="muted" style="font-size:1.15rem; max-width:950px;">
        The algorithm estimates labor by modeling the motions required to complete each task: reach, grasp, move, place, walk, scan, and repeat.
        Then it converts those motions into labor hours, adds realistic allowances, rounds into staffing rules, and builds an editable schedule.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# -----------------------------
# Section 1: Motion demo
# -----------------------------
st.header("1. Start with the task motions")
left, right = st.columns([1.2, 1])

with left:
    selected_motion = st.selectbox("Select a motion", [m.name for m in DEFAULT_MOTIONS], index=0)
    st.components.v1.html(avatar_svg(selected_motion), height=350)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Example task: Pick and place item")
    task_volume = st.slider("Items to process", 50, 2000, 420, step=10)
    allowance_pct = st.slider("Allowance for breaks, fatigue, delays", 0, 35, 15, step=1)
    rounding_increment = st.selectbox("Staffing time increment", [15, 30, 60], index=2, format_func=lambda x: f"{x} minutes")
    st.caption("Allowance covers breaks, fatigue, normal interruptions, and the fact that people are not machines.")
    st.markdown('</div>', unsafe_allow_html=True)

motions_df = pd.DataFrame([m.__dict__ for m in DEFAULT_MOTIONS])
sequence = ["Reach", "Grasp", "Move", "Place", "Walk", "Scan"]
selected_rows = motions_df[motions_df["name"].isin(sequence)].copy()
seconds_per_item = selected_rows["seconds"].sum()
raw_minutes = task_volume * seconds_per_item / 60
allowance_minutes = raw_minutes * allowance_pct / 100
required_minutes = raw_minutes + allowance_minutes
staffed_minutes = ceil_to_increment(required_minutes, rounding_increment)

st.write("")
metric_cols = st.columns(4)
metrics = [
    ("Seconds per item", f"{seconds_per_item:.1f}"),
    ("Raw labor", f"{raw_minutes:.1f} min"),
    ("With allowance", f"{required_minutes:.1f} min"),
    ("Staffed time", f"{staffed_minutes} min"),
]
for col, (label, value) in zip(metric_cols, metrics):
    with col:
        st.markdown(f'<div class="metric-card"><div class="muted">{label}</div><div class="big-number">{value}</div></div>', unsafe_allow_html=True)

# -----------------------------
# Section 2: Build time
# -----------------------------
st.header("2. Convert motion time into labor need")
chart_df = pd.DataFrame({
    "Component": ["Raw motion time", "Allowance", "Rounding gap"],
    "Minutes": [raw_minutes, allowance_minutes, max(staffed_minutes - required_minutes, 0)],
})
fig = px.bar(chart_df, x="Component", y="Minutes", text="Minutes", title="Labor time build-up")
fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
fig.update_layout(height=420, margin=dict(l=20, r=20, t=60, b=20))
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Section 3: Compare sales-based vs motion-based
# -----------------------------
st.header("3. Compare against a sales-per-labor-hour schedule")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Sales-based method")
    sales_forecast = st.number_input("Sales forecast", value=12000, step=500)
    sales_per_labor_hour = st.number_input("Sales per labor hour target", value=350, step=25)
    sales_based_hours = sales_forecast / sales_per_labor_hour
    st.metric("Labor hours suggested", f"{sales_based_hours:.1f}")
    st.caption("This method assumes sales are a good proxy for work. It can miss item complexity, walking distance, handling motions, and operational friction.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_b:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Motion-based method")
    motion_based_hours = staffed_minutes / 60
    st.metric("Labor hours required", f"{motion_based_hours:.1f}")
    st.caption("This method estimates the physical work directly, then converts it into a schedule with real staffing rules.")
    st.markdown('</div>', unsafe_allow_html=True)

compare_df = pd.DataFrame({
    "Method": ["Sales per labor hour", "Motion-based MOST"],
    "Labor hours": [sales_based_hours, motion_based_hours],
})
fig2 = px.bar(compare_df, x="Method", y="Labor hours", text="Labor hours", title="Labor hours comparison")
fig2.update_traces(texttemplate="%{text:.1f}", textposition="outside")
fig2.update_layout(height=420, margin=dict(l=20, r=20, t=60, b=20))
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Section 4: Schedule allocation
# -----------------------------
st.header("4. Build an editable schedule from availability")

availability = pd.DataFrame({
    "Employee": ["Ana", "Ben", "Carla", "David", "Elena"],
    "Available start": [8, 8, 9, 10, 12],
    "Available end": [12, 16, 15, 18, 18],
    "Preferred max hours": [4, 6, 5, 6, 5],
})
st.data_editor(availability, use_container_width=True, hide_index=True, key="availability_editor")

needed_hours = motion_based_hours
remaining = needed_hours
assignments = []
for _, row in availability.iterrows():
    available_hours = min(row["Available end"] - row["Available start"], row["Preferred max hours"])
    assigned = max(0, min(available_hours, remaining))
    if assigned > 0:
        assignments.append({
            "Employee": row["Employee"],
            "Start": row["Available start"],
            "End": row["Available start"] + assigned,
            "Assigned hours": assigned,
        })
        remaining -= assigned
    if remaining <= 0:
        break

schedule_df = pd.DataFrame(assignments)
if schedule_df.empty:
    st.warning("No hours assigned. Increase employee availability.")
else:
    timeline_df = schedule_df.copy()
    timeline_df["Start label"] = timeline_df["Start"].apply(lambda x: f"{int(x):02d}:00")
    timeline_df["End label"] = timeline_df["End"].apply(lambda x: f"{int(x):02d}:{int((x%1)*60):02d}")
    fig3 = px.timeline(
        timeline_df,
        x_start="Start",
        x_end="End",
        y="Employee",
        hover_data=["Assigned hours"],
        title="Algorithm-generated schedule draft",
    )
    fig3.update_yaxes(autorange="reversed")
    fig3.update_layout(height=420, margin=dict(l=20, r=20, t=60, b=20), xaxis_title="Hour of day")
    st.plotly_chart(fig3, use_container_width=True)
    st.dataframe(schedule_df, use_container_width=True, hide_index=True)

if remaining > 0:
    st.error(f"Uncovered labor need: {remaining:.1f} hours")
else:
    st.success("Labor need covered by available employees.")

# -----------------------------
# Section 5: Closing pitch
# -----------------------------
st.header("5. What the customer gets")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="card"><h3>Better labor estimates</h3><p class="muted">Labor is calculated from task motions, item types, process paths, and realistic allowances.</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="card"><h3>Smarter scheduling</h3><p class="muted">The algorithm places people where the work is, respecting availability and staffing rules.</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="card"><h3>Editable control</h3><p class="muted">Managers can adjust the schedule while still seeing the operational impact.</p></div>', unsafe_allow_html=True)

st.write("")
st.info("Next version: connect this to real task data, item categories, walking distances, employee availability, and customer-specific labor rules.")
