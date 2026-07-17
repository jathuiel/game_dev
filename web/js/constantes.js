"use strict";

// ==================== CONSTANTES ====================
const T = 32;                    // tamanho do tile em px de mundo (escala 2x da v1)
const MAP_W = 40, MAP_H = 24;    // tiles
const MAP_PX_W = MAP_W * T, MAP_PX_H = MAP_H * T; // 1280x768
const VIEW_W = 480, VIEW_H = 220; // area visivel = canvas, 1:1 (sem scale)
const SPEED = 240;                // px de mundo / s
const CW = 20, CH = 24;           // celula dos colecionaveis (nao usa T)

// ==================== HASH (replica nrand do tools/gerar_tilesets.py) ====================
function nrand(x, y, s) {
  let n = (Math.imul(x, 374761393) + Math.imul(y, 668265263) + Math.imul(s, 1442695041)) >>> 0;
  n = Math.imul(n ^ (n >>> 13), 1274126177) >>> 0;
  return (((n ^ (n >>> 16)) >>> 0) % 1000) / 1000;
}
// ponytail: checagem minima contra valores conhecidos gerados pelo script python
console.assert(Math.abs(nrand(5, 5, 99) - 0.579) < 1e-9, "nrand hash divergiu do python");
console.assert(Math.abs(nrand(19, 11, 99) - 0.909) < 1e-9, "nrand hash divergiu do python");
