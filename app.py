import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit.components.v1 import html

st.set_page_config(page_title="MOST Motion Scheduling Demo", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.block-container {padding-top: 1.2rem; max-width: 1400px;}
.hero {background: linear-gradient(135deg,#0b1220,#111f3d); border:1px solid #263855; border-radius:24px; padding:28px 32px; margin-bottom:22px;}
.hero h1 {font-size: 42px; margin:0; line-height:1.05;}
.hero p {font-size:18px; color:#cbd5e1; max-width:900px; margin-top:12px;}
.card {background:#0f172a; border:1px solid #263855; border-radius:20px; padding:20px;}
.metric {background:#0b1220; border:1px solid #263855; border-radius:16px; padding:18px; text-align:center;}
.metric .label {color:#94a3b8; font-size:13px; text-transform:uppercase; letter-spacing:.08em;}
.metric .value {font-size:30px; font-weight:800; margin-top:4px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>Motion-based labor scheduling</h1>
  <p>Instead of scheduling only from sales history, this demo builds labor demand from the physical work itself: reach, bend, grasp, lift, walk, place, scan, plus human allowances.</p>
</div>
""", unsafe_allow_html=True)

viewer_html = r'''
<div id="app">
  <div class="stage">
    <div class="topbar">
      <div>
        <div class="eyebrow">3D MOST capture</div>
        <div class="title">Picking Up motion</div>
      </div>
      <div class="controls">
        <button id="playBtn">Play</button>
        <button id="pauseBtn">Pause</button>
        <button id="resetBtn">Reset</button>
      </div>
    </div>
    <div class="body">
      <div class="viewerWrap">
        <canvas id="c"></canvas>
        <div id="motionLabel" class="floating">Loading FBX...</div>
      </div>
      <div class="panel">
        <div class="panelTitle">Live MOST breakdown</div>
        <div class="progressShell"><div id="progressBar"></div></div>
        <div id="stepList"></div>
        <div class="totals">
          <div><span>Raw time</span><b id="rawTime">0.0 sec</b></div>
          <div><span>Allowance</span><b>15%</b></div>
          <div><span>Standard time</span><b id="stdTime">0.0 sec</b></div>
        </div>
      </div>
    </div>
  </div>
</div>
<style>
#app {font-family: Inter, system-ui, Segoe UI, sans-serif; color:#f8fafc;}
.stage {background:linear-gradient(145deg,#0f172a,#111f3d); border:1px solid #2b3b5b; border-radius:24px; padding:20px; min-height:680px; box-shadow:0 20px 70px rgba(0,0,0,.35);}
.topbar {display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;}
.eyebrow {color:#60a5fa; font-size:13px; letter-spacing:.12em; text-transform:uppercase; font-weight:700;}
.title {font-size:30px; font-weight:900;}
.controls button {background:#172554; color:white; border:1px solid #3b82f6; border-radius:12px; padding:12px 18px; margin-left:8px; font-weight:800; cursor:pointer;}
.controls button:hover {background:#1d4ed8;}
.body {display:grid; grid-template-columns: 1.35fr .9fr; gap:18px;}
.viewerWrap {position:relative; min-height:590px; border-radius:20px; overflow:hidden; background:radial-gradient(circle at center,#1e293b,#020617); border:1px solid #334155;}
#c {width:100%; height:590px; display:block;}
.floating {position:absolute; left:24px; top:24px; background:rgba(15,23,42,.82); border:1px solid #60a5fa; border-radius:16px; padding:14px 18px; font-size:22px; font-weight:900; box-shadow:0 0 30px rgba(96,165,250,.25);}
.panel {background:rgba(2,6,23,.7); border:1px solid #334155; border-radius:20px; padding:20px; min-height:590px;}
.panelTitle {font-size:24px; font-weight:900; margin-bottom:14px;}
.progressShell {height:12px; background:#1e293b; border-radius:999px; overflow:hidden; margin-bottom:18px;}
#progressBar {height:100%; width:0%; background:linear-gradient(90deg,#38bdf8,#22c55e); transition:width .12s linear;}
.step {display:grid; grid-template-columns: 34px 1fr 72px; align-items:center; gap:10px; padding:14px 10px; border-bottom:1px solid #1e293b; opacity:.38; transform:translateX(10px); transition:all .25s ease;}
.step.active {opacity:1; transform:translateX(0); background:rgba(96,165,250,.09); border-radius:12px; border-bottom-color:transparent;}
.check {height:26px; width:26px; display:grid; place-items:center; border-radius:50%; background:#1e293b; color:#64748b; font-weight:900;}
.step.active .check {background:#22c55e; color:#022c22;}
.motion {font-weight:900; font-size:16px;}
.desc {color:#94a3b8; font-size:13px; margin-top:3px;}
.tmu {font-weight:900; color:#7dd3fc; text-align:right;}
.totals {margin-top:20px; display:grid; grid-template-columns:1fr; gap:12px;}
.totals div {display:flex; justify-content:space-between; align-items:center; padding:14px; background:#0f172a; border:1px solid #263855; border-radius:14px;}
.totals span {color:#94a3b8; text-transform:uppercase; font-size:12px; letter-spacing:.08em;}
.totals b {font-size:22px;}
@media (max-width: 900px) {.body{grid-template-columns:1fr}.viewerWrap,#c{height:470px;min-height:470px}.panel{min-height:auto}}
</style>
<script type="importmap">
{"imports":{"three":"https://unpkg.com/three@0.160.0/build/three.module.js","three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"}}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';

const steps = [
  {p:.08, name:'Approach', desc:'Body positions toward the item', tmu:10},
  {p:.22, name:'Reach', desc:'Arm extends toward the object', tmu:16},
  {p:.40, name:'Bend', desc:'Body lowers to access the item', tmu:30},
  {p:.58, name:'Grasp', desc:'Hand gains control of the item', tmu:3},
  {p:.76, name:'Lift', desc:'Object is raised under control', tmu:16},
  {p:.92, name:'Return', desc:'Worker returns to stable posture', tmu:10}
];
const secondsPerTMU = 0.036;
const allowance = .15;
const stepList = document.getElementById('stepList');
steps.forEach((s,i)=>{
  const row = document.createElement('div'); row.className='step'; row.id='step'+i;
  row.innerHTML = `<div class="check">✓</div><div><div class="motion">${s.name}</div><div class="desc">${s.desc}</div></div><div class="tmu">${s.tmu} TMU</div>`;
  stepList.appendChild(row);
});

const canvas = document.getElementById('c');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x020617);
const camera = new THREE.PerspectiveCamera(45, 1, .1, 1000);
camera.position.set(0, 145, 280);
const renderer = new THREE.WebGLRenderer({canvas, antialias:true});
renderer.shadowMap.enabled = true;
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 85, 0); controls.update();
scene.add(new THREE.HemisphereLight(0xffffff, 0x334155, 1.4));
const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(120,220,140); key.castShadow=true; scene.add(key);
const rim = new THREE.DirectionalLight(0x60a5fa, 1.4); rim.position.set(-120,140,-100); scene.add(rim);
const floor = new THREE.Mesh(new THREE.CircleGeometry(140,64), new THREE.MeshStandardMaterial({color:0x0f172a, roughness:.7}));
floor.rotation.x = -Math.PI/2; floor.receiveShadow=true; scene.add(floor);
const grid = new THREE.GridHelper(280, 14, 0x334155, 0x1e293b); scene.add(grid);

let mixer, action, duration=1, clock = new THREE.Clock(), playing=false, obj=null;
function resize(){ const w=canvas.clientWidth, h=canvas.clientHeight; renderer.setSize(w,h,false); camera.aspect=w/h; camera.updateProjectionMatrix(); }
new ResizeObserver(resize).observe(canvas);

const loader = new FBXLoader();
loader.load('/app/static/assets/Picking%20Up.fbx', (fbx)=>{
  obj = fbx; obj.scale.setScalar(.7); obj.position.set(0,0,0);
  obj.traverse(c=>{ if(c.isMesh){ c.castShadow=true; c.receiveShadow=true; if(c.material){ c.material.roughness=.45; c.material.metalness=.05; } }});
  scene.add(obj);
  mixer = new THREE.AnimationMixer(obj);
  if (fbx.animations && fbx.animations.length){
    action = mixer.clipAction(fbx.animations[0]);
    action.play(); action.paused=true; duration = fbx.animations[0].duration;
    document.getElementById('motionLabel').innerText = 'Ready: Picking Up';
  } else { document.getElementById('motionLabel').innerText = 'Loaded, but no animation found'; }
}, undefined, (err)=>{ document.getElementById('motionLabel').innerText = 'Could not load FBX'; console.error(err); });

function updatePanel(t){
  const p = Math.min(1, Math.max(0, t/duration));
  document.getElementById('progressBar').style.width = (p*100).toFixed(1)+'%';
  let active=-1, totalTMU=0;
  steps.forEach((s,i)=>{ if(p>=s.p){ active=i; totalTMU += s.tmu; }});
  steps.forEach((s,i)=> document.getElementById('step'+i).classList.toggle('active', i<=active));
  const raw = totalTMU * secondsPerTMU;
  document.getElementById('rawTime').innerText = raw.toFixed(1)+' sec';
  document.getElementById('stdTime').innerText = (raw*(1+allowance)).toFixed(1)+' sec';
  document.getElementById('motionLabel').innerText = active>=0 ? steps[active].name : 'Starting motion';
}

function animate(){ requestAnimationFrame(animate); resize(); const dt=clock.getDelta(); if(mixer && playing){ mixer.update(dt); updatePanel(action.time); if(action.time >= duration-.03){ playing=false; action.paused=true; }} renderer.render(scene,camera); }
animate();

document.getElementById('playBtn').onclick=()=>{ if(action){ playing=true; action.paused=false; }};
document.getElementById('pauseBtn').onclick=()=>{ if(action){ playing=false; action.paused=true; }};
document.getElementById('resetBtn').onclick=()=>{ if(action){ playing=false; action.stop(); action.reset(); action.play(); action.paused=true; updatePanel(0); }};
</script>
'''

html(viewer_html, height=750)

st.markdown("### From motion time to staffing")

motions = pd.DataFrame({
    "Motion": ["Approach", "Reach", "Bend", "Grasp", "Lift", "Return"],
    "TMU": [10, 16, 30, 3, 16, 10],
})
motions["Raw seconds"] = motions["TMU"] * 0.036
raw = motions["Raw seconds"].sum()
std = raw * 1.15

c1, c2, c3 = st.columns(3)
c1.markdown(f'<div class="metric"><div class="label">Raw motion time</div><div class="value">{raw:.1f}s</div></div>', unsafe_allow_html=True)
c2.markdown('<div class="metric"><div class="label">Allowance</div><div class="value">15%</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="metric"><div class="label">Standard time</div><div class="value">{std:.1f}s</div></div>', unsafe_allow_html=True)

hours = list(range(6,19))
labels = [f"{h}:00" if h <= 12 else f"{h-12}:00" for h in hours]
sales_based = [1,1,1,2,2,3,3,3,2,2,2,1,1]
most_fixed = [0.6,0.7,0.9,1.1,1.2,1.5,1.7,1.5,1.4,1.2,1.0,0.8,0.6]
most_allowance = [x*.15 for x in most_fixed]
most_rounded = [max(1, round(f+a+0.49)) for f,a in zip(most_fixed, most_allowance)]

fig = go.Figure()
fig.add_trace(go.Bar(name="MOST fixed motion labor", x=labels, y=most_fixed))
fig.add_trace(go.Bar(name="Human allowance", x=labels, y=most_allowance))
fig.add_trace(go.Scatter(name="Staffing after rounding rules", x=labels, y=most_rounded, mode="lines+markers", line=dict(width=4)))
fig.add_trace(go.Scatter(name="Sales/labor-hour schedule", x=labels, y=sales_based, mode="lines+markers", line=dict(width=4, dash="dot")))
fig.update_layout(
    barmode="stack",
    height=470,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,23,42,.5)",
    font=dict(color="#f8fafc"),
    margin=dict(l=20,r=20,t=45,b=20),
    title="Staffing view: 6 AM to 6 PM",
    xaxis_title="Hour",
    yaxis_title="Labor hours / people required",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)
st.plotly_chart(fig, use_container_width=True)

st.dataframe(motions, use_container_width=True, hide_index=True)
