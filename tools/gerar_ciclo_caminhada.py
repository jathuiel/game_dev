"""Gera walk_3 (contato B) a partir de walk_1 (contato A) TROCANDO as pernas de
posicao por TRANSLACAO HORIZONTAL (sem espelhar), para nao inverter o sentido
da dobra dos joelhos.

walk_1 = contato A (ja existente, pes na base, pernas abertas em passada)
walk_2, walk_4 = ja existem em assets\\personagem, nao sao recriados aqui
walk_3 = contato B: as duas pernas de walk_1 trocam de posicao horizontal
         (a perna da frente vai para onde estava a de tras, e vice-versa),
         mantendo cada perna com sua propria forma/dobra (so translada em x).

Algoritmo:
 1. bbox do alpha de walk_1; cut_y = topo + 0.72 * altura.
 2. Rotula componentes conectados (BFS 8-conectado) do alpha abaixo de cut_y.
    Se nao vier exatamente 2 componentes grandes, aumenta cut_y em passos de
    4px (a calca larga deste personagem so separa as pernas perto do
    tornozelo, entao na pratica isso ultrapassa o teto nominal de 0.78*altura
    sugerido -- ver aviso impresso).
 3. Cada perna e extraida pela sua mascara de pixels (nao pelo bbox inteiro,
    para nao arrastar pixels da outra perna). Cada uma e transladada em x de
    forma que seu centro-x va para o centro-x da outra perna. Sem flip. Y
    inalterado.
 4. Remonta: canvas transparente -> pernas transladadas -> alpha_composite do
    torso (crop de walk_1 de (0,0,336,cut_y+6)) por cima.
 5. Limpa a emenda: nas linhas cut_y..cut_y+12, zera pixels opacos no
    resultado que sao transparentes em walk_1 na mesma posicao.
"""

from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ASSETS = Path(r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\assets\personagem")
W, H = 336, 380
BIG_MIN = 80  # pixels minimos para um componente contar como "perna" (filtra ruido de antialiasing)


def load(name):
    return Image.open(ASSETS / name).convert("RGBA")


def last_opaque_row(img):
    bbox = img.split()[3].getbbox()
    if bbox is None:
        return None
    return bbox[3] - 1


def label_components(mask):
    """mask: array bool (h, w). Retorna lista de {pixels:[(y,x)...], bbox:(x0,y0,x1,y1), size}."""
    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    comps = []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not visited[y, x]:
                pixels = []
                dq = deque([(y, x)])
                visited[y, x] = True
                while dq:
                    cy, cx = dq.popleft()
                    pixels.append((cy, cx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            if dy == 0 and dx == 0:
                                continue
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                                visited[ny, nx] = True
                                dq.append((ny, nx))
                ys = [p[0] for p in pixels]
                xs = [p[1] for p in pixels]
                comps.append({
                    "pixels": pixels,
                    "bbox": (min(xs), min(ys), max(xs) + 1, max(ys) + 1),
                    "size": len(pixels),
                })
    return comps


def find_leg_components(arr, top, altura):
    """Aumenta cut_y ate achar exatamente 2 componentes grandes (pernas) separados."""
    start = top + int(0.72 * altura)
    nominal_max = top + int(0.78 * altura)
    hard_max = min(H - 4, top + int(0.95 * altura))
    cut_y = start
    warned = False
    while True:
        mask = arr[cut_y:H, :, 3] > 0
        comps = label_components(mask)
        big = sorted([c for c in comps if c["size"] >= BIG_MIN], key=lambda c: -c["size"])
        if len(big) >= 2:
            return cut_y, comps, big[:2]
        if cut_y > nominal_max and not warned:
            print(f"AVISO: cut_y ja passou do teto sugerido (0.78*altura = {nominal_max}) "
                  f"sem separar as pernas; continuando alem do limite (calca larga so separa perto do tornozelo).")
            warned = True
        if cut_y >= hard_max:
            # ultimo recurso: usa os 2 maiores componentes que existirem, mesmo que so 1 seja "grande"
            all_sorted = sorted(comps, key=lambda c: -c["size"])
            return cut_y, comps, all_sorted[:2]
        cut_y += 4


def make_walk3(walk1):
    arr = np.array(walk1)
    bbox = walk1.getbbox()
    top, bottom = bbox[1], bbox[3]
    altura = bottom - top

    cut_y, comps, legs = find_leg_components(arr, top, altura)

    # bbox global (offset de cut_y no y) de cada perna, antes da troca
    def global_bbox(comp):
        x0, y0, x1, y1 = comp["bbox"]
        return (x0, y0 + cut_y, x1, y1 + cut_y)

    bbox_a_antes = global_bbox(legs[0])
    bbox_b_antes = global_bbox(legs[1])
    center_a = (bbox_a_antes[0] + bbox_a_antes[2]) / 2
    center_b = (bbox_b_antes[0] + bbox_b_antes[2]) / 2
    dx_a = round(center_b - center_a)
    dx_b = round(center_a - center_b)

    pernas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pernas_px = pernas.load()
    walk1_px = walk1.load()

    for comp, dx in ((legs[0], dx_a), (legs[1], dx_b)):
        for y_local, x_local in comp["pixels"]:
            gy = y_local + cut_y
            nx = x_local + dx
            if 0 <= nx < W:
                pernas_px[nx, gy] = walk1_px[x_local, gy]

    bbox_a_depois = (bbox_a_antes[0] + dx_a, bbox_a_antes[1], bbox_a_antes[2] + dx_a, bbox_a_antes[3])
    bbox_b_depois = (bbox_b_antes[0] + dx_b, bbox_b_antes[1], bbox_b_antes[2] + dx_b, bbox_b_antes[3])

    walk3 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    walk3.alpha_composite(pernas)
    torso = walk1.crop((0, 0, W, cut_y + 6))
    torso_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    torso_layer.paste(torso, (0, 0))
    walk3.alpha_composite(torso_layer)

    # limpeza da emenda
    a3 = walk3.load()
    a1 = walk1.load()
    limpos = 0
    for y in range(cut_y, min(cut_y + 13, H)):
        for x in range(W):
            if a3[x, y][3] > 0 and a1[x, y][3] == 0:
                a3[x, y] = (0, 0, 0, 0)
                limpos += 1

    info = {
        "cut_y": cut_y,
        "n_componentes": len(comps),
        "bbox_a_antes": bbox_a_antes,
        "bbox_a_depois": bbox_a_depois,
        "bbox_b_antes": bbox_b_antes,
        "bbox_b_depois": bbox_b_depois,
        "limpos": limpos,
    }
    return walk3, info


def main():
    walk1 = load("walk_1.png")
    walk3, info = make_walk3(walk1)
    walk3.save(ASSETS / "walk_3.png")

    walk2 = load("walk_2.png")
    walk4 = load("walk_4.png")
    frames = {"walk_1": walk1, "walk_2": walk2, "walk_3": walk3, "walk_4": walk4}

    strip = Image.new("RGBA", (W * 4, H), (0, 0, 0, 0))
    for i, name in enumerate(["walk_1", "walk_2", "walk_3", "walk_4"]):
        strip.paste(frames[name], (i * W, 0))
    strip.save(ASSETS / "walk_strip.png")

    print(f"cut_y usado = {info['cut_y']}")
    print(f"numero de componentes conectados achados no crop = {info['n_componentes']}")
    print(f"perna A bbox antes  = {info['bbox_a_antes']}")
    print(f"perna A bbox depois = {info['bbox_a_depois']}")
    print(f"perna B bbox antes  = {info['bbox_b_antes']}")
    print(f"perna B bbox depois = {info['bbox_b_depois']}")
    print(f"emenda: {info['limpos']} pixels limpos (linhas y={info['cut_y']}..{min(info['cut_y'] + 12, H - 1)})")
    print()

    for name in ["walk_1", "walk_2", "walk_3", "walk_4"]:
        y = last_opaque_row(frames[name])
        dist_base = H - 1 - y if y is not None else None
        print(f"{name}: ultima linha nao-transparente y={y}  (dist. da base = {dist_base}px)")

    w1, w3 = frames["walk_1"], frames["walk_3"]
    b1, b3 = w1.getbbox(), w3.getbbox()
    largura1 = b1[2] - b1[0]
    largura3 = b3[2] - b3[0]
    print()
    print(f"walk_1 bbox largura = {largura1}  walk_3 bbox largura = {largura3}")
    if abs(largura1 - largura3) > 12:
        print(f"AVISO: pernas de walk_3 parecem deslocadas (diferenca de largura = {abs(largura1 - largura3)}px > 12px)")
    else:
        print("OK: largura de walk_3 dentro da tolerancia de 12px em relacao a walk_1")

    print()
    print("Arquivos salvos em:", ASSETS)


if __name__ == "__main__":
    main()
