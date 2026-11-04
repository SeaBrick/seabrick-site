/* SeaBrick builder: an interactive viewer showing how the smoothed SeaBrick shapes
   fit together into mats, tubes, towers and bridged layers.
   Geometry and layouts come from bricks-data.js (approved smoothed meshes, decimated).
   No external libraries, WebGL 2 only. */
'use strict';
(() => {
  const D = window.SEABRICK_DATA;
  const $ = id => document.getElementById(id);
  const params = new URLSearchParams(location.search);
  const embed = params.get('embed') === '1';
  if (embed) document.body.classList.add('embed');
  if (params.get('bar') === '0') document.body.classList.add('nobar');
  if (params.get('panel') === '1') document.body.classList.add('withpanel');

  /* ---------- palette ---------- */
  const hex = h => h.replace('#', '').match(/../g).map(x => parseInt(x, 16) / 255);
  const PAL = {
    layer: [hex('#8fbfdc'), hex('#8fcfbf'), hex('#e0cfae')],
    gold: hex('#e3b14f'), pink: hex('#e07a7a'), clad: hex('#d9954f'), sand: hex('#e9e1d2'),
    highlight: hex('#005492'),
  };
  const typeColours = D.meshes.map(m => hex(m.colour));

  /* ---------- WebGL ---------- */
  const canvas = $('view');
  const gl = canvas.getContext('webgl2', { antialias: true, alpha: true, premultipliedAlpha: false, preserveDrawingBuffer: true });
  const status = $('status');
  function fail(msg) { $('fallback').hidden = false; $('fallback').textContent = msg; throw new Error(msg); }
  if (!gl) fail('This viewer needs a browser with WebGL 2 (Chrome, Edge, Firefox or Safari 15+).');

  const VS = `#version 300 es
  in vec3 pos; in vec4 iA; in vec4 iB; in vec4 iC;
  uniform mat4 vp; uniform float flipY;
  out vec3 vC; out float vId; out vec3 vW;
  void main(){
    float c=cos(iA.w), s=sin(iA.w); mat3 r=mat3(c,0.,s, 0.,1.,0., -s,0.,c);
    vec3 p=pos;
    if(iB.x>.5){ p.y=flipY-p.y; p.z=-p.z; }
    vC=iB.yzw; vId=iC.x; vW=r*p+iA.xyz;
    gl_Position=vp*vec4(vW,1.);
  }`;
  const FS = `#version 300 es
  precision highp float;
  in vec3 vC; in float vId; in vec3 vW;
  uniform int pick; uniform vec3 eye;
  out vec4 o;
  void main(){
    if(pick==1){ float id=vId; o=vec4(mod(id,256.)/255., floor(id/256.)/255., 0., 1.); return; }
    vec3 n=normalize(cross(dFdx(vW),dFdy(vW)));
    vec3 L1=normalize(vec3(-.4,.9,.5)), L2=normalize(vec3(.7,.3,-.6));
    float d=max(dot(n,L1),0.), f=max(dot(n,L2),0.);
    float sky=n.y*.5+.5;
    vec3 v=normalize(eye-vW);
    float rim=pow(1.-max(dot(n,v),0.),3.)*.08;
    vec3 c=vC*(.30+.22*sky+.48*d+.14*f)+rim;
    o=vec4(c,1.);
  }`;
  const LVS = `#version 300 es
  in vec3 pos; uniform mat4 vp; void main(){ gl_Position=vp*vec4(pos,1.); }`;
  const LFS = `#version 300 es
  precision highp float; uniform vec4 col; out vec4 o; void main(){ o=col; }`;
  function shader(t, s) { const sh = gl.createShader(t); gl.shaderSource(sh, s); gl.compileShader(sh); if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) fail(gl.getShaderInfoLog(sh)); return sh; }
  function program(v, f) { const p = gl.createProgram(); gl.attachShader(p, shader(gl.VERTEX_SHADER, v)); gl.attachShader(p, shader(gl.FRAGMENT_SHADER, f)); gl.linkProgram(p); if (!gl.getProgramParameter(p, gl.LINK_STATUS)) fail(gl.getProgramInfoLog(p)); return p; }
  const prog = program(VS, FS), lineProg = program(LVS, LFS);
  const U = { vp: gl.getUniformLocation(prog, 'vp'), flipY: gl.getUniformLocation(prog, 'flipY'), pick: gl.getUniformLocation(prog, 'pick'), eye: gl.getUniformLocation(prog, 'eye') };
  const LU = { vp: gl.getUniformLocation(lineProg, 'vp'), col: gl.getUniformLocation(lineProg, 'col') };

  function b64(s, T) { const b = atob(s), u = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return new T(u.buffer); }
  function unpack(m) {
    const q = b64(m.positions, Uint16Array), pos = new Float32Array(q.length);
    const lo = m.bounds[0], hi = m.bounds[1];
    for (let i = 0; i < q.length; i++) { const a = i % 3; pos[i] = lo[a] + q[i] / 65535 * (hi[a] - lo[a]); }
    const idx = m.index16 ? b64(m.indices, Uint16Array) : b64(m.indices, Uint32Array);
    return { pos, idx, index16: !!m.index16 };
  }
  function upload(m) {
    const g = unpack(m), vao = gl.createVertexArray(); gl.bindVertexArray(vao);
    for (const [name, arr] of [['pos', g.pos]]) {
      const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, arr, gl.STATIC_DRAW);
      const l = gl.getAttribLocation(prog, name); gl.enableVertexAttribArray(l); gl.vertexAttribPointer(l, 3, gl.FLOAT, false, 0, 0);
    }
    const ib = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ib); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, g.idx, gl.STATIC_DRAW);
    const inst = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, inst);
    ['iA', 'iB', 'iC'].forEach((name, i) => { const l = gl.getAttribLocation(prog, name); gl.enableVertexAttribArray(l); gl.vertexAttribPointer(l, 4, gl.FLOAT, false, 48, i * 16); gl.vertexAttribDivisor(l, 1); });
    return { vao, inst, count: g.idx.length, type: g.index16 ? gl.UNSIGNED_SHORT : gl.UNSIGNED_INT };
  }
  const meshes = D.meshes.map(m => ({ full: upload(m.full), fast: upload(m.fast), label: m.label, role: m.role, bounds: m.full.bounds, cladding: m.cladding, uprightOnly: m.uprightOnly }));
  let heroState = 'none';
  function loadHero() {
    if (heroState !== 'none') return;
    heroState = 'loading';
    const sc = document.createElement('script'); sc.src = 'seabrick-hero.js';
    sc.onload = () => { try { const h = window.SEABRICK_HERO; meshes[h.mesh].hero = upload(h.data); heroState = 'ready'; dirty = true; } catch (e) { heroState = 'failed'; } };
    sc.onerror = () => { heroState = 'failed'; };
    document.head.appendChild(sc);
  }
  const lineVao = gl.createVertexArray(), lineBuf = gl.createBuffer(); gl.bindVertexArray(lineVao); gl.bindBuffer(gl.ARRAY_BUFFER, lineBuf);
  const lp = gl.getAttribLocation(lineProg, 'pos'); gl.enableVertexAttribArray(lp); gl.vertexAttribPointer(lp, 3, gl.FLOAT, false, 0, 0);
  gl.enable(gl.DEPTH_TEST); gl.enable(gl.CULL_FACE); gl.cullFace(gl.BACK);

  /* ---------- state ---------- */
  const S = {
    scene: params.get('scene') || 'mat', layers: +(params.get('layers') || 3), phase: +(params.get('phase') || 0),
    explode: +(params.get('explode') || 0), rotate: params.get('rotate') === '1', bridges: params.get('bridges') !== '0',
    tubeSize: +(params.get('tube') || 0), sides: +(params.get('sides') || 12), radius: +(params.get('radius') || 6), wall: +(params.get('wall') || 1.5),
    stack: params.get('stack') || 'abc', preset: params.get('preset') || '', shape: +(params.get('shape') || 0),
    colour: params.get('colour') || 'layer', guides: params.get('guides') !== '0', detail: 'auto',
    assemble: 1, playing: false, selected: -1,
  };
  const PRESETS = { wideHex: [6, 6, 2.5, 6], thickHex: [6, 8, 4, 10], lowDodec: [12, 6, 1.5, 3], thickDodec: [12, 6, 3, 8], tallDodec: [12, 4.5, 1.5, 16], wideDodec: [12, 8, 4, 12] };
  if (S.preset && PRESETS[S.preset]) { const [s, r, w, h] = PRESETS[S.preset]; S.sides = s; S.radius = r; S.wall = w; S.layers = h; S.scene = 'designer'; }

  const cam = { yaw: 0.55, pitch: 0.95, dist: 25, target: [0, 1, 0], centre: [0, 1, 0], radius: 5 };
  let dirty = true, needFit = true, lastScene = '';

  /* ---------- layouts ---------- */
  function designerCase() { return D.designer.cases[`${S.sides}:${S.radius}:${S.wall}`]; }
  function tubeCase() { return S.scene === 'designer' ? designerCase() : D.boundarySizes[S.tubeSize]; }
  function phaseAt(c, l) { const seq = c.phaseSequence, start = Math.max(0, seq.indexOf(S.phase)); return S.stack === 'aligned' ? seq[start] : seq[(start + l) % seq.length]; }
  function layerColour(phase) { return PAL.layer[phase % 3]; }

  function instances() {
    const out = [], H = D.height, ex = S.explode;
    if (S.scene === 'catalogue') {
      out.push({ mesh: S.shape, pos: [0, 0, 0], turn: 0, flip: false, layer: 0, colour: PAL.sand });
    } else if (S.scene === 'mat') {
      for (let l = 0; l < S.layers; l++) {
        const ph = (S.phase + l) % 3, off = D.offsets[ph], th = S.rotate && l % 2 ? Math.PI / 3 : 0, c = Math.cos(th), s = Math.sin(th);
        for (const p of D.mat) { const x = p[0] + off[0], z = p[1] + off[1]; out.push({ mesh: 0, pos: [c * x - s * z, l * (H + ex), s * x + c * z], turn: th, flip: false, layer: l, phase: ph, colour: layerColour(ph) }); }
      }
    } else if (S.scene === 'tube' || S.scene === 'designer') {
      const c = tubeCase(); if (!c) return out;
      for (let l = 0; l < S.layers; l++) {
        const ph = phaseAt(c, l), list = c.layers[ph * 2 + (S.rotate ? 1 : 0)] || [];
        for (const p of list) {
          const m = D.meshes[p.mesh];
          out.push({ mesh: p.mesh, pos: [p.x, l * (H + ex), p.z], turn: p.turn * Math.PI / 3, flip: m.uprightOnly ? false : !!p.flip, layer: l, phase: ph,
            cladding: !!p.cladding || m.cladding, feature: !!p.acceptedWallFeature || p.mesh === D.newMesh, correction: !!p.userCorrection,
            colour: (p.cladding || m.cladding) ? PAL.clad : (p.mesh === D.newMesh || p.acceptedWallFeature) ? PAL.gold : layerColour(ph) });
        }
      }
    } else if (S.scene === 'bridges') {
      const src = S.bridges ? D.bridged : D.aligned;
      for (const p of src) { if (p.layer + p.span > S.layers) continue; out.push({ mesh: p.mesh, pos: [p.x, p.layer * (H + (S.bridges ? 0 : ex)), p.z], turn: p.turn * Math.PI / 3, flip: !!p.flip, layer: p.layer, phase: p.layer % 3, span: p.span, colour: p.span === 2 ? PAL.gold : layerColour(p.layer % 3) }); }
    }
    if (S.colour === 'type') for (const p of out) p.colour = typeColours[p.mesh];
    if (S.colour === 'plain') for (const p of out) p.colour = p.cladding ? PAL.clad : PAL.sand;
    // assembly order: layer, then distance from centre
    out.forEach((p, i) => { p.id = i; });
    const order = out.slice().sort((a, b) => a.layer - b.layer || Math.hypot(a.pos[0], a.pos[2]) - Math.hypot(b.pos[0], b.pos[2]));
    order.forEach((p, i) => { p.order = i; });
    return out;
  }

  /* ---------- camera ---------- */
  const norm = v => { const l = Math.hypot(...v) || 1; return v.map(x => x / l); };
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  function mul(a, b) { const o = new Float32Array(16); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) { let s = 0; for (let k = 0; k < 4; k++) s += a[k * 4 + r] * b[c * 4 + k]; o[c * 4 + r] = s; } return o; }
  function axes() { const z = [Math.cos(cam.pitch) * Math.sin(cam.yaw), Math.sin(cam.pitch), Math.cos(cam.pitch) * Math.cos(cam.yaw)], x = norm(cross([0, 1, 0], z)); return { x, y: cross(z, x), z }; }
  function eye() { const { z } = axes(); return z.map((v, i) => cam.dist * v + cam.target[i]); }
  function viewProj() {
    const { x, y, z } = axes(), e = eye();
    const v = new Float32Array([x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0, -dot(x, e), -dot(y, e), -dot(z, e), 1]);
    const a = canvas.width / canvas.height, f = Math.min(1, a) / Math.tan(0.3);
    const depth = dot(e.map((q, i) => q - cam.centre[i]), z), n = Math.max(cam.radius * 1e-4, depth - cam.radius * 1.8), far = Math.max(n + cam.radius, depth + cam.radius * 2 + 10);
    return mul(new Float32Array([f / a, 0, 0, 0, 0, f, 0, 0, 0, 0, (far + n) / (n - far), -1, 0, 0, 2 * far * n / (n - far), 0]), v);
  }
  function fit(ins) {
    let lo = [1e9, 1e9, 1e9], hi = [-1e9, -1e9, -1e9];
    for (const p of ins) { const [a, b] = meshes[p.mesh].bounds, c = Math.cos(p.turn), s = Math.sin(p.turn); for (let bits = 0; bits < 8; bits++) { let x = bits & 1 ? b[0] : a[0], y = bits & 2 ? b[1] : a[1], z = bits & 4 ? b[2] : a[2]; if (p.flip) { y = D.flipY - y; z = -z; } const v = [c * x - s * z + p.pos[0], y + p.pos[1], s * x + c * z + p.pos[2]]; for (let j = 0; j < 3; j++) { lo[j] = Math.min(lo[j], v[j]); hi[j] = Math.max(hi[j], v[j]); } } }
    cam.target = lo.map((v, i) => (v + hi[i]) / 2); cam.centre = [...cam.target];
    cam.radius = Math.max(0.5, Math.hypot(...hi.map((v, i) => (v - lo[i]) / 2)));
    cam.dist = 0.98 * cam.radius / Math.sin(0.3); needFit = false;
  }
  function pan(dx, dy) { const { x, y } = axes(), r = canvas.getBoundingClientRect(), k = 2 * cam.dist * Math.tan(0.3) / Math.max(1, Math.min(r.width, r.height)); cam.target = cam.target.map((v, i) => v + (-x[i] * dx + y[i] * dy) * k); dirty = true; }
  function dolly(a) { cam.dist = Math.min(cam.radius * 40, Math.max(cam.radius * 0.05, cam.dist * Math.exp(Math.max(-2, Math.min(2, a))))); dirty = true; }
  function orbit(dx, dy) { cam.yaw -= dx * 0.006; cam.pitch = Math.min(Math.PI / 2 - 0.002, Math.max(-Math.PI / 2 + 0.002, cam.pitch + dy * 0.006)); dirty = true; }

  /* ---------- guides ---------- */
  function guideLines() {
    if (S.scene !== 'designer' || !S.guides) return [];
    const c = designerCase(); if (!c) return [];
    const bottom = meshes[0].bounds[0][1], top = meshes[0].bounds[1][1] + (S.layers - 1) * (D.height + S.explode), out = [];
    for (const ring of c.outlines) for (let i = 0; i < ring.length; i++) { const a = ring[i], b = ring[(i + 1) % ring.length]; for (const y of [bottom, top]) out.push(a[0], y, a[1], b[0], y, b[1]); out.push(a[0], bottom, a[1], a[0], top, a[1]); }
    return out;
  }

  /* ---------- draw ---------- */
  let current = [], visibleCount = 0, groupsCache = null;
  function build() {
    current = instances();
    if (!current.length) { status.textContent = 'No bricks for this setting.'; return; }
    if (needFit) fit(current);
    groupsCache = null; updateInfo();
    if (current.length <= 7 && current.some(p => p.mesh === 0)) loadHero();
  }
  function groups(pick) {
    const g = new Map(), limit = Math.round(S.assemble * current.length);
    for (const p of current) {
      if (p.order >= limit) continue;
      if (!g.has(p.mesh)) g.set(p.mesh, []);
      const sel = p.id === S.selected && !pick;
      const col = sel ? PAL.highlight : p.colour;
      g.get(p.mesh).push(p.pos[0], p.pos[1], p.pos[2], p.turn, p.flip ? 1 : 0, col[0], col[1], col[2], p.id + 1, 0, 0, 0);
    }
    visibleCount = Math.min(limit, current.length);
    return g;
  }
  function render(pick = false) {
    const vp = viewProj(), e = eye(), fast = S.detail === 'fast' || (S.detail === 'auto' && current.length > 160);
    gl.viewport(0, 0, canvas.width, canvas.height);
    if (pick) gl.clearColor(0, 0, 0, 1); else gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.useProgram(prog); gl.uniformMatrix4fv(U.vp, false, vp); gl.uniform1f(U.flipY, D.flipY); gl.uniform1i(U.pick, pick ? 1 : 0); gl.uniform3fv(U.eye, e);
    let tris = 0;
    for (const [mi, buf] of groups(pick)) {
      const m = (current.length <= 7 && meshes[mi].hero && !fast) ? meshes[mi].hero : meshes[mi][fast ? 'fast' : 'full'];
      gl.bindVertexArray(m.vao); gl.bindBuffer(gl.ARRAY_BUFFER, m.inst); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(buf), gl.DYNAMIC_DRAW);
      gl.drawElementsInstanced(gl.TRIANGLES, m.count, m.type, 0, buf.length / 12); tris += m.count / 3 * buf.length / 12;
    }
    if (!pick) {
      const lines = guideLines();
      if (lines.length) { gl.useProgram(lineProg); gl.uniformMatrix4fv(LU.vp, false, vp); gl.uniform4f(LU.col, 0, 0.33, 0.57, 0.8); gl.bindVertexArray(lineVao); gl.bindBuffer(gl.ARRAY_BUFFER, lineBuf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(lines), gl.DYNAMIC_DRAW); gl.drawArrays(gl.LINES, 0, lines.length / 3); }
      $('counter').textContent = `${visibleCount.toLocaleString()} of ${current.length.toLocaleString()} bricks · ${(tris / 1e6).toFixed(1)} M triangles · ${fast ? 'light' : 'full'} mesh`;
    }
  }
  function frame(t) {
    const r = canvas.getBoundingClientRect(), ratio = Math.min(window.devicePixelRatio || 1, 2), w = Math.max(1, Math.round(r.width * ratio)), h = Math.max(1, Math.round(r.height * ratio));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; dirty = true; }
    if (S.playing) { S.assemble = Math.min(1, S.assemble + 0.6 / Math.max(10, current.length) * (current.length > 400 ? 6 : current.length > 100 ? 3 : 1)); $('assemble').value = Math.round(S.assemble * 1000); if (S.assemble >= 1) { S.playing = false; $('play').textContent = 'Replay assembly'; } dirty = true; }
    if (dirty) { render(false); dirty = false; }
    requestAnimationFrame(frame);
  }

  /* ---------- picking ---------- */
  function pickAt(px, py) {
    render(true);
    const r = canvas.getBoundingClientRect(), x = Math.round((px - r.left) / r.width * canvas.width), y = Math.round(canvas.height - (py - r.top) / r.height * canvas.height);
    const buf = new Uint8Array(4); gl.readPixels(x, y, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, buf);
    const id = buf[0] + buf[1] * 256 - 1; dirty = true;
    return id >= 0 && id < current.length ? current[id] : null;
  }

  /* ---------- UI ---------- */
  const SCENES = {
    mat: { title: 'Floating mat', text: 'A 19-brick hexagonal mat. Each course sits in one of three registrations (A, B, C) so that bricks in one course bridge the joints below. Separate the courses to see the offset; rotate alternate courses to swap the two offset families. The perimeter is left open on purpose.' },
    tube: { title: 'Small tubes', text: 'The smallest closed rings. Half bricks (3-lock claw and tongue) and edge bricks (4- and 5-lock) close the ring so that every internal tongue meets a claw. Flat faces appear only on the real inner and outer walls.' },
    designer: { title: 'Tube and tower designer', text: 'Larger rings and towers assembled from the ten reversible shapes. Hexagonal tubes use straight runs between six corners; dodecagons use two wall families and are slightly irregular. Gold marks wall features; orange marks upright wedge cladding at the boundary. Compatible course sequences are listed below the model.' },
    bridges: { title: 'Bridged courses', text: 'A four-course hexagonal ring in which double-hex bricks span two courses, tying them together. Turn the bridges off to separate the courses.' },
    catalogue: { title: 'The shapes', text: 'The brick family. Every shape is a subset of the same hexagonal prism: the number in its name says how many of its six sides carry a connector; the rest are flat wall faces. Shown as smoothed visualization meshes of the final design: the connector surfaces are not modelled.' },
  };
  function updateInfo() {
    const sc = SCENES[S.scene]; $('sceneTitle').textContent = sc.title; $('sceneText').textContent = sc.text;
    let line = '';
    if (S.scene === 'designer' && designerCase()) { const c = designerCase(); line = `${c.sides === 6 ? 'Hexagon' : 'Dodecagon'} · ${S.layers} course${S.layers > 1 ? 's' : ''} · outer width ${c.actualOuter.map(v => (2 * v).toFixed(1)).join('–')} pitches · opening ${c.actualInner.map(v => (2 * v).toFixed(1)).join('–')} pitches · course sequence ${c.phaseSequence.map(p => 'ABC'[p]).join(' → ')}`; }
    else if (S.scene === 'tube') { const c = D.boundarySizes[S.tubeSize]; line = `${c.label} · outer radius ${c.radius} pitches · wall ${c.wall} pitches · ${S.layers} course${S.layers > 1 ? 's' : ''}`; }
    else if (S.scene === 'mat') line = `${S.layers} course${S.layers > 1 ? 's' : ''} · registration ${'ABC'[S.phase]} first · 19 bricks per course`;
    else if (S.scene === 'bridges') line = `${S.layers} course${S.layers > 1 ? 's' : ''} · ${S.bridges ? 'with' : 'without'} double-hex bridges`;
    else if (S.scene === 'catalogue') { const m = D.meshes[S.shape]; line = `${m.label}: ${m.role}.`; }
    $('sceneLine').textContent = line;
    const counts = new Map(); for (const p of current) counts.set(p.mesh, (counts.get(p.mesh) || 0) + 1);
    const leg = $('legend'); leg.replaceChildren();
    if (S.colour === 'type') for (const [mi, n] of [...counts].sort((a, b) => a[0] - b[0])) { const s = document.createElement('span'); s.innerHTML = `<i style="background:${D.meshes[mi].colour}"></i>${D.meshes[mi].label} × ${n}`; leg.append(s); }
    else if (S.scene !== 'catalogue') { ['A', 'B', 'C'].forEach((k, i) => { const s = document.createElement('span'); s.innerHTML = `<i style="background:${['#8fbfdc', '#8fcfbf', '#e0cfae'][i]}"></i>Course ${k}`; leg.append(s); }); if (S.scene !== 'mat') { const s = document.createElement('span'); s.innerHTML = `<i style="background:#e3b14f"></i>Bridge / wall feature`; leg.append(s); } if (S.scene === 'designer') { const s = document.createElement('span'); s.innerHTML = `<i style="background:#d9954f"></i>Wedge cladding`; leg.append(s); } }
  }
  function syncControls() {
    $('scene').value = S.scene; $('layers').value = S.layers; $('layersOut').textContent = S.layers; $('phase').value = S.phase; $('explode').value = S.explode; $('rotate').checked = S.rotate; $('bridges').checked = S.bridges; $('tubeSize').value = S.tubeSize; $('sides').value = S.sides; $('radius').value = S.radius; $('wall').value = S.wall; $('stack').value = S.stack; $('shape').value = S.shape; $('colour').value = S.colour; $('guides').checked = S.guides; $('detail').value = S.detail;
    const d = S.scene === 'designer', t = S.scene === 'tube', m = S.scene === 'mat', c = S.scene === 'catalogue', b = S.scene === 'bridges';
    $('designerControls').hidden = !d; $('tubeControls').hidden = !t; $('catalogueControls').hidden = !c; $('bridgeControls').hidden = !b;
    $('layersRow').hidden = c; $('phaseRow').hidden = !(d || t || m); $('explodeRow').hidden = c || (b && S.bridges); $('rotateRow').hidden = !(d || t || m); $('stackRow').hidden = !d; $('guidesRow').hidden = !d;
    $('layers').max = t ? 4 : b ? 4 : d ? D.designer.maxLayers : 12; if (S.layers > +$('layers').max) { S.layers = +$('layers').max; $('layers').value = S.layers; }
    $('rotateLabel').textContent = m ? 'Rotate alternate courses by 60°' : 'Other angular orientation (60°)';
    if (d) {
      for (const o of $('radius').options) o.disabled = !Object.values(D.designer.cases).some(k => k.sides === S.sides && k.radius === +o.value);
      if ($('radius').selectedOptions[0]?.disabled) { const ok = [...$('radius').options].filter(o => !o.disabled); S.radius = +ok.sort((a, b) => Math.abs(+a.value - S.radius) - Math.abs(+b.value - S.radius))[0].value; $('radius').value = S.radius; }
      for (const o of $('wall').options) o.disabled = !D.designer.cases[`${S.sides}:${S.radius}:${+o.value}`];
      if ($('wall').selectedOptions[0]?.disabled) { const ok = [...$('wall').options].filter(o => !o.disabled); S.wall = +ok.sort((a, b) => Math.abs(+a.value - S.wall) - Math.abs(+b.value - S.wall))[0].value; $('wall').value = S.wall; }
      const cs = designerCase(); for (const o of $('phase').options) o.disabled = !cs.allowedPhases.includes(+o.value); if (!cs.allowedPhases.includes(S.phase)) { S.phase = cs.allowedPhases[0]; $('phase').value = S.phase; }
      $('preset').value = S.preset || 'custom';
    } else if (t) { const cs = D.boundarySizes[S.tubeSize]; for (const o of $('phase').options) o.disabled = !cs.allowedPhases.includes(+o.value); if (!cs.allowedPhases.includes(S.phase)) { S.phase = cs.allowedPhases[0]; $('phase').value = S.phase; } }
    else for (const o of $('phase').options) o.disabled = false;
  }
  function change(id, refit = true) {
    if (S.scene !== lastScene) { cam.pitch = S.scene === 'catalogue' ? 0.6 : 0.95; cam.yaw = 0.55; lastScene = S.scene; refit = true; S.assemble = 1; S.playing = false; $('play').textContent = 'Watch it assemble'; S.selected = -1; $('pickInfo').textContent = ''; }
    if (id === 'preset' && PRESETS[S.preset]) { const [s, r, w, h] = PRESETS[S.preset]; S.sides = s; S.radius = r; S.wall = w; S.layers = h; S.phase = 0; S.stack = 'abc'; S.explode = 0; S.rotate = false; }
    else if (['sides', 'radius', 'wall', 'layers', 'stack', 'phase', 'rotate'].includes(id) && S.scene === 'designer') S.preset = '';
    syncControls(); if (refit) needFit = true; build(); dirty = true; writeUrl();
  }
  function writeUrl() {
    if (embed) return;
    const q = new URLSearchParams({ scene: S.scene, layers: S.layers, phase: S.phase, colour: S.colour });
    if (S.explode) q.set('explode', S.explode.toFixed(2)); if (S.rotate) q.set('rotate', '1'); if (!S.bridges) q.set('bridges', '0');
    if (S.scene === 'designer') { q.set('sides', S.sides); q.set('radius', S.radius); q.set('wall', S.wall); if (S.stack !== 'abc') q.set('stack', S.stack); if (!S.guides) q.set('guides', '0'); }
    if (S.scene === 'tube') q.set('tube', S.tubeSize); if (S.scene === 'catalogue') q.set('shape', S.shape);
    history.replaceState(null, '', '?' + q.toString());
  }
  const bind = (id, key, kind) => $(id).addEventListener('input', e => { S[key] = kind === 'num' ? +e.target.value : kind === 'bool' ? e.target.checked : e.target.value; change(id, !['explode', 'colour', 'guides', 'detail', 'rotate', 'bridges'].includes(id)); });
  bind('scene', 'scene'); bind('layers', 'layers', 'num'); bind('phase', 'phase', 'num'); bind('explode', 'explode', 'num'); bind('rotate', 'rotate', 'bool'); bind('bridges', 'bridges', 'bool'); bind('tubeSize', 'tubeSize', 'num'); bind('sides', 'sides', 'num'); bind('radius', 'radius', 'num'); bind('wall', 'wall', 'num'); bind('stack', 'stack'); bind('shape', 'shape', 'num'); bind('colour', 'colour'); bind('guides', 'guides', 'bool'); bind('detail', 'detail'); bind('preset', 'preset');
  $('layers').addEventListener('input', () => { $('layersOut').textContent = S.layers; });
  $('assemble').addEventListener('input', e => { S.assemble = +e.target.value / 1000; S.playing = false; $('play').textContent = 'Watch it assemble'; dirty = true; });
  $('play').onclick = () => { if (S.playing) { S.playing = false; $('play').textContent = 'Watch it assemble'; } else { S.assemble = 0; S.playing = true; $('play').textContent = 'Pause'; } };
  $('top').onclick = () => { cam.pitch = Math.PI / 2 - 0.002; cam.yaw = 0; dirty = true; };
  $('side').onclick = () => { cam.pitch = 0.08; cam.yaw = 0; dirty = true; };
  $('iso').onclick = () => { cam.pitch = 0.95; cam.yaw = 0.55; dirty = true; };
  $('fitBtn').onclick = () => { needFit = true; build(); dirty = true; };
  $('snap').onclick = () => { render(false); const a = document.createElement('a'); a.download = `seabrick-${S.scene}.png`; a.href = canvas.toDataURL('image/png'); a.click(); };
  document.querySelectorAll('[data-scene]').forEach(b => b.addEventListener('click', () => { S.scene = b.dataset.scene; if (b.dataset.layers) S.layers = +b.dataset.layers; if (b.dataset.preset) { S.preset = b.dataset.preset; change('preset'); return; } change('scene'); }));
  $('openFull')?.setAttribute('href', 'builder.html?' + [...params].filter(([k]) => !['embed', 'bar', 'panel'].includes(k)).map(([k, v]) => k + '=' + encodeURIComponent(v)).join('&'));

  /* pointer navigation */
  const pointers = new Map(); let downAt = null;
  canvas.onpointerdown = e => { if (e.button > 2) return; e.preventDefault(); canvas.focus({ preventScroll: true }); pointers.set(e.pointerId, { x: e.clientX, y: e.clientY, mode: e.shiftKey || e.button !== 0 ? 'pan' : 'orbit' }); canvas.setPointerCapture(e.pointerId); downAt = [e.clientX, e.clientY, performance.now()]; };
  canvas.onpointermove = e => { if (!pointers.has(e.pointerId)) return; e.preventDefault(); const old = [...pointers.values()], p = pointers.get(e.pointerId), dx = e.clientX - p.x, dy = e.clientY - p.y; pointers.set(e.pointerId, { ...p, x: e.clientX, y: e.clientY }); if (pointers.size === 2) { const nx = [...pointers.values()], mid = v => [(v[0].x + v[1].x) / 2, (v[0].y + v[1].y) / 2], len = v => Math.hypot(v[0].x - v[1].x, v[0].y - v[1].y), a = mid(old), b = mid(nx); pan(b[0] - a[0], b[1] - a[1]); if (len(old) > 1 && len(nx) > 1) dolly(Math.log(len(old) / len(nx))); } else if (p.mode === 'pan') pan(dx, dy); else orbit(dx, dy); };
  canvas.onpointerup = e => { pointers.delete(e.pointerId); if (canvas.hasPointerCapture(e.pointerId)) canvas.releasePointerCapture(e.pointerId); if (downAt && Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) < 4 && performance.now() - downAt[2] < 400 && e.button === 0) { const p = pickAt(e.clientX, e.clientY); S.selected = p ? p.id : -1; $('pickInfo').textContent = p ? `${D.meshes[p.mesh].label} · course ${p.layer + 1}${p.phase !== undefined ? ' (' + 'ABC'[p.phase] + ')' : ''}${p.flip ? ' · turned over' : ''}${p.cladding ? ' · cladding' : ''}${p.span === 2 ? ' · spans two courses' : ''}. ${D.meshes[p.mesh].role}.` : ''; dirty = true; } downAt = null; };
  canvas.onpointercancel = canvas.onpointerup; canvas.oncontextmenu = e => e.preventDefault();
  canvas.onwheel = e => { e.preventDefault(); dolly(e.deltaY * (e.deltaMode === 1 ? 16 : 1) * 0.0012); };
  canvas.onkeydown = e => { const k = e.key; const step = e.shiftKey ? 80 : 30; if (k === 'ArrowLeft') pan(-step, 0); else if (k === 'ArrowRight') pan(step, 0); else if (k === 'ArrowUp') pan(0, -step); else if (k === 'ArrowDown') pan(0, step); else if (k === '+' || k === '=') dolly(-0.15); else if (k === '-') dolly(0.15); else if (k === 'f' || k === 'F') $('fitBtn').click(); else return; e.preventDefault(); };

  window.seabrickBuilder = { state: S, set(k, v) { S[k] = v; change(k); }, count: () => current.length };
  lastScene = ''; change('scene'); if (params.get('play') === '1') $('play').click();
  requestAnimationFrame(frame);
  $('loading').hidden = true;
})();
