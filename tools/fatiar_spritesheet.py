"""Fatia um spritesheet em frames individuais com fundo transparente.

Abordagem: flood fill (BFS) a partir da borda para achar o fundo (que e um
gradiente suave), o que sobra e mascara de sprite; agrupa em componentes
conexos (BFS 8-conectividade), funde componentes proximos e recorta os 6
maiores como frames PNG com alpha.
"""
import os
import sys
from collections import deque

from PIL import Image

try:
    import numpy as np
except ImportError:
    np = None

SRC = r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\ChatGPT Image 14 de jul. de 2026, 21_19_59.png"
OUT_DIR = r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\assets\personagem"
NUM_FRAMES = 6
BG_THRESHOLD = 12      # soma das diferencas absolutas RGB entre pixels vizinhos
MARGIN = 2              # margem em px ao redor de cada recorte
MIN_COMPONENT_AREA = 30 # descarta ruido menor que isso antes de fundir/selecionar
MERGE_GAP = 10           # funde componentes cujas bboxes distam menos que isso (px)


def flood_fill_background(pixels, w, h, threshold):
    """BFS a partir de todos os pixels da borda; anda pelo gradiente do fundo.

    Retorna um bytearray (w*h) com 1 onde e fundo, 0 onde nao e (candidato a sprite).
    """
    visited = bytearray(w * h)
    q = deque()

    def seed(x, y):
        idx = y * w + x
        if not visited[idx]:
            visited[idx] = 1
            q.append((x, y))

    for x in range(w):
        seed(x, 0)
        seed(x, h - 1)
    for y in range(h):
        seed(0, y)
        seed(w - 1, y)

    while q:
        x, y = q.popleft()
        r0, g0, b0 = pixels[x, y][:3]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                nidx = ny * w + nx
                if not visited[nidx]:
                    r1, g1, b1 = pixels[nx, ny][:3]
                    if abs(r1 - r0) + abs(g1 - g0) + abs(b1 - b0) <= threshold:
                        visited[nidx] = 1
                        q.append((nx, ny))
    return visited


def label_components(sprite_mask, w, h):
    """BFS 8-conectividade sobre a mascara de sprite (1 = sprite).

    Retorna lista de componentes; cada um e dict com area, bbox e set de indices.
    """
    labels = bytearray(w * h)  # 0 = nao visitado, 1 = visitado
    components = []
    neighbors8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    for y in range(h):
        row = y * w
        for x in range(w):
            idx = row + x
            if sprite_mask[idx] and not labels[idx]:
                labels[idx] = 1
                q = deque([(x, y)])
                pix_idx = [idx]
                min_x = max_x = x
                min_y = max_y = y
                while q:
                    cx, cy = q.popleft()
                    for dx, dy in neighbors8:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h:
                            nidx = ny * w + nx
                            if sprite_mask[nidx] and not labels[nidx]:
                                labels[nidx] = 1
                                q.append((nx, ny))
                                pix_idx.append(nidx)
                                if nx < min_x: min_x = nx
                                if nx > max_x: max_x = nx
                                if ny < min_y: min_y = ny
                                if ny > max_y: max_y = ny
                components.append({
                    "pixels": pix_idx,
                    "bbox": (min_x, min_y, max_x, max_y),
                    "area": len(pix_idx),
                })
    return components


def bbox_gap(b1, b2):
    """Distancia (gap) entre duas bboxes; 0 ou negativo se sobrepoem/tocam."""
    ax0, ay0, ax1, ay1 = b1
    bx0, by0, bx1, by1 = b2
    dx = max(bx0 - ax1, ax0 - bx1, 0)
    dy = max(by0 - ay1, ay0 - by1, 0)
    if dx == 0 or dy == 0:
        return max(dx, dy)
    return (dx ** 2 + dy ** 2) ** 0.5


def union_bbox(b1, b2):
    return (min(b1[0], b2[0]), min(b1[1], b2[1]), max(b1[2], b2[2]), max(b1[3], b2[3]))


def merge_close_components(components, gap_threshold):
    """Une (union-find simples por repeticao) componentes cujas bboxes estao
    a menos de gap_threshold px umas das outras."""
    comps = list(components)
    changed = True
    while changed:
        changed = False
        n = len(comps)
        for i in range(n):
            for j in range(i + 1, n):
                if bbox_gap(comps[i]["bbox"], comps[j]["bbox"]) < gap_threshold:
                    merged = {
                        "pixels": comps[i]["pixels"] + comps[j]["pixels"],
                        "bbox": union_bbox(comps[i]["bbox"], comps[j]["bbox"]),
                        "area": comps[i]["area"] + comps[j]["area"],
                    }
                    new_comps = [c for k, c in enumerate(comps) if k != i and k != j]
                    new_comps.append(merged)
                    comps = new_comps
                    changed = True
                    break
            if changed:
                break
    return comps


def main():
    img = Image.open(SRC).convert("RGBA")
    w, h = img.size
    pixels = img.load()

    print(f"Imagem: {SRC} ({w}x{h})")

    bg_visited = flood_fill_background(pixels, w, h, BG_THRESHOLD)
    sprite_mask = bytearray(1 if not v else 0 for v in bg_visited)

    n_sprite_px = sum(sprite_mask)
    print(f"Pixels de fundo detectados: {w * h - n_sprite_px} / Pixels de sprite: {n_sprite_px}")

    components = label_components(sprite_mask, w, h)
    components = [c for c in components if c["area"] >= MIN_COMPONENT_AREA]
    print(f"Componentes conexos (apos filtro de ruido minimo): {len(components)}")

    if len(components) > NUM_FRAMES:
        components = merge_close_components(components, MERGE_GAP)
        print(f"Componentes apos fusao por proximidade (<{MERGE_GAP}px): {len(components)}")

    components.sort(key=lambda c: c["area"], reverse=True)
    top = components[:NUM_FRAMES]

    if len(top) != NUM_FRAMES:
        print(f"AVISO: esperado {NUM_FRAMES} componentes, obtido {len(top)}. "
              f"Ajuste BG_THRESHOLD / MERGE_GAP / MIN_COMPONENT_AREA.")

    # ordena por posicao: linha (centro y) depois coluna (centro x)
    def center(c):
        x0, y0, x1, y1 = c["bbox"]
        return ((y0 + y1) / 2, (x0 + x1) / 2)

    # agrupa em linhas aproximando por metade da altura media, para nao
    # confundir sprites levemente desalinhados como linhas diferentes
    top_sorted_y = sorted(top, key=lambda c: center(c)[0])
    avg_h = sum(c["bbox"][3] - c["bbox"][1] for c in top) / len(top) if top else 1
    row_bucket_size = avg_h * 0.6

    rows = []
    for c in top_sorted_y:
        cy = center(c)[0]
        placed = False
        for row in rows:
            if abs(row["y"] - cy) <= row_bucket_size:
                row["items"].append(c)
                placed = True
                break
        if not placed:
            rows.append({"y": cy, "items": [c]})

    rows.sort(key=lambda r: r["y"])
    ordered = []
    for row in rows:
        row["items"].sort(key=lambda c: center(c)[1])
        ordered.extend(row["items"])

    os.makedirs(OUT_DIR, exist_ok=True)

    results = []
    for i, comp in enumerate(ordered, start=1):
        x0, y0, x1, y1 = comp["bbox"]
        cx0 = max(0, x0 - MARGIN)
        cy0 = max(0, y0 - MARGIN)
        cx1 = min(w - 1, x1 + MARGIN)
        cy1 = min(h - 1, y1 + MARGIN)

        crop_w = cx1 - cx0 + 1
        crop_h = cy1 - cy0 + 1
        frame = Image.new("RGBA", (crop_w, crop_h), (0, 0, 0, 0))
        frame_px = frame.load()

        for idx in comp["pixels"]:
            py = idx // w
            px = idx % w
            fx = px - cx0
            fy = py - cy0
            if 0 <= fx < crop_w and 0 <= fy < crop_h:
                r, g, b, a = pixels[px, py]
                frame_px[fx, fy] = (r, g, b, 255)

        out_path = os.path.join(OUT_DIR, f"frame_{i}.png")
        frame.save(out_path)
        results.append((f"frame_{i}.png", (x0, y0, x1, y1), (crop_w, crop_h)))

    print("\nResultado final:")
    for name, bbox, size in results:
        print(f"  {name}: bbox={bbox} tamanho_recorte={size[0]}x{size[1]}")


if __name__ == "__main__":
    main()
