"use strict";

// ==================== ASSETS ====================
function loadImg(src) { return new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = src; }); }
const assets = {};

// dois herois jogaveis (tela Personagem escolhe qual fica ativo); mesmos
// nomes de strip nos dois diretorios, so o dir muda
const HERO_DIRS = ["personagem", "personagem2"];
const HERO_NAMES = ["ZÉ DA LATA", "SUPER OPERÁRIO"];
const HERO_PREVIEW = ["pad_view_3_4", "pad_tres_quartos"];
const STRIP_FILES = { walk: "walk_strip", idle: "idle_strip", idleLado: "idle_lado_strip", walkFront: "walk_front_strip", walkBack: "walk_back_strip", comemorar: "comemorar_strip", vitoria: "vitoria_strip" };
let activeHero = 0;
const heroAssets = [{}, {}];
const heroLoads = HERO_DIRS.flatMap((dir, hi) =>
  Object.entries(STRIP_FILES).map(([key, file]) =>
    loadImg(`../assets/${dir}/16bit/${file}.png`).then(img => { heroAssets[hi][key] = img; })));

const ready = Promise.all([
  loadImg("../assets/tileset_cenario.png").then(i => assets.cenario = i),
  loadImg("../assets/tileset_obstaculos.png").then(i => assets.obstaculos = i),
  loadImg("../assets/tileset_industrial.png").then(i => assets.industrial = i),
  loadImg("../assets/colecionaveis_strip.png").then(i => assets.collect = i),
  ...heroLoads,
]);

// terreno pre-renderizado numa vez (mapa e estatico)
let terrainCanvas;
function bakeTerrain() {
  terrainCanvas = document.createElement("canvas");
  terrainCanvas.width = MAP_PX_W; terrainCanvas.height = MAP_PX_H;
  const c = terrainCanvas.getContext("2d");
  c.imageSmoothingEnabled = false;
  for (let y = 0; y < MAP_H; y++) for (let x = 0; x < MAP_W; x++) {
    const name = baseTile(x, y);
    const west = x < 20;
    const [sx, sy] = (west ? CEN : IND)[name];
    c.drawImage(west ? assets.cenario : assets.industrial, sx, sy, T, T, x * T, y * T, T, T);
  }
  // camada de estruturas industriais POR CIMA do piso (muitas tem fundo transparente)
  Object.entries(INDUSTRIAL_OVERRIDES).forEach(([k, name]) => {
    const [x, y] = k.split(",").map(Number);
    const [sx, sy] = IND[name];
    c.drawImage(assets.industrial, sx, sy, T, T, x * T, y * T, T, T);
  });
  ARBUSTOS.forEach(([x, y]) => { const [sx, sy] = CEN["arbusto"]; c.drawImage(assets.cenario, sx, sy, T, T, x * T, y * T, T, T); });
}

// vinheta + luz quente, gerada uma vez
let vignette;
function buildVignette() {
  vignette = document.createElement("canvas");
  vignette.width = VIEW_W; vignette.height = VIEW_H;
  const v = vignette.getContext("2d");
  const g = v.createRadialGradient(VIEW_W / 2, VIEW_H / 2, 0, VIEW_W / 2, VIEW_H / 2, Math.max(VIEW_W, VIEW_H) * 0.62);
  g.addColorStop(0, "rgba(20,15,30,0)");
  g.addColorStop(1, "rgba(20,15,30,0.45)");
  v.fillStyle = g; v.fillRect(0, 0, VIEW_W, VIEW_H);
  v.fillStyle = "rgba(255,176,96,0.06)";
  v.fillRect(0, 0, VIEW_W, VIEW_H);
}
