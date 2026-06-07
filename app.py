import base64
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="RunSigma MOST Demo", layout="wide")

FBX_DEFAULTS = ["picking_up.fbx", "PickingUp.fbx", "Picking Up.fbx"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp { background: #070b14; color: #ffffff; }
.block-container { max-width: 1400px; padding-top: 24px; }
.hero {
  border: 1px solid #23487c;
  background: linear-gradient(135deg, #0b1427 0%, #111f3d 100%);
  border-radius: 24px;
  padding: 24px 28px;
  margin-bottom: 20px;
}
.kicker { color:#61a8ff; letter-spacing: 3px; font-weight:800; font-size: 13px; }
.title { font-size: 34px; font-weight: 900; line-height: 1.05; margin-top: 8px; }
.sub { color:#a8b7d4; max-width: 900px; margin-top: 10px; font-size: 15px; }
.note {
  border: 1px solid #233653;
  background: #0b1220;
  border-radius: 14px;
  padding: 14px 16px;
  color: #a8b7d4;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="kicker">RUNSIGMA 3D MOST CAPTURE</div>
  <div class="title">Motion-based staffing demo</div>
  <div class="sub">
    Instead of converting sales into labor hours, this demo captures the work motion by motion,
    converts each motion into engineered time, adds allowance, and turns the final labor requirement into a schedule.
  </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("3D file")
    uploaded = st.file_uploader("Upload FBX", type=["fbx"])
    st.caption("Recommended: Mixamo FBX Binary, preferably without skin if it is only an animation.")
    allowance = st.slider("Allowance", 0, 40, 15, 1)
    st.caption("Allowance covers breaks, fatigue, personal time, and normal human variation.")


def load_fbx_bytes():
    if uploaded is not None:
        return uploaded.read(), uploaded.name
    for name in FBX_DEFAULTS:
        p = Path(name)
        if p.exists():
            return p.read_bytes(), name
    return None, None

fbx_bytes, fbx_name = load_fbx_bytes()

if fbx_bytes is None:
    st.markdown("""
<div class="note">
No FBX found. Upload the file in the sidebar, or put it next to app.py and rename it <b>picking_up.fbx</b>.
</div>
""", unsafe_allow_html=True)
    st.stop()

fbx_b64 = base64.b64encode(fbx_bytes).decode("ascii")

motions = [
    {"t": 0.08, "name": "Approach", "desc": "Worker positions body toward the item", "tmu": 10},
    {"t": 0.22, "name": "Reach", "desc": "Arm extends toward the object", "tmu": 16},
    {"t": 0.40, "name": "Bend", "desc": "Body lowers to access the item", "tmu": 30},
    {"t": 0.58, "name": "Grasp", "desc": "Hand gains control of the item", "tmu": 3},
    {"t": 0.75, "name": "Lift", "desc": "Object is raised under control", "tmu": 16},
    {"t": 0.92, "name": "Return", "desc": "Worker returns to stable posture", "tmu": 10},
]

raw_tmu = sum(m["tmu"] for m in motions)
raw_sec = raw_tmu * 0.036
std_sec = raw_sec * (1 + allowance / 100)

html = f"""
<div id="app3d">
  <div class="topbar">
    <div>
      <div class="kicker2">3D MOST CAPTURE</div>
      <div class="headline">Picking Up motion</div>
      <div class="filetag">Loaded: {fbx_name}</div>
    </div>
    <div class="buttons">
      <button onclick="playAnim()">Play</button>
      <button onclick="pauseAnim()">Pause</button>
      <button onclick="resetAnim()">Reset</button>
    </div>
  </div>
  <div class="layout">
    <div class="stage">
      <div id="viewer"></div>
      <div id="loadStatus" class="status">Loading FBX...</div>
    </div>
    <div class="panel">
      <h2>Live MOST breakdown</h2>
      <div class="progress"><div id="progressBar"></div></div>
      <div id="steps"></div>
      <div class="metric"><span>Raw time</span><b id="rawTime">0.0 sec</b></div>
      <div class="metric"><span>Allowance</span><b>{allowance}%</b></div>
      <div class="metric strong"><span>Standard time</span><b id="stdTime">0.0 sec</b></div>
    </div>
  </div>
  <div class="schedule">
    <h2>Schedule view: 6 AM to 6 PM</h2>
    <div class="axis">{''.join([f'<span>{h}</span>' for h in ['6 AM','7','8','9','10','11','12','1','2','3','4','5','6 PM']])}</div>
    <div class="row"><div class="label">Sales-based</div><div class="bar"><div class="seg sales" style="left:6%;width:68%"></div></div></div>
    <div class="row"><div class="label">MOST-based</div><div class="bar"><div class="seg most" style="left:2%;width:24%"></div><div class="seg most2" style="left:31%;width:30%"></div><div class="seg most3" style="left:67%;width:20%"></div></div></div>
    <div class="row"><div class="label">Rounded staff blocks</div><div class="bar"><div class="seg round" style="left:0%;width:25%"></div><div class="seg round" style="left:30%;width:33%"></div><div class="seg round" style="left:66%;width:25%"></div></div></div>
  </div>
</div>

<style>
#app3d {{ color: white; font-family: Inter, Arial, sans-serif; }}
.topbar {{ display:flex; justify-content:space-between; align-items:center; padding:24px; border:1px solid #25477a; border-radius:22px 22px 0 0; background:#0d1830; }}
.kicker2 {{ color:#61a8ff; letter-spacing:3px; font-size:13px; font-weight:900; }}
.headline {{ font-size:30px; font-weight:900; margin-top:6px; }}
.filetag {{ color:#a8b7d4; font-size:12px; margin-top:8px; }}
.buttons button {{ background:#082d72; border:1px solid #56a1ff; color:white; border-radius:12px; padding:12px 22px; font-weight:800; margin-left:10px; cursor:pointer; }}
.layout {{ display:grid; grid-template-columns: 1.5fr 1fr; gap:18px; padding:18px; border-left:1px solid #25477a; border-right:1px solid #25477a; background:#0b1428; }}
.stage {{ position:relative; height:650px; border:1px solid #25395a; background:#030817; border-radius:20px; overflow:hidden; }}
#viewer {{ width:100%; height:100%; }}
.status {{ position:absolute; left:24px; top:24px; border:1px solid #56a1ff; border-radius:14px; padding:14px 18px; background:#0d1830; font-weight:900; }}
.panel {{ border:1px solid #25395a; background:#071020; border-radius:20px; padding:22px; }}
.panel h2, .schedule h2 {{ margin:0 0 16px 0; font-size:26px; }}
.progress {{ height:12px; background:#243249; border-radius:99px; overflow:hidden; margin-bottom:22px; }}
#progressBar {{ height:100%; width:0%; background:linear-gradient(90deg,#58a6ff,#7ee787); transition:width .25s; }}
.step {{ display:grid; grid-template-columns:38px 1fr 80px; gap:14px; align-items:center; padding:14px 10px; border-bottom:1px solid #17233a; opacity:.28; transition:.25s; }}
.step.active {{ opacity:1; transform:translateX(4px); }}
.check {{ width:28px; height:28px; border-radius:50%; background:#182238; display:grid; place-items:center; color:#7ee787; font-weight:900; }}
.stepname {{ font-size:16px; font-weight:900; }}
.stepdesc {{ color:#8fa1c0; font-size:13px; margin-top:3px; }}
.tmu {{ color:#8bd5ff; font-weight:900; text-align:right; }}
.metric {{ margin-top:12px; border:1px solid #263b5e; border-radius:14px; padding:16px; display:flex; justify-content:space-between; align-items:center; background:#0a162a; }}
.metric span {{ color:#9fb4d8; text-transform:uppercase; font-size:12px; letter-spacing:1px; }}
.metric b {{ font-size:22px; }}
.metric.strong {{ border-color:#57a6ff; background:#0b2346; }}
.schedule {{ padding:22px; border:1px solid #25477a; border-radius:0 0 22px 22px; background:#0b1428; }}
.axis {{ margin-left:170px; display:grid; grid-template-columns:repeat(13,1fr); color:#9fb4d8; font-size:12px; }}
.row {{ display:grid; grid-template-columns:160px 1fr; gap:10px; align-items:center; margin-top:14px; }}
.label {{ color:#d5e3ff; font-weight:800; }}
.bar {{ position:relative; height:42px; background:#071020; border:1px solid #203554; border-radius:12px; overflow:hidden; }}
.seg {{ position:absolute; height:100%; top:0; border-radius:10px; opacity:.9; }}
.sales {{ background:#4b5563; }}
.most {{ background:#3b82f6; }} .most2 {{ background:#06b6d4; }} .most3 {{ background:#22c55e; }}
.round {{ background:#f59e0b; opacity:.75; }}
</style>

<script type="importmap">
{{
  "imports": {{
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }}
}}
</script>

<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
import {{ FBXLoader }} from 'three/addons/loaders/FBXLoader.js';

const motions = {motions};
const rawSecTotal = {raw_sec:.4f};
const stdSecTotal = {std_sec:.4f};
const fbxBase64 = "{fbx_b64}";

let scene, camera, renderer, controls, mixer, clock, model, action;
let duration = 1;
let playing = false;

const viewer = document.getElementById('viewer');
const status = document.getElementById('loadStatus');
const stepsEl = document.getElementById('steps');
const progressBar = document.getElementById('progressBar');
const rawTime = document.getElementById('rawTime');
const stdTime = document.getElementById('stdTime');

stepsEl.innerHTML = motions.map((m, i) => `
  <div class="step" id="step-${{i}}">
    <div class="check">✓</div>
    <div><div class="stepname">${{m.name}}</div><div class="stepdesc">${{m.desc}}</div></div>
    <div class="tmu">${{m.tmu}} TMU</div>
  </div>
`).join('');

init();
loadFBX();
animate();

function init() {{
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x030817);

  camera = new THREE.PerspectiveCamera(45, viewer.clientWidth / viewer.clientHeight, 0.1, 2000);
  camera.position.set(0, 145, 310);

  renderer = new THREE.WebGLRenderer({{ antialias: true }});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(viewer.clientWidth, viewer.clientHeight);
  renderer.shadowMap.enabled = true;
  viewer.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 75, 0);
  controls.update();

  scene.add(new THREE.HemisphereLight(0xffffff, 0x223355, 2.0));
  const key = new THREE.DirectionalLight(0xffffff, 2.2);
  key.position.set(120, 200, 160);
  scene.add(key);

  const grid = new THREE.GridHelper(420, 24, 0x2c4773, 0x1a2a44);
  scene.add(grid);

  const floor = new THREE.Mesh(
    new THREE.CircleGeometry(190, 72),
    new THREE.MeshStandardMaterial({{ color: 0x111d34, roughness: 0.85 }})
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -1;
  scene.add(floor);

  clock = new THREE.Clock();
  window.addEventListener('resize', onResize);
}}

function loadFBX() {{
  try {{
    const bytes = Uint8Array.from(atob(fbxBase64), c => c.charCodeAt(0));
    const blob = new Blob([bytes], {{ type: 'application/octet-stream' }});
    const url = URL.createObjectURL(blob);

    const loader = new FBXLoader();
    loader.load(url, function(object) {{
      model = object;
      model.scale.setScalar(1.0);

      const box = new THREE.Box3().setFromObject(model);
      const size = new THREE.Vector3();
      const center = new THREE.Vector3();
      box.getSize(size);
      box.getCenter(center);

      model.position.x -= center.x;
      model.position.z -= center.z;
      model.position.y -= box.min.y;

      const maxDim = Math.max(size.x, size.y, size.z);
      if (maxDim > 0) model.scale.setScalar(150 / maxDim);

      scene.add(model);

      if (model.animations && model.animations.length > 0) {{
        mixer = new THREE.AnimationMixer(model);
        action = mixer.clipAction(model.animations[0]);
        action.play();
        action.paused = true;
        duration = model.animations[0].duration || 1;
        status.style.display = 'none';
      }} else {{
        status.innerText = 'FBX loaded, but no animation found';
      }}
      URL.revokeObjectURL(url);
    }}, undefined, function(error) {{
      console.error(error);
      status.innerText = 'Could not load FBX. Try GLB or rename without spaces.';
    }});
  }} catch (err) {{
    console.error(err);
    status.innerText = 'Could not parse FBX file';
  }}
}}

function updatePanel() {{
  if (!action) return;
  const p = Math.min(action.time / duration, 1);
  progressBar.style.width = (p * 100).toFixed(1) + '%';

  let tmu = 0;
  motions.forEach((m, i) => {{
    const active = p >= m.t;
    document.getElementById(`step-${{i}}`).classList.toggle('active', active);
    if (active) tmu += m.tmu;
  }});

  const raw = tmu * 0.036;
  const std = raw * (1 + {allowance} / 100);
  rawTime.innerText = raw.toFixed(1) + ' sec';
  stdTime.innerText = std.toFixed(1) + ' sec';
}}

function animate() {{
  requestAnimationFrame(animate);
  const delta = clock.getDelta();
  if (mixer && playing) mixer.update(delta);
  updatePanel();
  renderer.render(scene, camera);
}}

function onResize() {{
  camera.aspect = viewer.clientWidth / viewer.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(viewer.clientWidth, viewer.clientHeight);
}}

window.playAnim = function() {{
  if (!action) return;
  playing = true;
  action.paused = false;
}};

window.pauseAnim = function() {{
  playing = false;
  if (action) action.paused = true;
}};

window.resetAnim = function() {{
  playing = false;
  if (action) {{
    action.reset();
    action.paused = true;
  }}
  updatePanel();
}};
</script>
"""

st.components.v1.html(html, height=1120, scrolling=True)
