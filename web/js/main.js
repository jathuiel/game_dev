"use strict";

// ==================== LOOP ====================
function update(dt) {
  const kv = keyboardVector();
  const v = joy.active ? joy.vec : kv;
  player.moving = v.mag > 0;
  const speed = SPEED * v.mag;
  player.vx = v.x * speed; player.vy = v.y * speed;

  if (player.moving) {
    if (Math.abs(v.x) > Math.abs(v.y)) { player.dir = "side"; player.facingLeft = v.x < 0; }
    else player.dir = v.y < 0 ? "up" : "down";
  }

  const nx = player.x + player.vx * dt;
  if (!collides(nx, player.y)) player.x = nx;
  const ny = player.y + player.vy * dt;
  if (!collides(player.x, ny)) player.y = ny;
  player.x = Math.max(0, Math.min(MAP_PX_W, player.x));
  player.y = Math.max(0, Math.min(MAP_PX_H, player.y));

  animClock.t += dt;
  if (player.action === "comemorando" && animClock.t > player.actionUntil) player.action = null;
  checkCollect();

  camera.x = Math.max(0, Math.min(MAP_PX_W - VIEW_W, player.x - VIEW_W / 2));
  camera.y = Math.max(0, Math.min(MAP_PX_H - VIEW_H, player.y - VIEW_H / 2));
}

let last = 0;
function frame(ts) {
  const dt = Math.min(0.05, last ? (ts - last) / 1000 : 0);
  last = ts;
  if (screen === "jogo") {
    if (!canvas.clientWidth) resize(); // recupera do carregamento com painel 0x0
    update(dt);
    render();
  }
  requestAnimationFrame(frame);
}

// ==================== CANVAS/TELAS RESPONSIVO (letterbox) ====================
function resize() {
  const el = screen === "jogo" ? canvas : document.getElementById("screen-" + screen);
  const w = screen === "jogo" ? canvas.width : 640;
  const h = screen === "jogo" ? canvas.height : 360;
  const scale = Math.min(window.innerWidth / w, window.innerHeight / h);
  if (!isFinite(scale) || scale <= 0) return; // janela ainda sem layout (iframe/painel) — tenta de novo depois
  el.style.width = (w * scale) + "px";
  el.style.height = (h * scale) + "px";
}
window.addEventListener("resize", resize);
window.addEventListener("load", resize);
resize();

// ==================== START ====================
ready.then(() => {
  console.assert(assets.cenario.width === 8 * T, "tileset_cenario fora de escala");
  console.assert(assets.obstaculos.width === 5 * T, "tileset_obstaculos fora de escala");
  console.assert(assets.industrial.width === 8 * T, "tileset_industrial fora de escala");
  console.assert(heroAssets[0].walk.width === 4 * 64, "walk_strip fora de escala");
  console.assert(heroAssets[0].idleLado.width === 4 * 64, "idle_lado_strip fora de escala");
  console.assert(heroAssets[0].comemorar.width === 4 * 64, "comemorar_strip fora de escala");
  buildVignette();
  bakeTerrain();
  assetsReady = true;
  requestAnimationFrame(frame);
});
