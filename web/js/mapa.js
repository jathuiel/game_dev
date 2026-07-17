"use strict";

// ==================== MAPA ====================
// biomas: x<20 verde (oeste), x>=20 industrial (leste)
const LAGO_VERDE = { // 3x3 em (14..16, 3..5)
  "14,3": "agua_NW", "15,3": "agua_N", "16,3": "agua_NE",
  "14,4": "agua_W", "15,4": "agua_brilho", "16,4": "agua_E",
  "14,5": "agua_SW", "15,5": "agua_S", "16,5": "agua_SE",
};
const ARVORES = [[2, 3], [7, 4], [4, 9], [9, 13], [16, 15], [3, 19]]; // topo-esquerdo, 2x2, so bioma verde
const ARBUSTOS = [[11, 5], [8, 9], [6, 15], [13, 17]]; // decoracao nao-solida
const OBSTACULOS = [ // tile -> nome no tileset_obstaculos, todos solidos, so bioma verde
  { x: 3, y: 6, n: "pedra" }, { x: 9, y: 3, n: "espinhos" }, { x: 6, y: 7, n: "toco" },
  { x: 12, y: 8, n: "caixote" }, { x: 13, y: 8, n: "barril" }, { x: 5, y: 8, n: "placa" },
  { x: 18, y: 6, n: "pedregulho" }, { x: 18, y: 9, n: "arbusto_espinhoso" },
  { x: 4, y: 16, n: "cerca_h" }, { x: 5, y: 16, n: "cerca_h" },
  { x: 10, y: 18, n: "pedra" }, { x: 15, y: 20, n: "toco" },
];

// galpao industrial: overrides de tile por posicao, so bioma industrial (x>=20)
const INDUSTRIAL_OVERRIDES = {};
function ov(x, y, name) { INDUSTRIAL_OVERRIDES[x + "," + y] = name; }
for (let x = 22; x <= 30; x++) { ov(x, 2, "parede_topo"); ov(x, 3, "parede_face"); ov(x, 4, "parede_base"); }
ov(24, 3, "fachada_janela"); ov(27, 3, "porta_L"); ov(28, 3, "porta_R");
ov(32, 6, "tanque_T"); ov(32, 7, "tanque_B");
ov(34, 5, "chamine_T"); ov(34, 6, "chamine_M"); ov(34, 7, "chamine_B");
ov(22, 7, "maquina_TL"); ov(23, 7, "maquina_TR"); ov(22, 8, "maquina_BL"); ov(23, 8, "maquina_BR");
for (let x = 25; x <= 28; x++) ov(x, 8, "esteira_1");
for (let x = 22; x <= 25; x++) ov(x, 9, "cano_h");
ov(26, 9, "cano_curva_SE"); ov(26, 10, "cano_v");
for (let x = 30; x <= 32; x++) ov(x, 9, "barril_metal");
for (let x = 20; x <= 23; x++) ov(x, 14, "cerca_tela_h");
const PORTA = new Set(["porta_L", "porta_R"]); // unicas celulas de estrutura NAO solidas

// piso/terreno da celula (SEM as estruturas industriais — essas sao camada por cima)
function baseTile(x, y) {
  const key = x + "," + y;
  if (LAGO_VERDE[key]) return LAGO_VERDE[key];
  if (y === 11) return x < 20 ? "caminho_N" : "concreto_faixa";
  if (y === 12) return x < 20 ? "caminho_S" : "concreto_faixa";
  if (x < 20) {
    if (y === 0) return "penhasco_face";
    if (y === 1) return "penhasco_base";
    const r = nrand(x, y, 99);
    return r < 0.7 ? "grama" : r < 0.85 ? "grama_tufos" : "grama_flores";
  }
  if (y === 2 || y === 21) return "concreto"; // faixas de concreto no leste
  const r = nrand(x, y, 99);
  if (r < 0.05) return "piso_metal_oleo";
  if (r < 0.13) return "piso_rachado";
  if (r < 0.28) return "piso_xadrez";
  return "piso_metal";
}

const solidSet = new Set(); // "x,y" das celulas solidas
for (let x = 0; x < 20; x++) { solidSet.add(x + ",0"); solidSet.add(x + ",1"); } // penhasco, so bioma verde
Object.keys(LAGO_VERDE).forEach(k => solidSet.add(k));
OBSTACULOS.forEach(o => solidSet.add(o.x + "," + o.y));
ARVORES.forEach(([ax, ay]) => { solidSet.add(ax + "," + (ay + 1)); solidSet.add((ax + 1) + "," + (ay + 1)); });
Object.entries(INDUSTRIAL_OVERRIDES).forEach(([k, v]) => { if (!PORTA.has(v)) solidSet.add(k); });
function isSolidTile(tx, ty) {
  if (tx < 0 || ty < 0 || tx >= MAP_W || ty >= MAP_H) return true;
  return solidSet.has(tx + "," + ty);
}

// ==================== COLECIONAVEIS ====================
const COLECIONAVEIS = [
  { tx: 2, ty: 6, tipo: "chope" }, { tx: 9, ty: 5, tipo: "chope" }, { tx: 17, ty: 4, tipo: "chope" },
  { tx: 6, ty: 10, tipo: "chope" }, { tx: 12, ty: 4, tipo: "chope" }, { tx: 3, ty: 14, tipo: "chope" },
  { tx: 14, ty: 18, tipo: "chope" },
  { tx: 36, ty: 3, tipo: "budwise" }, { tx: 25, ty: 5, tipo: "budwise" }, { tx: 37, ty: 8, tipo: "budwise" },
  { tx: 29, ty: 13, tipo: "budwise" },
  { tx: 24, ty: 6, tipo: "hiniken" }, { tx: 33, ty: 9, tipo: "hiniken" }, { tx: 27, ty: 10, tipo: "hiniken" },
].map(it => ({ ...it, coletado: false }));
// ponytail: checagem barata contra o bug mais provavel de dado hand-authored - item nascendo dentro de parede
COLECIONAVEIS.forEach(it => console.assert(!isSolidTile(it.tx, it.ty), "colecionavel em tile solido: " + it.tx + "," + it.ty));

const TOTALS = { chope: 0, budwise: 0, hiniken: 0 };
COLECIONAVEIS.forEach(it => TOTALS[it.tipo]++);
const counts = { chope: 0, budwise: 0, hiniken: 0 };
let collectedTotal = 0, faseCompleta = false;
