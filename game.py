from flask import Flask, render_template_string

app = Flask(__name__)

PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DINO: LAST LIGHT</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#090d19;color:#f5f5ff;font-family:Arial,sans-serif;
min-height:100vh;display:grid;place-items:center;overflow:hidden}
body:before{content:"";position:fixed;inset:0;pointer-events:none;
background:radial-gradient(ellipse at 50% 45%,#402544 0%,#12172b 50%,#050711 100%)}
.app{width:min(1000px,94vw);position:relative;z-index:1}
.top{display:flex;justify-content:space-between;align-items:center;
margin-bottom:32px;gap:10px}
.logo{font-size:12px;letter-spacing:5px;color:#ffb978;font-weight:bold}
.status{font-size:10px;color:#8b9bb8;letter-spacing:2px}
h1{font-size:clamp(36px,7vw,76px);letter-spacing:-4px;margin:0;
line-height:1;text-shadow:0 0 40px #ff6d4940}
h1 span{color:#ffac74}
.subtitle{color:#9eabc3;letter-spacing:4px;font-size:10px;margin-top:15px}
.heading{display:flex;justify-content:space-between;align-items:end;
margin-bottom:24px;gap:15px}
.best{text-align:right;color:#9daac1;font-size:10px;letter-spacing:2px}
.best strong{display:block;color:#ffbd83;font-size:25px;margin-top:8px}
.screen{position:relative;border:1px solid #ffb97855;
background:#111526;box-shadow:0 0 60px #ff6d4914,0 25px 80px #0009}
canvas{width:100%;height:auto;display:block;aspect-ratio:1000/370}
.hud{position:absolute;top:18px;left:20px;right:20px;
display:flex;justify-content:space-between;pointer-events:none}
.hud small{display:block;color:#a5afc6;font-size:9px;letter-spacing:3px}
.hud strong{display:block;font-size:23px;margin-top:6px}
#score{color:#fff}
#level{color:#ffbd83}
.overlay{position:absolute;inset:0;display:grid;place-items:center;
text-align:center;background:#080b16a8;backdrop-filter:blur(3px)}
.dialog{padding:24px;max-width:90%}
.kicker{font-size:10px;letter-spacing:4px;color:#ffb978;margin-bottom:15px}
h2{font-size:clamp(22px,4vw,36px);letter-spacing:3px;margin:0}
.desc{font-size:12px;line-height:1.8;color:#b4bfd3;margin:15px 0 22px}
button{border:1px solid #ffbd83;background:transparent;color:#ffe2c2;
padding:13px 20px;cursor:pointer;letter-spacing:2px;font-weight:bold}
button:hover{background:#ffbd83;color:#17101a}
button.main{background:#ffbd83;color:#1b1117}
.controls{display:flex;justify-content:space-between;align-items:center;
gap:16px;margin-top:20px;flex-wrap:wrap}
.help{font-size:10px;color:#929fba;line-height:2;letter-spacing:1px}
kbd{padding:4px 7px;border:1px solid #4b536c;border-radius:3px;color:#fff}
.buttons{display:flex;gap:8px}
.footer{display:flex;justify-content:space-between;gap:12px;
margin-top:32px;color:#596681;font-size:9px;letter-spacing:2px}
@media(max-width:600px){
.heading{margin-bottom:16px}.top{margin-bottom:22px}
.subtitle{letter-spacing:2px;font-size:9px}.status{font-size:8px}
.controls{margin-top:12px}.help{font-size:9px}
.buttons button{padding:10px;font-size:9px}
.footer{font-size:7px;margin-top:20px}
}
</style>
</head>
<body>
<main class="app">
  <div class="top">
    <div class="logo">AFTERLIGHT / ARCADE</div>
    <div class="status">● OFFLINE SYSTEM READY</div>
  </div>

  <div class="heading">
    <div>
      <h1>DINO: <span>LAST LIGHT</span></h1>
      <div class="subtitle">SURVIVE THE DESERT. CHASE THE DAWN.</div>
    </div>
    <div class="best">PERSONAL BEST<strong id="best">00000</strong></div>
  </div>

  <div class="screen">
    <canvas id="game" width="1000" height="370"></canvas>
    <div class="hud">
      <div><small>DISTANCE</small><strong id="score">00000</strong></div>
      <div style="text-align:right"><small>THREAT LEVEL</small>
        <strong id="level">01</strong></div>
    </div>
    <div class="overlay" id="overlay">
      <div class="dialog">
        <div class="kicker">THE WORLD WENT SILENT</div>
        <h2 id="title">RUN INTO THE UNKNOWN</h2>
        <div class="desc" id="desc">
          Jump over the ruins. Duck beneath the shadows.<br>
          How long can you survive?
        </div>
        <button class="main" id="start">▶ START RUN</button>
      </div>
    </div>
  </div>

  <div class="controls">
    <div class="help">
      <kbd>SPACE</kbd> / <kbd>↑</kbd> JUMP &nbsp;
      <kbd>↓</kbd> DUCK &nbsp; <kbd>P</kbd> PAUSE
    </div>
    <div class="buttons">
      <button id="sound">SOUND: OFF</button>
      <button id="restart">↻ RESTART</button>
    </div>
  </div>
  <div class="footer">
    <span>CHAPTER 01 — THE LAST DESERT</span>
    <span>NO INTERNET REQUIRED</span>
  </div>
</main>

<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const W = 1000, H = 370, GROUND = 285;

let state = "ready", score = 0, best = 0, speed = 7;
let frame = 0, timer = 0, obstacles = [], clouds = [];
let ducking = false, soundOn = false, audioCtx = null;
let particles = [];

try { best = Number(localStorage.getItem("lastLightBest") || 0); }
catch(e) {}
document.getElementById("best").textContent =
  String(best).padStart(5, "0");

const dino = {x:110, y:GROUND-49, w:42, h:49, vy:0};

function tone(freq, duration=0.08) {
  if (!soundOn) return;
  try {
    audioCtx = audioCtx || new AudioContext();
    const o = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    o.frequency.value = freq;
    o.connect(g); g.connect(audioCtx.destination);
    g.gain.setValueAtTime(0.04, audioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(
      0.001, audioCtx.currentTime + duration);
    o.start(); o.stop(audioCtx.currentTime + duration);
  } catch(e) {}
}

function begin() {
  score=0; speed=7; frame=0; timer=0;
  obstacles=[]; particles=[];
  dino.y=GROUND-dino.h; dino.vy=0;
  ducking=false; state="playing";
  document.getElementById("overlay").style.display="none";
  tone(500);
}

function jump() {
  if (state==="ready" || state==="over") { begin(); return; }
  if (state!=="playing") return;
  if (dino.y >= GROUND-dino.h-1) {
    dino.vy=-15; ducking=false; tone(620);
  }
}

function pause() {
  if(state==="playing"){
    state="paused";
    show("PAUSED IN THE DESERT","Press P or Start to continue.");
  } else if(state==="paused"){
    state="playing";
    document.getElementById("overlay").style.display="none";
  }
}

function show(title,desc) {
  document.getElementById("title").textContent=title;
  document.getElementById("desc").textContent=desc;
  document.getElementById("overlay").style.display="grid";
}

function gameOver() {
  state="over"; tone(120,0.25);
  if(Math.floor(score)>best){
    best=Math.floor(score);
    try{localStorage.setItem("lastLightBest",best)}catch(e){}
    document.getElementById("best").textContent=
      String(best).padStart(5,"0");
  }
  show("THE DESERT CLAIMS YOU",
    "Distance: "+Math.floor(score)+" m. Press Space to run again.");
}

function spawnObstacle() {
  let bird=Math.random()<0.24 && score>60;
  obstacles.push({
    x:W+20, w:bird?46:24+Math.random()*17,
    h:bird?23:35+Math.random()*30,
    y:bird?GROUND-78-Math.random()*25:0,
    bird:bird
  });
  let o=obstacles[obstacles.length-1];
  if(!bird)o.y=GROUND-o.h;
}

function update() {
  if(state!=="playing") return;
  frame++; score+=speed*0.085;
  speed=Math.min(15,7+score/250);
  timer--;
  if(timer<=0){spawnObstacle();timer=65+Math.random()*40-speed}

  dino.vy+=0.78;
  dino.y+=dino.vy;
  if(dino.y>GROUND-dino.h){
    dino.y=GROUND-dino.h;dino.vy=0;
  }

  obstacles.forEach(o=>o.x-=speed);
  obstacles=obstacles.filter(o=>o.x+o.w>0);

  let px=dino.x, py=ducking?GROUND-27:dino.y;
  let pw=ducking?48:dino.w, ph=ducking?27:dino.h;
  for(const o of obstacles){
    if(px+pw-8>o.x+4 && px+7<o.x+o.w-3 &&
       py+ph-5>o.y+3 && py+5<o.y+o.h-3){
      gameOver();break;
    }
  }

  particles.forEach(p=>{
    p.x+=p.vx;p.y+=p.vy;p.life--;
  });
  particles=particles.filter(p=>p.life>0);

  document.getElementById("score").textContent=
    String(Math.floor(score)).padStart(5,"0");
  document.getElementById("level").textContent=
    String(Math.min(9,1+Math.floor(score/180))).padStart(2,"0");
}

function drawDino() {
  let x=dino.x,y=ducking?GROUND-27:dino.y;
  ctx.save();
  ctx.shadowColor="#b8ffad";ctx.shadowBlur=18;
  ctx.fillStyle="#c8ffb6";

  if(ducking){
    ctx.fillRect(x,y+8,43,18);
    ctx.fillRect(x+32,y,18,15);
    ctx.fillStyle="#17182b";ctx.fillRect(x+43,y+5,4,4);
  } else {
    // Pixel-inspired T-Rex silhouette
    ctx.fillRect(x+5,y+17,27,23);
    ctx.fillRect(x+22,y+3,18,21);
    ctx.fillRect(x+33,y+9,14,8);
    ctx.fillRect(x+30,y+20,9,6);
    ctx.fillRect(x+10,y+35,9,14);
    ctx.fillRect(x+25,y+35,9,14);
    ctx.fillRect(x,y+20,9,5);
    ctx.fillStyle="#19172b";
    ctx.fillRect(x+33,y+7,4,4);
  }
  ctx.restore();
}

function draw() {
  ctx.clearRect(0,0,W,H);

  // Cinematic dusk sky
  let sky=ctx.createLinearGradient(0,0,0,H);
  sky.addColorStop(0,"#17172e");
  sky.addColorStop(.48,"#773c50");
  sky.addColorStop(1,"#f5a66e");
  ctx.fillStyle=sky;ctx.fillRect(0,0,W,H);

  // Sun glow
  let glow=ctx.createRadialGradient(740,135,5,740,135,180);
  glow.addColorStop(0,"#ffd9a7");
  glow.addColorStop(.25,"#ffb27c77");
  glow.addColorStop(1,"#ffad7000");
  ctx.fillStyle=glow;ctx.fillRect(500,0,450,300);
  ctx.fillStyle="#ffe0ac";
  ctx.beginPath();ctx.arc(740,135,43,0,Math.PI*2);ctx.fill();

  // Distant mountain silhouettes
  for(let layer=0;layer<3;layer++){
    ctx.fillStyle=["#493044","#33283d","#211e32"][layer];
    ctx.beginPath();ctx.moveTo(0,GROUND);
    for(let x=0;x<=W;x+=80){
      let y=175+layer*27+
        Math.sin(x*.017+layer*2)*30+
        Math.sin(x*.041+layer)*14;
      ctx.lineTo(x,y);
    }
    ctx.lineTo(W,GROUND);ctx.closePath();ctx.fill();
  }

  // Moving desert dunes
  ctx.fillStyle="#bd795e";
  ctx.beginPath();ctx.moveTo(0,GROUND);
  for(let x=0;x<=W;x+=10){
    ctx.lineTo(x,GROUND-12-
      Math.sin((x-frame*speed*.22)*.012)*9);
  }
  ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.fill();

  // Ground and glowing horizon
  ctx.fillStyle="#171729";ctx.fillRect(0,GROUND,W,H-GROUND);
  ctx.strokeStyle="#ffbd83";ctx.lineWidth=2;
  ctx.shadowColor="#ff925e";ctx.shadowBlur=12;
  ctx.beginPath();ctx.moveTo(0,GROUND);ctx.lineTo(W,GROUND);ctx.stroke();
  ctx.shadowBlur=0;

  // Ground dashes
  ctx.strokeStyle="#74445a";ctx.lineWidth=2;
  for(let x=-((frame*speed)%65);x<W;x+=65){
    ctx.beginPath();ctx.moveTo(x,GROUND+25);
    ctx.lineTo(x+28,GROUND+25);ctx.stroke();
  }

  // Obstacles
  obstacles.forEach(o=>{
    ctx.save();
    ctx.shadowColor=o.bird?"#ffe0a0":"#c8ffb6";
    ctx.shadowBlur=12;
    ctx.fillStyle=o.bird?"#e9b58c":"#b9e69e";

    if(o.bird){
      let flap=Math.sin(frame*.25)*6;
      ctx.fillRect(o.x+8,o.y+8,30,10);
      ctx.fillRect(o.x+15,o.y,10,10+flap);
      ctx.fillRect(o.x+2,o.y+13,10,5);
      ctx.fillRect(o.x+34,o.y+9,12,5);
    } else {
      ctx.fillRect(o.x+7,o.y,12,o.h);
      ctx.fillRect(o.x,o.y+12,9,18);
      ctx.fillRect(o.x+15,o.y+25,12,8);
      ctx.fillRect(o.x+20,o.y+31,7,o.h-31);
    }
    ctx.restore();
  });

  // Runner
  drawDino();

  // Minimal cinematic frame
  ctx.strokeStyle="#ffe0a033";ctx.lineWidth=1;
  ctx.strokeRect(12,12,W-24,H-24);
  ctx.fillStyle="#ffe0a0";ctx.font="10px monospace";
  ctx.fillText("DUST SECTOR / 01",25,H-16);
  ctx.textAlign="right";
  ctx.fillText("VELOCITY "+speed.toFixed(1),W-25,H-16);
  ctx.textAlign="left";
}

function loop(){update();draw();requestAnimationFrame(loop)}

document.addEventListener("keydown",e=>{
  if(["Space","ArrowUp","ArrowDown"].includes(e.code))e.preventDefault();
  if(e.repeat && e.code!=="ArrowDown")return;
  if(e.code==="Space"||e.code==="ArrowUp")jump();
  if(e.code==="ArrowDown")ducking=true;
  if(e.code==="KeyP")pause();
});
document.addEventListener("keyup",e=>{
  if(e.code==="ArrowDown")ducking=false;
});
canvas.addEventListener("pointerdown",()=>{
  if(state==="playing")jump();else if(state!=="paused")begin();
});
document.getElementById("start").onclick=()=>{
  if(state==="paused"){
    state="playing";
    document.getElementById("overlay").style.display="none";
  }else begin();
};
document.getElementById("restart").onclick=begin;
document.getElementById("sound").onclick=e=>{
  soundOn=!soundOn;
  e.target.textContent="SOUND: "+(soundOn?"ON":"OFF");
  tone(650);
};
loop();
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(PAGE)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)