"use strict";

// ==================== RENDER ====================
const camera = { x: 0, y: 0 };

function drawShadow(cx, footY, w, h) {
  ctx.save();
  ctx.fillStyle = "rgba(0,0,0,0.28)";
  ctx.beginPath();
  ctx.ellipse(cx - camera.x, footY - camera.y, w / 2, h / 2, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawSprite(img, sx, sy, worldX, worldY, mirror) {
  const dx = worldX - camera.x, dy = worldY - camera.y;
  ctx.save();
  if (mirror) { ctx.translate(dx, dy); ctx.scale(-1, 1); ctx.drawImage(img, sx, sy, 64, 72, -32, -72, 64, 72); }
  else ctx.drawImage(img, sx, sy, 64, 72, dx - 32, dy - 72, 64, 72);
  ctx.restore();
}

function drawPlayer() {
  drawShadow(player.x, player.y, 28, 10);
  const t = animClock.t;
  const hero = heroAssets[activeHero];
  if (player.action === "comemorando") {
    const f = Math.floor(t * 3) % 4; // 3fps cravado (fator fixo, nao ajustado por olho)
    drawSprite(hero.comemorar, f * 64, 0, player.x, player.y, player.facingLeft);
  } else if (player.action === "vitoria") {
    drawSprite(hero.vitoria, 0, 0, player.x, player.y, false); // pose unica
  } else if (player.dir === "side" && player.moving) {
    const f = Math.floor(t * 8) % 4;
    drawSprite(hero.walk, f * 64, 0, player.x, player.y, player.facingLeft);
  } else if (player.dir === "up" && player.moving) {
    const f = Math.floor(t * 8) % 4;
    drawSprite(hero.walkBack, f * 64, 0, player.x, player.y, false);
  } else if (player.dir === "down" && player.moving) {
    const f = Math.floor(t * 8) % 4;
    drawSprite(hero.walkFront, f * 64, 0, player.x, player.y, false);
  } else if (player.dir === "up") {
    drawSprite(hero.walkBack, 1 * 64, 0, player.x, player.y, false); // frame neutro parado de costas
  } else if (player.dir === "side") {
    const f = Math.floor(t * 4) % 4;
    drawSprite(hero.idleLado, f * 64, 0, player.x, player.y, player.facingLeft);
  } else {
    const f = Math.floor(t * 4) % 4;
    drawSprite(hero.idle, f * 64, 0, player.x, player.y, false);
  }
}

function drawEntities() {
  const list = [];
  OBSTACULOS.forEach(o => list.push({
    footY: (o.y + 1) * T,
    draw: () => {
      drawShadow(o.x * T + T / 2, (o.y + 1) * T, 24, 10);
      const [sx, sy] = OBS[o.n];
      ctx.drawImage(assets.obstaculos, sx, sy, T, T, o.x * T - camera.x, o.y * T - camera.y, T, T);
    }
  }));
  ARVORES.forEach(([ax, ay]) => list.push({
    footY: (ay + 2) * T,
    draw: () => {
      const bl = CEN["arvore_BL"], br = CEN["arvore_BR"];
      ctx.drawImage(assets.cenario, bl[0], bl[1], T, T, ax * T - camera.x, (ay + 1) * T - camera.y, T, T);
      ctx.drawImage(assets.cenario, br[0], br[1], T, T, (ax + 1) * T - camera.x, (ay + 1) * T - camera.y, T, T);
    }
  }));
  COLECIONAVEIS.forEach(it => {
    if (it.coletado) return;
    list.push({
      footY: it.ty * T + T,
      draw: () => {
        drawShadow(it.tx * T + T / 2, it.ty * T + T, 14, 6);
        const frame = Math.floor(animClock.t * 3) % 2 === 0 ? "_1" : "_2";
        const [sx, sy] = COLLECT[it.tipo + frame];
        const dx = it.tx * T + (T - CW) / 2 - camera.x, dy = it.ty * T + (T - CH) / 2 - camera.y;
        ctx.drawImage(assets.collect, sx, sy, CW, CH, dx, dy, CW, CH);
      }
    });
  });
  list.push({ footY: player.y, draw: drawPlayer });
  list.sort((a, b) => a.footY - b.footY);
  list.forEach(e => e.draw());
}

function drawCanopy() {
  ARVORES.forEach(([ax, ay]) => {
    const tl = CEN["arvore_TL"], tr = CEN["arvore_TR"];
    ctx.drawImage(assets.cenario, tl[0], tl[1], T, T, ax * T - camera.x, ay * T - camera.y, T, T);
    ctx.drawImage(assets.cenario, tr[0], tr[1], T, T, (ax + 1) * T - camera.x, ay * T - camera.y, T, T);
  });
}

// ==================== HUD ====================
function drawHUD() {
  ctx.save();
  ctx.font = "16px monospace";
  ctx.textBaseline = "middle";
  ctx.lineWidth = 3;
  [["chope", "chope_1"], ["budwise", "budwise_1"], ["hiniken", "hiniken_1"]].forEach(([tipo, frame], i) => {
    const x = 8 + i * 100, y = 8, iw = CW * 1.2, ih = CH * 1.2;
    const [sx, sy] = COLLECT[frame];
    ctx.drawImage(assets.collect, sx, sy, CW, CH, x, y, iw, ih);
    const text = counts[tipo] + "/" + TOTALS[tipo];
    const tx = x + iw + 6, ty = y + ih / 2;
    ctx.strokeStyle = "rgba(0,0,0,0.8)"; ctx.strokeText(text, tx, ty);
    ctx.fillStyle = "#fff"; ctx.fillText(text, tx, ty);
  });
  ctx.restore();
  if (faseCompleta) drawFaseCompleta();
}
function drawFaseCompleta() {
  ctx.save();
  ctx.fillStyle = "rgba(0,0,0,0.5)";
  ctx.fillRect(0, 0, VIEW_W, VIEW_H);
  ctx.font = "bold 40px monospace";
  ctx.textAlign = "center"; ctx.textBaseline = "middle";
  ctx.lineWidth = 5; ctx.strokeStyle = "rgba(0,0,0,0.9)";
  ctx.strokeText("FASE COMPLETA!", VIEW_W / 2, VIEW_H / 2);
  ctx.fillStyle = "#ffd54a";
  ctx.fillText("FASE COMPLETA!", VIEW_W / 2, VIEW_H / 2);
  ctx.restore();
}

function drawJoystickUI() {
  if (!joy.active) return;
  ctx.save();
  ctx.fillStyle = "rgba(255,255,255,0.25)";
  ctx.beginPath(); ctx.arc(joy.base.x, joy.base.y, 40, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = "rgba(255,255,255,0.55)";
  ctx.beginPath(); ctx.arc(joy.thumb.x, joy.thumb.y, 18, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}

function render() {
  ctx.imageSmoothingEnabled = false;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(terrainCanvas, camera.x, camera.y, VIEW_W, VIEW_H, 0, 0, VIEW_W, VIEW_H);
  drawEntities();
  drawCanopy();
  ctx.drawImage(vignette, 0, 0);
  drawHUD();
  drawJoystickUI();
}
