"use strict";

// ==================== ENTIDADES ====================
const player = { x: 200, y: 384, vx: 0, vy: 0, moving: false, dir: "down", facingLeft: false, action: null, actionUntil: 0 };
const COMEMORAR_DUR = 0.6; // segundos que a acao de comemorar fica tocando apos coletar um item
const animClock = { t: 0 };

function feetBox(px, py) { return { x: px - 12, y: py - 6, w: 24, h: 12 }; }
function collides(px, py) {
  const b = feetBox(px, py);
  const x0 = Math.floor(b.x / T), x1 = Math.floor((b.x + b.w - 0.01) / T);
  const y0 = Math.floor(b.y / T), y1 = Math.floor((b.y + b.h - 0.01) / T);
  for (let ty = y0; ty <= y1; ty++) for (let tx = x0; tx <= x1; tx++) if (isSolidTile(tx, ty)) return true;
  return false;
}
function checkCollect() {
  const b = feetBox(player.x, player.y);
  COLECIONAVEIS.forEach(it => {
    if (it.coletado) return;
    const rx0 = it.tx * T, ry0 = it.ty * T, rx1 = rx0 + T, ry1 = ry0 + T;
    if (b.x < rx1 && b.x + b.w > rx0 && b.y < ry1 && b.y + b.h > ry0) {
      it.coletado = true; counts[it.tipo]++; collectedTotal++;
      if (collectedTotal === COLECIONAVEIS.length) {
        faseCompleta = true;
        player.action = "vitoria"; // fica ate o fim da fase, nao expira
      } else {
        player.action = "comemorando";
        player.actionUntil = animClock.t + COMEMORAR_DUR;
      }
    }
  });
}
