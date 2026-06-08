import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="RunSigma | 3D MOST Motion Demo", layout="wide", initial_sidebar_state="collapsed")

ROOT = Path(__file__).parent
ASSET_PATHS = [ROOT / "assets" / "UAL1_Standard.glb", ROOT / "UAL1_Standard.glb"]
ASSET_PATH = next((p for p in ASSET_PATHS if p.exists()), None)

st.markdown("""
<style>
#MainMenu, footer, header {visibility:hidden;}
.block-container {padding:0 !important; max-width:100% !important;}
html, body, [data-testid="stAppViewContainer"] {background:#050914;}
iframe {display:block;}
</style>
""", unsafe_allow_html=True)

if ASSET_PATH is None:
    st.error("Missing model file. Add UAL1_Standard.glb to assets/ or repo root.")
    st.stop()

model_b64 = base64.b64encode(ASSET_PATH.read_bytes()).decode("utf-8")
model_name = ASSET_PATH.name
model_size = f"{ASSET_PATH.stat().st_size / 1024 / 1024:.1f} MB"

html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  :root { --bg:#050914; --panel:#0a1428; --line:#1e3e70; --blue:#55a7ff; --cyan:#76ddff; --green:#7df0a2; --text:#f8fbff; --muted:#8ba0bd; --yellow:#ffd25a; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--text); font-family:Inter,Segoe UI,Arial,sans-serif; }
  .wrap { padding:24px; }
  .top { display:flex; justify-content:space-between; align-items:flex-start; gap:20px; margin-bottom:18px; }
  .kicker { color:var(--blue); letter-spacing:7px; font-weight:900; font-size:14px; }
  h1 { margin:8px 0 6px; font-size:44px; line-height:1; }
  .sub { color:#bdd4f2; font-size:16px; max-width:980px; }
  .btns { display:flex; gap:12px; flex-wrap:wrap; justify-content:flex-end; }
  button { border:1px solid #3989ff; background:#092b62; color:white; padding:13px 18px; border-radius:12px; font-weight:900; cursor:pointer; }
  button:hover { filter:brightness(1.18); }
  .grid { display:grid; grid-template-columns: 1.55fr 1fr; gap:20px; }
  .card { border:1px solid #24436f; border-radius:20px; background:#061020; overflow:hidden; }
  #viewer { height:620px; position:relative; }
  .badge { position:absolute; left:24px; top:24px; z-index:2; border:1px solid #3989ff; color:white; background:rgba(9,43,98,.8); padding:12px 16px; border-radius:14px; font-weight:900; }
  .hint { position:absolute; left:24px; bottom:20px; z-index:2; color:#9eb5d5; font-size:13px; }
  .panel { padding:24px; }
  .panel h2 { margin:0 0 14px; font-size:30px; }
  .progress { height:12px; border-radius:999px; background:#263953; overflow:hidden; margin:10px 0 22px; }
  #bar { height:100%; width:0%; background:linear-gradient(90deg,var(--blue),var(--green)); transition:.35s ease; }
  .row { display:grid; grid-template-columns:42px 1fr 90px; gap:14px; align-items:center; padding:13px 8px; border-bottom:1px solid rgba(80,130,200,.16); opacity:.35; transition:.3s; }
  .row.active, .row.done { opacity:1; }
  .dot { width:30px; height:30px; border-radius:50%; background:#11223e; display:flex; align-items:center; justify-content:center; color:var(--green); font-weight:900; }
  .row.active .dot { background:#0d3970; box-shadow:0 0 22px rgba(85,167,255,.6); }
  .motion { font-size:18px; font-weight:900; }
  .desc { color:var(--muted); font-size:13px; margin-top:3px; }
  .tmu { text-align:right; color:var(--cyan); font-weight:900; font-size:18px; }
  .clipName { color:#8aa3c5; font-size:11px; margin-top:4px; }
  .metrics { display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; margin-top:18px; }
  .metric { border:1px solid #24436f; border-radius:14px; background:#0a1830; padding:15px; }
  .label { color:#9cc9ff; letter-spacing:1.4px; font-size:12px; text-transform:uppercase; }
  .value { font-size:26px; font-weight:900; text-align:right; margin-top:5px; }
  .section { margin-top:20px; border:1px solid var(--line); border-radius:20px; background:#071225; padding:24px; }
  .axis { display:grid; grid-template-columns:repeat(13,1fr); color:#9bb2d1; font-size:12px; margin-top:18px; }
  .axis span { border-left:1px solid rgba(120,160,220,.25); padding-left:5px; }
  .track { display:grid; grid-template-columns:130px 1fr; align-items:center; margin:15px 0; gap:16px; }
  .name { color:white; font-weight:900; }
  .timeline { position:relative; height:38px; background:repeating-linear-gradient(90deg,rgba(120,160,220,.11) 0, rgba(120,160,220,.11) 1px, transparent 1px, transparent 8.333%); border:1px solid #203a61; border-radius:10px; overflow:hidden; }
  .block { position:absolute; top:7px; height:24px; border-radius:7px; background:linear-gradient(90deg,#55a7ff,#76ddff); box-shadow:0 0 18px rgba(85,167,255,.35); }
  .block.sales { background:linear-gradient(90deg,#ff5c73,#ffd25a); }
  .stack { position:absolute; height:10px; border-radius:999px; background:rgba(125,240,162,.85); }
  .map { margin-top:12px; padding:12px; background:#08142a; border:1px solid #24436f; border-radius:14px; color:#a7bddb; font-size:13px; }
  select { width:100%; background:#071225; color:#eaf3ff; border:1px solid #24436f; border-radius:10px; padding:8px; margin-top:8px; }
</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <div>
      <div class="kicker">RUNSIGMA 3D MOST CAPTURE</div>
      <h1>Motion-based staffing demo</h1>
      <div class="sub">Each MOST step now triggers a real embedded animation clip. Use the motion buttons to control the presentation step by step.</div>
    </div>
    <div class="btns">
      <button onclick="playStep(0)">Approach</button><button onclick="playStep(1)">Reach</button><button onclick="playStep(2)">Bend</button><button onclick="playStep(3)">Grasp</button><button onclick="playStep(4)">Lift</button><button onclick="nextStep()">Next</button><button onclick="autoDemo()">Auto</button><button onclick="resetDemo()">Reset</button>
    </div>
  </div>
  <div class="grid">
    <div class="card"><div id="viewer"><div class="badge" id="status">Loading 3D worker...</div><div class="hint">Drag to rotate. Scroll to zoom.</div></div></div>
    <div class="card panel">
      <h2>Live MOST breakdown</h2>
      <div class="progress"><div id="bar"></div></div>
      <div id="motionRows"></div>
      <div class="metrics"><div class="metric"><div class="label">Raw time</div><div class="value" id="raw">0.0 sec</div></div><div class="metric"><div class="label">Allowance</div><div class="value">15%</div></div><div class="metric"><div class="label">Standard time</div><div class="value" id="std">0.0 sec</div></div></div>
      <div class="map"><b>Animation mapping</b><div id="clipMap">Loading clips...</div></div>
    </div>
  </div>
  <div class="section">
    <h2>Schedule view: 6 AM to 6 PM</h2>
    <div class="sub">MOST demand grows as motions are captured, then becomes staffing blocks.</div>
    <div class="axis"><span>6 AM</span><span>7</span><span>8</span><span>9</span><span>10</span><span>11</span><span>12 PM</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6 PM</span></div>
    <div class="track"><div class="name">Sales-based</div><div class="timeline"><div class="block sales" style="left:17%;width:29%"></div><div class="block sales" style="left:58%;width:25%"></div></div></div>
    <div class="track"><div class="name">MOST demand</div><div class="timeline" id="mostLine"></div></div>
    <div class="track"><div class="name">Final schedule</div><div class="timeline"><div class="block" style="left:8.33%;width:25%"></div><div class="block" style="left:33.3%;width:25%"></div><div class="block" style="left:58.3%;width:25%"></div></div></div>
  </div>
</div>
<script type="importmap">
{"imports":{"three":"https://unpkg.com/three@0.160.0/build/three.module.js","three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"}}
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const motions = [
  {name:'Approach', desc:'Worker positions body toward the item', tmu:10, keys:['walk','run','idle','ready']},
  {name:'Reach', desc:'Arm extends toward the object', tmu:16, keys:['reach','aim','point','punch','interact']},
  {name:'Bend', desc:'Body lowers to access the item', tmu:30, keys:['pick','pickup','crouch','bend','down','kneel']},
  {name:'Grasp', desc:'Hand gains control of the item', tmu:3, keys:['grab','pick','pickup','use','interact']},
  {name:'Lift', desc:'Object is raised under control', tmu:16, keys:['lift','carry','pickup','hold']},
  {name:'Return', desc:'Worker returns to stable posture', tmu:10, keys:['idle','stand','tpose','ready']}
];
let step = 0, mixer, activeAction, clock = new THREE.Clock(), clips = [], clipMap = {}, model;
const viewer = document.getElementById('viewer');
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x040914);
const camera = new THREE.PerspectiveCamera(45, viewer.clientWidth/viewer.clientHeight, .1, 1000); camera.position.set(2.8,1.8,4.2);
const renderer = new THREE.WebGLRenderer({antialias:true}); renderer.setSize(viewer.clientWidth, viewer.clientHeight); renderer.setPixelRatio(Math.min(window.devicePixelRatio,2)); renderer.outputColorSpace = THREE.SRGBColorSpace; viewer.appendChild(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement); controls.target.set(0,1,0); controls.update();
scene.add(new THREE.HemisphereLight(0xffffff,0x223355,2.2));
const dir = new THREE.DirectionalLight(0xffffff,2); dir.position.set(3,5,4); scene.add(dir);
scene.add(new THREE.GridHelper(8,28,0x1e5aa0,0x183250));
const floor = new THREE.Mesh(new THREE.CircleGeometry(2.2,64), new THREE.MeshStandardMaterial({color:0x101c32, roughness:.8})); floor.rotation.x=-Math.PI/2; floor.position.y=-.01; scene.add(floor);

function pickClip(keys, fallbackIndex) {
  if (!clips.length) return null;
  for (const k of keys) {
    const found = clips.find(c => c.name.toLowerCase().replaceAll('_','').replaceAll(' ','').includes(k));
    if (found) return found;
  }
  return clips[Math.min(fallbackIndex, clips.length - 1)];
}
function updateClipMapUI() {
  const el = document.getElementById('clipMap'); el.innerHTML = '';
  motions.forEach((m,i) => {
    const select = document.createElement('select');
    select.id = 'clipSelect' + i;
    clips.forEach((c,idx) => {
      const opt = document.createElement('option'); opt.value = idx; opt.textContent = c.name; select.appendChild(opt);
    });
    const chosen = clipMap[i];
    if (chosen) select.value = clips.indexOf(chosen);
    select.onchange = () => { clipMap[i] = clips[Number(select.value)]; };
    const label = document.createElement('div'); label.style.marginTop='8px'; label.innerHTML = '<b>' + m.name + '</b>';
    el.appendChild(label); el.appendChild(select);
  });
}
function renderRows() {
  const box = document.getElementById('motionRows'); box.innerHTML='';
  motions.forEach((m,i)=>{
    const cls = i < step ? 'row done' : i === step ? 'row active' : 'row';
    const clip = clipMap[i] ? clipMap[i].name : 'No clip mapped';
    box.innerHTML += `<div class="${cls}"><div class="dot">✓</div><div><div class="motion">${m.name}</div><div class="desc">${m.desc}</div><div class="clipName">Animation: ${clip}</div></div><div class="tmu">${m.tmu} TMU</div></div>`;
  });
  const done = motions.slice(0,step).reduce((a,b)=>a+b.tmu,0);
  const sec = done * 0.036;
  document.getElementById('raw').textContent = sec.toFixed(1)+' sec';
  document.getElementById('std').textContent = (sec*1.15).toFixed(1)+' sec';
  document.getElementById('bar').style.width = (step/motions.length*100)+'%';
  const line = document.getElementById('mostLine'); line.innerHTML='';
  for(let i=0;i<step;i++) line.innerHTML += `<div class="stack" style="left:${8+i*12}%;top:${7+i*4}px;width:${Math.max(5,motions[i].tmu/3)}%"></div>`;
}
function playClip(clip) {
  if (!mixer || !clip) return;
  const next = mixer.clipAction(clip);
  next.reset(); next.setLoop(THREE.LoopOnce, 1); next.clampWhenFinished = true; next.enabled = true; next.paused = false;
  if (activeAction && activeAction !== next) { activeAction.fadeOut(.15); next.fadeIn(.15); }
  next.play(); activeAction = next;
}
window.playStep = function(i) { step = Math.max(step, i+1); playClip(clipMap[i]); renderRows(); };
window.nextStep = function() { const i = Math.min(step, motions.length-1); playStep(i); };
window.resetDemo = function() { step=0; if(activeAction) activeAction.stop(); renderRows(); };
window.autoDemo = async function() { resetDemo(); for(let i=0;i<motions.length;i++) { playStep(i); await new Promise(r=>setTimeout(r,1300)); } };

const blob = Uint8Array.from(atob('__MODEL_B64__'), c => c.charCodeAt(0));
const url = URL.createObjectURL(new Blob([blob], {type:'model/gltf-binary'}));
new GLTFLoader().load(url, (gltf)=>{
  model = gltf.scene;
  const box = new THREE.Box3().setFromObject(model);
  const size = box.getSize(new THREE.Vector3()).length();
  const center = box.getCenter(new THREE.Vector3());
  model.position.sub(center); model.scale.setScalar(2.8 / size); scene.add(model);
  mixer = new THREE.AnimationMixer(model); clips = gltf.animations || [];
  motions.forEach((m,i)=>clipMap[i] = pickClip(m.keys, i));
  document.getElementById('status').textContent = 'Loaded: __MODEL_NAME__ | __MODEL_SIZE__ | ' + clips.length + ' animations';
  updateClipMapUI(); renderRows();
}, undefined, (err)=>{ document.getElementById('status').textContent='Could not load GLB'; console.error(err); });
function animate() { requestAnimationFrame(animate); if(mixer) mixer.update(clock.getDelta()); renderer.render(scene,camera); }
animate();
window.addEventListener('resize',()=>{ const w=viewer.clientWidth,h=viewer.clientHeight; camera.aspect=w/h; camera.updateProjectionMatrix(); renderer.setSize(w,h); });
</script>
</body>
</html>
"""
html = html.replace("__MODEL_B64__", model_b64).replace("__MODEL_NAME__", model_name).replace("__MODEL_SIZE__", model_size)
components.html(html, height=1120, scrolling=True)
