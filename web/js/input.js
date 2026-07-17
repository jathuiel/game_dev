"use strict";

// ==================== INPUT: teclado ====================
const keys = new Set();
window.addEventListener("keydown", e => keys.add(e.key.toLowerCase()));
window.addEventListener("keyup", e => keys.delete(e.key.toLowerCase()));
function keyboardVector() {
  if (screen !== "jogo") return { x: 0, y: 0, mag: 0 };
  let dx = 0, dy = 0;
  if (keys.has("a") || keys.has("arrowleft")) dx -= 1;
  if (keys.has("d") || keys.has("arrowright")) dx += 1;
  if (keys.has("w") || keys.has("arrowup")) dy -= 1;
  if (keys.has("s") || keys.has("arrowdown")) dy += 1;
  const len = Math.hypot(dx, dy);
  return len > 0 ? { x: dx / len, y: dy / len, mag: 1 } : { x: 0, y: 0, mag: 0 };
}

// ==================== INPUT: joystick virtual ====================
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
ctx.imageSmoothingEnabled = false;

const joy = { active: false, pointerId: null, base: { x: 0, y: 0 }, thumb: { x: 0, y: 0 }, vec: { x: 0, y: 0, mag: 0 } };
const DEAD = 8, MAXR = 40;

function canvasPos(e) {
  const r = canvas.getBoundingClientRect();
  return { x: (e.clientX - r.left) / r.width * canvas.width, y: (e.clientY - r.top) / r.height * canvas.height };
}
canvas.addEventListener("pointerdown", e => {
  if (screen !== "jogo") return;
  const p = canvasPos(e);
  if (p.x >= canvas.width / 2) return; // so metade esquerda
  joy.active = true; joy.pointerId = e.pointerId;
  joy.base = { x: p.x, y: p.y }; joy.thumb = { x: p.x, y: p.y }; joy.vec = { x: 0, y: 0, mag: 0 };
  canvas.setPointerCapture(e.pointerId);
});
canvas.addEventListener("pointermove", e => {
  if (!joy.active || e.pointerId !== joy.pointerId) return;
  const p = canvasPos(e);
  const dx = p.x - joy.base.x, dy = p.y - joy.base.y;
  const dist = Math.hypot(dx, dy);
  if (dist < DEAD) { joy.vec = { x: 0, y: 0, mag: 0 }; joy.thumb = { x: joy.base.x, y: joy.base.y }; return; }
  const clamped = Math.min(dist, MAXR);
  const nx = dx / dist, ny = dy / dist;
  const mag = (clamped - DEAD) / (MAXR - DEAD);
  joy.vec = { x: nx * mag, y: ny * mag, mag };
  joy.thumb = { x: joy.base.x + nx * clamped, y: joy.base.y + ny * clamped };
});
function endJoy(e) {
  if (!joy.active || e.pointerId !== joy.pointerId) return;
  joy.active = false; joy.vec = { x: 0, y: 0, mag: 0 };
}
canvas.addEventListener("pointerup", endJoy);
canvas.addEventListener("pointercancel", endJoy);
