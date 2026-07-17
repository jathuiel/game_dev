document.getElementById("screen-config").innerHTML = `
<div class="wood-panel" style="position:absolute;left:90px;top:30px;width:460px;height:290px;"></div>
<div class="title" style="font-size:16px;top:44px;">CONFIGURAÇÕES</div>

<div class="cfg-row" style="top:96px;">
  <span class="lbl">MÚSICA</span>
  <span class="ctrl"><input id="cfg-music" type="range" min="0" max="100" value="70" oninput="settings.music=+this.value"></span>
</div>
<div class="cfg-row" style="top:140px;">
  <span class="lbl">SOM</span>
  <span class="ctrl"><input id="cfg-sound" type="range" min="0" max="100" value="50" oninput="settings.sound=+this.value"></span>
</div>
<div class="cfg-row" style="top:184px;">
  <span class="lbl">VIBRAÇÃO</span>
  <span class="ctrl"><div id="cfg-vib" class="toggle-sw on" onclick="toggleVibracao()"><div class="knob"></div></div></span>
</div>
<div class="cfg-row" style="top:228px;">
  <span class="lbl">IDIOMA</span>
  <span class="ctrl choice-ctrl">
    <span class="arrow" onclick="cycleIdioma(-1)">&lt;</span>
    <span id="cfg-lang">PT-BR</span>
    <span class="arrow" onclick="cycleIdioma(1)">&gt;</span>
  </span>
</div>

<button class="wood-btn" style="left:230px;top:268px;width:180px;height:32px;" onclick="showScreen('menu')">VOLTAR</button>
`;
