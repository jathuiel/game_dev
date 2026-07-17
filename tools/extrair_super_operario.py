"""Extrai poses do Super Operario a partir da folha de referencia (que tem
logo/texto/paineis, nao e uma spritesheet limpa) em
`tilsets de referencia\\super operario.png`.

Reaproveita a segmentacao por componentes conexos de fatiar_spritesheet.py
(label_components/merge_close_components); a unica diferenca e o fundo, que
aqui e branco solido (nao gradiente), entao a mascara de fundo e um threshold
simples em vez do flood-fill BFS.

Para cada pose: recorta uma regiao ampla (com folga generosa) ao redor da
celula na folha de referencia, segmenta o maior componente nao-branco dentro
dela (o sprite - rotulos de texto ficam fora da regiao ou sao bem menores) e
salva com alpha em assets/personagem2/.
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from fatiar_spritesheet import label_components, merge_close_components

SRC = r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\tilsets de referência\super operario.png"
OUT_DIR = r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\assets\personagem2"
WHITE_THRESHOLD = 235   # canal >= isso conta como "quase branco" (fundo)
MIN_COMPONENT_AREA = 40
MERGE_GAP = 8
MARGIN = 3

# regioes amplas (x0,y0,x1,y1) com folga generosa ao redor de cada pose na
# folha de referencia (calibradas visualmente); a segmentacao pega o maior
# componente nao-branco dentro de cada uma
REGIOES = {
    # limites entre colunas calibrados por histograma de densidade de pixels
    # nao-brancos (vales = gap real entre personagens vizinhos); usar o
    # "maior componente" sem isso funde a mao/braco de um vizinho ao lado
    "frente":      (5,   235, 108, 470),
    "lado":        (108, 235, 193, 470),
    "costas":      (193, 235, 293, 470),
    "tres_quartos": (293, 235, 402, 470),
    "idle":        (435, 25,  525, 220),
    "andando":     (560, 25,  665, 220),   # pose de passada, base p/ walk lateral
    "comemorando": (825, 385, 975, 585),
    "vitoria":     (685, 565, 835, 765),
}


def white_mask(img, x0, y0, x1, y1):
    """Mascara (1 = nao-branco / sprite) dentro do recorte, em coordenadas
    absolutas da imagem original (indices continuos por linha do recorte)."""
    crop = img.crop((x0, y0, x1, y1))
    w, h = crop.size
    px = crop.load()
    mask = bytearray(w * h)
    for y in range(h):
        row = y * w
        for x in range(w):
            r, g, b = px[x, y][:3]
            if not (r >= WHITE_THRESHOLD and g >= WHITE_THRESHOLD and b >= WHITE_THRESHOLD):
                mask[row + x] = 1
    return mask, w, h, crop


def extrair_pose(img, nome, regiao):
    x0, y0, x1, y1 = regiao
    mask, w, h, crop = white_mask(img, x0, y0, x1, y1)
    components = label_components(mask, w, h)
    components = [c for c in components if c["area"] >= MIN_COMPONENT_AREA]
    if not components:
        raise RuntimeError(f"{nome}: nenhum componente encontrado na regiao {regiao}")
    components = merge_close_components(components, MERGE_GAP)
    components.sort(key=lambda c: c["area"], reverse=True)
    maior = components[0]

    cx0, cy0, cx1, cy1 = maior["bbox"]
    cx0 = max(0, cx0 - MARGIN)
    cy0 = max(0, cy0 - MARGIN)
    cx1 = min(w - 1, cx1 + MARGIN)
    cy1 = min(h - 1, cy1 + MARGIN)

    out_w, out_h = cx1 - cx0 + 1, cy1 - cy0 + 1
    frame = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))
    crop_px = crop.convert("RGBA").load()
    frame_px = frame.load()
    px_set = set(maior["pixels"])
    for idx in px_set:
        py, px_ = idx // w, idx % w
        fx, fy = px_ - cx0, py - cy0
        if 0 <= fx < out_w and 0 <= fy < out_h:
            r, g, b, _ = crop_px[px_, py]
            frame_px[fx, fy] = (r, g, b, 255)

    out_path = os.path.join(OUT_DIR, f"{nome}.png")
    frame.save(out_path)
    return out_path, (out_w, out_h), maior["area"]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    img = Image.open(SRC).convert("RGB")
    print(f"Fonte: {SRC} ({img.size[0]}x{img.size[1]})")
    for nome, regiao in REGIOES.items():
        path, size, area = extrair_pose(img, nome, regiao)
        print(f"  {nome}: regiao={regiao} -> {os.path.basename(path)} {size[0]}x{size[1]} (area={area}px)")


if __name__ == "__main__":
    main()
