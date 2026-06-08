import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="RunSigma | 3D MOST Demo", layout="wide", initial_sidebar_state="collapsed")

ROOT = Path(__file__).parent
MODEL_PATH = ROOT / "UAL1_Standard.glb"
ANIM_PATH = ROOT / "picking_up.fbx"

st.markdown("""
<style>
#MainMenu, footer, header {visibility:hidden;}
.block-container {padding:0 !important; max-width:100% !important;}
html, body, [data-testid="stAppViewContainer"] {background:#050914;}
iframe {display:block;}
</style>
""", unsafe_allow_html=True)

if not MODEL_PATH.exists():
    st.error("Missing UAL1_Standard.glb")
    st.stop()

model_b64 = base64.b64encode(MODEL_PATH.read_bytes()).decode("utf-8")
fbx_b64 = base64.b64encode(ANIM_PATH.read_bytes()).decode("utf-8") if ANIM_PATH.exists() else ""

html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
:root{--bg:#050914;--panel:#0a1428;--panel2:#0d1b35;--line:#1e3e70;--blue:#55a7ff;--cyan:#76ddff;--green:#7df0a2;--text:#f8fbff;--muted:#8ba0bd;--yellow:#ffd25a;--red:#ff5c73;}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,Segoe UI,Arial,sans-serif}.wrap{padding:22px}.hero{border:1px solid var(--line);background:linear-gradient(135deg,#0c1b36,#081225 70%);border-radius:22px;padding:24px;box-shadow:0 20px 70px rgba(0,0,0,.35)}.top{display:flex;justify-content:space-between;align-items:flex-start;gap:18px;margin-bottom:18px}.kicker{color:var(--blue);letter-spacing:6px;font-weight:900;font-size:13px}h1{margin:8px 0 6px;font-size:42px;line-height:1}.sub{color:#bdd4f2;font-size:16px;max-width:980px}.btns{display:flex;gap:12px;flex-wrap:wrap;justify-content:flex-end}button{border:1px solid #3989ff;background:#092b62;color:white;padding:13px 18px;border-radius:12px;font-weight:800;cursor:pointer;box-shadow:inset 0 0 0 1px rgba(255,255,255,.05)}button:hover{filter:brightness(1.18)}.grid{display:grid;grid-template-columns:1.55fr 1fr;gap:20px}.card{border:1px solid #24436f;border-radius:20px;background:#061020;overflow:hidden}#viewer{height:610px;position:relative}.badge{position:absolute;left:24px;top:24px;z-index:2;border:1px solid #3989ff;color:white;background:rgba(9,43,98,.78);padding:12px 16px;border-radius:14px;font-weight:900}.hint{position:absolute;left:24px;bottom:20px;z-index:2;color:#9eb5d5;font-size:13px}.callout{position:absolute;z-index:4;border:1px solid rgba(118,221,255,.9);background:rgba(7,18,37,.9);border-radius:14px;padding:12px 14px;min-width:170px;box-shadow:0 0 30px rgba(85,167,255,.28);transform:translate(-50%,-50%);opacity:0;transition:.25s}.callout.show{opacity:1}.callout b{display:block;font-size:18px}.callout span{font-size:12px;color:#bdd4f2}.arrow{position:absolute;z-index:3;height:3px;background:linear-gradient(90deg,transparent,var(--cyan));transform-origin:left center;opacity:0;border-radius:99px;box-shadow:0 0 18px var(--cyan);transition:.25s}.arrow.show{opacity:1}.panel{padding:24px}.panel h2{margin:0 0 14px;font-size:29px}.progress{height:12px;border-radius:999px;background:#263953;overflow:hidden;margin:10px 0 22px}#bar{height:100%;width:0%;background:linear-gradient(90deg,var(--blue),var(--green));transition:.35s ease}.row{display:grid;grid-template-columns:42px 1fr 92px;gap:14px;align-items:center;padding:15px 8px;border-bottom:1px solid rgba(80,130,200,.16);opacity:.32;transition:.3s}.row.active,.row.done{opacity:1}.dot{width:30px;height:30px;border-radius:50%;background:#11223e;display:flex;align-items:center;justify-content:center;color:var(--green);font-weight:900}.row.active .dot{background:#0d3970;box-shadow:0 0 22px rgba(85,167,255,.6)}.motion{font-size:18px;font-weight:900}.desc{color:var(--muted);font-size:13px;margin-top:3px}.tmu{text-align:right;color:var(--cyan);font-weight:900;font-size:18px}.metrics{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:18px}.metric{border:1px solid #24436f;border-radius:14px;background:#0a1830;padding:15px}.label{color:#9cc9ff;letter-spacing:1.4px;font-size:12px;text-transform:uppercase}.value{font-size:26px;font-weight:900;text-align:right;margin-top:5px}.section{margin-top:20px;border:1px solid var(--line);border-radius:20px;background:#071225;padding:24px}.section h2{margin:0 0 6px;font-size:30px}.axis{display:grid;grid-template-columns:repeat(13,1fr);color:#9bb2d1;font-size:12px;margin-top:18px}.axis span{border-left:1px solid rgba(120,160,220,.25);padding-left:5px}.sched{margin-top:10px;border:1px solid #203a61;border-radius:16px;background:#040b18;padding:16px}.track{display:grid;grid-template-columns:130px 1fr;align-items:center;margin:15px 0;gap:16px}.name{color:white;font-weight:900}.timeline{position:relative;height:36px;background:repeating-linear-gradient(90deg,rgba(120,160,220,.11) 0,rgba(120,160,220,.11) 1px,transparent 1px,transparent 8.333%);border-radius:10px;overflow:hidden}.block{position:absolute;top:6px;height:24px;border-radius:7px;background:linear-gradient(90deg,#55a7ff,#76ddff);box-shadow:0 0 18px rgba(85,167,255,.35)}.block.sales{background:linear-gradient(90deg,#ff5c73,#ffd25a)}.stack{position:absolute;height:10px;border-radius:999px;background:rgba(125,240,162,.85)}.explain{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:16px}.mini{background:#091932;border:1px solid #24436f;border-radius:16px;padding:16px}.mini p{color:#9eb5d5;margin:6px 0 0;font-size:14px}@media(max-width:1000px){.grid,.explain{grid-template-columns:1fr}.top{flex-direction:column}#viewer{height:520px}}
</style>
</head>
<body>
<div class="wrap">
<div class="hero">
<div class="top"><div><div class="kicker">RUNSIGMA 3D MOST CAPTURE</div><h1>Motion-based staffing demo</h1><div class="sub">One continuous task motion drives the MOST table. As the worker reaches, bends, grasps, lifts, and returns, the engineered time stacks into labor demand.</div></div><div class="btns"><button onclick="playDemo()">Play Motion</button><button onclick="pauseDemo()">Pause</button><button onclick="nextStep()">Next Motion</button><button onclick="autoDemo()">Auto Demo</button><button onclick="resetDemo()">Reset</button></div></div>
<div class="grid"><div class="card"><div id="viewer"><div class="badge" id="status">Loading 3D worker...</div><div class="arrow" id="arrow"></div><div class="callout" id="callout"><b id="calloutTitle">Reach</b><span id="calloutText">Arm extends toward object</span></div><div class="hint">Drag to rotate. Scroll to zoom.</div></div></div><div class="card panel"><h2>Live MOST breakdown</h2><div class="progress"><div id="bar"></div></div><div id="motionRows"></div><div class="metrics"><div class="metric"><div class="label">Raw time</div><div class="value" id="raw">0.0 sec</div></div><div class="metric"><div class="label">Allowance</div><div class="value">15%</div></div><div class="metric"><div class="label">Standard time</div><div class="value" id="std">0.0 sec</div></div></div></div></div>
</div>
<div class="section"><h2>Schedule view: 6 AM to 6 PM</h2><div class="sub">MOST-based demand is generated from the work content. The final schedule rounds that demand into practical staffing blocks.</div><div class="axis"><span>6 AM</span><span>7</span><span>8</span><span>9</span><span>10</span><span>11</span><span>12 PM</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6 PM</span></div><div class="sched"><div class="track"><div class="name">Sales-based</div><div class="timeline"><div class="block sales" style="left:17%;width:29%"></div><div class="block sales" style="left:58%;width:25%"></div></div></div><div class="track"><div class="name">MOST demand</div><div class="timeline" id="mostLine"></div></div><div class="track"><div class="name">Final schedule</div><div class="timeline"><div class="block" style="left:8.33%;width:25%"></div><div class="block" style="left:33.3%;width:25%"></div><div class="block" style="left:58.3%;width:25%"></div></div></div></div><div class="explain"><div class="mini"><b>1. Capture motion</b><p>Reach, grasp, bend, lift, move, and place are translated into engineered time.</p></div><div class="mini"><b>2. Add allowance</b><p>Breaks, fatigue, personal time, and normal human variation are added.</p></div><div class="mini"><b>3. Build schedule</b><p>The algorithm rounds practical labor into real staffing blocks and availability windows.</p></div></div></div>
</div>
<script type="importmap">{"imports":{"three":"https://unpkg.com/three@0.160.0/build/three.module.js","three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';

const motions=[
{name:'Approach',desc:'Worker positions body toward the item',tmu:10,cue:.08,arrow:[48,46,265,0],call:[55,38]},
{name:'Reach',desc:'Arm extends toward the object',tmu:16,cue:.22,arrow:[49,41,230,-15],call:[66,31]},
{name:'Bend',desc:'Body lowers to access the item',tmu:30,cue:.40,arrow:[50,50,210,25],call:[65,50]},
{name:'Grasp',desc:'Hand gains control of the item',tmu:3,cue:.57,arrow:[51,52,185,15],call:[67,57]},
{name:'Lift',desc:'Object is raised under control',tmu:16,cue:.74,arrow:[52,48,210,-35],call:[67,41]},
{name:'Return',desc:'Worker returns to stable posture',tmu:10,cue:.91,arrow:[50,42,180,180],call:[42,35]}
];
let step=0,clock=new THREE.Clock(),playing=false,elapsed=0,duration=5.4,model,baseRot={},bones={},mixer,fbxAction;
const viewer=document.getElementById('viewer');
const scene=new THREE.Scene(); scene.background=new THREE.Color(0x040914);
const camera=new THREE.PerspectiveCamera(45,viewer.clientWidth/viewer.clientHeight,.1,1000); camera.position.set(2.8,1.8,4.2);
const renderer=new THREE.WebGLRenderer({antialias:true}); renderer.setSize(viewer.clientWidth,viewer.clientHeight); renderer.setPixelRatio(Math.min(window.devicePixelRatio,2)); renderer.outputColorSpace=THREE.SRGBColorSpace; viewer.appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement); controls.target.set(0,1,0); controls.update();
scene.add(new THREE.HemisphereLight(0xffffff,0x223355,2.3)); const dir=new THREE.DirectionalLight(0xffffff,2.0); dir.position.set(3,5,4); scene.add(dir);
const grid=new THREE.GridHelper(8,28,0x1e5aa0,0x183250); scene.add(grid);
const floor=new THREE.Mesh(new THREE.CircleGeometry(2.4,64),new THREE.MeshStandardMaterial({color:0x101c32,roughness:.8,metalness:.05})); floor.rotation.x=-Math.PI/2; floor.position.y=-.01; scene.add(floor);
const boxObj=new THREE.Mesh(new THREE.BoxGeometry(.45,.32,.45),new THREE.MeshStandardMaterial({color:0xffd25a,roughness:.55})); boxObj.position.set(.72,.16,.28); scene.add(boxObj);

function findBones(root){
  root.traverse(o=>{ if(o.isBone){ const n=o.name.toLowerCase(); if(n.includes('spine')&&!bones.spine) bones.spine=o; if((n.includes('rightarm')||n.includes('upperarm_r')||n.includes('arm.r'))&&!bones.rArm) bones.rArm=o; if((n.includes('rightforearm')||n.includes('lowerarm_r')||n.includes('forearm.r'))&&!bones.rFore) bones.rFore=o; if((n.includes('lefthand')||n.includes('hand_l')||n.includes('hand.l'))&&!bones.lHand) bones.lHand=o; if((n.includes('righthand')||n.includes('hand_r')||n.includes('hand.r'))&&!bones.rHand) bones.rHand=o; if(n.includes('hips')&&!bones.hips) bones.hips=o; }});
  [bones.spine,bones.rArm,bones.rFore,bones.rHand,bones.lHand,bones.hips].forEach(b=>{ if(b) baseRot[b.uuid]=b.rotation.clone(); });
}
function resetPose(){ Object.values(bones).forEach(b=>{ if(b&&baseRot[b.uuid]) b.rotation.copy(baseRot[b.uuid]); }); if(model){ model.rotation.y=0; model.position.y=0; } boxObj.position.set(.72,.16,.28); }
function setRot(b,x=0,y=0,z=0){ if(!b||!baseRot[b.uuid]) return; b.rotation.x=baseRot[b.uuid].x+x; b.rotation.y=baseRot[b.uuid].y+y; b.rotation.z=baseRot[b.uuid].z+z; }
function smooth(a,b,t){ t=Math.max(0,Math.min(1,t)); t=t*t*(3-2*t); return a+(b-a)*t; }
function proceduralMotion(p){
  resetPose();
  const bend=Math.sin(Math.PI*Math.min(1,Math.max(0,(p-.18)/.42)))*.55;
  setRot(bones.spine,bend,0,0);
  if(bones.hips) setRot(bones.hips, -bend*.35, 0, 0);
  let reach=smooth(0,1,(p-.10)/.22);
  let lift=smooth(0,1,(p-.58)/.25);
  let ret=smooth(0,1,(p-.83)/.14);
  let armX=-1.15*reach + .80*lift + .35*ret;
  let armZ=-.55*reach + .35*lift;
  setRot(bones.rArm,armX,0,armZ);
  setRot(bones.rFore,-.55*reach + .65*lift,0,-.15);
  setRot(bones.rHand, .20*reach - .45*lift,0,0);
  if(model) model.rotation.y = smooth(0,.28,(p-.02)/.18) - smooth(0,.28,(p-.82)/.12);
  if(p>.55 && p<.86){ boxObj.position.y = .16 + smooth(0,.55,(p-.55)/.22); boxObj.position.x = .72 - smooth(0,.18,(p-.55)/.22); }
}
function renderRows(){
 const box=document.getElementById('motionRows'); box.innerHTML='';
 motions.forEach((m,i)=>{ const cls=i<step?'row done':i===step?'row active':'row'; box.innerHTML+=`<div class="${cls}"><div class="dot">✓</div><div><div class="motion">${m.name}</div><div class="desc">${m.desc}</div></div><div class="tmu">${m.tmu} TMU</div></div>`; });
 const done=motions.slice(0,step).reduce((a,b)=>a+b.tmu,0), sec=done*.036;
 document.getElementById('raw').textContent=sec.toFixed(1)+' sec'; document.getElementById('std').textContent=(sec*1.15).toFixed(1)+' sec'; document.getElementById('bar').style.width=(step/motions.length*100)+'%'; buildMostLine(); showCallout();
}
function buildMostLine(){ const line=document.getElementById('mostLine'); line.innerHTML=''; for(let i=0;i<step;i++){ const left=8+i*12, width=Math.max(5,motions[i].tmu/3); line.innerHTML+=`<div class="stack" style="left:${left}%;top:${7+i*4}px;width:${width}%"></div>`; }}
function showCallout(){ const c=document.getElementById('callout'), a=document.getElementById('arrow'); if(step<=0){ c.classList.remove('show'); a.classList.remove('show'); return; } const m=motions[Math.min(step-1,motions.length-1)]; document.getElementById('calloutTitle').textContent=m.name; document.getElementById('calloutText').textContent=m.desc; c.style.left=m.call[0]+'%'; c.style.top=m.call[1]+'%'; c.classList.add('show'); a.style.left=m.arrow[0]+'%'; a.style.top=m.arrow[1]+'%'; a.style.width=m.arrow[2]+'px'; a.style.transform=`rotate(${m.arrow[3]}deg)`; a.classList.add('show'); }
renderRows();

const modelBlob=Uint8Array.from(atob('__MODEL_B64__'),c=>c.charCodeAt(0)); const modelUrl=URL.createObjectURL(new Blob([modelBlob],{type:'model/gltf-binary'}));
new GLTFLoader().load(modelUrl,(gltf)=>{ model=gltf.scene; const bb=new THREE.Box3().setFromObject(model); const size=bb.getSize(new THREE.Vector3()).length(); const center=bb.getCenter(new THREE.Vector3()); model.position.sub(center); model.scale.setScalar(2.4/size); scene.add(model); findBones(model); document.getElementById('status').textContent='Loaded GLB worker + procedural MOST motion'; },undefined,(err)=>{document.getElementById('status').textContent='Could not load GLB'; console.error(err);});

// Optional: loads the uploaded small Mixamo FBX in memory only to confirm it is web-safe. The visual motion is procedural so the demo remains controllable.
if('__FBX_B64__'.length>10){
 const fbxBlob=Uint8Array.from(atob('__FBX_B64__'),c=>c.charCodeAt(0)); const fbxUrl=URL.createObjectURL(new Blob([fbxBlob],{type:'application/octet-stream'}));
 new FBXLoader().load(fbxUrl,(fbx)=>{ console.log('Small FBX loaded:', fbx.animations?.length || 0, 'animations'); },undefined,(err)=>console.warn('FBX check failed',err));
}
window.playDemo=()=>{playing=true}; window.pauseDemo=()=>{playing=false}; window.resetDemo=()=>{playing=false;elapsed=0;step=0;resetPose();renderRows();}; window.nextStep=()=>{ step=Math.min(motions.length,step+1); elapsed=(motions[Math.max(0,step-1)]?.cue||0)*duration; proceduralMotion(elapsed/duration); renderRows();}; window.autoDemo=async()=>{window.resetDemo(); for(let i=0;i<motions.length;i++){ await new Promise(r=>setTimeout(r,850)); window.nextStep(); }};
function animate(){ requestAnimationFrame(animate); const dt=clock.getDelta(); if(playing){ elapsed+=dt; if(elapsed>duration){ elapsed=duration; playing=false; } const p=elapsed/duration; proceduralMotion(p); const newStep=motions.filter(m=>p>=m.cue).length; if(newStep!==step){ step=newStep; renderRows(); }} renderer.render(scene,camera); }
animate(); window.addEventListener('resize',()=>{const w=viewer.clientWidth,h=viewer.clientHeight; camera.aspect=w/h; camera.updateProjectionMatrix(); renderer.setSize(w,h);});
</script>
</body>
</html>
"""
html = html.replace("__MODEL_B64__", model_b64).replace("__FBX_B64__", fbx_b64)
components.html(html, height=1140, scrolling=True)
