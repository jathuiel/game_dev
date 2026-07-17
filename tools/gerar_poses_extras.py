"""Gera as poses/acoes que faltavam no heroi principal (Ze da Lata),
reaproveitando as 6 poses ja existentes na spritesheet de referencia original
(pad_frame_1..6) em vez de pedir arte nova:

- idle_lado: ciclo de respiracao a partir de pad_frame_6 (perfil parado,
  ja usado hoje como pose lateral estatica na tela de personagem).
- pad_view_3_4: pose unica, pad_frame_6 tambem — e a pose mais proxima de
  3/4 que existe (corpo de perfil, cabeca quase de frente); nao ha vista 3/4
  real desenhada, entao esta e uma aproximacao, nao uma projecao correta.
- comemorar: ciclo de "pulinho" (hop) a partir de pad_frame_1 (de frente,
  segurando a lata) — shifts maiores e negativos (sobe) que o idle, pra dar
  sensacao de acao rapida e repetivel, sem sintetizar um braco erguido do
  zero (arriscado geometricamente).
- vitoria: pose unica, pad_frame_5 (pulo com a lata erguida, ja existe na
  spritesheet original, hoje so usada no mockup do menu) — pose completa e
  distinta de comemorar, sem precisar sintetizar nada.
"""
from pathlib import Path

from PIL import Image

import gerar_idle_respiracao as gir

ASSETS = Path(r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\assets\personagem")


def main():
    gir.gerar_idle("pad_frame_6.png", "idle_lado")

    Image.open(ASSETS / "pad_frame_6.png").save(ASSETS / "pad_view_3_4.png")
    print("salvo: pad_view_3_4.png (aproximacao a partir de pad_frame_6)")

    gir.gerar_ciclo_vertical(
        "pad_frame_1.png", "comemorar",
        shifts=(0, -4, -7, -4), ordem_strip=(0, 1, 2, 3),
    )

    Image.open(ASSETS / "pad_frame_5.png").save(ASSETS / "pad_vitoria.png")
    print("salvo: pad_vitoria.png (pad_frame_5, pulo com lata erguida)")


if __name__ == "__main__":
    main()
