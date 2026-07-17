"""Gera ciclos de caminhada DE FRENTE e DE COSTAS (4 frames cada) a partir das
poses paradas pad_frame_1 (frente) e pad_frame_3 (costas).

Sem componentes conectados: as pernas se tocam pela calca larga. Corte
geometrico abaixo de cut_y = topo_bbox + 0.80*altura_bbox -> perna ESQUERDA =
x < centro_x do bbox, perna DIREITA = x >= centro_x.

f1: perna esquerda levantada 7px, perna direita no chao, torso desce 2px (bob)
f2: pose neutra original, torso sobe 1px
f3: espelho de f1 (perna direita levantada, esquerda no chao, torso desce 2px)
f4: igual a f2

Remontagem: canvas transparente -> pernas (com translacao) -> alpha_composite
do torso (crop 0..cut_y+6 da pose original, com o bob) por cima, escondendo a
emenda com a sobreposicao de 6px. Depois, limpeza: nas linhas cut_y-4..cut_y+12
zera pixels opacos do resultado que sejam transparentes na pose original.
"""

from pathlib import Path

import numpy as np
from PIL import Image

ASSETS = Path(r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\assets\personagem")
W, H = 336, 380
LIFT = 7


def load(name):
    return Image.open(ASSETS / name).convert("RGBA")


def last_opaque_row(arr, x0=0, x1=W):
    """arr: array HxWx4. Ultima linha com algum pixel opaco na faixa [x0,x1)."""
    col = arr[:, x0:x1, 3]
    rows = np.where(col.max(axis=1) > 0)[0]
    return int(rows[-1]) if len(rows) else None


def split_legs(arr, cut_y, centro_x):
    """Retorna (leg_left, leg_right): arrays HxWx4 so com os pixels de cada
    perna (regiao y>=cut_y), na posicao original."""
    ys, xs = np.indices((H, W))
    region = (ys >= cut_y) & (arr[:, :, 3] > 0)
    mask_left = region & (xs < centro_x)
    mask_right = region & (xs >= centro_x)
    leg_left = np.where(mask_left[:, :, None], arr, 0).astype(np.uint8)
    leg_right = np.where(mask_right[:, :, None], arr, 0).astype(np.uint8)
    return leg_left, leg_right


def translate_up(leg_arr, dy):
    """Translada a perna dy pixels para cima e apaga linhas que fiquem abaixo
    de (ultima_linha_original_da_perna - dy) -- o pe recolhido nao flutua."""
    last_row = last_opaque_row(leg_arr)
    if last_row is None:
        return leg_arr.copy()
    limiar = last_row - dy
    out = np.zeros_like(leg_arr)
    out[0:H - dy, :, :] = leg_arr[dy:H, :, :]
    out[limiar + 1:, :, :] = 0
    return out


def torso_layer(original, cut_y, bob_dy):
    crop = original.crop((0, 0, W, cut_y + 6))
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.paste(crop, (0, bob_dy), crop)
    return canvas


def assemble(original_arr, original_img, cut_y, centro_x, lift_side, bob_dy):
    leg_left, leg_right = split_legs(original_arr, cut_y, centro_x)
    if lift_side == "left":
        leg_left = translate_up(leg_left, LIFT)
    elif lift_side == "right":
        leg_right = translate_up(leg_right, LIFT)
    legs_arr = leg_left + leg_right  # disjoint (particionadas por x), soma = uniao
    legs_img = Image.fromarray(legs_arr, "RGBA")

    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    frame.alpha_composite(legs_img)
    frame.alpha_composite(torso_layer(original_img, cut_y, bob_dy))
    return frame


def clean_seam(frame, original_arr, cut_y):
    farr = np.array(frame)
    y0, y1 = max(0, cut_y - 4), min(H, cut_y + 13)
    band = farr[y0:y1]
    erase = (band[:, :, 3] > 0) & (original_arr[y0:y1, :, 3] == 0)
    n = int(erase.sum())
    band[erase] = 0
    return Image.fromarray(farr, "RGBA"), n


def gerar_view(pose_name, prefix):
    original_img = load(pose_name)
    original_arr = np.array(original_img)
    bbox = original_img.getbbox()
    top, bottom = bbox[1], bbox[3]
    altura = bottom - top
    cut_y = top + int(0.80 * altura)
    centro_x = (bbox[0] + bbox[2]) / 2

    specs = [
        ("1", "left", 2),
        ("2", None, -1),
        ("3", "right", 2),
        ("4", None, -1),
    ]
    frames = {}
    print(f"--- {prefix} (pose={pose_name}) ---")
    print(f"bbox original = {bbox}  cut_y = {cut_y}  centro_x = {centro_x}")
    for suf, lift_side, bob_dy in specs:
        f = assemble(original_arr, original_img, cut_y, centro_x, lift_side, bob_dy)
        f, n = clean_seam(f, original_arr, cut_y)
        frames[suf] = f
        f.save(ASSETS / f"walk_{prefix}_{suf}.png")
        print(f"walk_{prefix}_{suf}: emenda limpou {n} pixels")

    strip = Image.new("RGBA", (W * 4, H), (0, 0, 0, 0))
    for i, suf in enumerate(["1", "2", "3", "4"]):
        strip.paste(frames[suf], (i * W, 0))
    strip.save(ASSETS / f"_debug_{prefix}_strip.png")

    # checagens
    orig_last = last_opaque_row(original_arr)
    largura_orig = bbox[2] - bbox[0]
    for suf in ["2", "4"]:
        last = last_opaque_row(np.array(frames[suf]))
        ok = last is not None and abs(last - orig_last) <= 1
        print(f"walk_{prefix}_{suf}: ultima linha={last} (original={orig_last}) "
              f"{'OK' if ok else 'AVISO: fora de +-1px'}")

    grounded = {"1": ("right", centro_x, W), "3": ("left", 0, centro_x)}
    for suf, (_, x0, x1) in grounded.items():
        last_frame = last_opaque_row(np.array(frames[suf]), int(x0), int(x1))
        last_orig = last_opaque_row(original_arr, int(x0), int(x1))
        ok = last_frame is not None and last_orig is not None and abs(last_frame - last_orig) <= 1
        print(f"walk_{prefix}_{suf}: perna no chao ultima linha={last_frame} "
              f"(original={last_orig}) {'OK' if ok else 'AVISO: perna no chao se moveu'}")

    for suf in ["1", "2", "3", "4"]:
        b = frames[suf].getbbox()
        largura = (b[2] - b[0]) if b else 0
        diff = abs(largura - largura_orig)
        ok = diff <= 10
        print(f"walk_{prefix}_{suf}: largura bbox={largura} (original={largura_orig}, diff={diff}) "
              f"{'OK' if ok else 'AVISO: fora de +-10px'}")
    print()


def main():
    gerar_view("pad_frame_1.png", "front")
    gerar_view("pad_frame_3.png", "back")
    print("Arquivos salvos em:", ASSETS)


if __name__ == "__main__":
    main()
