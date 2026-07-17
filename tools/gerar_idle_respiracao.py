#!/usr/bin/env python3
"""
Gera ciclos verticais simples (idle/respiracao, pulo/comemorar) para
personagem pixel art: desloca tronco+cabeca, mantendo pernas/pes fixos.
"""
from pathlib import Path

from PIL import Image

ASSETS = Path(r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\assets\personagem")


def gerar_ciclo_vertical(pose_name, prefix, shifts, ordem_strip=None, cut_ratio=0.62):
    """A partir de uma pose parada (pes na base) em ASSETS/pose_name, gera um
    frame por valor em `shifts` (tronco+cabeca deslocam esse tanto, +desce/
    -sobe; pernas fixas) + strip com `ordem_strip` (indices em `shifts`,
    default = todos em ordem). Salva em ASSETS/{prefix}_N.png e
    {prefix}_strip.png."""
    img_original = Image.open(ASSETS / pose_name).convert("RGBA")
    width, height = img_original.size
    print(f"--- {prefix} (pose={pose_name}) --- imagem {width}x{height}")

    bbox = img_original.split()[3].getbbox()
    if not bbox:
        raise ValueError(f"{pose_name}: nenhum pixel nao-transparente encontrado")
    bbox_top, bbox_bottom = bbox[1], bbox[3]
    cut_y = bbox_top + int(cut_ratio * (bbox_bottom - bbox_top))
    print(f"cut_y calculado: {cut_y}")

    def gerar_frame(shift):
        # shift negativo (sobe) precisa de um crop mais alto: senao o topo
        # deslocado para cima termina antes de alcancar a base fixa (cut_y) e
        # deixa uma lacuna transparente ali. Estende o crop pra baixo pelo
        # mesmo tanto que ele vai subir, usando conteudo real da imagem
        # original nessa faixa (a cintura, que nao se move).
        crop_bottom = cut_y + max(0, -shift)
        img2 = img_original.copy()
        pixels = img2.load()
        for y in range(cut_y):  # zera so ate cut_y (fixo) — a faixa extra
            for x in range(width):  # ate crop_bottom fica com o conteudo
                pixels[x, y] = (0, 0, 0, 0)  # original, coberta pelo crop maior
        topo = img_original.crop((0, 0, width, crop_bottom))
        img2.alpha_composite(topo, (0, shift))
        return img2

    frames = [gerar_frame(s) for s in shifts]
    for i, f in enumerate(frames, 1):
        f.save(ASSETS / f"{prefix}_{i}.png")
        print(f"salvo: {prefix}_{i}.png")

    idx_strip = ordem_strip if ordem_strip is not None else list(range(len(frames)))
    strip = Image.new("RGBA", (width * len(idx_strip), height), (0, 0, 0, 0))
    for i, idx in enumerate(idx_strip):
        strip.paste(frames[idx], (i * width, 0))
    strip_path = ASSETS / f"{prefix}_strip.png"
    strip.save(strip_path)
    print(f"salvo: {prefix}_strip.png ({strip.width}x{strip.height})")
    return frames


def gerar_idle(pose_name, prefix, cut_ratio=0.62):
    """Respiracao: 3 frames (desce 0/2/4px), strip 1-2-3-2."""
    return gerar_ciclo_vertical(pose_name, prefix, shifts=(0, 2, 4), ordem_strip=(0, 1, 2, 1), cut_ratio=cut_ratio)


def main():
    gerar_idle("pad_frame_1.png", "idle")


if __name__ == "__main__":
    main()
