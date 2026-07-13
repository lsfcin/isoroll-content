<!-- isoroll painter feel rig — P6.5 UX prototype v16; per-voxel scene + unified sloped groups (roofs/stairs), paints layout DSL, renders real gray kit -->
<title>isoroll painter — feel rig</title>
<style>
  :root{
    --bg:#16151B; --panel:#1F1E26; --line:#34323E; --ink:#D9D5CA; --dim:#8B8798;
    --accent:#E0A458; --accent-ink:#1a1206; --mark:#59D2CE; --danger:#C4574E;
    --canvas-bg:#101014;
  }
  @media (prefers-color-scheme: light){
    :root{ --bg:#ECE8DF; --panel:#F7F5EF; --line:#CFC9BC; --ink:#2B2833; --dim:#6F6A7A;
      --accent:#A66B2A; --accent-ink:#fff; --mark:#177E7A; --danger:#A33F38; --canvas-bg:#E2DDD2; }
  }
  :root[data-theme="dark"]{
    --bg:#16151B; --panel:#1F1E26; --line:#34323E; --ink:#D9D5CA; --dim:#8B8798;
    --accent:#E0A458; --accent-ink:#1a1206; --mark:#59D2CE; --danger:#C4574E; --canvas-bg:#101014;
  }
  :root[data-theme="light"]{
    --bg:#ECE8DF; --panel:#F7F5EF; --line:#CFC9BC; --ink:#2B2833; --dim:#6F6A7A;
    --accent:#A66B2A; --accent-ink:#fff; --mark:#177E7A; --danger:#A33F38; --canvas-bg:#E2DDD2;
  }
  html,body{height:100%;}
  body{ background:var(--bg); color:var(--ink);
    font:14px/1.5 system-ui, "Segoe UI", sans-serif; display:flex; flex-direction:column; margin:0; }
  header{ display:flex; align-items:baseline; gap:1.1rem; padding:.6rem 1.1rem;
    border-bottom:1px solid var(--line); flex-wrap:wrap; }
  header h1{ font:600 1.02rem/1 "Iowan Old Style", Palatino, Georgia, serif;
    letter-spacing:.06em; font-variant:small-caps; margin:0; }
  header h1 em{ color:var(--accent); font-style:normal; }
  .hud{ display:flex; gap:.9rem; align-items:baseline; font-family:ui-monospace, Menlo, Consolas, monospace;
    font-size:.76rem; color:var(--dim); flex-wrap:wrap; }
  .hud b{ color:var(--ink); font-weight:600; }
  #viewChip,#lvlChip{ background:var(--accent); color:var(--accent-ink); border-radius:3px;
    padding:.1rem .5rem; font-weight:700; letter-spacing:.08em; }
  #lvlChip{ background:var(--mark); color:#0d2321; }
  #scopeChip{ background:var(--panel); border:1px solid var(--line); border-radius:3px; padding:.1rem .4rem; }
  main{ flex:1; display:flex; min-height:0; }
  nav{ display:flex; flex-direction:column; gap:.32rem; padding:.7rem .6rem;
    border-right:1px solid var(--line); background:var(--panel); overflow-y:auto; }
  nav button{ display:flex; align-items:center; gap:.5rem; width:9rem;
    background:none; border:1px solid var(--line); border-radius:4px; color:var(--ink);
    padding:.36rem .6rem; font:inherit; font-size:.8rem; cursor:pointer; text-align:left; }
  nav button:hover{ border-color:var(--accent); }
  nav button:focus-visible{ outline:2px solid var(--mark); outline-offset:1px; }
  nav button.active{ background:var(--accent); color:var(--accent-ink); border-color:var(--accent); font-weight:600; }
  nav button.danger.active{ background:var(--danger); color:#fff; border-color:var(--danger); }
  nav kbd{ margin-left:auto; font:600 .66rem ui-monospace, monospace; color:inherit; opacity:.65;
    border:1px solid currentColor; border-radius:3px; padding:0 .28rem; }
  nav .sep{ height:1px; background:var(--line); margin:.25rem 0; }
  nav .rail-label{ font-size:.62rem; text-transform:uppercase; letter-spacing:.14em; color:var(--dim); padding:.15rem .1rem 0; }
  .stepper{ display:flex; align-items:center; gap:.3rem; padding:0 .15rem; font-size:.68rem; color:var(--dim); }
  .stepper button{ width:1.4rem; padding:.06rem; border:1px solid var(--line); background:none; color:var(--ink); border-radius:3px; cursor:pointer; }
  .stepper b{ font:600 .76rem ui-monospace,monospace; min-width:1.3rem; text-align:center; color:var(--ink); }
  #typeRow{ font-size:.68rem; color:var(--dim); padding:0 .15rem; }
  #typeRow b{ color:var(--ink); font:600 .74rem ui-monospace,monospace; }
  #stage{ flex:1; position:relative; background:var(--canvas-bg); min-width:0; }
  #cv{ position:absolute; inset:0; width:100%; height:100%; touch-action:none; cursor:crosshair; }
  #cv.panning{ cursor:grab; }
  #hint{ position:absolute; left:50%; bottom:.9rem; transform:translateX(-50%);
    background:var(--panel); border:1px solid var(--line); color:var(--dim);
    padding:.3rem .8rem; border-radius:4px; font-size:.78rem; opacity:0; transition:opacity .25s; pointer-events:none; }
  #hint.show{ opacity:1; }
  #coord{ position:absolute; right:.8rem; top:.6rem; font:.72rem ui-monospace,monospace; color:var(--dim); }
  aside{ width:19.5rem; border-left:1px solid var(--line); background:var(--panel);
    display:flex; flex-direction:column; gap:.85rem; padding:.85rem; overflow-y:auto; }
  aside h2{ font-size:.66rem; text-transform:uppercase; letter-spacing:.14em; color:var(--dim);
    margin:0 0 .3rem; font-weight:600; }
  textarea{ width:100%; box-sizing:border-box; background:var(--bg); color:var(--ink);
    border:1px solid var(--line); border-radius:4px; font:.72rem/1.42 ui-monospace, monospace;
    padding:.5rem; resize:vertical; white-space:pre; }
  #dsl{ height:12rem; }
  aside .row{ display:flex; gap:.5rem; }
  aside .row button{ flex:1; background:none; border:1px solid var(--line); border-radius:4px;
    color:var(--ink); padding:.32rem; font:inherit; font-size:.76rem; cursor:pointer; }
  aside .row button:hover{ border-color:var(--accent); }
  #copied{ color:var(--mark); font-size:.72rem; visibility:hidden; }
  ul.feel{ margin:0; padding-left:1.05rem; font-size:.78rem; color:var(--dim); display:flex; flex-direction:column; gap:.4rem; }
  ul.feel li::marker{ color:var(--accent); }
  ul.feel b{ color:var(--ink); }
  footer{ border-top:1px solid var(--line); padding:.35rem 1.1rem; font:.7rem ui-monospace,monospace; color:var(--dim); }
  @media (max-width:820px){ aside{ display:none; } }
</style>

<header>
  <h1>isoroll <em>painter</em> — feel rig <span style="color:var(--dim);font-variant:normal;font-size:.72rem">P6.5 v16</span></h1>
  <div class="hud">
    <span>view <span id="viewChip">NW</span></span>
    <span>layer <span id="lvlChip">0</span></span>
    <span>scope <span id="scopeChip">cell</span></span>
    <span>walls <b id="cWall">0</b></span>
    <span>doors <b id="cDoor">0</b></span>
    <span>win <b id="cWin">0</b></span>
    <span>stairs <b id="cStair">0</b></span>
    <span>floor <b id="cFloor">0</b></span>
    <span>grps <b id="cRoof">0</b></span>
  </div>
</header>

<main>
  <nav aria-label="tools">
    <div class="rail-label">paint</div>
    <button data-tool="#" class="active">Wall <kbd>1</kbd></button>
    <button data-tool=".">Floor <kbd>2</kbd></button>
    <button data-tool="D">Door <kbd>3</kbd></button>
    <button data-tool="W">Window <kbd>4</kbd></button>
    <button data-tool="^" id="stairBtn">Stairs <span id="stairChip">solid ↑</span> <kbd>5</kbd></button>
    <button data-tool="R" id="roofBtn">Roof <span id="roofChip">shed1 ↑</span> <kbd>6</kbd></button>
    <button data-tool=" " class="danger">Erase <kbd>X</kbd></button>
    <div id="typeRow">type <b id="typeChip">stone</b> <span style="opacity:.7">(M)</span></div>
    <div class="stepper"><span>height</span>
      <button id="hMinus">−</button><b id="hVal">2</b><button id="hPlus">+</button></div>
    <div class="stepper"><span>slope ft</span>
      <button id="iMinus">−</button><b id="iVal">5</b><button id="iPlus">+</button></div>
    <div class="stepper"><span>layer</span>
      <button id="lvlMinus">−</button><b id="lvlVal">0</b><button id="lvlPlus">+</button></div>
    <div class="sep"></div>
    <div class="rail-label">visibility</div>
    <div class="stepper"><span>opaque win</span>
      <button id="wMinus">−</button><b id="wVal">2</b><button id="wPlus">+</button></div>
    <div class="stepper"><span>fade %</span>
      <button id="oMinus">−</button><b id="oVal">20</b><button id="oPlus">+</button></div>
    <div class="sep"></div>
    <div class="rail-label">camera</div>
    <button id="rotL">⟲ Rotate <kbd>Q</kbd></button>
    <button id="rotR">⟳ Rotate <kbd>E</kbd></button>
    <button id="topBtn">Top view <kbd>T</kbd></button>
    <button id="fitBtn">Reset camera <kbd>C</kbd></button>
    <div class="sep"></div>
    <div class="rail-label">board</div>
    <div class="stepper"><span>cols</span>
      <button id="colMinus">−</button><b id="colVal">16</b><button id="colPlus">+</button></div>
    <div class="stepper"><span>rows</span>
      <button id="rowMinus">−</button><b id="rowVal">14</b><button id="rowPlus">+</button></div>
    <div class="sep"></div>
    <button id="undoBtn">Undo <kbd>⌃Z</kbd></button>
    <button id="clearBtn" class="danger">Clear all</button>
  </nav>

  <div id="stage">
    <canvas id="cv"></canvas>
    <div id="coord"></div>
    <div id="hint"></div>
  </div>

  <aside>
    <div>
      <h2>layout DSL v2 draft — levels + roof groups</h2>
      <textarea id="dsl" readonly spellcheck="false" aria-label="layout DSL"></textarea>
      <div class="row" style="margin-top:.4rem">
        <button id="copyBtn">Copy DSL</button>
        <button id="lroomBtn">Reset to l-room</button>
      </div>
      <div id="copied">copied — DSL v2 parser lands with the memo</div>
    </div>
    <div>
      <h2>v16 — stairs = roofs = sloped groups</h2>
      <ul class="feel">
        <li><b>One concept</b>: roofs and stairs are both sloped-surface groups (cells, direction, slope, base z). Roof surface is smooth (slope 1–5 ft/cell); stair surface is stepped.</li>
        <li><b>Stairs land on floors</b>, so they get exactly two slopes: 45° (1 voxel/cell, 1ft risers) or half (1 voxel per 2 cells, ½ft risers) — slope stepper / Ctrl+wheel toggles.</li>
        <li><b>Stair types cycle on the button / F</b>: <code>solid</code> (supported down to base) or <code>thin</code> (floating stepped slab). R rotates direction — same as roofs.</li>
        <li><b>DSL is slope-aware</b>: R/S voxels land in the level grid their surface actually passes through (a climbing shed marks rising levels), plus <code>roof:</code>/<code>stair:</code> parameter lines.</li>
        <li><b>Floors have thickness</b>: height stepper on the floor tool = 0/1/2 ft slab; +/− edits a placed floor.</li>
        <li>v15 base rules stand: voxel grid is the ground truth, painting substitutes, [/] moves stacks with riders.</li>
      </ul>
    </div>
    <div>
      <h2>notes (copy into INBOX)</h2>
      <textarea id="notes" style="height:4rem" placeholder="what felt wrong / right..."></textarea>
    </div>
  </aside>
</main>

<footer>drag: wall=line(+45°) · floor/erase/roof/stairs=rect · RMB erase · MMB pan · wheel zoom · Ctrl+wheel h/slope · Shift+wheel z/layer · +/− [/] · Space scope · M type · F roof form · V enclosure · PgUp/Dn layer · Q/E rotate · R spin · T top · C cam · ⌃Z undo</footer>

<script>
"use strict";
const KIT_META={px_per_unit:96, wall_h:3, pieces:{
  floor:{origin:[104,8],size:[208,112]},
  wall:{origin:[104,296],size:[208,400]}
}};
const KIT_SRC={
/*__KIT_SRC__*/
};

const S=96, UNIT=96, NLVL=10;
const WALLISH=new Set(["#","D","W"]);
const DIAG=new Set(["/","\\"]);
const STAIRS=new Set(["^",">","v","<"]);
const ARROW_CW={"^":">", ">":"v", "v":"<", "<":"^"};
const ARROW_OPP={"^":"v","v":"^","<":">",">":"<"};
const ASCENT={"^":[0,-1], ">":[1,0], "v":[0,1], "<":[-1,0]};
const ARROW_GLYPH={"^":"↑", ">":"→", "v":"↓", "<":"←"};
const SIDE_NAME={"^":"N", ">":"E", "v":"S", "<":"W"};
const DIAG_CW={"/":"\\", "\\":"/"};
const ROOF_FORMS=["flat","shed1","shed2"];
const STAIR_TYPES=["solid","thin"];
const ENCLOSE=["none","edge","inset"];
const TYPES={"#":["stone","wood"], ".":["stone","grass","road"], "D":["wood","iron"], "W":["bars","glass"]};
const TINT={grass:"rgba(70,140,60,.45)", road:"rgba(130,95,55,.5)", wood:"rgba(140,95,45,.28)",
  iron:"rgba(90,100,120,.6)", glass:"rgba(120,180,200,.5)"};
const L_ROOM=["########","#......#","#......W","#......#","#..#####","#..#","#..#","#D##"];
const VIEWS=["SW","SE","NE","NW"];
let COLS=16, ROWS=14;
let layers=[], grps=[], grpSeq=1;          // layers[L] = {g, side, dim, type, wmat}
let viewIdx=3, topView=false, tool="#", stairDir="^", undoStack=[], scopeGroup=false;
let brushHt={"#":2,"D":2,"W":1,".":0}, brushIncl=5, roofFormIdx=1, roofDir="^", level=0;
let stairTypeIdx=0;                  /* stair brush type: solid/thin (direction = stairDir) */
let brushStairIncl=5;                /* stairs land on floors: only 45° (5ft/cell) or half (2.5ft/cell) */
let viewWin=2, fadeOp=0.2;              // opaque window above the slice (voxels) + opacity beyond it
function alphaFor(vz){ if(vz<level) return 1;              // below the plane: the sheet itself occludes
  return (vz-level)<viewWin ? 1 : fadeOp; }                // win=1 -> exactly the plane's voxel opaque
const brushType={"#":0,".":0,"D":0,"W":0};
const H_MAX=6, GHOST=0.2;
const sprites={};

function blankGrid(r,c){ return Array.from({length:r},()=>Array(c).fill(" ")); }
function blankLayer(){ return {g:blankGrid(ROWS,COLS), side:{}, type:{}, wmat:{}, fh:{}}; }
function initLayers(){ layers=Array.from({length:NLVL},()=>blankLayer()); }
function L(n){ return layers[n]; }
function loadLRoom(){
  initLayers(); grps=[];
  const r0=Math.floor((ROWS-L_ROOM.length)/2), c0=Math.floor((COLS-8)/2);
  L_ROOM.forEach((row,r)=>{ [...row].forEach((ch,c)=>{
    const br=r0+r, bcC=c0+c, key=br+","+bcC;
    if(ch==="#"){ L(0).g[br][bcC]="#"; L(1).g[br][bcC]="#"; }
    else if(ch==="D"){ for(const l of [0,1]){ L(l).g[br][bcC]="D"; L(l).side[key]="v"; } }
    else if(ch==="W"){ L(0).g[br][bcC]="#"; L(1).g[br][bcC]="W"; L(1).side[key]=">"; }
    else if(ch==="."){ L(0).g[br][bcC]="."; }
  }); });
}
function snapshot(){ return {ly:JSON.stringify(layers.map(l=>({g:l.g.map(r=>r.join("")),s:l.side,t:l.type,w:l.wmat,f:l.fh}))),
  rf:JSON.stringify(grps), C:COLS, R:ROWS}; }
function pushUndo(){ undoStack.push(snapshot()); if(undoStack.length>200) undoStack.shift(); }
function restore(st){ COLS=st.C; ROWS=st.R;
  layers=JSON.parse(st.ly).map(l=>({g:l.g.map(r=>r.split("")), side:l.s, type:l.t, wmat:l.w, fh:l.f||{}}));
  grps=JSON.parse(st.rf); syncSteppers(); }
/* ---------- TRUE voxel model: each layer cell IS one voxel; no base+height ---------- */
function vox(l,br,bc){ return L(l).g[br][bc]; }
function isOcc(l,br,bc){ return vox(l,br,bc)!==" "; }
function clearVox(l,br,bc){ const lay=L(l); lay.g[br][bc]=" "; const key=br+","+bc;
  delete lay.side[key]; delete lay.type[key]; delete lay.wmat[key]; delete lay.fh[key]; }
function setVox(l,br,bc,ch,tIdx){ clearVox(l,br,bc); L(l).g[br][bc]=ch;
  if(tIdx) L(l).type[br+","+bc]=tIdx; }
function copyVox(fromL,toL,br,bc){ const A=L(fromL), B=L(toL), key=br+","+bc;
  clearVox(toL,br,bc);
  B.g[br][bc]=A.g[br][bc];
  for(const m of ["side","type","wmat","fh"]) if(A[m][key]!==undefined) B[m][key]=A[m][key];
  clearVox(fromL,br,bc); }
function stackTop(l0,br,bc){ let b=l0; while(b+1<NLVL&&isOcc(b+1,br,bc)) b++; return b; }
function moveStack(l0,br,bc,dz){   /* slice voxel + contiguous voxels above ride (any kind); landing substitutes */
  const b=stackTop(l0,br,bc);
  if(dz>0){ if(b+1>=NLVL) return false;
    for(let l=b;l>=l0;l--) copyVox(l,l+1,br,bc);
    return true; }
  if(l0-1<0) return false;
  for(let l=l0;l<=b;l++) copyVox(l,l-1,br,bc);
  return true; }
function openRun(l0,br,bc){ const ch=vox(l0,br,bc); let a=l0,b=l0;
  while(a-1>=0&&vox(a-1,br,bc)===ch) a--;
  while(b+1<NLVL&&vox(b+1,br,bc)===ch) b++;
  return [a,b]; }

/* rotation — rotate never mirror; arrows + diagonals follow */
function chRot(ch){ if(STAIRS.has(ch)) return ARROW_CW[ch]; if(DIAG.has(ch)) return DIAG_CW[ch]; return ch; }
function rotateGridCW(g){
  const M=g.length,out=[];
  for(let i=0;i<g[0].length;i++){ const row=[];
    for(let j=0;j<M;j++) row.push(chRot(g[M-1-j][i])); out.push(row); }
  return out;
}
function viewGridOf(n){ let g=L(n).g.map(r=>r.slice()); for(let k=0;k<viewIdx;k++) g=rotateGridCW(g); return g; }
function viewCellToBase(r,c){
  let M=ROWS,N=COLS;
  const dims=[[M,N]]; for(let k=0;k<viewIdx;k++){ const t=M;M=N;N=t; dims.push([M,N]); }
  for(let k=viewIdx;k>0;k--){ const Mp=dims[k-1][0]; const r2=Mp-1-c,c2=r; r=r2;c=c2; }
  return [r,c];
}
function baseCellToView(r,c){
  let M=ROWS,N=COLS;
  for(let k=0;k<viewIdx;k++){ const r2=c, c2=M-1-r; r=r2; c=c2; const t=M;M=N;N=t; }
  return [r,c];
}
function rotArrow(ch){ let a=ch; for(let k=0;k<viewIdx;k++) a=ARROW_CW[a]; return a; }
function unrotArrow(ch){ let a=ch; for(let k=0;k<(4-viewIdx)%4;k++) a=ARROW_CW[a]; return a; }

function proj(u,v,z){ return [(u-v)*S,(u+v)*0.5*S-z*S]; }

const cv=document.getElementById("cv"), ctx=cv.getContext("2d");
const cam={s:1,dx:0,dy:0};
let hover=null, hoverFrac=null;
const FACE={top:"#d4d4d4",long:"#9a9a9a",cap:"#5f5f5f"};
const ROOF_NEAR="#c9c9c9", ROOF_FAR="#8a8a8a", ROOF_SKIRT="#9a9a9a";

function viewDims(){ return viewIdx%2 ? [COLS,ROWS] : [ROWS,COLS]; }
function gridBounds(M,N){
  let a=1e9,b=1e9,x=-1e9,y=-1e9;
  for(const uv of [[0,0],[N,0],[N,M],[0,M]]) for(const z of [0,4]){
    const p=proj(uv[0],uv[1],z);
    a=Math.min(a,p[0]);b=Math.min(b,p[1]);x=Math.max(x,p[0]);y=Math.max(y,p[1]); }
  return [a,b,x,y];
}
function fitCamera(){
  const W=cv.clientWidth,H=cv.clientHeight,[M,N]=viewDims();
  if(topView){ cam.s=Math.min((W-60)/N,(H-60)/M)/S;
    cam.dx=(W-N*S*cam.s)/2; cam.dy=(H-M*S*cam.s)/2; return; }
  const b=gridBounds(M,N);
  cam.s=Math.min((W-60)/(b[2]-b[0]),(H-60)/(b[3]-b[1]),0.9);
  cam.dx=(W-(b[2]-b[0])*cam.s)/2-b[0]*cam.s;
  cam.dy=(H-(b[3]-b[1])*cam.s)/2-b[1]*cam.s;
}
function getVar(n){ return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
function cellDiamond(u,v,z){ z=z||0; return [proj(u,v,z),proj(u+1,v,z),proj(u+1,v+1,z),proj(u,v+1,z)]; }
function fillPoly(q,color){ ctx.beginPath(); ctx.moveTo(q[0][0],q[0][1]);
  for(let i=1;i<q.length;i++) ctx.lineTo(q[i][0],q[i][1]); ctx.closePath(); ctx.fillStyle=color; ctx.fill(); }
function strokePoly(q,color,lw){ ctx.beginPath(); ctx.moveTo(q[0][0],q[0][1]);
  for(let i=1;i<q.length;i++) ctx.lineTo(q[i][0],q[i][1]); ctx.closePath();
  ctx.strokeStyle=color; ctx.lineWidth=lw; ctx.stroke(); }
function quad(pts,fill,stroke,lw){ ctx.beginPath(); ctx.moveTo(pts[0][0],pts[0][1]);
  for(let i=1;i<pts.length;i++) ctx.lineTo(pts[i][0],pts[i][1]); ctx.closePath();
  ctx.fillStyle=fill; ctx.fill();
  if(stroke){ ctx.strokeStyle="rgba(0,0,0,.35)"; ctx.lineWidth=lw; ctx.stroke(); } }

/* ---------- full-piece drawers (clipping handled by iso clip paths per pass) ---------- */
/* full-piece drawers — per-voxel opacity is applied via iso hexagon clips in drawOneCell */
function drawWallStack(px,py,h,z){
  const img=sprites.wall, x=px-104, lift=z*UNIT;
  ctx.drawImage(img,0,296,208,104, x,py-lift,208,104);
  for(let j=2;j<=h;j++) ctx.drawImage(img,0,200,208,96, x,py-UNIT*(j-1)-lift,208,96);
  ctx.drawImage(img,0,0,208,104, x,py-296-(h-3)*UNIT-lift,208,104);
}
function tintBand(u,v,zLo,zHi,tintName,withTop){   /* per-voxel band tint: side faces + optional top diamond */
  if(!tintName||!TINT[tintName]) return;
  const P=(a,b,z)=>proj(a,b,z), col=TINT[tintName];
  if(withTop) fillPoly([P(u,v,zHi),P(u+1,v,zHi),P(u+1,v+1,zHi),P(u,v+1,zHi)],col);
  fillPoly([P(u,v+1,zHi),P(u+1,v+1,zHi),P(u+1,v+1,zLo),P(u,v+1,zLo)],col);
  fillPoly([P(u+1,v,zHi),P(u+1,v+1,zHi),P(u+1,v+1,zLo),P(u+1,v,zLo)],col);
}
function faceQuad(u,v,side,zlo,zhi){
  const P=(a,b,z)=>proj(a,b,z);
  if(side==="v") return [P(u,v+1,zlo),P(u+1,v+1,zlo),P(u+1,v+1,zhi),P(u,v+1,zhi)];
  if(side===">") return [P(u+1,v,zlo),P(u+1,v+1,zlo),P(u+1,v+1,zhi),P(u+1,v,zhi)];
  return null;
}
function drawOpening(u,v,ch,frontSide,zlo,zhi,typeName){
  if(zhi<=zlo) return {frontVisible:false};
  const back=faceQuad(u,v,ARROW_OPP[frontSide],zlo,zhi);
  if(back) fillPoly(back,"#141418");
  const front=faceQuad(u,v,frontSide,zlo,zhi);
  if(front){
    if(ch==="D") fillPoly(front, typeName==="iron"?"#5a6470":"#6b4a2a");
    else{ fillPoly(front, typeName==="glass"?"rgba(140,190,205,.85)":"#1c2226");
      if(typeName!=="glass"){ ctx.strokeStyle="#69717a"; ctx.lineWidth=3;
        const a=front[0],b=front[1],c=front[2],d=front[3];
        for(const t of [0.33,0.66]){ ctx.beginPath();
          ctx.moveTo(a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t);
          ctx.lineTo(d[0]+(c[0]-d[0])*t, d[1]+(c[1]-d[1])*t); ctx.stroke(); } } }
  }
  return {frontVisible:!!front};
}
function drawBoxP(u0,v0,l,d,z0,h,lw,strokeSides){
  const P=(u,v,z)=>proj(u,v,z);
  quad([P(u0,v0,z0+h),P(u0+l,v0,z0+h),P(u0+l,v0+d,z0+h),P(u0,v0+d,z0+h)],FACE.top,true,lw);
  quad([P(u0,v0+d,z0+h),P(u0+l,v0+d,z0+h),P(u0+l,v0+d,z0),P(u0,v0+d,z0)],FACE.long,strokeSides,lw);
  quad([P(u0+l,v0,z0+h),P(u0+l,v0+d,z0+h),P(u0+l,v0+d,z0),P(u0+l,v0,z0)],FACE.cap,strokeSides,lw);
}
function diagSolid(g,r,c,ch){
  const M=g.length,N=g[0].length;
  const W_=(rr,cc)=>rr>=0&&rr<M&&cc>=0&&cc<N&&WALLISH.has(g[rr][cc]);
  const n=W_(r-1,c), s=W_(r+1,c), w=W_(r,c-1), e=W_(r,c+1);
  if(ch==="\\"){ if(n&&e&&!W_(r-1,c+1)) return "NE"; if(s&&w&&!W_(r+1,c-1)) return "SW"; }
  else{ if(n&&w&&!W_(r-1,c-1)) return "NW"; if(s&&e&&!W_(r+1,c+1)) return "SE"; }
  return null;
}
function drawDiagVox(u,v,ch,solid,h,z,lw){
  const P=(a,b,zz)=>proj(a,b,zz+z);
  const cut = ch==="/" ? [[u+1,v],[u,v+1]] : [[u,v],[u+1,v+1]];
  quad([P(cut[0][0],cut[0][1],0),P(cut[1][0],cut[1][1],0),P(cut[1][0],cut[1][1],h),P(cut[0][0],cut[0][1],h)],"#8f8f8f",true,lw);
  if(!solid) return;
  const TRI={NE:[[u,v],[u+1,v],[u+1,v+1]], NW:[[u,v],[u+1,v],[u,v+1]],
             SE:[[u+1,v],[u+1,v+1],[u,v+1]], SW:[[u,v],[u,v+1],[u+1,v+1]]}[solid];
  if(solid==="SE"||solid==="SW")
    quad([P(u,v+1,h),P(u+1,v+1,h),P(u+1,v+1,0),P(u,v+1,0)],FACE.long,true,lw);
  if(solid==="NE"||solid==="SE")
    quad([P(u+1,v,h),P(u+1,v+1,h),P(u+1,v+1,0),P(u+1,v,0)],FACE.cap,true,lw);
  quad(TRI.map(p=>P(p[0],p[1],h)),FACE.top,true,lw);
}
function derivedDiagsOf(g,lvl){   /* per-voxel: smoothing derives independently at each layer */
  const M=g.length, N=g[0].length, out=[];
  for(let r=0;r<M;r++) for(let c=0;c<N;c++){
    if(g[r][c]!==" " && g[r][c]!==".") continue;
    for(const dch of ["/","\\"]){
      const solid=diagSolid(g,r,c,dch);
      if(solid){ out.push({u:c,v:r,ch:dch,derived:true,solid,lvl}); break; } } }
  return out;
}

/* ---------- sloped-surface GROUPS: roofs and stairs share one model ----------
   {kind:"roof"|"stair", cells, form, dir, incl(ft/cell), z, enclose/sideMode(roof only)}
   roof forms: flat/shed1/shed2 (smooth surface). stair types: solid/thin (stepped shed1 surface). */
function grpAtBase(br,bc){ let roof=null;          /* selection priority: stair groups beat roofs */
  for(let i=grps.length-1;i>=0;i--){ const rf=grps[i];
    if(rf.cells.some(rc=>rc[0]===br&&rc[1]===bc)){
      if(rf.kind==="stair") return rf;
      if(!roof) roof=rf; } }
  return roof; }
function grpForm(rf){ return rf.kind==="stair" ? "shed1" : ROOF_FORMS[rf.form]; }
function grpFormName(rf){ return rf.kind==="stair" ? STAIR_TYPES[rf.form] : ROOF_FORMS[rf.form]; }
function grpViewData(rf){
  const cellsV=rf.cells.map(rc=>baseCellToView(rc[0],rc[1]));
  const dir=rotArrow(rf.dir), rise=rf.incl/5;
  const aOf=(u,v)=> dir===">"?u : dir==="<"?-u : dir==="v"?v : -v;
  let aLow=1e9,aHigh=-1e9;
  for(const rc of cellsV){ for(const d of [0,1]){
    const a = (dir===">"||dir==="<") ? aOf(rc[1]+d,0) : aOf(0,rc[0]+d);
    aLow=Math.min(aLow,a); aHigh=Math.max(aHigh,a); } }
  const form=grpForm(rf);
  const hAt=(u,v)=>{ if(form==="flat") return rf.z;
    const a=aOf(u,v);
    if(form==="shed1") return rf.z + (a-aLow)*rise;
    return rf.z + Math.min(a-aLow, aHigh-a)*rise; };
  const set=new Set(cellsV.map(rc=>rc[0]+","+rc[1]));
  return {cellsV,dir,rise,hAt,set,aOf,aLow,aHigh,form};
}
function grpBaseData(rf){                /* base-frame twin of grpViewData — for DSL export + voxel claiming */
  const dir=rf.dir, rise=rf.incl/5;
  const aOf=(r,c)=> dir===">"?c : dir==="<"?-c : dir==="v"?r : -r;
  let aLow=1e9,aHigh=-1e9;
  for(const rc of rf.cells) for(const d of [0,1]){
    const a=(dir===">"||dir==="<") ? aOf(0,rc[1]+d) : aOf(rc[0]+d,0);
    aLow=Math.min(aLow,a); aHigh=Math.max(aHigh,a); }
  const form=grpForm(rf);
  const hAt=(r,c)=>{ if(form==="flat") return rf.z;
    const a=aOf(r,c);
    if(form==="shed1") return rf.z + (a-aLow)*rise;
    return rf.z + Math.min(a-aLow, aHigh-a)*rise; };
  return {aOf,aLow,aHigh,rise,form,hAt};
}
function grpCellVoxels(B,rf,br,bc){      /* [voxLo,voxHi) the surface passes through over this cell */
  const hs=[B.hAt(br,bc),B.hAt(br+1,bc),B.hAt(br,bc+1),B.hAt(br+1,bc+1)];
  const lo=Math.min(...hs), hi=Math.max(...hs);
  const voxLo=Math.max(0,Math.floor(lo+1e-9));
  const voxHi=Math.min(NLVL,Math.max(voxLo+1,Math.ceil(hi-1e-9)));
  return [voxLo,voxHi];
}
function modeOf(rf,baseSide){ const m=rf.sideMode&&rf.sideMode[baseSide];
  return m!==undefined ? m : (rf.enclose||0); }
function grpRectView(rf){
  const rs=[],cs2=[];
  for(const rc of rf.cells){ const vc=baseCellToView(rc[0],rc[1]); rs.push(vc[0]); cs2.push(vc[1]); }
  return {r0:Math.min(...rs), r1:Math.max(...rs), c0:Math.min(...cs2), c1:Math.max(...cs2)};
}
/* ---------- iso clip paths: the slice cuts along iso lines, per cell ---------- */
const BIG=1e6;
function clipBelow(u,v){ const Pl=proj(u,v+1,level), Pb=proj(u,v,level), Pr=proj(u+1,v,level);
  ctx.beginPath(); ctx.moveTo(Pl[0]-2,Pl[1]); ctx.lineTo(Pb[0],Pb[1]); ctx.lineTo(Pr[0]+2,Pr[1]);
  ctx.lineTo(Pr[0]+2,BIG); ctx.lineTo(Pl[0]-2,BIG); ctx.closePath(); ctx.clip(); }
function clipAbove(u,v){ const Pl=proj(u,v+1,level), Pf=proj(u+1,v+1,level), Pr=proj(u+1,v,level);
  ctx.beginPath(); ctx.moveTo(Pl[0]-2,Pl[1]); ctx.lineTo(Pf[0],Pf[1]); ctx.lineTo(Pr[0]+2,Pr[1]);
  ctx.lineTo(Pr[0]+2,-BIG); ctx.lineTo(Pl[0]-2,-BIG); ctx.closePath(); ctx.clip(); }
/* hexagon between two iso planes over a cell — top diamond back edges at zHi, front edges at zLo */
function clipBand(u,v,zLo,zHi){
  const Lh=proj(u,v+1,zHi), Bh=proj(u,v,zHi), Rh=proj(u+1,v,zHi);
  const Rl=proj(u+1,v,zLo), Fl=proj(u+1,v+1,zLo), Ll=proj(u,v+1,zLo);
  ctx.beginPath(); ctx.moveTo(Lh[0]-1,Lh[1]); ctx.lineTo(Bh[0],Bh[1]); ctx.lineTo(Rh[0]+1,Rh[1]);
  ctx.lineTo(Rl[0]+1,Rl[1]); ctx.lineTo(Fl[0],Fl[1]); ctx.lineTo(Ll[0]-1,Ll[1]);
  ctx.closePath(); ctx.clip(); }

function render(){
  const W=cv.clientWidth,H=cv.clientHeight;
  cv.width=W*devicePixelRatio; cv.height=H*devicePixelRatio;
  ctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);
  ctx.clearRect(0,0,W,H);
  const [M,N]=viewDims();
  if(topView){ renderTop(W,H); updateHud(); return; }
  ctx.save(); ctx.translate(cam.dx,cam.dy); ctx.scale(cam.s,cam.s);
  const lw=1/cam.s;

  /* collect draw entries: per-COLUMN runs of contiguous voxels (render merges what storage keeps independent) */
  const cells=[], vgrids=[], rfData=new Map();
  for(let lvl=0;lvl<NLVL;lvl++) vgrids[lvl]=viewGridOf(lvl);
  const derived=new Map();
  for(let lvl=0;lvl<NLVL;lvl++)
    for(const dc of derivedDiagsOf(vgrids[lvl],lvl)) derived.set(dc.v+","+dc.u+","+lvl,dc);
  for(let r=0;r<M;r++) for(let c=0;c<N;c++){
    let run=null;
    const flush=()=>{ if(run){ cells.push(run); run=null; } };
    for(let lvl=0;lvl<NLVL;lvl++){
      const ch=vgrids[lvl][r][c], dd=derived.get(r+","+c+","+lvl);
      if(ch==="."){ const bcF=viewCellToBase(r,c), f=L(lvl).fh[bcF[0]+","+bcF[1]]||0;
        cells.push({u:c,v:r,kind:"floor",ch:".",zBot:lvl,zTop:lvl+f*0.2,lvl}); }
      let fam=null, dch=null, dsolid=null;
      if(WALLISH.has(ch)) fam="wall";
      else if(DIAG.has(ch)){ dch=ch; dsolid=diagSolid(vgrids[lvl],r,c,ch); fam="diag:"+ch+":"+(dsolid||""); }
      else if(dd){ dch=dd.ch; dsolid=dd.solid; fam="diag:"+dd.ch+":"+dd.solid+":d"; }
      if(!fam){ flush(); continue; }
      if(run&&run.fam===fam&&run.zTop===lvl){ run.zTop=lvl+1; run.items.push({lvl,ch}); }
      else{ flush();
        run={u:c,v:r,fam,zBot:lvl,zTop:lvl+1,lvl,items:[{lvl,ch}],
          kind:fam==="wall"?"wall":"diag", ch:dch, solid:dsolid}; }
    }
    flush();
  }
  for(const rf of grps){
    const G=grpViewData(rf);
    rfData.set(rf, {G, R:grpRectView(rf)});
    for(const rc of rf.cells){ const vc=baseCellToView(rc[0],rc[1]), gu=vc[1], gv=vc[0];
      const hs=[G.hAt(gu,gv),G.hAt(gu+1,gv),G.hAt(gu,gv+1),G.hAt(gu+1,gv+1)];
      /* draw extent reaches BASE for roofs (skirts hang there) + solid stairs; only thin stairs float */
      const lo=(rf.kind==="stair"&&STAIR_TYPES[rf.form]==="thin") ? Math.min(...hs) : rf.z;
      cells.push({u:gu,v:gv,kind:"GRP",ch:"GRP",zBot:Math.floor(lo+1e-9),zTopf:Math.max(...hs)+0.01,
        lvl:Math.floor(lo+1e-9),rf}); } }
  cells.sort((a,b)=>((a.u+a.v)-(b.u+b.v)) || (a.zBot-b.zBot) || ((a.kind!=="floor"?1:0)-(b.kind!=="floor"?1:0)));

  const hoverBB = hover? {x:proj(hover[1],hover[0],level)[0]-104,y:proj(hover[1],hover[0],level)[1]-96,w:208,h:160} : null;
  const hoverSum = hover? hover[0]+hover[1] : null;
  const badges=[];

  function pieceTopBot(cell){
    if(cell.kind==="GRP") return [cell.zBot, cell.zTopf];
    return [cell.zBot, cell.zTop]; }

  function drawGrpCell(cell,lw,extra){
    const rf=cell.rf, u=cell.u, v=cell.v, {G,R}=rfData.get(rf);
    const zB=cell.zBot, nv=Math.max(1,Math.ceil(cell.zTopf-zB));
    const runs=[]; let rs=0, ra=alphaFor(zB);
    for(let j=1;j<nv;j++){ const a2=alphaFor(zB+j);
      if(a2!==ra){ runs.push({lo:rs,hi:j,a:ra}); rs=j; ra=a2; } }
    runs.push({lo:rs,hi:nv,a:ra});
    for(const run of runs){ const aR=run.a*extra; if(aR<=0) continue;
      ctx.save();
      if(runs.length>1) clipBand(u,v,zB+run.lo,zB+run.hi);
      if(rf.kind==="stair") drawStairCellInner(rf,u,v,lw,aR,G);
      else drawRoofCellInner(rf,u,v,lw,aR,G,R);
      ctx.restore(); }
  }
  function drawStairCellInner(rf,u,v,lw,a,G){   /* stepped shed1 surface: incl steps/cell, 1ft (0.2 voxel) each */
    ctx.globalAlpha=a;
    const steps=5, riser=rf.incl/25;   /* per-tread rise in voxels: 1ft at 45°, 0.5ft at half slope */
    const hLo=Math.min(G.hAt(u,v),G.hAt(u+1,v),G.hAt(u,v+1),G.hAt(u+1,v+1));
    const solid=STAIR_TYPES[rf.form]==="solid";
    const slices=[];
    for(let i=0;i<steps;i++){
      const t0=i/steps, t1=(i+1)/steps, hi=hLo+(i+1)*riser;
      let u0=u, v0=v, l=1, d=1;
      if(G.dir===">"){ u0=u+t0; l=t1-t0; }
      else if(G.dir==="<"){ u0=u+1-t1; l=t1-t0; }
      else if(G.dir==="v"){ v0=v+t0; d=t1-t0; }
      else { v0=v+1-t1; d=t1-t0; }
      const zb = solid ? rf.z : hi-Math.max(riser,0.1);
      slices.push([u0,v0,l,d,zb,hi-zb]);
    }
    slices.sort((p,q)=>(p[0]+p[1])-(q[0]+q[1]));
    for(const s of slices) drawBoxP(s[0],s[1],s[2],s[3],s[4],s[5],lw,false);
    ctx.globalAlpha=1;
  }
  function drawRoofCellInner(rf,u,v,lw,a,G,R){
    ctx.globalAlpha=a;
    const mo=(vs)=>modeOf(rf,unrotArrow(vs));
    const off=(vs)=>mo(vs)===2?1:0;
    /* this cell's skirt sub-segments (south + east lines) */
    const skirtSub=(x0,y0,x1,y1,color)=>{
      const pts=[[x0,y0]];
      const aStar=(G.aLow+G.aHigh)/2;
      const a0=G.aOf(x0,y0), a1=G.aOf(x1,y1);
      if(G.form==="shed2" && Math.min(a0,a1)<aStar-1e-9 && Math.max(a0,a1)>aStar+1e-9){
        if(y0===y1) pts.push([G.dir===">"?aStar:-aStar, y0]);
        else pts.push([x0, G.dir==="v"?aStar:-aStar]); }
      pts.push([x1,y1]);
      for(let i=0;i<pts.length-1;i++){ const A=pts[i],B=pts[i+1];
        quad([proj(A[0],A[1],rf.z),proj(B[0],B[1],rf.z),
              proj(B[0],B[1],G.hAt(B[0],B[1])),proj(A[0],A[1],G.hAt(A[0],A[1]))],color,true,lw); } };
    if(mo("v")>0){ const y=R.r1+1-off("v"), x0=Math.max(R.c0+off("<"),u), x1=Math.min(R.c1+1-off(">"),u+1);
      if(v+1===y && x1>x0) skirtSub(x0,y,x1,y,ROOF_SKIRT); }
    if(mo(">")>0){ const x=R.c1+1-off(">"), y0=Math.max(R.r0+off("^"),v), y1=Math.min(R.r1+1-off("v"),v+1);
      if(u+1===x && y1>y0) skirtSub(x,y0,x,y1,FACE.cap); }
    /* surface patch for this cell */
    const corners=[[u,v],[u+1,v],[u+1,v+1],[u,v+1]];
    const aStar=(G.aLow+G.aHigh)/2;
    const cellA=corners.map(p=>G.aOf(p[0],p[1]));
    const crosses = G.form==="shed2" && Math.min(...cellA)<aStar-1e-9 && Math.max(...cellA)>aStar+1e-9;
    const shade=(pts)=>{ const h0=G.hAt(pts[0][0],pts[0][1]);
      const gradTo=G.hAt(pts[0][0]+0.01,pts[0][1]+0.01)-h0;
      return gradTo<-1e-9?ROOF_FAR:ROOF_NEAR; };
    const drawPatch=(pts)=>{ quad(pts.map(p=>proj(p[0],p[1],G.hAt(p[0],p[1]))), shade(pts), true, lw); };
    if(!crosses) drawPatch(corners);
    else{ const horiz=(G.dir==="^"||G.dir==="v");
      if(horiz){ const vr = G.dir==="v"? aStar : -aStar;
        drawPatch([[u,v],[u+1,v],[u+1,vr],[u,vr]]);
        drawPatch([[u,vr],[u+1,vr],[u+1,v+1],[u,v+1]]); }
      else{ const ur = G.dir===">"? aStar : -aStar;
        drawPatch([[u,v],[ur,v],[ur,v+1],[u,v+1]]);
        drawPatch([[ur,v],[u+1,v],[u+1,v+1],[ur,v+1]]); } }
    ctx.globalAlpha=1;
  }

  function drawOneCell(cell,pass){                     // pass: 'below' | 'above'
    const [zBot,zTop]=pieceTopBot(cell);
    if(pass==="below" && zBot>=level) return;
    if(pass==="above" && zTop<=level && !(cell.kind==="floor"&&cell.lvl===level)) return;
    const bc=viewCellToBase(cell.v,cell.u), key=bc[0]+","+bc[1];
    const needsClip = zBot<level && zTop>level;
    ctx.save();
    if(needsClip){ if(pass==="below") clipBelow(cell.u,cell.v); else clipAbove(cell.u,cell.v); }
    let extra=1;                                      // hover-behind ghosting
    if(hoverBB && (cell.u+cell.v)>hoverSum &&
       rectsOverlap({x:proj(cell.u,cell.v,0)[0]-104,y:proj(cell.u,cell.v,0)[1]-296-(zTop-3)*UNIT,w:208,h:400},hoverBB))
      extra=GHOST;
    if(cell.kind==="GRP"){ drawGrpCell(cell,lw,extra); ctx.restore(); return; }
    const px=proj(cell.u,cell.v,0);
    let subs=null;                                     /* opening sub-runs inside a wall run */
    if(cell.kind==="wall"){
      subs=[]; let i=0;
      while(i<cell.items.length){ const it=cell.items[i];
        if(it.ch==="#"){ i++; continue; }
        const sd=L(it.lvl).side[key]; let j=i;
        while(j+1<cell.items.length&&cell.items[j+1].ch===it.ch&&L(cell.items[j+1].lvl).side[key]===sd) j++;
        subs.push({ch:it.ch, zLo:cell.items[i].lvl, zHi:cell.items[j].lvl+1,
          side: sd?rotArrow(sd):"v", tname:TYPES[it.ch][L(it.lvl).type[key]||0]});
        i=j+1; }
    }
    const drawPiece=()=>{
      if(cell.kind==="floor"){
        const f=L(cell.lvl).fh[key]||0, tn=TYPES["."][L(cell.lvl).type[key]||0];
        if(f>0){ drawBoxP(cell.u,cell.v,1,1,cell.lvl,f*0.2,lw,true);
          if(tn&&TINT[tn]) fillPoly(cellDiamond(cell.u,cell.v,cell.lvl+f*0.2),TINT[tn]); }
        else{
          const py=proj(cell.u,cell.v,cell.lvl);
          ctx.drawImage(sprites.floor,py[0]-104,py[1]-8);
          if(tn&&TINT[tn]) fillPoly(cellDiamond(cell.u,cell.v,cell.lvl),TINT[tn]); }
      }
      else if(cell.kind==="diag")
        drawDiagVox(cell.u,cell.v,cell.ch,cell.solid,cell.zTop-cell.zBot,cell.zBot,lw);
      else{                                            /* wall run: one stack, per-voxel band tints, merged openings */
        drawWallStack(px[0],px[1],cell.zTop-cell.zBot,cell.zBot);
        for(const it of cell.items){ const lay2=L(it.lvl);
          const tn = it.ch==="#" ? TYPES["#"][lay2.type[key]||0] : TYPES["#"][lay2.wmat[key]||0];
          tintBand(cell.u,cell.v,it.lvl,it.lvl+1,tn,it.lvl+1===cell.zTop); }
        for(const s of subs) drawOpening(cell.u,cell.v,s.ch,s.side,s.zLo,s.zHi,s.tname);
      }
    };
    /* per-VOXEL opacity: group contiguous voxels of equal alpha, draw the FULL piece clipped
       to each run's iso hexagon — boundaries follow the diamond, never horizontal crops */
    const nvox=Math.max(1,Math.ceil(zTop-zBot));
    const runs=[]; let rs=0, ra=alphaFor(zBot);
    for(let j=1;j<nvox;j++){ const a2=alphaFor(zBot+j);
      if(a2!==ra){ runs.push({lo:rs,hi:j,a:ra}); rs=j; ra=a2; } }
    runs.push({lo:rs,hi:nvox,a:ra});
    for(const run of runs){
      const a=run.a*extra; if(a<=0) continue;
      ctx.save();
      if(runs.length>1) clipBand(cell.u,cell.v,zBot+run.lo,zBot+run.hi);
      ctx.globalAlpha=a; drawPiece(); ctx.globalAlpha=1;
      ctx.restore();
      /* cut cap: a run ending mid-piece exposes side pixels of the voxel above — cover with a top-face diamond */
      if(run.hi<nvox && cell.kind!=="floor"){
        ctx.globalAlpha=a;
        const zc=zBot+run.hi;
        if(cell.kind==="diag"){
          if(cell.solid){ const u2=cell.u,v2=cell.v;
            const TRI={NE:[[u2,v2],[u2+1,v2],[u2+1,v2+1]], NW:[[u2,v2],[u2+1,v2],[u2,v2+1]],
                       SE:[[u2+1,v2],[u2+1,v2+1],[u2,v2+1]], SW:[[u2,v2],[u2,v2+1],[u2+1,v2+1]]}[cell.solid];
            quad(TRI.map(p=>proj(p[0],p[1],zc)),FACE.top,true,lw); } }
        else quad(cellDiamond(cell.u,cell.v,zc),FACE.top,true,lw);
        ctx.globalAlpha=1; }
    }
    if(subs&&(pass==="above"||zTop<=level))
      for(const s of subs) badges.push({u:cell.u,v:cell.v,ch:s.ch,alpha:alphaFor(s.zLo)*extra,
        dimmed:!(s.side==="v"||s.side===">"),z:s.zLo});
    ctx.restore();
  }

  for(const cell of cells) drawOneCell(cell,"below");
  /* plane sheet + lines */
  ctx.globalAlpha=0.5;
  fillPoly([proj(0,0,level),proj(N,0,level),proj(N,M,level),proj(0,M,level)],getVar("--canvas-bg"));
  ctx.globalAlpha=1;
  ctx.strokeStyle = level===0 ? "rgba(128,128,140,.35)" : "rgba(89,210,206,.4)";
  ctx.lineWidth=lw;
  for(let r=0;r<=M;r++){ const a=proj(0,r,level), b=proj(N,r,level);
    ctx.beginPath(); ctx.moveTo(a[0],a[1]); ctx.lineTo(b[0],b[1]); ctx.stroke(); }
  for(let c=0;c<=N;c++){ const a=proj(c,0,level), b=proj(c,M,level);
    ctx.beginPath(); ctx.moveTo(a[0],a[1]); ctx.lineTo(b[0],b[1]); ctx.stroke(); }
  for(const cell of cells) drawOneCell(cell,"above");
  for(const b of badges){
    const col=b.ch==="D"?getVar("--accent"):getVar("--mark");
    ctx.globalAlpha=(b.dimmed?0.4:1)*b.alpha;
    const c0=proj(b.u+0.5,b.v+0.5,b.z);
    ctx.fillStyle=col; ctx.font=(16/cam.s)+"px ui-monospace, monospace";
    ctx.textAlign="center"; ctx.textBaseline="middle"; ctx.fillText(b.ch,c0[0],c0[1]);
    ctx.globalAlpha=1;
  }
  if(preview){ const col=previewErase?getVar("--danger"):getVar("--mark");
    for(const key of preview){ const rc=key.split(",");
      strokePoly(cellDiamond(+rc[1],+rc[0],level),col,2.5*lw); } }
  if(hover){
    const bcH=viewCellToBase(hover[0],hover[1]);
    const rfH0=grpAtBase(bcH[0],bcH[1]);
    const rfH=(rfH0&&Math.floor(rfH0.z)===level&&vox(level,bcH[0],bcH[1])===" ")?rfH0:null;
    const gH=vgrids[level];
    if(scopeGroup){
      for(const rc of groupCells(gH,hover[0],hover[1]))
        strokePoly(cellDiamond(rc[1],rc[0],level),"rgba(89,210,206,.55)",1.6*lw);
    }
    if(rfH){ for(const rc of rfH.cells){ const vc=baseCellToView(rc[0],rc[1]);
        strokePoly(cellDiamond(vc[1],vc[0],rfH.z),"rgba(224,164,88,.7)",1.6*lw); }
      const pick=roofEdgePick();
      if(pick&&pick.side){ const seg=edgeSegAt(hover[1],hover[0],pick.side,rfH.z);
        ctx.beginPath(); ctx.moveTo(seg[0][0],seg[0][1]); ctx.lineTo(seg[1][0],seg[1][1]);
        ctx.strokeStyle=getVar("--accent"); ctx.lineWidth=6*lw; ctx.lineCap="round"; ctx.stroke(); } }
    strokePoly(cellDiamond(hover[1],hover[0],level),getVar("--mark"),2*lw);
    if((tool==="D"||tool==="W")&&hoverFrac){
      const bcW=viewCellToBase(hover[0],hover[1]);
      if(WALLISH.has(vox(level,bcW[0],bcW[1]))){
        const s=nearestSide(hoverFrac);
        if(s==="v"||s===">") fillPoly(faceQuad(hover[1],hover[0],s,level,level+brushHt[tool]),"rgba(224,164,88,.5)");
      }
    }
  }
  ctx.restore(); updateHud();
}
function rectsOverlap(a,b){ return a.x<b.x+b.w && b.x<a.x+a.w && a.y<b.y+b.h && b.y<a.y+a.h; }

function topDiagStroke(dx,dy,cs,r,c,ch,solid){
  ctx.strokeStyle=FACE.long; ctx.lineWidth=3;
  if(ch==="/"){ ctx.beginPath(); ctx.moveTo(dx+c*cs,dy+(r+1)*cs); ctx.lineTo(dx+(c+1)*cs,dy+r*cs); ctx.stroke(); }
  else{ ctx.beginPath(); ctx.moveTo(dx+c*cs,dy+r*cs); ctx.lineTo(dx+(c+1)*cs,dy+(r+1)*cs); ctx.stroke(); }
  ctx.lineWidth=1;
  if(solid){ const T={NE:[[1,0],[1,1],[0,0]],NW:[[0,0],[1,0],[0,1]],
      SE:[[1,0],[1,1],[0,1]],SW:[[0,0],[0,1],[1,1]]}[solid];
    ctx.beginPath(); ctx.moveTo(dx+(c+T[0][0])*cs,dy+(r+T[0][1])*cs);
    for(let i=1;i<3;i++) ctx.lineTo(dx+(c+T[i][0])*cs,dy+(r+T[i][1])*cs);
    ctx.closePath(); ctx.fillStyle="rgba(154,154,154,.55)"; ctx.fill(); }
}
function renderTop(W,H){
  const [M,N]=viewDims(), cs=S*cam.s, dx=cam.dx, dy=cam.dy;
  const colors={"#":FACE.long,".":"rgba(128,128,128,.18)","D":getVar("--accent"),"W":getVar("--mark")};
  for(let lvl=0;lvl<NLVL;lvl++){
    const g=viewGridOf(lvl); let any=false;
    for(const row of L(lvl).g) for(const ch of row) if(ch!==" "){ any=true; break; }
    if(!any) continue;
    ctx.globalAlpha = lvl>level ? 0.15 : 1;
    for(const dcell of derivedDiagsOf(g,lvl)) topDiagStroke(dx,dy,cs,dcell.v,dcell.u,dcell.ch,dcell.solid);
    for(let r=0;r<M;r++)for(let c=0;c<N;c++){ const ch=g[r][c]; if(ch===" ")continue;
      if(DIAG.has(ch)){ topDiagStroke(dx,dy,cs,r,c,ch,diagSolid(g,r,c,ch)); continue; }
      ctx.fillStyle=colors[ch];
      ctx.fillRect(dx+c*cs+1,dy+r*cs+1,cs-2,cs-2); }
    ctx.globalAlpha=1;
  }
  for(const rf of grps){
    ctx.globalAlpha = rf.z>level+1e-9 ? 0.15 : 0.6;
    for(const rc of rf.cells){ const vc=baseCellToView(rc[0],rc[1]);
      ctx.fillStyle="#c9c9c9"; ctx.fillRect(dx+vc[1]*cs+2,dy+vc[0]*cs+2,cs-4,cs-4); }
    const c0=rf.cells[Math.floor(rf.cells.length/2)], vc0=baseCellToView(c0[0],c0[1]);
    ctx.fillStyle="#3a3a40"; ctx.font=(cs*0.45)+"px ui-monospace,monospace";
    ctx.textAlign="center"; ctx.textBaseline="middle";
    ctx.fillText((rf.kind==="stair"?"S":grpFormName(rf)[0])+ARROW_GLYPH[rotArrow(rf.dir)],dx+(vc0[1]+0.5)*cs,dy+(vc0[0]+0.5)*cs);
    ctx.globalAlpha=1; }
  ctx.strokeStyle="rgba(128,128,128,.3)";
  for(let r=0;r<=M;r++){ctx.beginPath();ctx.moveTo(dx,dy+r*cs);ctx.lineTo(dx+N*cs,dy+r*cs);ctx.stroke();}
  for(let c=0;c<=N;c++){ctx.beginPath();ctx.moveTo(dx+c*cs,dy);ctx.lineTo(dx+c*cs,dy+M*cs);ctx.stroke();}
  if(preview){ ctx.strokeStyle=previewErase?getVar("--danger"):getVar("--mark"); ctx.lineWidth=2;
    for(const key of preview){ const rc=key.split(",");
      ctx.strokeRect(dx+(+rc[1])*cs,dy+(+rc[0])*cs,cs,cs); } ctx.lineWidth=1; }
  if(hover){ ctx.strokeStyle=getVar("--mark"); ctx.lineWidth=2;
    ctx.strokeRect(dx+hover[1]*cs,dy+hover[0]*cs,cs,cs); ctx.lineWidth=1; }
}

function cellAt(mx,my){
  const [M,N]=viewDims();
  if(topView){ const cs=S*cam.s;
    const cf=(mx-cam.dx)/cs, rf=(my-cam.dy)/cs, c=Math.floor(cf), r=Math.floor(rf);
    if(!(r>=0&&r<M&&c>=0&&c<N)) return null;
    hoverFrac=[cf-c,rf-r]; return [r,c]; }
  const X=(mx-cam.dx)/cam.s/S, Y=(my-cam.dy)/cam.s/S + level;
  const uf=(X+2*Y)/2, vf=(2*Y-X)/2, u=Math.floor(uf), v=Math.floor(vf);
  if(!(v>=0&&v<M&&u>=0&&u<N)){ hoverFrac=null; return null; }
  hoverFrac=[uf-u,vf-v]; return [v,u];
}
function nearestSide(f){ const d=[["^",f[1]],[">",1-f[0]],["v",1-f[1]],["<",f[0]]];
  d.sort((a,b)=>a[1]-b[1]); return d[0][0]; }
function edgeSegAt(u,v,side,z){
  if(side==="^") return [proj(u,v,z),proj(u+1,v,z)];
  if(side===">") return [proj(u+1,v,z),proj(u+1,v+1,z)];
  if(side==="v") return [proj(u,v+1,z),proj(u+1,v+1,z)];
  return [proj(u,v,z),proj(u,v+1,z)];
}
function familyOf(ch){
  if(WALLISH.has(ch)||DIAG.has(ch)) return "wall";
  if(STAIRS.has(ch)) return "stair"; if(ch===".") return "floor";
  return null;
}
function groupCells(g,r0,c0){
  const fam=familyOf(g[r0][c0]); if(!fam) return [[r0,c0]];
  const dirs = fam==="wall"
    ? [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]
    : [[1,0],[-1,0],[0,1],[0,-1]];
  const M=g.length,N=g[0].length, seen=new Set([r0+","+c0]), out=[[r0,c0]], q=[[r0,c0]];
  while(q.length){ const rc=q.pop();
    for(const dd of dirs){
      const r=rc[0]+dd[0], c=rc[1]+dd[1], k=r+","+c;
      if(r<0||r>=M||c<0||c>=N||seen.has(k)) continue;
      if(familyOf(g[r][c])===fam){ seen.add(k); out.push([r,c]); q.push([r,c]); } } }
  return out;
}

/* gestures */
let painting=false, eraseDrag=false, panning=false, panStart=null;
let anchor=null, preview=null, previewErase=false;
function lineCells45(a,b){
  const out=new Set(), dr=b[0]-a[0], dc=b[1]-a[1], adr=Math.abs(dr), adc=Math.abs(dc);
  if(adr<=adc/2){ const r=a[0];
    for(let c=Math.min(a[1],b[1]);c<=Math.max(a[1],b[1]);c++) out.add(r+","+c); }
  else if(adc<=adr/2){ const c=a[1];
    for(let r=Math.min(a[0],b[0]);r<=Math.max(a[0],b[0]);r++) out.add(r+","+c); }
  else{ const n=Math.min(adr,adc), sr=Math.sign(dr)||1, sc=Math.sign(dc)||1;
    for(let i=0;i<=n;i++) out.add((a[0]+i*sr)+","+(a[1]+i*sc)); }
  return out;
}
function rectCells(a,b){ const out=new Set();
  for(let r=Math.min(a[0],b[0]);r<=Math.max(a[0],b[0]);r++)
    for(let c=Math.min(a[1],b[1]);c<=Math.max(a[1],b[1]);c++) out.add(r+","+c);
  return out; }
function commitStroke(){
  if(!preview||preview.size===0) return;
  pushUndo();
  const baseCells=[...preview].map(k=>{ const rc=k.split(",").map(Number);
    return viewCellToBase(rc[0],rc[1]); });
  const baseSet=new Set(baseCells.map(rc=>rc[0]+","+rc[1]));
  const evictGrps=(zLo,zHi)=>{ grps=grps.filter(rf=>{   /* span-aware: a group dies when the stroke hits ITS voxels */
    if(!rf.cells.some(rc=>baseSet.has(rc[0]+","+rc[1]))) return true;
    const B=grpBaseData(rf);
    return !rf.cells.some(rc=>{ if(!baseSet.has(rc[0]+","+rc[1])) return false;
      const [vl,vh]=grpCellVoxels(B,rf,rc[0],rc[1]);
      return vl<zHi&&vh>zLo; }); }); };
  if(previewErase){
    const before=grps.length; evictGrps(level,level+1);
    let cleared=grps.length<before;
    for(const rc of baseCells) if(isOcc(level,rc[0],rc[1])){ clearVox(level,rc[0],rc[1]); cleared=true; }
    if(!cleared) hint("layer "+level+" is empty here — PgUp/Dn to change layer");
  }
  else if(tool==="R"||tool==="^"){                      /* roofs and stairs: same sloped-group placement */
    const nrf = tool==="R"
      ? {id:grpSeq++, kind:"roof", cells:baseCells, form:roofFormIdx, dir:unrotArrow(roofDir), incl:brushIncl, z:level, enclose:0}
      : {id:grpSeq++, kind:"stair", cells:baseCells, form:stairTypeIdx, dir:unrotArrow(stairDir), incl:brushStairIncl, z:level};
    const NB=grpBaseData(nrf);
    grps=grps.filter(rf=>{ const B=grpBaseData(rf);     /* replace groups whose voxels overlap the new one */
      return !rf.cells.some(rc=>{ if(!baseSet.has(rc[0]+","+rc[1])) return false;
        const [al,ah]=grpCellVoxels(B,rf,rc[0],rc[1]);
        const [bl,bh]=grpCellVoxels(NB,nrf,rc[0],rc[1]);
        return al<bh&&ah>bl; }); });
    for(const rc of nrf.cells){ const [vl,vh]=grpCellVoxels(NB,nrf,rc[0],rc[1]);
      for(let l=vl;l<vh;l++) clearVox(l,rc[0],rc[1]); } /* groups claim the voxels their surface passes through */
    grps.push(nrf);
  }
  else{
    const hN = tool==="#"?brushHt["#"]:1;
    evictGrps(level,level+hN);
    for(const rc of baseCells){
      if(tool==="."){ setVox(level,rc[0],rc[1],".",brushType["."]);
        if(brushHt["."]>0) L(level).fh[rc[0]+","+rc[1]]=brushHt["."]; }
      else for(let j=0;j<hN&&level+j<NLVL;j++) setVox(level+j,rc[0],rc[1],"#",brushType["#"]);
    }
  }
  preview=null; render(); updateDsl();
}
function clickPlace(cell){
  const bc=viewCellToBase(cell[0],cell[1]), key=bc[0]+","+bc[1];
  const cur=vox(level,bc[0],bc[1]);
  if(!WALLISH.has(cur)){
    hint((tool==="D"?"Doors":"Windows")+" replace wall voxels — move the slice onto one first"); return; }
  const side=unrotArrow(nearestSide(hoverFrac||[0.5,0.9]));
  if(cur===tool&&L(level).side[key]===side) return;
  pushUndo();
  for(let j=0;j<brushHt[tool]&&level+j<NLVL;j++){   /* opening substitutes wall voxels upward from the slice */
    const lay=L(level+j), was=lay.g[bc[0]][bc[1]];
    if(j>0&&was!=="#"&&was!==" ") break;            /* grow only through wall or air */
    const wm = was==="#" ? lay.type[key] : lay.wmat[key];
    lay.g[bc[0]][bc[1]]=tool; lay.side[key]=side;
    if(wm) lay.wmat[key]=wm; else delete lay.wmat[key];
    if(brushType[tool]) lay.type[key]=brushType[tool]; else delete lay.type[key];
  }
  render(); updateDsl();
}
function hoveredGrp(){ if(!hover) return null; const bc=viewCellToBase(hover[0],hover[1]);
  const rf=grpAtBase(bc[0],bc[1]);
  return (rf && Math.floor(rf.z)===level) ? rf : null;
}
function roofEdgePick(){
  const rf=hoveredGrp(); if(!rf||rf.kind!=="roof") return null;   /* enclosure/skirts are roof-only */
  if(!hover||!hoverFrac) return {rf,side:null};
  const side=nearestSide(hoverFrac);
  const dist=Math.min(hoverFrac[1],1-hoverFrac[0],1-hoverFrac[1],hoverFrac[0]);
  const d=ASCENT[side], nb=[hover[0]+d[1],hover[1]+d[0]];
  const nbBase=(nb[0]>=0&&nb[1]>=0)?viewCellToBase(nb[0],nb[1]):null;
  const outside=!nbBase||grpAtBase(nbBase[0],nbBase[1])!==rf;
  return {rf, side:(dist<0.3&&outside)?side:null};
}
function adjustHovered(dz,isElev){
  if(!hover) return;
  const bcH=viewCellToBase(hover[0],hover[1]), key=bcH[0]+","+bcH[1];
  const ch=vox(level,bcH[0],bcH[1]);
  const rf = ch===" " ? hoveredGrp() : null;   /* priority: slice voxels (D/W, walls, floors) beat groups */
  if(rf){ pushUndo();
    if(isElev){ rf.z=Math.max(0,Math.min(NLVL-1, rf.z+dz)); hint(rf.kind+" base z="+rf.z); }
    else if(rf.kind==="stair"){ rf.incl = rf.incl===5 ? 2.5 : 5;   /* two slopes only: voxels crop clean */
      brushStairIncl=rf.incl; syncSteppers();
      hint("stair slope "+(rf.incl===5?"45° — 1 voxel/cell":"half — 1 voxel per 2 cells")+" (brush follows)"); }
    else{ rf.incl=Math.max(1,Math.min(5,rf.incl+dz)); brushIncl=rf.incl; iVal.textContent=brushIncl;
      hint("roof slope "+rf.incl+" ft/cell (brush follows)"); }
    render(); updateDsl(); return; }
  if(ch===" ") return;
  if(!scopeGroup&&(ch==="D"||ch==="W")){   /* opening: slide/resize its voxel run within the wall column */
    const [o0,o1]=openRun(level,bcH[0],bcH[1]);
    const toOpen=(l)=>{ const lay=L(l), was=lay.g[bcH[0]][bcH[1]];
      const wm = was==="#" ? lay.type[key] : lay.wmat[key];
      lay.g[bcH[0]][bcH[1]]=ch; lay.side[key]=L(level).side[key];
      if(wm) lay.wmat[key]=wm; else delete lay.wmat[key];
      const t=L(level).type[key]; if(t) lay.type[key]=t; else delete lay.type[key]; };
    const toWall=(l)=>{ const lay=L(l), wm=lay.wmat[key];
      lay.g[bcH[0]][bcH[1]]="#"; delete lay.side[key]; delete lay.wmat[key];
      if(wm) lay.type[key]=wm; else delete lay.type[key]; };
    pushUndo();
    if(isElev){
      if(dz>0){ if(o1+1<NLVL&&vox(o1+1,bcH[0],bcH[1])==="#"){ toOpen(o1+1); toWall(o0); } else hint("no wall voxel above to slide into"); }
      else{ if(o0-1>=0&&vox(o0-1,bcH[0],bcH[1])==="#"){ toOpen(o0-1); toWall(o1); } else hint("no wall voxel below to slide into"); }
    } else {
      if(dz>0){ if(o1+1<NLVL&&vox(o1+1,bcH[0],bcH[1])==="#"){ toOpen(o1+1); brushHt[ch]=o1+2-o0; }
        else hint("opening already fills the wall top"); }
      else{ if(o1>o0){ toWall(o1); brushHt[ch]=o1-o0; } else hint((ch==="D"?"door":"window")+" is already 1 voxel"); }
      syncSteppers();
    }
    render(); updateDsl(); return;
  }
  const gE=viewGridOf(level);
  const targets = scopeGroup ? groupCells(gE,hover[0],hover[1]) : [[hover[0],hover[1]]];
  pushUndo();
  if(isElev){
    let moved=0;
    for(const rc of targets){ const b2=viewCellToBase(rc[0],rc[1]);
      if(isOcc(level,b2[0],b2[1])&&moveStack(level,b2[0],b2[1],dz)) moved++; }
    if(moved){ setLevel(level+dz,true);
      hint("moved "+moved+" stack(s) — voxels above ride along (slice follows)"); }
  } else {
    let shownH=null;
    for(const rc of targets){
      const b2=viewCellToBase(rc[0],rc[1]), k2=b2[0]+","+b2[1], c2=vox(level,b2[0],b2[1]);
      if(c2==="."){                        /* floor slab thickness: 0 / 1ft / 2ft */
        const lay=L(level), nf=Math.min(2,Math.max(0,(lay.fh[k2]||0)+dz));
        if(nf) lay.fh[k2]=nf; else delete lay.fh[k2];
        if(rc[0]===hover[0]&&rc[1]===hover[1]){ brushHt["."]=nf; syncSteppers();
          hint("floor slab "+nf+"ft (brush follows)"); }
        continue; }
      const isDg=DIAG.has(c2);
      if(!(c2==="#"||isDg)) continue;
      let a=level,b=level;
      const match=(cc)=> isDg ? cc===c2 : WALLISH.has(cc);
      while(a-1>=0&&match(vox(a-1,b2[0],b2[1]))) a--;
      while(b+1<NLVL&&match(vox(b+1,b2[0],b2[1]))) b++;
      if(dz>0){
        if(b+1>=NLVL) continue;
        if(isOcc(b+1,b2[0],b2[1])&&!moveStack(b+1,b2[0],b2[1],1)) continue;  /* riders shift up first */
        setVox(b+1,b2[0],b2[1], isDg?c2:"#", L(b).type[k2]||0);
        if(rc[0]===hover[0]&&rc[1]===hover[1]) shownH=b+2-a;
      } else {
        if(b===a) continue;                /* min 1 voxel */
        if(isOcc(b+1,b2[0],b2[1])) moveStack(b+1,b2[0],b2[1],-1);   /* riders land on the removed top */
        else clearVox(b,b2[0],b2[1]);
        if(rc[0]===hover[0]&&rc[1]===hover[1]) shownH=b-a;
      }
    }
    if(shownH!==null){
      brushHt["#"]=Math.min(shownH,H_MAX); syncSteppers();
      hint((scopeGroup?("group of "+targets.length+" — "):"")+"column h="+shownH+" (brush follows)");
    }
  }
  render(); updateDsl();
}
function rotateAtHover(){
  const spinBrush=()=>{ if(tool==="R"){ roofDir=ARROW_CW[roofDir]; syncGrpChips();
      hint("roof brush direction "+ARROW_GLYPH[roofDir]); return true; }
    if(tool==="^"){ stairDir=ARROW_CW[stairDir]; syncGrpChips();
      hint("stair brush direction "+ARROW_GLYPH[stairDir]); return true; }
    return false; };
  if(!hover){ spinBrush(); return; }
  const g=viewGridOf(level), ch=g[hover[0]][hover[1]];
  if(ch===" "){                                /* priority: slice voxels beat groups */
    const rf=hoveredGrp();
    if(rf){ pushUndo(); rf.dir=ARROW_CW[rf.dir];
      hint(rf.kind+" direction "+ARROW_GLYPH[rotArrow(rf.dir)]); render(); updateDsl(); return; }
    if(spinBrush()) return; }
  if(!familyOf(ch)) return;
  if(!scopeGroup){
    const bc=viewCellToBase(hover[0],hover[1]);
    const lay=L(level), cur=lay.g[bc[0]][bc[1]];
    if(DIAG.has(cur)){ pushUndo(); lay.g[bc[0]][bc[1]]=DIAG_CW[cur]; render(); updateDsl(); }
    return;
  }
  const cellsG=groupCells(g,hover[0],hover[1]);
  const set=new Set(cellsG.map(rc=>rc[0]+","+rc[1]));
  const [M,N]=viewDims(), r0=hover[0], c0=hover[1];
  for(const rc of cellsG){ const nr=r0+(rc[1]-c0), nc=c0-(rc[0]-r0);
    if(nr<0||nr>=M||nc<0||nc>=N){ hint("no room to rotate the group"); return; }
    if(!set.has(nr+","+nc)){ const tb=viewCellToBase(nr,nc);
      for(let l=0;l<NLVL;l++) if(isOcc(l,tb[0],tb[1])){ hint("group rotation blocked by other pieces"); return; } } }
  pushUndo();
  const stash=cellsG.map(rc=>{            /* whole COLUMNS rotate: every layer of each group cell */
    const bc=viewCellToBase(rc[0],rc[1]), key=bc[0]+","+bc[1], col=[];
    for(let l=0;l<NLVL;l++){ const lay2=L(l);
      col.push({ch:lay2.g[bc[0]][bc[1]], sd:lay2.side[key], ty:lay2.type[key], wm:lay2.wmat[key], f:lay2.fh[key]});
      clearVox(l,bc[0],bc[1]); }
    return {to:[r0+(rc[1]-c0), c0-(rc[0]-r0)], col}; });
  for(const rec of stash){
    const bc=viewCellToBase(rec.to[0],rec.to[1]), key=bc[0]+","+bc[1];
    rec.col.forEach((vx,l)=>{ if(vx.ch===" ") return;
      let ch2=vx.ch;
      if(STAIRS.has(ch2)) ch2=ARROW_CW[ch2]; else if(DIAG.has(ch2)) ch2=DIAG_CW[ch2];
      const lay2=L(l); lay2.g[bc[0]][bc[1]]=ch2;
      if(vx.sd) lay2.side[key]=ARROW_CW[vx.sd];
      if(vx.ty) lay2.type[key]=vx.ty;
      if(vx.wm!==undefined) lay2.wmat[key]=vx.wm; });
  }
  hint("rotated group of "+stash.length+" columns around the selected cell");
  render(); updateDsl();
}
cv.addEventListener("pointerdown",e=>{ e.preventDefault(); cv.setPointerCapture(e.pointerId);
  if(e.button===1){ panning=true; panStart=[e.clientX-cam.dx,e.clientY-cam.dy]; cv.classList.add("panning"); return; }
  const cell=cellAt(e.offsetX,e.offsetY); if(!cell) return;
  eraseDrag=(e.button===2)||tool===" ";
  if(!eraseDrag&&(tool==="D"||tool==="W")){ clickPlace(cell); return; }
  painting=true; anchor=cell; previewErase=eraseDrag;
  preview=new Set([cell[0]+","+cell[1]]); render(); });
cv.addEventListener("pointermove",e=>{
  if(panning){ cam.dx=e.clientX-panStart[0]; cam.dy=e.clientY-panStart[1]; render(); return; }
  const cell=cellAt(e.offsetX,e.offsetY);
  if(cell){ const lay=L(level), g=viewGridOf(level), ch=g[cell[0]][cell[1]];
    const bc=viewCellToBase(cell[0],cell[1]), key=bc[0]+","+bc[1];
    const tname=TYPES[ch]?TYPES[ch][lay.type[key]||0]:null;
    const rf0=grpAtBase(bc[0],bc[1]);
    let stack=""; for(let l2=0;l2<NLVL;l2++) if(l2!==level&&L(l2).g[bc[0]][bc[1]]!==" ") stack+=(stack?",":"")+l2;
    coord.textContent="u "+cell[1]+" · v "+cell[0]+
      (ch!==" "?("  "+ch+(tname?("·"+tname):"")):"")+
      (rf0?("  "+rf0.kind+"·"+grpFormName(rf0)+" "+rf0.incl+"ft z"+rf0.z+
        (rf0.kind==="roof"?" enc:"+ENCLOSE[rf0.enclose||0]:"")):"")+
      (stack?("  [also @ "+stack+"]"):"")+"  layer "+level; }
  else coord.textContent="";
  const changed=JSON.stringify(cell)!==JSON.stringify(hover); hover=cell;
  if(painting&&cell){
    preview=(eraseDrag||tool==="."||tool==="R"||tool==="^")?rectCells(anchor,cell):lineCells45(anchor,cell);
    render(); }
  else if(changed||(tool==="D"||tool==="W")) render(); });
cv.addEventListener("pointerup",()=>{ if(panning){ panning=false; cv.classList.remove("panning"); return; }
  if(painting){ painting=false; commitStroke(); } });
cv.addEventListener("pointerleave",()=>{ hover=null; if(!panning) render(); });
cv.addEventListener("contextmenu",e=>e.preventDefault());
cv.addEventListener("wheel",e=>{ e.preventDefault();
  if(e.ctrlKey){ adjustHovered(e.deltaY<0?1:-1,false); return; }
  if(e.shiftKey){
    let overPiece=false;
    if(hover){
      if(hoveredGrp()) overPiece=true;
      else{ const bcS=viewCellToBase(hover[0],hover[1]), cS=vox(level,bcS[0],bcS[1]);
        overPiece=cS!==" "&&cS!=="."; } }
    if(overPiece) adjustHovered(e.deltaY<0?1:-1,true);
    else setLevel(level+(e.deltaY<0?1:-1));
    return; }
  const f=e.deltaY<0?1.12:1/1.12, ns=Math.min(Math.max(cam.s*f,0.05),6);
  cam.dx=e.offsetX-(e.offsetX-cam.dx)*(ns/cam.s);
  cam.dy=e.offsetY-(e.offsetY-cam.dy)*(ns/cam.s);
  cam.s=ns; render(); },{passive:false});

let hintTimer;
function hint(msg){ const el=document.getElementById("hint"); el.textContent=msg; el.classList.add("show");
  clearTimeout(hintTimer); hintTimer=setTimeout(()=>el.classList.remove("show"),2400); }
function updateHud(){
  let w=0,d=0,win=0,f=0,st=0;
  for(let l=0;l<NLVL;l++){ const g0=layers[l].g, below=l>0?layers[l-1].g:null;
    g0.forEach((row,r)=>row.forEach((ch,c)=>{
      if(ch==="#"||DIAG.has(ch))w++;                     /* voxel counts */
      else if(ch===".")f++;
      else if(ch==="D"||ch==="W"){                       /* openings count RUNS, not voxels */
        if(!(below&&below[r][c]===ch)){ if(ch==="D")d++; else win++; } }
    })); }
  for(const rf of grps) if(rf.kind==="stair") st++;
  cWall.textContent=w; cDoor.textContent=d; cWin.textContent=win;
  cStair.textContent=st; cFloor.textContent=f; cRoof.textContent=grps.length-st;
  viewChip.textContent=topView?"TOP":VIEWS[viewIdx]; lvlChip.textContent=level;
  scopeChip.textContent=scopeGroup?"group":"cell";
}
function updateDsl(){
  const out=["name: feel-rig"];
  const gvox=new Map();                    /* "lvl:r,c" -> R/S — the voxels each group surface passes through */
  for(const rf of grps){ const B=grpBaseData(rf), gch=rf.kind==="stair"?"S":"R";
    for(const rc of rf.cells){ const [vl,vh]=grpCellVoxels(B,rf,rc[0],rc[1]);
      for(let l=vl;l<vh;l++) gvox.set(l+":"+rc[0]+","+rc[1],gch); } }
  for(let lvl=0;lvl<NLVL;lvl++){
    const lay=L(lvl); let any=false;
    for(const [k] of gvox) if(k.startsWith(lvl+":")){ any=true; break; }
    for(const row of lay.g) for(const ch of row) if(ch!==" "){ any=true; break; }
    if(!any) continue;
    out.push("","level "+lvl+":");
    out.push(...lay.g.map((row,ri)=>row.map((ch,ci)=>gvox.get(lvl+":"+ri+","+ci)||ch).join("").replace(/\s+$/,"")||" "));
    const mk=(fn)=>{ let has=false;
      const rows=lay.g.map((row,r)=>row.map((ch,c)=>{ const v=fn(ch,r+","+c); if(v!==".")has=true; return v; }).join(""));
      return has?rows:null; };
    const sL=mk((ch,k)=>lay.side[k]?SIDE_NAME[lay.side[k]]:".");
    const tL=mk((ch,k)=>lay.type[k]?String(lay.type[k]):".");
    const wL=mk((ch,k)=>lay.wmat[k]?String(lay.wmat[k]):".");
    const fL=mk((ch,k)=>lay.fh[k]?String(lay.fh[k]):".");
    if(sL) out.push("layer side:",...sL);
    if(tL) out.push("layer type:",...tL);
    if(wL) out.push("layer wmat:",...wL);
    if(fL) out.push("layer fh:",...fL);
  }
  for(const rf of grps){
    const rs=rf.cells.map(rc=>rc[0]), cs2=rf.cells.map(rc=>rc[1]);
    out.push((rf.kind==="stair"?"stair: ":"roof: ")+Math.min(...rs)+","+Math.min(...cs2)+" "+Math.max(...rs)+","+Math.max(...cs2)+
      " form="+grpFormName(rf)+" dir="+SIDE_NAME[rf.dir]+" incl="+rf.incl+"ft z="+rf.z+
      (rf.kind==="roof"?" enclose="+ENCLOSE[rf.enclose||0]:""));
  }
  dsl.value=out.join("\n");
}
function syncGrpChips(){ roofChip.textContent=ROOF_FORMS[roofFormIdx]+" "+ARROW_GLYPH[roofDir];
  stairChip.textContent=STAIR_TYPES[stairTypeIdx]+" "+ARROW_GLYPH[stairDir]; }
function syncSteppers(){ colVal.textContent=COLS; rowVal.textContent=ROWS;
  hVal.textContent=brushHt[brushHt[tool]!==undefined?tool:"#"]+(tool==="."?"ft":"");
  lvlVal.textContent=level; iVal.textContent = tool==="^" ? brushStairIncl : brushIncl;
  typeChip.textContent=TYPES[tool]?TYPES[tool][brushType[tool]||0]:"—"; syncGrpChips(); }
function resizeGrid(dc,dr){
  pushUndo();
  const nc=Math.min(Math.max(COLS+dc,4),40), nr=Math.min(Math.max(ROWS+dr,4),40);
  for(const lay of layers){
    const ng=blankGrid(nr,nc);
    for(let r=0;r<Math.min(ROWS,nr);r++) for(let c=0;c<Math.min(COLS,nc);c++) ng[r][c]=lay.g[r][c];
    lay.g=ng; }
  grps=grps.filter(rf=>rf.cells.every(rc=>rc[0]<nr&&rc[1]<nc));
  COLS=nc; ROWS=nr; syncSteppers(); fitCamera(); render(); updateDsl();
}
function setLevel(l,silent){ level=Math.min(Math.max(l,0),NLVL-1); lvlVal.textContent=level;
  if(!silent) hint("editing layer "+level); render(); }

document.querySelectorAll("nav [data-tool]").forEach(b=>{
  b.addEventListener("click",()=>{
    if(b.id==="stairBtn"&&tool==="^"){ stairTypeIdx=(stairTypeIdx+1)%STAIR_TYPES.length;
      syncGrpChips(); hint("stair type: "+STAIR_TYPES[stairTypeIdx]+" (R rotates direction)"); }
    if(b.id==="roofBtn"&&tool==="R"){ roofFormIdx=(roofFormIdx+1)%ROOF_FORMS.length;
      syncGrpChips(); hint("roof form: "+ROOF_FORMS[roofFormIdx]); }
    tool=b.dataset.tool; syncSteppers();
    document.querySelectorAll("nav [data-tool]").forEach(x=>x.classList.toggle("active",x===b)); }); });
function rotate(dir){ viewIdx=(viewIdx+dir+4)%4; topView=false; fitCamera(); render(); }
rotL.onclick=()=>rotate(1); rotR.onclick=()=>rotate(-1);
topBtn.onclick=()=>{ topView=!topView; fitCamera(); render(); };
fitBtn.onclick=()=>{ fitCamera(); render(); };
undoBtn.onclick=undo;
clearBtn.onclick=()=>{ pushUndo(); initLayers(); grps=[]; render(); updateDsl(); };
function undo(){ const p=undoStack.pop(); if(!p){ hint("nothing to undo"); return; }
  restore(p); render(); updateDsl(); }
copyBtn.onclick=()=>{ navigator.clipboard.writeText(dsl.value).then(()=>{
  copied.style.visibility="visible"; setTimeout(()=>copied.style.visibility="hidden",1800); }); };
lroomBtn.onclick=()=>{ pushUndo(); loadLRoom(); render(); updateDsl(); };
function brushHTool(){ return brushHt[tool]!==undefined ? tool : "#"; }
hMinus.onclick=()=>{ const t=brushHTool(); brushHt[t]=Math.max(t==="."?0:1,brushHt[t]-1); syncSteppers(); };
hPlus.onclick=()=>{ const t=brushHTool(); brushHt[t]=Math.min(t==="."?2:H_MAX,brushHt[t]+1); syncSteppers(); };
function slopeStep(dz){ if(tool==="^"){ brushStairIncl = brushStairIncl===5 ? 2.5 : 5;
    hint("stair brush slope: "+(brushStairIncl===5?"45°":"half")); }
  else brushIncl=Math.max(1,Math.min(5,brushIncl+dz));
  syncSteppers(); }
iMinus.onclick=()=>slopeStep(-1);
iPlus.onclick=()=>slopeStep(1);
lvlMinus.onclick=()=>setLevel(level-1); lvlPlus.onclick=()=>setLevel(level+1);
wMinus.onclick=()=>{ viewWin=Math.max(1,viewWin-1); wVal.textContent=viewWin; render(); };
wPlus.onclick=()=>{ viewWin=Math.min(9,viewWin+1); wVal.textContent=viewWin; render(); };
oMinus.onclick=()=>{ fadeOp=Math.max(0,+(fadeOp-0.1).toFixed(1)); oVal.textContent=Math.round(fadeOp*100); render(); };
oPlus.onclick=()=>{ fadeOp=Math.min(1,+(fadeOp+0.1).toFixed(1)); oVal.textContent=Math.round(fadeOp*100); render(); };
colMinus.onclick=()=>resizeGrid(-2,0); colPlus.onclick=()=>resizeGrid(2,0);
rowMinus.onclick=()=>resizeGrid(0,-2); rowPlus.onclick=()=>resizeGrid(0,2);
addEventListener("keydown",e=>{
  if(e.target.tagName==="TEXTAREA") return;
  if(e.code==="Space"){ e.preventDefault();
    scopeGroup=!scopeGroup; scopeChip.textContent=scopeGroup?"group":"cell";
    hint("selection scope: "+(scopeGroup?"connected group":"single cell")); render(); return; }
  const k=e.key;
  const tools={"1":"#","2":".","3":"D","4":"W","5":"^","6":"R","x":" ","X":" "};
  if(tools[k]!==undefined){
    const sel=k==="5"?"#stairBtn":k==="6"?"#roofBtn":'nav [data-tool="'+tools[k]+'"]';
    const btn=document.querySelector(sel); if(btn) btn.click(); return; }
  if(k==="+"||k==="=") adjustHovered(1,false);
  else if(k==="-"||k==="_") adjustHovered(-1,false);
  else if(k==="]") adjustHovered(1,true);
  else if(k==="[") adjustHovered(-1,true);
  else if(k==="f"||k==="F"){ const rf=hoveredGrp();
    if(rf){ pushUndo();
      const forms = rf.kind==="stair"?STAIR_TYPES:ROOF_FORMS;
      rf.form=(rf.form+1)%forms.length;
      hint(rf.kind+" form: "+forms[rf.form]); render(); updateDsl(); }
    else if(tool==="^"){ stairTypeIdx=(stairTypeIdx+1)%STAIR_TYPES.length; syncGrpChips();
      hint("stair brush type: "+STAIR_TYPES[stairTypeIdx]); }
    else{ roofFormIdx=(roofFormIdx+1)%ROOF_FORMS.length; syncGrpChips();
      hint("roof brush form: "+ROOF_FORMS[roofFormIdx]); } }
  else if(k==="v"||k==="V"){ const pick=roofEdgePick();
    if(pick){ pushUndo();
      if(pick.side){
        const baseSide=unrotArrow(pick.side);
        pick.rf.sideMode=pick.rf.sideMode||{};
        const cur=modeOf(pick.rf,baseSide);
        pick.rf.sideMode[baseSide]=(cur+1)%3;
        hint("skirt "+SIDE_NAME[baseSide]+" side: "+ENCLOSE[pick.rf.sideMode[baseSide]]);
      } else {
        pick.rf.enclose=((pick.rf.enclose||0)+1)%ENCLOSE.length; pick.rf.sideMode={};
        hint("roof enclosure (all sides): "+ENCLOSE[pick.rf.enclose]);
      }
      render(); updateDsl(); } }
  else if(k==="m"||k==="M"){ const list=TYPES[tool];
    if(list){ brushType[tool]=((brushType[tool]||0)+1)%list.length;
      typeChip.textContent=list[brushType[tool]];
      hint(tool+" type: "+list[brushType[tool]]); } }
  else if(k==="q"||k==="Q") rotate(1); else if(k==="e"||k==="E") rotate(-1);
  else if(k==="t"||k==="T"){ topView=!topView; fitCamera(); render(); }
  else if(k==="c"||k==="C"){ fitCamera(); render(); }
  else if(k==="PageUp"){ setLevel(level+1); e.preventDefault(); }
  else if(k==="PageDown"){ setLevel(level-1); e.preventDefault(); }
  else if(k==="r"||k==="R") rotateAtHover();
  else if((k==="z"||k==="Z")&&(e.ctrlKey||e.metaKey)){ e.preventDefault(); undo(); }
});
new ResizeObserver(()=>{ fitCamera(); render(); }).observe(document.getElementById("stage"));
matchMedia("(prefers-color-scheme: dark)").addEventListener("change",()=>render());

function recolor(img){
  const c=document.createElement("canvas"); c.width=img.width; c.height=img.height;
  const x=c.getContext("2d"); x.drawImage(img,0,0);
  const d=x.getImageData(0,0,c.width,c.height), p=d.data;
  for(let i=0;i<p.length;i+=4){
    const magenta = p[i]>150&&p[i+2]>150&&p[i+1]<110;
    const cyan = p[i]<120&&p[i+1]>150&&p[i+2]>150;
    if(magenta||cyan){ p[i]=43;p[i+1]=43;p[i+2]=48; } }
  x.putImageData(d,0,0); return c;
}
let toLoad=Object.keys(KIT_SRC).length;
for(const name of Object.keys(KIT_SRC)){
  const img=new Image();
  img.onload=()=>{ sprites[name]=recolor(img);
    if(--toLoad===0){ loadLRoom(); syncSteppers(); fitCamera(); render(); updateDsl(); } };
  img.src=KIT_SRC[name];
}
</script>
