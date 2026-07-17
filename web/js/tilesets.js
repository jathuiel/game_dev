"use strict";

// ==================== TILESETS ====================
// ordem exata das listas em tools/gerar_tilesets.py e tools/gerar_tileset_industrial.py
const CENARIO_ORDER = [
  "grama", "grama_tufos", "grama_flores", "grama_alta", "terra", "terra_pedras", "areia", "piso_pedra",
  "caminho_NW", "caminho_N", "caminho_NE", "agua_NW", "agua_N", "agua_NE", "penhasco_topo", "ponte_h",
  "caminho_W", "caminho_C", "caminho_E", "agua_W", "agua_C", "agua_E", "penhasco_face", "ponte_v",
  "caminho_SW", "caminho_S", "caminho_SE", "agua_SW", "agua_S", "agua_SE", "penhasco_base", "agua_brilho",
  "arvore_TL", "arvore_TR", "arbusto", "grama_sombra", "penhasco_ao", null, null, null,
  "arvore_BL", "arvore_BR", null, null, null, null, null, null,
];
const OBST_ORDER = [
  "pedra", "pedregulho", "toco", "espinhos", "caixote",
  "barril", "cerca_h", "cerca_v", "placa", "arbusto_espinhoso",
];
const INDUSTRIAL_ORDER = [
  "piso_metal", "piso_xadrez", "piso_metal_oleo", "piso_rachado", "concreto", "concreto_faixa", "parede_topo", "parede_face",
  "parede_base", "fachada_janela", "porta_L", "porta_R", "cano_h", "cano_v", "cano_curva_NE", "cano_curva_NW",
  "cano_curva_SE", "cano_curva_SW", "maquina_TL", "maquina_TR", "maquina_BL", "maquina_BR", "esteira_1", "esteira_2",
  "tanque_T", "tanque_B", "chamine_T", "chamine_M", "chamine_B", "barril_metal", "cerca_tela_h", "cerca_tela_v", "engrenagem",
  null, null, null, null, null, null, null,
];
function cell(order, name, cols) {
  const i = order.indexOf(name);
  return [(i % cols) * T, Math.floor(i / cols) * T];
}
function buildLookup(order, cols) {
  const map = {};
  order.forEach(name => { if (name) map[name] = cell(order, name, cols); });
  return map;
}
const CEN = buildLookup(CENARIO_ORDER, 8);
const OBS = buildLookup(OBST_ORDER, 5);
const IND = buildLookup(INDUSTRIAL_ORDER, 8);

const COLLECT_ORDER = ["chope_1", "chope_2", "budwise_1", "budwise_2", "hiniken_1", "hiniken_2"];
const COLLECT = {};
COLLECT_ORDER.forEach((name, i) => { COLLECT[name] = [(i % 6) * CW, Math.floor(i / 6) * CH]; });
