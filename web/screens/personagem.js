document.getElementById("screen-personagem").innerHTML = `
<div class="title" style="font-size:18px;">ESCOLHA SEU HERÓI</div>

<div class="wood-panel gold" style="position:absolute;left:245px;top:60px;width:150px;height:170px;overflow:hidden;">
  <img id="hero-center-img" src="../assets/personagem/16bit/pad_view_3_4.png" style="position:absolute;left:11px;top:16px;width:128px;height:144px;image-rendering:pixelated;">
</div>
<span class="arrow" style="position:absolute;left:200px;top:132px;font-size:26px;" onclick="trocarHeroi(-1)">&lt;</span>
<span class="arrow" style="position:absolute;left:405px;top:132px;font-size:26px;" onclick="trocarHeroi(1)">&gt;</span>

<div class="wood-panel hero-side" style="position:absolute;left:435px;top:90px;width:100px;height:120px;overflow:hidden;" onclick="trocarHeroi(1)">
  <img id="hero-side-img" src="../assets/personagem2/16bit/pad_tres_quartos.png" style="position:absolute;left:2px;top:6px;width:96px;height:108px;image-rendering:pixelated;">
</div>

<div class="wood-panel" id="hero-name" style="position:absolute;left:230px;top:240px;width:180px;height:26px;text-align:center;line-height:26px;font-size:12px;">ZÉ DA LATA</div>

<button class="wood-btn" style="left:230px;top:322px;width:180px;height:30px;" onclick="showScreen('menu')">CONFIRMAR</button>
`;
