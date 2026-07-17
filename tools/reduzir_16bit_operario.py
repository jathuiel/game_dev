"""Reduz os frames do Super Operario (assets/personagem2) para 64x72,
reaproveitando o pipeline generico de reduzir_16bit.py (paleta compartilhada,
strips, poses avulsas). Sem checagem de cor (nao ha regra de negocio tipo a
lata verde do heroi principal).

comemorar_strip/vitoria_strip tem so 1 celula: a folha de referencia so trouxe
1 frame por pose para essas duas acoes (sem ciclo de animacao) — funcionam
como pose estatica no jogo; ganhar mais frames exigiria mais poses de
referencia do usuario.
"""
from pathlib import Path

import reduzir_16bit as r16

ASSETS2 = Path(r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\assets\personagem2")
OUT2 = ASSETS2 / "16bit"

FRAMES = (
    ["pad_frente", "pad_lado", "pad_costas", "pad_tres_quartos", "pad_andando",
     "pad_comemorando", "pad_vitoria"]
    + [f"idle_{i}" for i in range(1, 4)]
    + [f"idle_lado_{i}" for i in range(1, 4)]
    + [f"walk_{i}" for i in range(1, 5)]
    + [f"walk_front_{i}" for i in range(1, 5)]
    + [f"walk_back_{i}" for i in range(1, 5)]
)
STRIPS = {
    "idle_strip": ["idle_1", "idle_2", "idle_3", "idle_2"],
    "idle_lado_strip": ["idle_lado_1", "idle_lado_2", "idle_lado_3", "idle_lado_2"],
    "walk_strip": ["walk_1", "walk_2", "walk_3", "walk_4"],
    "walk_front_strip": ["walk_front_1", "walk_front_2", "walk_front_3", "walk_front_4"],
    "walk_back_strip": ["walk_back_1", "walk_back_2", "walk_back_3", "walk_back_4"],
    "comemorar_strip": ["pad_comemorando"],
    "vitoria_strip": ["pad_vitoria"],
}
# poses avulsas p/ mockups de UI (tela de personagem, menu)
UI_POSES = ["pad_frente", "pad_lado", "pad_tres_quartos"]


def main():
    r16.reduzir(ASSETS2, OUT2, FRAMES, STRIPS, singles=UI_POSES)


if __name__ == "__main__":
    main()
