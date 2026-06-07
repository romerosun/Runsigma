import base64
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="MOST Scheduling Demo", layout="wide")

st.markdown("""
<style>
.stApp {background:#070b14;color:#f8fafc;}
.block-container {padding-top:2rem; max-width:1500px;}
.card {background:linear-gradient(180deg,#0e1b33,#08111f); border:1px solid #21436d; border-radius:18px; padding:22px;}
.kicker {letter-spacing:6px;color:#60a5fa;font-weight:900;font-size:13px;}
.big {font-size:34px;font-weight:900;margin:0;}
.metric {border:1px solid #21436d;border-radius:14px;padding:14px;background:#08172b;margin-bottom:10px;}
.metric small{color:#93c5fd;text-transform:uppercase;letter-spacing:1.5px;}
.metric b{float:right;font-size:24px;}
.motion-row {display:flex;align-items:center;gap:12px;border-bottom:1px solid #132641;padding:12px 0;}
.check {width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#052e1a;color:#4ade80;font-weight:900;}
.wait {width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#111827;color:#64748b;font-weight:900;}
</style>
""", unsafe_allow_html=True)

MOTIONS = [
    ("Approach", "Worker positions body toward the item", 10, 0.10),
    ("Reach", "Arm extends toward the object", 16, 0.25),
    ("Bend", "Body lowers to access the item", 30, 0.43),
    ("Grasp", "Hand gains control of the item", 3, 0.58),
    ("Lift", "Object is raised under control", 16, 0.75),
    ("Return", "Worker returns to stable posture", 10, 0.92),
]

with st.sidebar:
    st.header("3D file")
    uploaded = st.file_uploader("Upload model", type=["glb", "gltf", "fbx"])
    st.caption("Best: GLB under 25 MB. Large FBX files often crash browsers.")
    allowance = st.slider("Allowance %", 0, 35, 15)
    step = st.slider("Demo progress", 0, len(MOTIONS), 1)

left, right = st.columns([1.65, 1], gap="large")

with left:
    st.markdown('<div class="card"><div class="kicker">3D MOST CAPTURE</div><p class="big">Picking Up motion</p>', unsafe_allow_html=True)
    if uploaded:
        size_mb = uploaded.size / 1024 / 1024
        st.caption(f"Loaded: {uploaded.name} | {size_mb:.1f} MB")
        if uploaded.name.lower().endswith(".fbx"):
            st.error("FBX is not loaded in-browser in this safe version. Convert it to GLB first.")
        elif size_mb > 25:
            st.error("Model is too large for a stable web demo. Compress under 25 MB.")
        else:
            data = base64.b64encode(uploaded.getvalue()).decode("utf-8")
            html = f"""
            <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{data}" camera-controls autoplay animation-name="*" exposure="1" shadow-intensity="1" style="width:100%;height:620px;background:#050a16;border:1px solid #21436d;border-radius:16px;"></model-viewer>
            """
            st.components.v1.html(html, height=650)
    else:
        st.markdown("""
        <div style="height:620px;border:1px solid #21436d;border-radius:16px;background:radial-gradient(circle at 50% 60%,#1f2d46 0,#111b2f 32%,#050a16 70%);display:flex;align-items:center;justify-content:center;color:#93c5fd;font-weight:800;">
          Upload a compressed GLB model here<br><br>FBX → Blender → Export GLB
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

active = MOTIONS[:step]
raw_sec = sum(x[2] for x in active) * 0.036
std_sec = raw_sec * (1 + allowance / 100)

with right:
    st.markdown('<div class="card"><h2>Live MOST breakdown</h2>', unsafe_allow_html=True)
    progress = int(100 * step / len(MOTIONS))
    st.progress(progress)
    for i, (name, desc, tmu, _) in enumerate(MOTIONS):
        done = i < step
        icon_class = "check" if done else "wait"
        icon = "✓" if done else "•"
        opacity = "1" if done else ".35"
        st.markdown(f"""
        <div class="motion-row" style="opacity:{opacity}">
          <div class="{icon_class}">{icon}</div>
          <div style="flex:1"><b>{name}</b><br><span style="color:#94a3b8;font-size:13px">{desc}</span></div>
          <div style="color:#7dd3fc;font-weight:900">{tmu} TMU</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metric"><small>Raw time</small><b>{raw_sec:.1f} sec</b></div>
    <div class="metric"><small>Allowance</small><b>{allowance}%</b></div>
    <div class="metric"><small>Standard time</small><b>{std_sec:.1f} sec</b></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### Schedule view: 6 AM to 6 PM")
hours = list(range(6,19))
sales = [1,1,2,2,3,4,5,5,4,3,3,2,1]
most =  [1,2,2,3,4,5,6,5,5,4,3,2,2]
fig = go.Figure()
fig.add_trace(go.Bar(x=hours, y=sales, name="Sales/labor-hour staffing"))
fig.add_trace(go.Bar(x=hours, y=most, name="MOST-based staffing"))
fig.update_layout(barmode="stack", height=420, paper_bgcolor="#070b14", plot_bgcolor="#070b14", font_color="white", xaxis=dict(tickmode="array", tickvals=hours, ticktext=[f"{h} AM" if h<12 else ("12 PM" if h==12 else f"{h-12} PM") for h in hours], title="Hour"), yaxis_title="Staff hours", legend=dict(orientation="h"))
st.plotly_chart(fig, use_container_width=True)
