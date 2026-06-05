import math
from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="MOST Labor Scheduling Demo", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 3rem;}
html, body, [class*="css"] {font-family: Inter, Arial, sans-serif;}
.hero {padding: 2rem; border-radius: 28px; background: linear-gradient(135deg,#0b1020,#13244a 55%,#163b5f); border:1px solid rgba(255,255,255,.12); box-shadow: 0 20px 50px rgba(0,0,0,.22);}
.hero h1 {font-size: 2.8rem; line-height: 1.04; color:white; margin:0 0 .8rem 0;}
.hero p {font-size:1.1rem; color:rgba(255,255,255,.78); max-width:1000px;}
.card {padding:1.15rem; border-radius:22px; background:rgba(20,31,58,.72); border:1px solid rgba(255,255,255,.12); height:100%;}
.metric-card {padding:1rem; border-radius:18px; background:linear-gradient(135deg,#13244a,#0e182f); border:1px solid rgba(255,255,255,.12); text-align:center;}
.big {font-size:1.8rem; font-weight:800; color:white;}
.muted {color:rgba(255,255,255,.72);}
.pill {display:inline-block; padding:.32rem .75rem; border-radius:99px; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.16); color:white; margin-bottom:.65rem;}
.motion-row {display:flex; align-items:center; gap:.7rem; padding:.72rem .8rem; border-radius:16px; margin-bottom:.45rem; background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.10);}
.motion-row-active {background:rgba(88,166,255,.18); border:1px solid rgba(88,166,255,.42);}
.motion-icon {width:34px; height:34px; border-radius:12px; display:flex; align-items:center; justify-content:center; background:rgba(255,255,255,.12); font-weight:800;}
</style>
""", unsafe_allow_html=True)

@dataclass
class Motion:
    name: str
    label: str
    seconds: float
    most: str
    x: int
    y: int

MOTIONS = [
    Motion("Reach", "Extend arm to item", 1.2, "A1 B0 G1", 286, 86),
    Motion("Grasp", "Secure item", 0.7, "G1", 318, 120),
    Motion("Move", "Move item across station", 1.8, "A1 B1 P1", 364, 160),
    Motion("Place", "Release into tote", 0.9, "P1", 396, 218),
    Motion("Walk", "Walk to next position", 4.5, "A6", 198, 265),
    Motion("Scan", "Confirm item/location", 1.5, "A1 B0 P1", 300, 72),
]

if "step" not in st.session_state:
    st.session_state.step = 0

def clamp_step():
    st.session_state.step = max(0, min(st.session_state.step, len(MOTIONS)))

def next_step():
    st.session_state.step += 1
    clamp_step()

def reset_step():
    st.session_state.step = 0

def ceil_to_increment(minutes, inc):
    return int(math.ceil(minutes / inc) * inc)

def avatar_html(step: int) -> str:
    visible = MOTIONS[:step]
    active = MOTIONS[step-1] if step else MOTIONS[0]
    rows = ""
    for i, m in enumerate(visible, start=1):
        rows += f"""
        <div class='motion-row {'motion-row-active' if i == step else ''}'>
          <div class='motion-icon'>{i}</div>
          <div><b>{m.name}</b><br><span class='muted'>{m.label} · {m.most} · {m.seconds:.1f}s</span></div>
        </div>"""
    if not rows:
        rows = "<div class='muted'>Click Next motion to start filling the MOST sequence.</div>"

    arrows = ""
    for i, m in enumerate(visible, start=1):
        delay = max(0, i-1) * .06
        arrows += f"""
        <line x1='190' y1='130' x2='{m.x}' y2='{m.y}' class='arrow' style='animation-delay:{delay}s' />
        <circle cx='{m.x}' cy='{m.y}' r='7' fill='#70d6ff' opacity='.95'/>
        <text x='{m.x + 10}' y='{m.y - 5}' fill='white' font-size='13' font-weight='700'>{m.name}</text>
        """

    # arm and body positions change by active motion
    angles = {"Reach": -35, "Grasp": -10, "Move": 18, "Place": 45, "Walk": -5, "Scan": -25}
    leg_shift = 20 if active.name == "Walk" else 0
    arm_angle = angles.get(active.name, -25)

    return f"""
    <html><head><style>
    body {{margin:0; background:transparent; font-family:Inter,Arial,sans-serif; color:white;}}
    .wrap {{display:grid; grid-template-columns: 1.15fr .85fr; gap:18px; align-items:stretch;}}
    .panel {{background:linear-gradient(135deg,#0b1020,#122044); border:1px solid rgba(255,255,255,.13); border-radius:24px; padding:16px; min-height:430px;}}
    .muted {{color:rgba(255,255,255,.68);}}
    .motion-row {{display:flex; align-items:center; gap:.7rem; padding:.72rem .8rem; border-radius:16px; margin-bottom:.45rem; background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.10);}}
    .motion-row-active {{background:rgba(88,166,255,.18); border:1px solid rgba(88,166,255,.42);}}
    .motion-icon {{width:34px; height:34px; border-radius:12px; display:flex; align-items:center; justify-content:center; background:rgba(255,255,255,.12); font-weight:800;}}
    .arrow {{stroke:#70d6ff; stroke-width:4; stroke-linecap:round; marker-end:url(#arrowhead); stroke-dasharray:260; stroke-dashoffset:260; animation: draw .75s ease forwards;}}
    @keyframes draw {{to {{stroke-dashoffset:0;}}}}
    .arm {{transition: transform .5s ease; transform-origin: 180px 126px; transform: rotate({arm_angle}deg);}}
    .walkleg {{transform: translateX({leg_shift}px); transition: transform .5s ease;}}
    </style></head><body>
    <div class='wrap'>
      <div class='panel'>
        <svg viewBox='0 0 520 360' width='100%' height='400'>
          <defs>
            <marker id='arrowhead' markerWidth='10' markerHeight='10' refX='7' refY='3' orient='auto'>
              <path d='M0,0 L0,6 L7,3 z' fill='#70d6ff'/>
            </marker>
            <filter id='shadow'><feDropShadow dx='0' dy='8' stdDeviation='8' flood-color='#000' flood-opacity='.35'/></filter>
          </defs>
          <rect x='22' y='24' width='476' height='310' rx='28' fill='rgba(255,255,255,.035)' stroke='rgba(255,255,255,.13)'/>
          <line x1='70' y1='285' x2='455' y2='285' stroke='rgba(255,255,255,.22)' stroke-width='3'/>
          <rect x='360' y='185' width='76' height='55' rx='10' fill='#ffd166' filter='url(#shadow)'/>
          <rect x='298' y='112' width='48' height='36' rx='8' fill='#ff7b7b'/>
          <circle cx='165' cy='76' r='29' fill='#f1c79b' filter='url(#shadow)'/>
          <path d='M151 75 Q165 88 180 75' fill='none' stroke='#51311d' stroke-width='3' stroke-linecap='round'/>
          <rect x='132' y='108' width='67' height='98' rx='26' fill='#5aa7ff' filter='url(#shadow)'/>
          <line x1='143' y1='198' x2='118' y2='278' stroke='#dfe8ff' stroke-width='14' stroke-linecap='round'/>
          <line class='walkleg' x1='181' y1='198' x2='220' y2='278' stroke='#dfe8ff' stroke-width='14' stroke-linecap='round'/>
          <line x1='118' y1='278' x2='94' y2='284' stroke='#dfe8ff' stroke-width='10' stroke-linecap='round'/>
          <line x1='220' y1='278' x2='252' y2='284' stroke='#dfe8ff' stroke-width='10' stroke-linecap='round'/>
          <line x1='135' y1='130' x2='88' y2='164' stroke='#dfe8ff' stroke-width='14' stroke-linecap='round'/>
          <g class='arm'><line x1='180' y1='126' x2='260' y2='112' stroke='#dfe8ff' stroke-width='14' stroke-linecap='round'/><circle cx='268' cy='111' r='9' fill='#f1c79b'/></g>
          {arrows}
          <text x='50' y='56' fill='rgba(255,255,255,.72)' font-size='15'>Animated MOST motion capture</text>
          <text x='50' y='82' fill='white' font-size='26' font-weight='800'>{active.name if step else 'Ready'}</text>
        </svg>
      </div>
      <div class='panel'>
        <h3 style='margin-top:4px'>Live motion list</h3>
        {rows}
      </div>
    </div></body></html>
    """

def timeline_chart(df, title):
    fig = go.Figure()
    for _, r in df.iterrows():
        fig.add_trace(go.Bar(
            x=[r["End"] - r["Start"]], y=[r["Employee"]], base=[r["Start"]], orientation="h",
            text=[f'{r["Start"]}:00 to {r["End"]}:00'], hovertemplate="%{y}<br>%{text}<extra></extra>"
        ))
    fig.update_layout(
        title=title, barmode="stack", height=300, showlegend=False,
        xaxis=dict(range=[6,18], tickmode="array", tickvals=list(range(6,19)), ticktext=[f"{h}:00" for h in range(6,19)], title="Time"),
        yaxis=dict(autorange="reversed"), margin=dict(l=20,r=20,t=55,b=35)
    )
    return fig

st.markdown("""
<div class='hero'>
  <div class='pill'>Interactive MOST scheduling walkthrough</div>
  <h1>We build schedules from the work itself.</h1>
  <p>Instead of only using sales or historical labor ratios, we model the actual motions: reach, grasp, move, place, walk, scan. Those motions become labor minutes, labor minutes become staffed hours, and the algorithm builds a schedule managers can adjust.</p>
</div>
""", unsafe_allow_html=True)

st.write("")
st.header("1. Capture the work motion by motion")

c1, c2, c3, c4 = st.columns([.7,.7,.7,4])
with c1:
    st.button("Next motion", on_click=next_step, use_container_width=True)
with c2:
    st.button("Reset", on_click=reset_step, use_container_width=True)
with c3:
    st.metric("Step", f"{st.session_state.step}/{len(MOTIONS)}")

st.components.v1.html(avatar_html(st.session_state.step), height=470)

visible_df = pd.DataFrame([m.__dict__ for m in MOTIONS[:st.session_state.step]])
if not visible_df.empty:
    visible_df["Cumulative seconds"] = visible_df["seconds"].cumsum()
    st.dataframe(visible_df[["name", "label", "most", "seconds", "Cumulative seconds"]], use_container_width=True, hide_index=True)

st.header("2. Convert motions into labor minutes")
col1, col2, col3 = st.columns(3)
with col1:
    volume = st.slider("Items to process", 50, 2000, 420, 10)
with col2:
    allowance_pct = st.slider("Allowance", 0, 35, 15, 1)
with col3:
    increment = st.selectbox("Minimum staffing block", [15, 30, 60], index=2, format_func=lambda x: f"{x} minutes")

seconds_per_item = sum(m.seconds for m in MOTIONS)
raw_minutes = volume * seconds_per_item / 60
allowance_minutes = raw_minutes * allowance_pct / 100
required_minutes = raw_minutes + allowance_minutes
staffed_minutes = ceil_to_increment(required_minutes, increment)
rounding_gap = max(staffed_minutes - required_minutes, 0)

m1, m2, m3, m4 = st.columns(4)
for col, label, value in [
    (m1, "Seconds per item", f"{seconds_per_item:.1f}"),
    (m2, "Raw labor", f"{raw_minutes:.1f} min"),
    (m3, "With allowance", f"{required_minutes:.1f} min"),
    (m4, "Staffed time", f"{staffed_minutes} min"),
]:
    with col:
        st.markdown(f"<div class='metric-card'><div class='muted'>{label}</div><div class='big'>{value}</div></div>", unsafe_allow_html=True)

fig = go.Figure()
fig.add_bar(x=["Labor build"], y=[raw_minutes], name="Raw motion time", text=[f"{raw_minutes:.1f}"])
fig.add_bar(x=["Labor build"], y=[allowance_minutes], name="Allowance", text=[f"{allowance_minutes:.1f}"])
fig.add_bar(x=["Labor build"], y=[rounding_gap], name="Rounding gap", text=[f"{rounding_gap:.1f}"])
fig.update_layout(barmode="stack", height=360, title="Raw time + allowance + staffing rounding", yaxis_title="Minutes", margin=dict(l=20,r=20,t=55,b=30))
st.plotly_chart(fig, use_container_width=True)

st.header("3. Compare schedule logic from 6 AM to 6 PM")
left, right = st.columns(2)
with left:
    sales_forecast = st.number_input("Sales forecast", value=12000, step=500)
with right:
    sales_per_labor_hour = st.number_input("Sales per labor hour target", value=350, step=25)

sales_hours = sales_forecast / sales_per_labor_hour
most_hours = staffed_minutes / 60

sales_schedule = pd.DataFrame({
    "Employee": ["Sales method"] * 5,
    "Start": [8, 9, 10, 11, 12],
    "End": [9, 10, 11, 12, min(18, 12 + max(0, math.ceil(sales_hours)-4))],
})
most_needed = math.ceil(most_hours)
most_schedule = pd.DataFrame({
    "Employee": ["MOST method"] * max(1, min(most_needed, 12)),
    "Start": [8 + i for i in range(max(1, min(most_needed, 12)))],
    "End": [9 + i for i in range(max(1, min(most_needed, 12)))],
})

st.plotly_chart(timeline_chart(sales_schedule, "Sales-based coverage"), use_container_width=True)
st.plotly_chart(timeline_chart(most_schedule, "MOST-based coverage"), use_container_width=True)

st.header("4. Let the algorithm place people, then let the manager edit")
availability = pd.DataFrame({
    "Employee": ["Ana", "Ben", "Carla", "David", "Elena", "Marco"],
    "Available start": [6, 8, 9, 10, 12, 14],
    "Available end": [11, 16, 15, 18, 18, 18],
    "Preferred max hours": [4, 6, 5, 6, 5, 4],
})
edited = st.data_editor(availability, use_container_width=True, hide_index=True, key="availability")

remaining = most_hours
assignments = []
for _, r in edited.iterrows():
    available = max(0, min(r["Available end"] - r["Available start"], r["Preferred max hours"]))
    assigned = min(available, remaining)
    if assigned > 0:
        assignments.append({"Employee": r["Employee"], "Start": r["Available start"], "End": min(r["Available start"] + assigned, r["Available end"]), "Assigned hours": assigned})
        remaining -= assigned
    if remaining <= 0:
        break

assigned_df = pd.DataFrame(assignments)
if not assigned_df.empty:
    st.plotly_chart(timeline_chart(assigned_df, "Algorithm-generated draft schedule"), use_container_width=True)
    st.dataframe(assigned_df, use_container_width=True, hide_index=True)
else:
    st.warning("No coverage assigned.")

if remaining > 0:
    st.error(f"Uncovered labor need: {remaining:.1f} hours")
else:
    st.success("Labor need covered by available employees.")

st.header("5. Customer message")
st.markdown("""
<div class='card'>
<b>What this shows:</b><br>
Sales-based scheduling estimates labor from revenue. MOST-based scheduling estimates labor from the actual work. That makes it easier to explain why labor is needed, where time is being lost, and how staffing should change when item mix, walking distance, or task design changes.
</div>
""", unsafe_allow_html=True)
