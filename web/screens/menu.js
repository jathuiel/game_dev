document.getElementById("screen-menu").innerHTML = `
<button class="wood-btn" style="left:60px;top:100px;width:220px;height:44px" onclick="if(assetsReady) showScreen('jogo')"></button>
<button class="wood-btn" style="left:60px;top:158px;width:220px;height:44px" onclick="showScreen('config')"></button>
<button class="wood-btn" style="left:60px;top:216px;width:220px;height:44px" onclick="showScreen('personagem')"></button>
`;
