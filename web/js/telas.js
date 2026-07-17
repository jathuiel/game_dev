"use strict";

// ==================== TELAS (menu / config / personagem) ====================
// markup de cada tela: ver screens/*.js (rodam antes deste script e ja
// preenchem os containers #screen-*); handlers inline (onclick) neles
// referenciam as funcoes hoisted abaixo, entao funcionam normalmente
let screen = "menu"; // "menu" | "config" | "personagem" | "jogo"
let assetsReady = false;
const settings = { music: 70, sound: 50, vibration: true, lang: 0 };
const LANGS = ["PT-BR", "EN"]; // ponytail: so guarda a preferencia, HUD do jogo continua fixo em PT-BR

function showScreen(name) {
  screen = name;
  document.getElementById("game").classList.toggle("hidden", name !== "jogo");
  ["menu", "config", "personagem"].forEach(s => document.getElementById("screen-" + s).classList.toggle("hidden", name !== s));
  resize();
}

function refreshHeroUI() {
  const other = 1 - activeHero;
  document.getElementById("hero-center-img").src = `../assets/${HERO_DIRS[activeHero]}/16bit/${HERO_PREVIEW[activeHero]}.png`;
  document.getElementById("hero-side-img").src = `../assets/${HERO_DIRS[other]}/16bit/${HERO_PREVIEW[other]}.png`;
  document.getElementById("hero-name").textContent = HERO_NAMES[activeHero];
}
function trocarHeroi(dir) { // so 2 herois -> alternar cobre os dois sentidos
  activeHero = (activeHero + dir + 2) % 2;
  refreshHeroUI();
}

function toggleVibracao() {
  settings.vibration = !settings.vibration;
  document.getElementById("cfg-vib").classList.toggle("on", settings.vibration);
  if (settings.vibration && navigator.vibrate) navigator.vibrate(40);
}
function cycleIdioma(dir) {
  settings.lang = (settings.lang + dir + LANGS.length) % LANGS.length;
  document.getElementById("cfg-lang").textContent = LANGS[settings.lang];
}
