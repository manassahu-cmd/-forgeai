"""
app.py — NameForge AI  |  "Digital Ritual" UI — Elite Edition
==============================================================
3D hero canvas · Magnetic cursor glow · Glassmorphism cards
Cinematic preloader → ENTER THE FORGE → animated cover hero
BUILD BOLD. WIN BIG. — full char-by-char stagger animation
"""

import os
import json
import logging
import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

logging.basicConfig(
    filename="app_debug.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

st.set_page_config(
    page_title="NameForge AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from logic import run_pipeline, AgentStep, AgentResult  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# UNIFIED PRELOADER + COVER HERO
# Flow: Preloader runs (7s) → "ENTER THE FORGE" button pulses in →
#       Click → cinematic exit + cover slides in → BUILD BOLD. WIN BIG. animates →
#       Scroll hint → main app sections
# ─────────────────────────────────────────────────────────────────────────────
st.components.v1.html("""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@800&family=DM+Sans:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap');

*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:100%;height:100%;background:#050505;overflow:hidden;}

/* ═══════════════════ PRELOADER ═══════════════════ */
#preloader{
  position:fixed;inset:0;z-index:9999;
  background:#050505;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  overflow:hidden;
  transition:opacity 1.4s cubic-bezier(.4,0,.2,1),transform 1.4s cubic-bezier(.4,0,.2,1);
}
#preloader.exit{opacity:0;transform:scale(1.08) translateY(-32px);pointer-events:none;}
#bgCanvas{position:absolute;inset:0;z-index:0;}

.ring-wrap{position:relative;width:180px;height:180px;display:flex;align-items:center;justify-content:center;z-index:2;}
.ring{position:absolute;border-radius:50%;border-style:solid;animation:spin linear infinite;}
.r1{width:180px;height:180px;border-width:1.5px;border-color:#7b61ff transparent transparent transparent;animation-duration:2.4s;}
.r2{width:148px;height:148px;border-width:1px;border-color:transparent #00e5ff transparent transparent;animation-duration:1.8s;animation-direction:reverse;}
.r3{width:116px;height:116px;border-width:1px;border-color:#c8ff00 transparent transparent transparent;animation-duration:3.2s;}
.ring-inner{width:72px;height:72px;border-radius:50%;background:radial-gradient(circle,rgba(123,97,255,.25),rgba(0,229,255,.08),transparent);border:1px solid rgba(123,97,255,.4);display:flex;align-items:center;justify-content:center;animation:pulse-glow 2s ease-in-out infinite;z-index:3;}
.bolt{font-size:28px;animation:bolt-flicker 1.6s ease-in-out infinite;}

.brand-name{margin-top:34px;z-index:2;font-family:'Syne',sans-serif;font-size:42px;font-weight:800;letter-spacing:.18em;text-transform:uppercase;display:flex;align-items:center;}
.brand-name span{display:inline-block;opacity:0;transform:translateY(16px);animation:letter-rise .6s cubic-bezier(.4,0,.2,1) forwards;}
.pf{color:#fff;text-shadow:0 0 40px rgba(123,97,255,.6),0 0 80px rgba(123,97,255,.2);}
.pa{color:#00e5ff;text-shadow:0 0 30px rgba(0,229,255,.8),0 0 60px rgba(0,229,255,.3);}

.status-line{margin-top:20px;z-index:2;font-family:'Courier New',monospace;font-size:10px;letter-spacing:.2em;color:rgba(0,229,255,.65);min-height:14px;}
.prog-track{margin-top:14px;width:200px;height:1px;background:rgba(255,255,255,.08);border-radius:99px;z-index:2;overflow:hidden;}
.prog-bar{height:100%;width:0%;background:linear-gradient(90deg,#7b61ff,#00e5ff,#c8ff00);background-size:300% 100%;border-radius:99px;transition:width .45s ease;animation:shimmer 2s linear infinite;}

/* ENTER button */
#enter-btn{
  margin-top:48px;z-index:10;
  font-family:'Syne',sans-serif;font-size:.88rem;font-weight:800;
  letter-spacing:.28em;text-transform:uppercase;
  color:#fff;
  background:linear-gradient(135deg,#7b61ff,#00e5ff);
  border:none;border-radius:99px;
  padding:15px 48px;
  cursor:pointer;
  opacity:0;transform:translateY(20px) scale(.94);
  transition:opacity .9s ease,transform .9s cubic-bezier(.34,1.56,.64,1);
  box-shadow:0 0 0 0 rgba(0,229,255,.4);
  pointer-events:none;
  position:relative;z-index:10;
}
#enter-btn.show{opacity:1;transform:translateY(0) scale(1);pointer-events:all;animation:enter-pulse 2.2s ease-in-out infinite 1.2s;}
#enter-btn:hover{transform:scale(1.07)!important;box-shadow:0 0 50px rgba(0,229,255,.55);}
#enter-btn:active{transform:scale(.97)!important;}

@keyframes enter-pulse{0%,100%{box-shadow:0 0 0 0 rgba(0,229,255,.55);}50%{box-shadow:0 0 0 22px rgba(0,229,255,0);}}
@keyframes spin{to{transform:rotate(360deg);}}
@keyframes pulse-glow{0%,100%{box-shadow:0 0 0 0 rgba(123,97,255,0);}50%{box-shadow:0 0 26px 7px rgba(123,97,255,.38);}}
@keyframes bolt-flicker{0%,100%{opacity:1;transform:scale(1);}45%{opacity:.55;transform:scale(.91);}50%{opacity:1;transform:scale(1.09);}55%{opacity:.68;transform:scale(.96);}}
@keyframes letter-rise{to{opacity:1;transform:translateY(0);}}
@keyframes shimmer{0%{background-position:100% 0;}100%{background-position:-100% 0;}}

/* ═══════════════════ COVER HERO ═══════════════════ */
#cover{
  position:fixed;inset:0;z-index:9998;
  background:radial-gradient(ellipse at 50% 40%,#0d0820 0%,#050505 70%);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  overflow:hidden;
  opacity:0;pointer-events:none;
  transition:opacity .6s ease;
}
#cover.visible{opacity:1;pointer-events:all;}
#coverCanvas{position:absolute;inset:0;z-index:0;}

/* ambient orbs */
.orb{
  position:absolute;border-radius:50%;filter:blur(80px);
  pointer-events:none;z-index:1;
}
.orb-v{width:600px;height:600px;background:rgba(123,97,255,.07);top:-10%;left:-15%;}
.orb-c{width:500px;height:500px;background:rgba(0,229,255,.05);bottom:-10%;right:-10%;}
.orb-l{width:300px;height:300px;background:rgba(212,242,90,.04);top:30%;left:60%;}

/* scan line on entry */
.scan-line{
  position:absolute;left:0;right:0;height:2px;top:0;z-index:4;
  background:linear-gradient(90deg,transparent,rgba(0,229,255,.7),transparent);
  opacity:0;
}
#cover.animate .scan-line{opacity:1;animation:scan-sweep 1s ease forwards;}
@keyframes scan-sweep{0%{top:0;opacity:1;}100%{top:100%;opacity:0;}}

.cover-inner{
  position:relative;z-index:3;
  display:flex;flex-direction:column;align-items:center;
  text-align:center;padding:0 20px;
  max-width:900px;
}

/* pill badge */
.cover-pill{
  display:inline-flex;align-items:center;gap:8px;
  border:1px solid rgba(0,229,255,.3);border-radius:99px;
  padding:6px 20px 6px 12px;background:rgba(0,229,255,.06);
  font-family:'JetBrains Mono',monospace;font-size:.72rem;font-weight:500;
  color:#38bdf8;letter-spacing:.06em;
  margin-bottom:52px;
  opacity:0;transform:translateY(14px);
  transition:opacity .7s ease .15s,transform .7s cubic-bezier(.34,1.2,.64,1) .15s;
}
#cover.animate .cover-pill{opacity:1;transform:translateY(0);}
.pill-dot{width:6px;height:6px;border-radius:50%;background:#38bdf8;animation:pill-blink 1.8s ease-in-out infinite;}

/* headline container */
.cover-headline{
  display:flex;flex-direction:column;align-items:center;
  margin:0 0 36px;
  line-height:.88;
}
.hl-line{
  display:flex;align-items:center;justify-content:center;
  overflow:hidden;
}
/* each char */
.ch{
  display:inline-block;
  font-family:'Syne',sans-serif;
  font-size:clamp(3.8rem,11vw,9rem);
  font-weight:800;
  letter-spacing:-.04em;
  opacity:0;
  transform:translateY(115%) rotateX(-45deg);
  transform-origin:center bottom;
  transition:opacity .55s ease, transform .55s cubic-bezier(.34,1.25,.64,1);
  /* per-line gradient set inline via JS */
}
#cover.animate .ch.go{
  opacity:1;transform:translateY(0) rotateX(0deg);
}
.ch-space{display:inline-block;width:.28em;}

/* after headline — kinetic tag */
.cover-tag{
  font-family:'JetBrains Mono',monospace;
  font-size:.75rem;
  letter-spacing:.22em;
  text-transform:uppercase;
  color:rgba(167,139,250,.6);
  margin-bottom:30px;
  opacity:0;transform:translateY(10px);
  transition:opacity .7s ease 1.7s,transform .7s ease 1.7s;
}
#cover.animate .cover-tag{opacity:1;transform:translateY(0);}

/* subtitle */
.cover-sub{
  font-family:'DM Sans',sans-serif;
  font-size:clamp(.95rem,1.8vw,1.2rem);
  color:#94a3b8;
  max-width:520px;line-height:1.85;
  margin:0 0 52px;
  opacity:0;transform:translateY(18px);
  transition:opacity .8s ease 1.9s,transform .8s cubic-bezier(.4,0,.2,1) 1.9s;
}
#cover.animate .cover-sub{opacity:1;transform:translateY(0);}

/* stats */
.cover-stats{
  display:flex;
  border:1px solid rgba(255,255,255,.07);border-radius:16px;
  overflow:hidden;background:rgba(255,255,255,.025);backdrop-filter:blur(20px);
  opacity:0;transform:translateY(20px);
  transition:opacity .8s ease 2.3s,transform .8s cubic-bezier(.4,0,.2,1) 2.3s;
  margin-bottom:52px;
}
#cover.animate .cover-stats{opacity:1;transform:translateY(0);}
.stat{padding:18px 28px;border-right:1px solid rgba(255,255,255,.07);text-align:center;}
.stat:last-child{border-right:none;}
.stat-num{font-family:'Syne',sans-serif;font-size:1.7rem;font-weight:800;line-height:1;}
.stat-lbl{font-size:.65rem;color:#64748b;letter-spacing:.1em;text-transform:uppercase;margin-top:3px;}

/* scroll CTA */
.scroll-cta{
  display:flex;flex-direction:column;align-items:center;gap:10px;
  opacity:0;
  transition:opacity .8s ease 2.9s;
}
#cover.animate .scroll-cta{opacity:1;}
.scroll-lbl{font-family:'JetBrains Mono',monospace;font-size:.68rem;color:#334155;letter-spacing:.22em;text-transform:uppercase;}
.scroll-mouse{width:26px;height:38px;border:1.5px solid rgba(56,189,248,.35);border-radius:13px;display:flex;justify-content:center;padding-top:6px;}
.scroll-dot{width:3px;height:7px;border-radius:2px;background:#38bdf8;animation:scroll-fall 2s ease-in-out infinite;}

@keyframes pill-blink{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.3;transform:scale(.6);}}
@keyframes scroll-fall{0%,100%{transform:translateY(0);opacity:1;}65%{transform:translateY(14px);opacity:0;}66%{transform:translateY(0);opacity:0;}80%{opacity:1;}}
</style>
</head>
<body>

<!-- ═══ PRELOADER ═══ -->
<div id="preloader">
  <canvas id="bgCanvas"></canvas>
  <div class="ring-wrap">
    <div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div>
    <div class="ring-inner"><span class="bolt">⚡</span></div>
  </div>
  <div class="brand-name" id="brandLetters"></div>
  <div class="status-line" id="statusLine">INITIALISING FORGE ENGINE…</div>
  <div class="prog-track"><div class="prog-bar" id="progBar"></div></div>
  <button id="enter-btn" onclick="enterForge()">⚡ &nbsp;ENTER THE FORGE</button>
</div>

<!-- ═══ COVER HERO ═══ -->
<div id="cover">
  <canvas id="coverCanvas"></canvas>
  <div class="orb orb-v"></div>
  <div class="orb orb-c"></div>
  <div class="orb orb-l"></div>
  <div class="scan-line"></div>

  <div class="cover-inner">
    <div class="cover-pill">
      <span class="pill-dot"></span>
      Agentic AI &nbsp;·&nbsp; Real-Time Research &nbsp;·&nbsp; LLM Scoring
    </div>

    <div class="cover-headline" id="coverHead">
      <!-- built by JS -->
    </div>

    <div class="cover-tag">— Powered by Agentic Intelligence —</div>

    <p class="cover-sub">
      Market intelligence meets AI creativity.<br>
      Your name is <em>engineered</em> to cut through the noise and own the room.
    </p>

    <div class="cover-stats">
      <div class="stat"><div class="stat-num" style="color:#38bdf8;">5</div><div class="stat-lbl">Names Forged</div></div>
      <div class="stat"><div class="stat-num" style="color:#a78bfa;">Live</div><div class="stat-lbl">Web Research</div></div>
      <div class="stat"><div class="stat-num" style="color:#d4f25a;">4</div><div class="stat-lbl">Score Axes</div></div>
      <div class="stat"><div class="stat-num" style="color:#f472b6;">~30s</div><div class="stat-lbl">End-to-End</div></div>
    </div>

    <div class="scroll-cta">
      <div class="scroll-lbl">Scroll to forge</div>
      <div class="scroll-mouse"><div class="scroll-dot"></div></div>
    </div>
  </div>
</div>

<script>
/* ─── PRELOADER PARTICLES ─── */
const bc=document.getElementById('bgCanvas'),bctx=bc.getContext('2d');
bc.width=window.innerWidth;bc.height=window.innerHeight;
const bpts=Array.from({length:90},()=>({
  x:Math.random()*bc.width,y:Math.random()*bc.height,
  vx:(Math.random()-.5)*.28,vy:(Math.random()-.5)*.28,
  r:Math.random()*1.2+.3,a:Math.random()*.5+.1,
  c:['#7b61ff','#00e5ff','#c8ff00'][Math.floor(Math.random()*3)]
}));
function drawBg(){
  bctx.clearRect(0,0,bc.width,bc.height);
  bpts.forEach(p=>{
    p.x+=p.vx;p.y+=p.vy;
    if(p.x<0)p.x=bc.width;if(p.x>bc.width)p.x=0;
    if(p.y<0)p.y=bc.height;if(p.y>bc.height)p.y=0;
    bctx.beginPath();bctx.arc(p.x,p.y,p.r,0,Math.PI*2);
    bctx.fillStyle=p.c;bctx.globalAlpha=p.a;bctx.fill();
  });
  bctx.globalAlpha=1;
  for(let i=0;i<bpts.length;i++)for(let j=i+1;j<bpts.length;j++){
    const dx=bpts[i].x-bpts[j].x,dy=bpts[i].y-bpts[j].y,d=Math.sqrt(dx*dx+dy*dy);
    if(d<90){
      bctx.beginPath();bctx.moveTo(bpts[i].x,bpts[i].y);bctx.lineTo(bpts[j].x,bpts[j].y);
      bctx.strokeStyle='rgba(123,97,255,'+(0.07*(1-d/90))+')';bctx.lineWidth=.5;bctx.stroke();
    }
  }
  requestAnimationFrame(drawBg);
}
drawBg();

/* brand letter reveal */
const forge='NAMEFORGE',ai='\u00A0\u00A0AI',cont=document.getElementById('brandLetters');
let idx=0;
forge.split('').forEach(ch=>{const s=document.createElement('span');s.textContent=ch;s.className='pf';s.style.animationDelay=(0.3+idx*.055)+'s';cont.appendChild(s);idx++;});
ai.split('').forEach(ch=>{const s=document.createElement('span');s.textContent=ch;s.className=(ch==='\u00A0')?'pf':'pa';s.style.animationDelay=(0.3+idx*.055)+'s';cont.appendChild(s);idx++;});

/* progress sequence */
const seq=[
  [0,'INITIALISING FORGE ENGINE…'],
  [18,'LOADING AGENT MODULES…'],
  [38,'CONFIGURING AI ENGINE…'],
  [56,'CONNECTING LIVE SEARCH…'],
  [72,'WARMING UP LLM JUDGE…'],
  [88,'CALIBRATING BRAND MATRIX…'],
  [100,'READY TO DOMINATE ⚡']
];
const bar=document.getElementById('progBar'),sl=document.getElementById('statusLine');
let step=0;
function tick(){
  if(step>=seq.length)return;
  const[pct,msg]=seq[step];bar.style.width=pct+'%';sl.textContent=msg;step++;
  if(step<seq.length)setTimeout(tick,480+Math.random()*300);
}
setTimeout(tick,400);

/* show ENTER button after sequence completes */
setTimeout(()=>{document.getElementById('enter-btn').classList.add('show');},6300);

/* ─── ENTER TRANSITION ─── */
function enterForge(){
  const pre=document.getElementById('preloader');
  const cov=document.getElementById('cover');
  pre.classList.add('exit');
  cov.classList.add('visible');
  setTimeout(()=>{
    cov.classList.add('animate');
    buildHeadline();
  },250);
  setTimeout(()=>{
    try{window.frameElement.style.height='100vh';}catch(e){}
  },2000);
}

/* ─── COVER MESH CANVAS ─── */
const cm=document.getElementById('coverCanvas'),cmctx=cm.getContext('2d');
cm.width=window.innerWidth;cm.height=window.innerHeight;
const COLS=26,ROWS=15;
let mpts=[];
for(let r=0;r<=ROWS;r++)for(let c=0;c<=COLS;c++)
  mpts.push({bx:(c/COLS)*cm.width,by:(r/ROWS)*cm.height,ox:0,oy:0,vx:(Math.random()-.5)*.32,vy:(Math.random()-.5)*.28});
function meshTick(){
  cmctx.clearRect(0,0,cm.width,cm.height);
  mpts.forEach(p=>{p.ox+=p.vx;p.oy+=p.vy;if(Math.abs(p.ox)>15)p.vx*=-1;if(Math.abs(p.oy)>12)p.vy*=-1;});
  for(let r=0;r<ROWS;r++){for(let c=0;c<COLS;c++){
    const i=r*(COLS+1)+c;
    const p=mpts[i],pr=mpts[i+1],pb=mpts[i+COLS+1];
    cmctx.beginPath();cmctx.moveTo(p.bx+p.ox,p.by+p.oy);cmctx.lineTo(pr.bx+pr.ox,pr.by+pr.oy);
    cmctx.strokeStyle='rgba(167,139,250,0.08)';cmctx.lineWidth=.5;cmctx.stroke();
    cmctx.beginPath();cmctx.moveTo(p.bx+p.ox,p.by+p.oy);cmctx.lineTo(pb.bx+pb.ox,pb.by+pb.oy);
    cmctx.strokeStyle='rgba(56,189,248,0.06)';cmctx.lineWidth=.5;cmctx.stroke();
  }}
  requestAnimationFrame(meshTick);
}
meshTick();

/* ─── HEADLINE CHAR-BY-CHAR REVEAL ─── */
const LINES=[
  {text:'BUILD BOLD.',  grad:'linear-gradient(135deg,#ffffff 0%,#c4b5fd 40%,#38bdf8 100%)'},
  {text:'WIN BIG.',     grad:'linear-gradient(135deg,#d4f25a 0%,#38bdf8 45%,#a78bfa 100%)'},
];
function buildHeadline(){
  const head=document.getElementById('coverHead');
  head.innerHTML='';
  let totalDelay=320;
  LINES.forEach((line)=>{
    const lineDiv=document.createElement('div');
    lineDiv.className='hl-line';
    line.text.split('').forEach((ch)=>{
      if(ch===' '){
        const sp=document.createElement('span');
        sp.className='ch-space';
        lineDiv.appendChild(sp);
        return;
      }
      const span=document.createElement('span');
      span.className='ch';
      span.textContent=ch;
      span.style.background=line.grad;
      span.style.backgroundSize='300% 300%';
      span.style.webkitBackgroundClip='text';
      span.style.webkitTextFillColor='transparent';
      span.style.backgroundClip='text';
      span.style.animation='grad-shift 7s ease infinite';
      lineDiv.appendChild(span);
      const d=totalDelay;
      setTimeout(()=>span.classList.add('go'),d);
      totalDelay+=58;
    });
    head.appendChild(lineDiv);
    totalDelay+=120; /* gap between lines */
  });
}

/* scroll to dismiss cover */
document.addEventListener('wheel',()=>{
  try{
    window.parent.scrollBy({top:window.parent.innerHeight,behavior:'smooth'});
    setTimeout(()=>{
      try{window.frameElement.style.height='0px';window.frameElement.style.display='none';}catch(e){}
    },700);
  }catch(e){}
},{once:true,passive:true});

/* also handle touch */
let ty0=0;
document.addEventListener('touchstart',e=>{ty0=e.touches[0].clientY;},{passive:true});
document.addEventListener('touchend',e=>{
  if(ty0-e.changedTouches[0].clientY>40){
    try{
      window.parent.scrollBy({top:window.parent.innerHeight,behavior:'smooth'});
      setTimeout(()=>{try{window.frameElement.style.height='0px';window.frameElement.style.display='none';}catch(e){}},700);
    }catch(e){}
  }
},{once:true,passive:true});
</script>
<style>
@keyframes grad-shift{0%{background-position:0% 50%;}50%{background-position:100% 50%;}100%{background-position:0% 50%;}}
</style>
</body>
</html>
""", height=700, scrolling=False)

# ─────────────────────────────────────────────────────────────────────────────
# MASTER CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Hard-kill Streamlit chrome ── */
.stApp { background-color: #050505 !important; }
div[data-baseweb="notification"], .stAlert,
div[class*="stAlert"], [data-testid="stStatusWidget"] {
  background-color: rgba(255,255,255,0.03) !important;
  color: #fff !important;
  border: 1px solid #222 !important;
  border-radius: 12px !important;
  backdrop-filter: blur(10px);
}
h1, h2, h3, p { font-family: 'DM Sans', sans-serif; }
[data-testid="stSidebar"]          { display: none !important; }
[data-testid="stHeader"]           { background: transparent !important; }
#MainMenu, footer                  { visibility: hidden; }
[data-testid="stToolbar"],
[data-testid="stDecoration"],
button[kind="header"],
.stDeployButton,
[data-testid="stBaseButton-header"]{ display: none !important; }

/* ── CSS Vars ── */
:root {
  --ink:    #040407;
  --s1:     #0a0a12;
  --s2:     rgba(255,255,255,0.03);
  --border: rgba(255,255,255,0.07);
  --border2:rgba(255,255,255,0.14);
  --cyan:   #38bdf8;
  --violet: #a78bfa;
  --lime:   #d4f25a;
  --text:   #f1f5f9;
  --muted:  #94a3b8;
  --r:      16px;
}

* { box-sizing: border-box; }

/* ── Cursor glow ── */
#cursor-glow {
  pointer-events: none;
  position: fixed;
  width: 500px; height: 500px;
  border-radius: 50%;
  transform: translate(-50%,-50%);
  background: radial-gradient(circle, rgba(0,229,255,.06) 0%, transparent 70%);
  transition: left .12s ease, top .12s ease;
  z-index: 9999;
  mix-blend-mode: screen;
}

/* ── 3D Canvas ── */
#three-canvas-wrap {
  position: relative;
  width: 100%;
  height: 420px;
  overflow: hidden;
  border-radius: 0 0 40px 40px;
  margin-bottom: -60px;
}
#three-canvas-wrap canvas {
  display: block;
  width: 100% !important;
  height: 100% !important;
}

/* ── Hero overlay ── */
.hero-overlay {
  position: relative;
  z-index: 10;
  text-align: center;
  padding: 0 20px 60px;
  pointer-events: none;
}
.hero-eyebrow {
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
  font-size: .68rem;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--cyan);
  border: 1px solid rgba(0,229,255,.25);
  padding: 5px 18px;
  border-radius: 99px;
  margin-bottom: 20px;
  background: rgba(0,229,255,.04);
}
.hero-title {
  font-family: 'Syne', sans-serif !important;
  font-size: clamp(2.4rem, 8vw, 5.6rem) !important;
  font-weight: 800 !important;
  line-height: 1.0 !important;
  letter-spacing: -3px !important;
  margin: 0 0 20px !important;
  color: transparent !important;
  background: linear-gradient(135deg, #ffffff 0%, #c4b5fd 40%, #38bdf8 100%);
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  background-clip: text !important;
}
.hero-sub {
  color: #c8d5e8 !important;
  font-size: 1.15rem !important;
  max-width: 520px;
  margin: 0 auto 0 !important;
  line-height: 1.8 !important;
  -webkit-text-fill-color: #c8d5e8 !important;
}

/* ── Input panel ── */
.input-panel {
  max-width: 780px;
  margin: 0 auto 60px;
  background: rgba(13,13,20,0.85);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 40px 44px;
  backdrop-filter: blur(30px);
  box-shadow: 0 40px 80px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.06);
}
.input-panel-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 28px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.input-panel-title::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* ── Inputs ── */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stSelectbox>div>div>div {
  background: rgba(255,255,255,0.02) !important;
  border: 1px solid rgba(255,255,255,0.09) !important;
  border-radius: 12px !important;
  color: #f0f0f5 !important;
  font-family: 'DM Sans', sans-serif !important;
  transition: border-color .2s, box-shadow .2s !important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {
  border-color: var(--violet) !important;
  box-shadow: 0 0 0 3px rgba(123,97,255,.12) !important;
}
label[data-testid="stWidgetLabel"] p {
  font-size: .82rem !important;
  font-weight: 500 !important;
  letter-spacing: 1.2px !important;
  text-transform: uppercase !important;
  color: var(--muted) !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* ── CTA Button ── */
.stButton>button {
  background: linear-gradient(135deg, var(--violet), #5a3fd4) !important;
  color: #fff !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  font-size: .95rem !important;
  border: none !important;
  border-radius: 14px !important;
  padding: .8rem 2.5rem !important;
  letter-spacing: .5px !important;
  transition: transform .15s, box-shadow .15s !important;
  box-shadow: 0 4px 30px rgba(123,97,255,.3) !important;
  position: relative !important;
}
.stButton>button:hover {
  transform: translateY(-3px) scale(1.02) !important;
  box-shadow: 0 0 0 1px var(--violet), 0 8px 40px rgba(123,97,255,.45) !important;
}
.stButton>button:active { transform: scale(.97) !important; }

/* ── Pipeline tracker ── */
.pipeline-track {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  max-width: 680px;
  margin: 32px auto 36px;
}
.p-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
  position: relative;
}
.p-step::after {
  content: '';
  position: absolute;
  top: 20px; left: 50%;
  width: 100%; height: 1px;
  background: var(--border);
  z-index: 0;
}
.p-step:last-child::after { display: none; }
.p-icon {
  width: 42px; height: 42px;
  border-radius: 50%;
  background: var(--s1);
  border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  z-index: 1;
  transition: all .4s;
  position: relative;
  color: var(--muted);
}
.p-icon.active {
  border-color: var(--cyan);
  background: rgba(0,229,255,.08);
  box-shadow: 0 0 20px rgba(0,229,255,.3);
  animation: pulse-ring 1.5s infinite;
}
.p-icon.done {
  border-color: var(--lime);
  background: rgba(200,255,0,.08);
  box-shadow: 0 0 16px rgba(200,255,0,.2);
}
.p-label {
  font-size: .84rem;
  font-family: 'DM Sans', sans-serif;
  font-weight: 500;
  color: var(--muted);
  text-align: center;
  letter-spacing: .2px;
  transition: color .3s;
}
.p-step.active .p-label { color: var(--cyan); }
.p-step.done .p-label   { color: var(--lime); }
@keyframes pulse-ring {
  0%   { box-shadow: 0 0 0 0 rgba(0,229,255,.4); }
  70%  { box-shadow: 0 0 0 10px rgba(0,229,255,0); }
  100% { box-shadow: 0 0 0 0 rgba(0,229,255,0); }
}

/* ── Trace cards ── */
.trace-wrap { max-width: 780px; margin: 0 auto; }
.trace-card {
  display: flex;
  gap: 14px;
  background: rgba(13,13,20,0.7);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 18px;
  margin: 8px 0;
  animation: slide-up .35s ease both;
  backdrop-filter: blur(10px);
}
.trace-icon {
  width: 32px; height: 32px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: .9rem;
  flex-shrink: 0;
}
.trace-card.thought     .trace-icon { background: rgba(123,97,255,.15); }
.trace-card.action      .trace-icon { background: rgba(0,229,255,.1); }
.trace-card.observation .trace-icon { background: rgba(110,231,183,.1); }
.trace-body { flex: 1; }
.trace-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: .6rem; font-weight: 500;
  letter-spacing: 2px; text-transform: uppercase;
  margin-bottom: 5px;
}
.trace-card.thought     .trace-tag { color: #a991ff; }
.trace-card.action      .trace-tag { color: var(--cyan); }
.trace-card.observation .trace-tag { color: #6ee7b7; }
.trace-text {
  font-size: .96rem;
  color: rgba(241,245,249,.8);
  line-height: 1.7;
  font-family: 'DM Sans', sans-serif;
}

/* ── Score cards ── */
.scores-section { max-width: 900px; margin: 0 auto; }
.score-card {
  background: rgba(13,13,20,0.85);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 28px;
  position: relative;
  overflow: hidden;
  transition: transform .3s cubic-bezier(.4,0,.2,1), border-color .3s, box-shadow .3s;
  animation: slide-up .4s ease both;
  backdrop-filter: blur(20px);
  margin-bottom: 20px;
}
.score-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--violet), transparent);
  opacity: 0;
  transition: opacity .3s;
}
.score-card:hover {
  transform: translateY(-8px);
  border-color: rgba(123,97,255,.4);
  box-shadow: 0 30px 60px rgba(0,0,0,.6), 0 0 40px rgba(123,97,255,.1);
}
.score-card:hover::before { opacity: 1; }
.score-card.champion {
  border-color: rgba(200,255,0,.3);
  box-shadow: 0 0 50px rgba(200,255,0,.06);
}
.score-card.champion::before {
  background: linear-gradient(90deg, transparent, var(--lime), transparent);
}
.card-rank {
  position: absolute;
  top: 18px; right: 18px;
  font-family: 'Syne', sans-serif;
  font-size: .6rem; font-weight: 800;
  letter-spacing: 2px; text-transform: uppercase;
  padding: 4px 12px; border-radius: 99px;
}
.card-rank.champion-badge {
  background: rgba(200,255,0,.12); color: var(--lime);
  border: 1px solid rgba(200,255,0,.3);
}
.card-rank.runner-badge {
  background: rgba(123,97,255,.1); color: #a991ff;
  border: 1px solid rgba(123,97,255,.25);
}
.card-name {
  font-family: 'Syne', sans-serif !important;
  font-size: 2rem !important; font-weight: 800 !important;
  letter-spacing: -1px !important;
  color: #fff !important; margin: 0 0 4px !important;
  -webkit-text-fill-color: #fff !important;
}
.card-domain {
  font-family: 'JetBrains Mono', monospace;
  font-size: .75rem; color: var(--cyan);
  margin-bottom: 16px; opacity: .8;
}
.card-rationale {
  font-size: .98rem !important;
  color: rgba(241,245,249,.72) !important;
  line-height: 1.75 !important; margin-bottom: 18px !important;
  -webkit-text-fill-color: rgba(241,245,249,.72) !important;
}
.card-score-bar {
  display: flex; align-items: center; gap: 14px;
  background: rgba(255,255,255,.03);
  border: 1px solid var(--border);
  border-radius: 12px; padding: 12px 18px; margin-bottom: 14px;
}
.score-num {
  font-family: 'Syne', sans-serif;
  font-size: 2rem; font-weight: 800;
  color: var(--lime); line-height: 1;
}
.score-of {
  font-size: .75rem; color: var(--muted);
  font-family: 'JetBrains Mono', monospace;
}
.score-track-wrap { flex: 1; }
.score-track {
  height: 4px; background: rgba(255,255,255,.08);
  border-radius: 2px; overflow: hidden;
}
.score-fill {
  height: 100%; border-radius: 2px;
  background: linear-gradient(90deg, #a78bfa, #38bdf8);
  transition: width 1s ease;
}
.card-verdict {
  font-size: .82rem !important;
  color: rgba(200,200,220,.7) !important;
  font-style: italic !important; line-height: 1.55 !important;
  padding-left: 12px;
  border-left: 2px solid rgba(123,97,255,.35);
  -webkit-text-fill-color: rgba(200,200,220,.7) !important;
}

/* ── Section headers ── */
.sec-head {
  font-family: 'Syne', sans-serif;
  font-size: 1.3rem; font-weight: 700;
  color: var(--text);
  display: flex; align-items: center; gap: 12px;
  max-width: 780px; margin: 52px auto 0;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}

/* ── How it works ── */
.how-strip {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 0; max-width: 900px; margin: 48px auto;
  border: 1px solid var(--border); border-radius: 20px;
  overflow: hidden; background: var(--s2);
}
.how-cell {
  padding: 28px 22px;
  border-right: 1px solid var(--border);
  transition: background .3s;
}
.how-cell:hover { background: rgba(167,139,250,.05); }
.how-cell:last-child { border-right: none; }
.how-num {
  font-family: 'Syne', sans-serif;
  font-size: 2.5rem; font-weight: 800;
  color: rgba(167,139,250,.25);
  line-height: 1; margin-bottom: 8px;
}
.how-icon { font-size: 1.3rem; margin-bottom: 10px; }
.how-title {
  font-family: 'Syne', sans-serif;
  font-size: .85rem; font-weight: 700;
  color: var(--text); margin-bottom: 6px;
}
.how-desc { font-size: .92rem; color: #c8d0e0; line-height: 1.7; font-family: 'DM Sans', sans-serif; }

/* ── Architecture diagram ── */
.arch-diagram {
  max-width: 900px; margin: 0 auto 52px;
  background: rgba(13,13,20,0.7);
  border: 1px solid var(--border);
  border-radius: 20px; padding: 32px 28px;
  backdrop-filter: blur(12px);
}
.arch-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: .68rem; letter-spacing: 2px;
  text-transform: uppercase; color: var(--muted);
  margin-bottom: 24px;
}
.arch-row {
  display: flex; align-items: center;
  justify-content: center; gap: 0; flex-wrap: wrap;
}
.arch-node {
  display: flex; flex-direction: column; align-items: center;
  gap: 6px; padding: 16px 20px;
  background: rgba(255,255,255,.02);
  border: 1px solid var(--border);
  border-radius: 14px; min-width: 110px; text-align: center;
  transition: transform .25s, border-color .25s, box-shadow .25s;
}
.arch-node:hover {
  transform: translateY(-4px);
  border-color: rgba(167,139,250,.35);
  box-shadow: 0 12px 32px rgba(167,139,250,.1);
}
.arch-node-icon { font-size: 1.4rem; }
.arch-node-label {
  font-family: 'Syne', sans-serif;
  font-size: .88rem; font-weight: 700; color: var(--text);
}
.arch-node-sub {
  font-size: .76rem; color: var(--muted);
  font-family: 'DM Sans', sans-serif; letter-spacing: .2px;
}
.arch-node.highlight-v { border-color: rgba(123,97,255,.4); background: rgba(123,97,255,.06); }
.arch-node.highlight-c { border-color: rgba(0,229,255,.3);  background: rgba(0,229,255,.05); }
.arch-node.highlight-l { border-color: rgba(200,255,0,.3);  background: rgba(200,255,0,.05); }
.arch-arrow { font-size: 1.1rem; color: var(--muted); padding: 0 6px; }

/* ── Error/maintenance ── */
.err-banner {
  max-width: 780px; margin: 20px auto;
  background: rgba(255,60,60,.05);
  border: 1px solid rgba(255,60,60,.2);
  border-radius: 14px; padding: 20px 24px;
  color: #ff9999; font-size: .9rem; line-height: 1.6;
}
.maint-banner {
  max-width: 900px; margin: 16px auto;
  background: rgba(255,150,0,.04);
  border: 1px solid rgba(255,150,0,.2);
  border-radius: 14px; padding: 18px 22px;
  color: #ffd580; font-size: .88rem; line-height: 1.6;
}

/* ── Animations ── */
@keyframes slide-up {
  from { opacity:0; transform: translateY(20px); }
  to   { opacity:1; transform: translateY(0); }
}
@keyframes fade-in-up {
  from { opacity:0; transform: translateY(32px); }
  to   { opacity:1; transform: translateY(0); }
}
.how-cell, .arch-node, .score-card {
  animation: fade-in-up .5s cubic-bezier(.4,0,.2,1) both;
}
.how-cell:nth-child(1) { animation-delay:.05s; }
.how-cell:nth-child(2) { animation-delay:.12s; }
.how-cell:nth-child(3) { animation-delay:.19s; }
.how-cell:nth-child(4) { animation-delay:.26s; }
@keyframes flicker {
  0%,100% { opacity:1; } 50% { opacity:.4; }
}

hr { border-color: var(--border) !important; margin: 0 !important; }
[data-testid="stCaptionContainer"] p {
  color: var(--muted) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: .72rem !important;
  -webkit-text-fill-color: var(--muted) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CURSOR GLOW + THREE.JS 3D HERO CANVAS
# ─────────────────────────────────────────────────────────────────────────────
st.components.v1.html("""
<div id="cursor-glow"></div>
<div id="three-canvas-wrap">
  <canvas id="heroCanvas"></canvas>
</div>

<style>
#cursor-glow {
  pointer-events:none; position:fixed; width:500px; height:500px;
  border-radius:50%; transform:translate(-50%,-50%);
  background:radial-gradient(circle,rgba(0,229,255,.06) 0%,transparent 70%);
  transition:left .12s ease,top .12s ease; z-index:9999; mix-blend-mode:screen;
}
#three-canvas-wrap {
  width:100%; height:420px; overflow:hidden;
  border-radius:0 0 40px 40px; margin-bottom:-60px;
}
#three-canvas-wrap canvas { display:block; width:100%!important; height:100%!important; }
</style>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const glow=document.getElementById('cursor-glow');
document.addEventListener('mousemove',e=>{
  glow.style.left=e.clientX+'px';
  glow.style.top=e.clientY+'px';
});

const wrap=document.getElementById('three-canvas-wrap');
const canvas=document.getElementById('heroCanvas');
const W=wrap.clientWidth||1200,H=420;

const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true});
renderer.setSize(W,H);
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));

const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(60,W/H,0.1,100);
camera.position.set(0,0,5);

const group=new THREE.Group();
scene.add(group);

const matV=new THREE.MeshBasicMaterial({color:0x7b61ff,wireframe:true,transparent:true,opacity:0.35});
const matC=new THREE.MeshBasicMaterial({color:0x00e5ff,wireframe:true,transparent:true,opacity:0.2});

const shapes=[];
for(let i=0;i<18;i++){
  const geo=i%3===0
    ?new THREE.IcosahedronGeometry(0.18+Math.random()*0.24,0)
    :i%3===1
      ?new THREE.OctahedronGeometry(0.2+Math.random()*0.22,0)
      :new THREE.TetrahedronGeometry(0.22+Math.random()*0.2,0);
  const mesh=new THREE.Mesh(geo,i%2===0?matV:matC);
  mesh.position.set((Math.random()-.5)*9,(Math.random()-.5)*3.5,(Math.random()-.5)*3);
  mesh.rotation.set(Math.random()*6,Math.random()*6,Math.random()*6);
  const speed=0.003+Math.random()*0.006;
  const axis=new THREE.Vector3(Math.random(),Math.random(),Math.random()).normalize();
  shapes.push({mesh,speed,axis});
  group.add(mesh);
}

const torusGeo=new THREE.TorusGeometry(0.9,0.03,8,80);
const torus=new THREE.Mesh(torusGeo,new THREE.MeshBasicMaterial({color:0x7b61ff,transparent:true,opacity:0.5}));
scene.add(torus);

const torus2=new THREE.Mesh(new THREE.TorusGeometry(1.3,0.02,6,100),new THREE.MeshBasicMaterial({color:0x00e5ff,transparent:true,opacity:0.25}));
torus2.rotation.x=Math.PI/3;
scene.add(torus2);

const pCount=400;
const pGeo=new THREE.BufferGeometry();
const pPos=new Float32Array(pCount*3);
for(let i=0;i<pCount*3;i++) pPos[i]=(Math.random()-.5)*14;
pGeo.setAttribute('position',new THREE.BufferAttribute(pPos,3));
const pts=new THREE.Points(pGeo,new THREE.PointsMaterial({color:0xffffff,size:0.025,transparent:true,opacity:0.3}));
scene.add(pts);

let mx=0,my=0;
document.addEventListener('mousemove',e=>{
  mx=(e.clientX/window.innerWidth-.5)*.4;
  my=(e.clientY/window.innerHeight-.5)*.2;
});

function animate(){
  requestAnimationFrame(animate);
  shapes.forEach(({mesh,speed,axis})=>mesh.rotateOnAxis(axis,speed));
  torus.rotation.z+=0.004; torus.rotation.x+=0.002;
  torus2.rotation.y+=0.003; torus2.rotation.z-=0.002;
  group.rotation.y+=0.001;
  pts.rotation.y+=0.0003;
  camera.position.x+=(mx-camera.position.x)*.05;
  camera.position.y+=(-my-camera.position.y)*.05;
  camera.lookAt(0,0,0);
  renderer.render(scene,camera);
}
animate();
</script>
""", height=430)

# ─────────────────────────────────────────────────────────────────────────────
# HERO TEXT (under the 3D canvas)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-overlay" style="margin-top:-400px;">
  <div class="hero-eyebrow">Agentic · Real-Time Research · LLM Judge</div>
  <h1 class="hero-title">THE SOUL OF<br>YOUR VENTURE</h1>
  <p class="hero-sub">Your agent scans the live market, forges five battle-tested brand identities — then an independent AI judge ranks them by dominance.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:90px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HOW IT WORKS STRIP
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="how-strip">
  <div class="how-cell">
    <div class="how-num">01</div>
    <div class="how-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><polygon points="16.24,7.76 14.12,14.12 7.76,16.24 9.88,9.88" fill="rgba(167,139,250,.2)" stroke="#a78bfa"/></svg></div>
    <div class="how-title">Brief</div>
    <div class="how-desc">Describe your industry, mission &amp; brand vibe</div>
  </div>
  <div class="how-cell">
    <div class="how-num">02</div>
    <div class="how-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="1.8" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.35-4.35"/></svg></div>
    <div class="how-title">Research</div>
    <div class="how-desc">Agent scans the live web for competitors &amp; trends</div>
  </div>
  <div class="how-cell">
    <div class="how-num">03</div>
    <div class="how-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#d4f25a" stroke-width="1.8" stroke-linecap="round"><polygon points="13,2 3,14 12,14 11,22 21,10 12,10"/></svg></div>
    <div class="how-title">Generate</div>
    <div class="how-desc">AI crafts 5 distinct, market-aware brand identities</div>
  </div>
  <div class="how-cell">
    <div class="how-num">04</div>
    <div class="how-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f472b6" stroke-width="1.8" stroke-linecap="round"><path d="M12 3v18"/><path d="M3 9l4-4 4 4M17 9l4-4"/><line x1="3" y1="20" x2="21" y2="20"/></svg></div>
    <div class="how-title">Judge</div>
    <div class="how-desc">A second LLM scores each name on a 4-axis rubric</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ARCHITECTURE DIAGRAM
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="arch-diagram">
  <div class="arch-title">// HOW THE MACHINE THINKS</div>
  <div class="arch-row">
    <div class="arch-node">
      <div class="arch-node-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg></div>
      <div class="arch-node-label">Your Brief</div>
      <div class="arch-node-sub">industry · vibe · mission</div>
    </div>
    <div class="arch-arrow">→</div>
    <div class="arch-node highlight-v">
      <div class="arch-node-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/><circle cx="12" cy="16" r="1.5" fill="#38bdf8" stroke="none"/></svg></div>
      <div class="arch-node-label">ReAct Agent</div>
      <div class="arch-node-sub">think · act · observe</div>
    </div>
    <div class="arch-arrow">⇄</div>
    <div class="arch-node highlight-c">
      <div class="arch-node-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="1.8" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.35-4.35"/></svg></div>
      <div class="arch-node-label">Live Search</div>
      <div class="arch-node-sub">live web results</div>
    </div>
    <div class="arch-arrow">→</div>
    <div class="arch-node highlight-v">
      <div class="arch-node-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#d4f25a" stroke-width="1.8" stroke-linecap="round"><polygon points="13,2 3,14 12,14 11,22 21,10 12,10"/></svg></div>
      <div class="arch-node-label">AI Engine</div>
      <div class="arch-node-sub">name generator</div>
    </div>
    <div class="arch-arrow">→</div>
    <div class="arch-node highlight-c">
      <div class="arch-node-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#f472b6" stroke-width="1.8" stroke-linecap="round"><path d="M12 3v18M5 8l14 0M3 12l4-4 4 4M17 12l4-4"/><circle cx="12" cy="3" r="1" fill="#f472b6" stroke="none"/></svg></div>
      <div class="arch-node-label">Score Engine</div>
      <div class="arch-node-sub">scoring engine</div>
    </div>
    <div class="arch-arrow">→</div>
    <div class="arch-node highlight-l">
      <div class="arch-node-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#d4f25a" stroke-width="1.8" stroke-linecap="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg></div>
      <div class="arch-node-label">Your Brands</div>
      <div class="arch-node-sub">score + verdict</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# INPUT PANEL
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="input-panel">', unsafe_allow_html=True)
st.markdown('<div class="input-panel-title">✦ Your Startup Brief</div>', unsafe_allow_html=True)

c1, c2 = st.columns([3, 2])
with c1:
    industry = st.text_input("Industry / Sector", placeholder="e.g. Neo-Banking · Eco-Tech · HealthTech")
with c2:
    vibe = st.selectbox(
        "Brand DNA",
        ["Professional", "Playful", "Bold", "Minimal", "Futuristic", "Wellness", "Luxury"],
    )

keywords = st.text_area(
    "Core Mission",
    placeholder="e.g. Making sustainable living effortless for urban millennials aged 25–40…",
    height=88,
)

_, bc, _ = st.columns([3, 2, 3])
with bc:
    generate_btn = st.button("⚡ Forge Identity", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for k in ["results", "error"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ─────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────
STEP_CONFIG = [("search", "Researching Niche"), ("gen", "Generating Names"), ("judge", "Judging Brandability")]

def render_pipeline(active: int):
    pills = ""
    for i, (icon, label) in enumerate(STEP_CONFIG):
        cls = "done" if i < active else ("active" if i == active else "")
        pills += f'<div class="p-step {cls}"><div class="p-icon {cls}">{icon}</div><div class="p-label">{label}</div></div>'
    st.markdown(f'<div class="pipeline-track">{pills}</div>', unsafe_allow_html=True)

TRACE_ICONS = {"thought": "◈", "action": "›", "observation": "○"}

def render_trace(step: AgentStep):
    icon = TRACE_ICONS.get(step.step_type, "·")
    tool_html = (
        f'<div style="margin-top:6px;font-family:JetBrains Mono,monospace;font-size:.72rem;color:#555570;">'
        f'tool: {step.tool_name}("{step.tool_input[:55]}…")</div>'
    ) if step.tool_name else ""
    st.markdown(
        f'<div class="trace-wrap"><div class="trace-card {step.step_type}">'
        f'<div class="trace-icon">{icon}</div>'
        f'<div class="trace-body"><div class="trace-tag">{step.step_type}</div>'
        f'<div class="trace-text">{step.content[:400]}</div>{tool_html}</div></div></div>',
        unsafe_allow_html=True,
    )

def render_thinking_animation():
    st.components.v1.html("""
<div style="text-align:center;padding:36px 20px;">
  <canvas id="thinkCanvas" width="160" height="160" style="display:block;margin:0 auto 16px;"></canvas>
  <div style="font-family:'JetBrains Mono',monospace;font-size:.78rem;color:#555570;
              animation:flicker 2s infinite;">judging brandability...</div>
</div>
<style>
@keyframes flicker{0%,100%{opacity:1}50%{opacity:.35}}
</style>
<script>
const cv=document.getElementById('thinkCanvas');
const ctx=cv.getContext('2d');
let angle=0;
const rings=[
  {r:60,speed:0.012,color:'rgba(123,97,255,0.5)',dash:[8,6]},
  {r:44,speed:-0.018,color:'rgba(0,229,255,0.4)',dash:[4,8]},
  {r:28,speed:0.025,color:'rgba(200,255,0,0.35)',dash:[3,5]},
];
function draw(){
  ctx.clearRect(0,0,160,160);
  rings.forEach(ring=>{
    ctx.save();ctx.translate(80,80);
    ctx.rotate(angle*ring.speed/0.012);
    ctx.strokeStyle=ring.color;ctx.lineWidth=1.5;
    ctx.setLineDash(ring.dash);ctx.beginPath();
    ctx.arc(0,0,ring.r,0,Math.PI*2);ctx.stroke();ctx.restore();
  });
  const pulse=0.5+0.5*Math.sin(angle*2);
  ctx.beginPath();ctx.arc(80,80,5+pulse*3,0,Math.PI*2);
  ctx.fillStyle=`rgba(123,97,255,${0.6+pulse*0.4})`;ctx.fill();
  angle+=0.04;requestAnimationFrame(draw);
}
draw();
</script>
""", height=220)

def render_score_card(score_data: dict, orig: dict, rank: int):
    name      = score_data.get("name", "—")
    score_raw = score_data.get("score", 0)
    verdict   = score_data.get("verdict", "")
    domain    = orig.get("domain", "")
    rationale = orig.get("rationale", "")
    try:
        score_f = float(score_raw)
        score_disp = f"{score_f:.1f}"
        pct = min(score_f / 10, 1.0) * 100
    except (TypeError, ValueError):
        score_disp = "—"; pct = 0
    is_champ = rank == 1
    card_cls = "score-card champion" if is_champ else "score-card"
    badge = (
        '<div class="card-rank champion-badge">★ TOP PICK</div>' if is_champ
        else f'<div class="card-rank runner-badge">#{rank}</div>'
    )
    st.markdown(f"""
    <div class="{card_cls}">
      {badge}
      <p class="card-name">{name}</p>
      <div class="card-domain">{domain}</div>
      <p class="card-rationale">{rationale}</p>
      <div class="card-score-bar">
        <div><div class="score-num">{score_disp}</div><div class="score-of">/ 10</div></div>
        <div class="score-track-wrap">
          <div class="score-track"><div class="score-fill" style="width:{pct}%"></div></div>
        </div>
      </div>
      <div class="card-verdict">"{verdict}"</div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE EXECUTION
# ─────────────────────────────────────────────────────────────────────────────
if generate_btn:
    if not industry.strip():
        st.warning("Please enter an industry to get started.")
        st.stop()

    st.session_state["results"] = None
    st.session_state["error"]   = None

    st.markdown('<div class="sec-head"><span style="font-family:monospace;font-size:.9em;color:#38bdf8;">[ AI ]</span> Agent Reasoning</div>', unsafe_allow_html=True)
    phase_ph = st.empty()
    with phase_ph.container():
        render_pipeline(0)

    try:
        gen, scorer, _, __ = run_pipeline(industry, keywords, vibe)

        agent_result = None
        phase = 0

        while True:
            try:
                step = next(gen)
            except StopIteration as e:
                agent_result = e.value
                break

            if step.step_type == "final":
                try:
                    names = json.loads(step.content)
                    agent_result = type("R", (), {"names": names, "research_context": "", "error": ""})()
                except Exception:
                    pass
                continue

            if step.step_type == "action":
                phase = 0
            elif step.step_type == "thought" and phase == 0:
                phase = 1
            with phase_ph.container():
                render_pipeline(phase)
            render_trace(step)

        with phase_ph.container():
            render_pipeline(2)

    except RuntimeError as e:
        st.session_state["error"] = str(e)
        st.rerun()
    except Exception as e:
        logging.exception("Pipeline error")
        st.session_state["error"] = f"Unexpected error: {e}"
        st.rerun()

    # ── Judge phase ──
    st.markdown('<div class="sec-head"><span style="font-family:monospace;font-size:.9em;color:#d4f25a;">[ # ]</span> Brandability Scores</div>', unsafe_allow_html=True)

    if agent_result and agent_result.names:
        judge_slot = st.empty()
        with judge_slot.container():
            render_thinking_animation()

        scores = None
        try:
            scores = scorer.score_names(industry, agent_result.names, getattr(agent_result, "research_context", ""))
            logging.info("Judge succeeded")
        except Exception as e:
            logging.error("Judge: %s", e)
            scores = {"error": str(e)}

        judge_slot.empty()

        if isinstance(scores, dict) and "error" in scores:
            err = scores["error"]
            st.markdown(
                f'<div class="maint-banner"><strong>⚙️ Evaluation Unavailable</strong> — '
                f'Names generated. Scoring hit a temporary issue — retry for scores.<br>'
                f'<small style="opacity:.55;">{err}</small></div>',
                unsafe_allow_html=True,
            )
            scores = [{"name": n["name"], "score": "—", "verdict": "Score pending."} for n in agent_result.names]

        def _sort(s):
            try: return float(s.get("score", 0))
            except: return 0.0

        scores_sorted = sorted(scores, key=_sort, reverse=True)
        orig_map      = {n["name"]: n for n in agent_result.names}

        st.markdown('<div class="scores-section">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        for i, sd in enumerate(scores_sorted):
            orig = orig_map.get(sd.get("name", ""), {})
            with (col1 if i % 2 == 0 else col2):
                render_score_card(sd, orig, i + 1)
        st.markdown("</div>", unsafe_allow_html=True)

        st.session_state["results"] = scores_sorted
    else:
        st.warning("No names generated — please try again.")

# ── Error banner ──
if st.session_state.get("error"):
    st.markdown(
        f'<div class="err-banner"><strong>❌ Error</strong><br>{st.session_state["error"]}</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:80px 20px 20px;border-top:1px solid rgba(255,255,255,.06);margin-top:60px;">
  <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;
              color:#fff;letter-spacing:.1em;margin-bottom:6px;">NAMEFORGE AI</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:.68rem;
              color:rgba(153,153,184,.5);letter-spacing:.2em;text-transform:uppercase;
              margin-bottom:40px;">Agentic Brand Intelligence</div>
  <div style="display:flex;justify-content:center;gap:16px;max-width:560px;
              margin:0 auto 40px;flex-wrap:wrap;">
    <div style="display:inline-flex;align-items:center;gap:10px;
                background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);
                border-radius:10px;padding:11px 18px;user-select:none;pointer-events:none;">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="rgba(167,139,250,.6)" stroke-width="1.8" stroke-linecap="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 7 10-7"/></svg>
      <span style="font-family:'JetBrains Mono',monospace;font-size:.78rem;
                   color:rgba(241,245,249,.45);letter-spacing:.02em;">manassahu.bsp@gmail.com</span>
    </div>
    <div style="display:inline-flex;align-items:center;gap:10px;
                background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);
                border-radius:10px;padding:11px 18px;user-select:none;pointer-events:none;">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="rgba(56,189,248,.6)" stroke-width="1.8" stroke-linecap="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 7 10-7"/></svg>
      <span style="font-family:'JetBrains Mono',monospace;font-size:.78rem;
                   color:rgba(241,245,249,.45);letter-spacing:.02em;">24damahed@rbunagpur.in</span>
    </div>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:.65rem;
              color:rgba(153,153,184,.3);letter-spacing:.15em;">
    © 2025 NameForge AI · All rights reserved
  </div>
</div>
""", unsafe_allow_html=True)