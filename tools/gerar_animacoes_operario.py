"""Gera as animacoes do Super Operario (walk front/back, idle frente/lado)
reaproveitando 100% da logica generica ja existente para o heroi principal —
so aponta os modulos para assets/personagem2 antes de chamar as mesmas
funcoes (gerar_view, gerar_idle).
"""
from pathlib import Path

from PIL import Image

import gerar_ciclo_caminhada as gcc
import gerar_ciclos_verticais as gcv
import gerar_idle_respiracao as gir

ASSETS2 = Path(r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\assets\personagem2")


def gerar_walk_lateral():
    """Nao ha pose de 'passing' (pernas cruzadas no meio do passo) nem uma
    segunda pose de contato na folha de referencia, so uma pose de CORRIDA
    (ANDANDO, uma perna claramente no ar) — mesma limitacao que o heroi 1 tem
    hoje (walk_2/walk_4 la sao pre-existentes, nao gerados por script).

    A tecnica de troca de pernas por translacao (gcc.make_walk3) foi feita
    para passadas PLANAS, onde as duas pernas tocam a mesma linha de base —
    tentada aqui (com e sem realinhamento de Y), sempre deixa a perna
    trocada com uma forma torta/flutuante, porque a perna "no ar" da pose de
    corrida nao vira uma perna reta apoiada so por deslocamento.

    Fallback mais simples e honesto: usa a MESMA pose real (pad_andando) em
    todos os frames de contato, variando so um bob vertical leve (como o
    idle), e pad_lado como quadro neutro — ciclo mais discreto que o do
    heroi 1, mas sem artefatos. Melhora real exigiria uma segunda pose de
    referencia (outra perna a frente) fornecida pelo usuario."""
    gcc.ASSETS = ASSETS2
    walk1 = gcc.load("pad_andando.png")
    walk3 = Image.new("RGBA", walk1.size, (0, 0, 0, 0))
    walk3.paste(walk1, (0, -2), walk1)  # leve bob pra diferenciar do frame 1

    neutro = Image.open(ASSETS2 / "pad_lado.png").convert("RGBA")
    frames = {"walk_1": walk1, "walk_2": neutro, "walk_3": walk3, "walk_4": neutro}
    for name, img in frames.items():
        img.save(ASSETS2 / f"{name}.png")

    strip = Image.new("RGBA", (gcc.W * 4, gcc.H), (0, 0, 0, 0))
    for i, name in enumerate(["walk_1", "walk_2", "walk_3", "walk_4"]):
        strip.paste(frames[name], (i * gcc.W, 0))
    strip.save(ASSETS2 / "walk_strip_debug.png")


def main():
    gcv.ASSETS = ASSETS2
    gcv.gerar_view("pad_frente.png", "front")
    gcv.gerar_view("pad_costas.png", "back")

    gir.ASSETS = ASSETS2
    gir.gerar_idle("pad_frente.png", "idle")
    gir.gerar_idle("pad_lado.png", "idle_lado")

    gerar_walk_lateral()

    print("Animacoes do Super Operario salvas em:", ASSETS2)


if __name__ == "__main__":
    main()
