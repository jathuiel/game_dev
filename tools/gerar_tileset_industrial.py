# Gera tileset industrial pixel art (fabrica de bebidas) no MESMO estilo/escala
# do tileset de cenario (tiles 32x32, contorno K de 2px, dithering via speckle).
# Regeneravel: python tools/gerar_tileset_industrial.py
import math
import os
from PIL import Image

from gerar_tilesets import T, S, K_METAL, nrand, put, novo, montar, salvar, METAL, STONE, WOOD

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

# --- paleta local (tons coerentes com o K escuro do jogo) ---
# progressao propria (nao herdada de METAL do cenario): o salto ESC->CLA do METAL
# do cenario (2 tons, p/ silhuetas pequenas) e grande demais p/ um speckle de tile
# inteiro — gerava efeito de "estatica" em vez de textura. STONE[1] reaproveitado
# como medium_metal (mesmo tom do JSON de referencia).
METAL_ESC = (40, 46, 44, 255)
METAL_MED = STONE[1]           # medium_metal (104,112,106,255)
METAL_CLA = (156, 162, 156, 255)
FERRUGEM = [(163, 61, 16, 255), (231, 91, 13, 255)]   # rust / orange
AMARELO = (255, 210, 46, 255)   # impact_yellow
VERDE_GARRAFA = (89, 101, 43, 255)   # olive_green
VERMELHO = (180, 25, 11, 255)   # red_accent
VIDRO = (60, 110, 130, 255)
VIDRO_CLA = (110, 160, 180, 255)
CONCRETO = [(100, 90, 72, 255), (140, 124, 96, 255), (176, 162, 132, 255)]
# concreto usa tom bege proprio p/ nao se confundir com o piso metalico (cinza-frio);
# piso_rachado reaproveita STONE (concreto desgastado, mais cinza) — ferrugem/vermelho
# ecoam os colecionaveis, amarelo+K formam as faixas de perigo.

def rect(img, x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1):
            put(img, x, y, c)

def manchas_ferrugem(img, seed, n=2, raio=2):
    """Manchas pequenas e esparsas sobre pixels de metal — raio maior com limiar alto
    criava um floco simetrico (artefato do hash em area pequena), reduzido aqui."""
    for i in range(n):
        cx = int(nrand(i, 0, seed) * T)
        cy = int(nrand(i, 1, seed) * T)
        r = raio
        for y in range(max(0, cy - r), min(T, cy + r)):
            for x in range(max(0, cx - r), min(T, cx + r)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r and nrand(x, y, seed + 50) < 0.4:
                    if img.getpixel((x, y)) in (METAL_ESC, METAL_MED):
                        put(img, x, y, FERRUGEM[0] if nrand(x, y, seed + 60) < 0.7 else FERRUGEM[1])

def outline(img, x0, y0, x1, y1, w=S, c=K_METAL):
    rect(img, x0, y0, x1, y0 + w, c)
    rect(img, x0, y1 - w, x1, y1, c)
    rect(img, x0, y0, x0 + w, y1, c)
    rect(img, x1 - w, y0, x1, y1, c)

# ---------- pisos ----------
def i_piso_metal():
    img = novo()
    speckle_local(img, [METAL_ESC, METAL_MED, METAL_CLA], 100, pd=0.12, pl=0.12)
    for cx, cy in [(5, 5), (27, 5), (5, 27), (27, 27)]:
        rect(img, cx - 2, cy - 2, cx + 2, cy + 2, METAL_CLA)
        put(img, cx + 1, cy + 1, METAL_ESC)
        put(img, cx - 2, cy - 2, K_METAL)
    return img

def speckle_local(img, cores, seed, pd=0.12, pl=0.12):
    # mesma formula do speckle() de gerar_tilesets (nao exportada na lista de import).
    for y in range(T):
        for x in range(T):
            r = nrand(x, y, seed)
            c = cores[2] if r < pl else cores[0] if r > 1 - pd else cores[1]
            put(img, x, y, c)

def i_piso_xadrez():
    img = novo()
    for gy in range(4):
        for gx in range(4):
            c = METAL_MED if (gx + gy) % 2 == 0 else METAL_ESC
            rect(img, gx * 8, gy * 8, gx * 8 + 8, gy * 8 + 8, c)
    return img

def i_piso_metal_oleo():
    img = i_piso_metal()
    cx, cy = 18, 21
    for y in range(T):
        for x in range(T):
            dx, dy = x - cx, (y - cy) * 1.3
            if dx * dx + dy * dy < 49 and nrand(x, y, 101) > 0.12:
                put(img, x, y, (24, 26, 30, 255))
    for x, y in [(16, 19), (19, 20), (15, 23), (20, 17)]:
        put(img, x, y, (74, 120, 160, 255))
    return img

def i_piso_rachado():
    img = novo()
    speckle_local(img, STONE, 102, pd=0.10, pl=0.10)
    y = 14
    for x in range(3, 29):
        y += int(nrand(x, 0, 103) * 3) - 1
        y = max(4, min(27, y))
        put(img, x, y, K_METAL); put(img, x, y + 1, K_METAL)
    x2 = 9
    for yy in range(6, 26):
        x2 += int(nrand(0, yy, 104) * 3) - 1
        x2 = max(4, min(27, x2))
        put(img, x2, yy, K_METAL); put(img, x2 + 1, yy, K_METAL)
    return img

def i_concreto():
    img = novo(); speckle_local(img, CONCRETO, 106, pd=0.10, pl=0.10); return img

def i_concreto_faixa():
    img = i_concreto()
    largura = 10
    for y in range(T):
        for x in range(T):
            d = x - y
            if -largura // 2 <= d <= largura // 2:
                stripe = ((x + y) // 4) % 2
                put(img, x, y, AMARELO if stripe == 0 else K_METAL)
    return img

# ---------- paredes ----------
def i_parede_topo():
    img = novo()
    speckle_local(img, [METAL_MED, METAL_MED, METAL_CLA], 107, pd=0.05, pl=0.12)
    rect(img, 0, 0, T, 6, METAL_CLA)
    rect(img, 0, 0, T, S, K_METAL)
    rect(img, 0, 6, T, 8, METAL_ESC)
    for x in range(4, T, 8):
        rect(img, x, 8, x + 2, T, METAL_ESC)
    return img

def i_parede_face():
    img = novo()
    speckle_local(img, [METAL_MED, METAL_MED, METAL_CLA], 108, pd=0.04, pl=0.08)
    for x in range(4, T, 8):
        rect(img, x, 0, x + 2, T, METAL_ESC)
        rect(img, x + 2, 0, x + 3, T, METAL_CLA)
    for cx, cy in [(4, 8), (28, 8), (4, 24), (28, 24)]:
        rect(img, cx - 1, cy - 1, cx + 1, cy + 1, METAL_CLA)
        put(img, cx, cy, METAL_ESC)
    for cx, cy in [(4, 16), (28, 16), (16, 8), (16, 24)]:  # rivets extras nas bordas
        rect(img, cx - S // 2, cy - S // 2, cx + S // 2, cy + S // 2, K_METAL)
    return img

def i_parede_base():
    img = i_parede_face()
    for y in range(T - 6, T):
        peso = (y - (T - 6)) / 6
        for x in range(T):
            if nrand(x, y, 109) < 0.4 + peso * 0.5:
                put(img, x, y, METAL_ESC)
    rect(img, 0, T - S, T, T, K_METAL)
    return img

def i_fachada_janela():
    img = i_parede_face()
    x0, y0, x1, y1 = 6, 6, 26, 26
    rect(img, x0, y0, x1, y1, METAL_ESC)
    ix0, iy0, ix1, iy1 = x0 + 3, y0 + 3, x1 - 3, y1 - 3
    rect(img, ix0, iy0, ix1, iy1, VIDRO)
    midx, midy = (ix0 + ix1) // 2, (iy0 + iy1) // 2
    rect(img, midx - 1, iy0, midx + 1, iy1, METAL_MED)
    rect(img, ix0, midy - 1, ix1, midy + 1, METAL_MED)
    for px, py in [(ix0 + 2, iy0 + 2), (ix0 + 3, iy0 + 3), (midx + 3, iy0 + 2)]:
        put(img, px, py, VIDRO_CLA)
    outline(img, x0, y0, x1, y1, w=S, c=K_METAL)
    return img

def _porta_base():
    img = novo()
    speckle_local(img, [METAL_ESC, METAL_MED, METAL_MED], 110, pd=0.06, pl=0.10)
    rect(img, 0, 0, T, 4, METAL_CLA)
    rect(img, 0, 0, T, S, K_METAL)
    for y in range(8, T, 6):
        rect(img, 0, y, T, y + 2, METAL_ESC)
    rect(img, 0, T - S, T, T, K_METAL)
    return img

def i_porta_L():
    img = _porta_base()
    rect(img, 0, 0, S, T, K_METAL)
    rect(img, T - 2, 12, T, 20, METAL_CLA)
    put(img, T - 3, 15, K_METAL); put(img, T - 3, 16, K_METAL)
    return img

def i_porta_R():
    img = _porta_base()
    rect(img, T - S, 0, T, T, K_METAL)
    rect(img, 0, 12, 2, 20, METAL_CLA)
    put(img, 2, 15, K_METAL); put(img, 2, 16, K_METAL)
    return img

# ---------- canos ----------
def i_cano_h():
    img = novo()
    y0, y1 = 11, 21
    rect(img, 0, y0, T, y1, METAL_MED)
    rect(img, 0, y0, T, y0 + 3, METAL_CLA)
    rect(img, 0, y1 - 3, T, y1, METAL_ESC)
    rect(img, 0, y0, T, y0 + S, K_METAL)
    rect(img, 0, y1 - S, T, y1, K_METAL)
    for x in (6, 26):
        rect(img, x - 3, y0 - 3, x + 3, y1 + 3, METAL_ESC)
        rect(img, x - 3, y0 - 3, x - 1, y1 + 3, K_METAL)
        rect(img, x + 1, y0 - 3, x + 3, y1 + 3, K_METAL)
    return img

def i_cano_v():
    img = novo()
    x0, x1 = 11, 21
    rect(img, x0, 0, x1, T, METAL_MED)
    rect(img, x0, 0, x0 + 3, T, METAL_CLA)
    rect(img, x1 - 3, 0, x1, T, METAL_ESC)
    rect(img, x0, 0, x0 + S, T, K_METAL)
    rect(img, x1 - S, 0, x1, T, K_METAL)
    for y in (6, 26):
        rect(img, x0 - 3, y - 3, x1 + 3, y + 3, METAL_ESC)
        rect(img, x0 - 3, y - 3, x1 + 3, y - 1, K_METAL)
        rect(img, x0 - 3, y + 1, x1 + 3, y + 3, K_METAL)
    return img

CORNER = {
    frozenset(("N", "E")): (T, 0), frozenset(("N", "W")): (0, 0),
    frozenset(("S", "E")): (T, T), frozenset(("S", "W")): (0, T),
}

def _cano_curva(d1, d2):
    """Curva de cano conectando dois lados do tile (mesma espessura de cano_h/v)."""
    img = novo()
    ox, oy = CORNER[frozenset((d1, d2))]
    r_out, r_in = 21, 11
    for y in range(T):
        for x in range(T):
            d = ((x - ox) ** 2 + (y - oy) ** 2) ** 0.5
            if r_out - 2 <= d <= r_out:
                put(img, x, y, K_METAL)
            elif r_in <= d <= r_in + 2:
                put(img, x, y, K_METAL)
            elif r_in < d < r_out:
                c = METAL_CLA if d > r_out - 5 else METAL_ESC if d < r_in + 5 else METAL_MED
                put(img, x, y, c)
    return img

def i_cano_curva_NE(): return _cano_curva("N", "E")
def i_cano_curva_NW(): return _cano_curva("N", "W")
def i_cano_curva_SE(): return _cano_curva("S", "E")
def i_cano_curva_SW(): return _cano_curva("S", "W")

# ---------- maquina 2x2 ----------
def maquina_64():
    W = 2 * T
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    def p(x, y, c):
        if 0 <= x < W and 0 <= y < W:
            img.putpixel((x, y), c)
    def r(x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(W, y1)):
            for x in range(max(0, x0), min(W, x1)):
                p(x, y, c)
    r(0, 0, W, W, METAL_MED)
    for y in range(W):
        for x in range(W):
            if nrand(x, y, 120) < 0.07:
                p(x, y, METAL_CLA if nrand(x, y, 121) < 0.5 else METAL_ESC)
    r(0, 0, W, 4, K_METAL); r(0, W - 4, W, W, K_METAL); r(0, 0, 4, W, K_METAL); r(W - 4, 0, W, W, K_METAL)

    r(6, 6, 58, 28, K_METAL)                              # moldura do painel de luzes
    r(8, 8, 56, 26, METAL_ESC)
    for bx, cor in [(14, VERMELHO), (30, (64, 200, 96, 255)), (42, AMARELO)]:
        r(bx, 12, bx + 8, 20, K_METAL)
        r(bx + 1, 13, bx + 7, 19, cor)

    r(10, 38, 54, 50, K_METAL)                            # moldura dos botoes
    r(11, 39, 53, 49, METAL_ESC)
    for i, bx in enumerate((14, 26, 38, 46)):
        cor = [VERMELHO, AMARELO, (64, 200, 96, 255), METAL_CLA][i]
        r(bx, 41, bx + 6, 47, K_METAL)
        r(bx + 1, 42, bx + 5, 46, cor)

    r(12, 50, 52, 60, K_METAL)                            # moldura do mostrador
    r(14, 52, 50, 58, (22, 42, 32, 255))
    for x in range(16, 48, 4):
        p(x, 55, (96, 224, 128, 255))
    return img

# ---------- esteira ----------
def i_esteira(offset):
    img = novo()
    y0, y1 = 11, 21
    rect(img, 0, y0, T, y1, (42, 42, 48, 255))
    for i in range(-1, 5):
        x = (i * 8 + offset) % 40 - 4
        rect(img, x, y0 + 1, x + 3, y1 - 1, (150, 150, 160, 255))
    rect(img, 0, y0 - S, T, y0, METAL_ESC); rect(img, 0, y1, T, y1 + S, METAL_ESC)
    rect(img, 0, y0 - S, T, y0 - S + S, K_METAL); rect(img, 0, y1, T, y1 + S, K_METAL)
    rect(img, 0, T - 4, 4, T, METAL_ESC); rect(img, T - 4, T - 4, T, T, METAL_ESC)
    return img

def i_esteira_1(): return i_esteira(0)
def i_esteira_2(): return i_esteira(4)

# ---------- tanque 1x2 ----------
def i_tanque_T():
    img = novo()
    rect(img, 6, 14, 26, T, METAL_MED)
    for y in range(2, 14):
        for x in range(T):
            dx, dy = (x - 16) / 11.0, (y - 8) / 7.0
            if dx * dx + dy * dy <= 1:
                put(img, x, y, METAL_CLA if dy < -0.2 else METAL_MED)
    rect(img, 14, 0, 18, 4, METAL_ESC)
    rect(img, 13, 2, 19, 6, METAL_CLA)
    for y in range(2, 14):
        for x in range(T):
            dx, dy = (x - 16) / 11.0, (y - 8) / 7.0
            d = dx * dx + dy * dy
            if 0.85 <= d <= 1.05:
                put(img, x, y, K_METAL)
    rect(img, 5, 14, 7, T, K_METAL); rect(img, 25, 14, 27, T, K_METAL)
    return img

def i_tanque_B():
    img = novo()
    rect(img, 6, 0, 26, T - 4, METAL_MED)
    rect(img, 5, 0, 7, T, K_METAL); rect(img, 25, 0, 27, T, K_METAL)
    rect(img, 11, 6, 21, 22, K_METAL)
    rect(img, 12, 7, 20, 21, (20, 30, 26, 255))
    for y in range(8, 20):
        for x in range(13, 19):
            put(img, x, y, VERDE_GARRAFA if nrand(x, y, 130) > 0.2 else (60, 150, 84, 255))
    rect(img, 4, T - 4, 28, T, METAL_ESC)
    rect(img, 4, T - S, 28, T, K_METAL)
    return img

# ---------- chamine 1x3 ----------
def chamine_96():
    H = 3 * T
    img = Image.new("RGBA", (T, H), (0, 0, 0, 0))
    def p(x, y, c):
        if 0 <= x < T and 0 <= y < H:
            img.putpixel((x, y), c)
    def r(x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(H, y1)):
            for x in range(max(0, x0), min(T, x1)):
                p(x, y, c)
    r(6, 0, 26, H, FERRUGEM[0])
    for y in range(H):
        for x in range(6, 26):
            if nrand(x, y, 140) < 0.15:
                p(x, y, FERRUGEM[1] if nrand(x, y, 141) < 0.5 else (110, 60, 30, 255))
    r(4, 0, 28, 4, K_METAL)
    r(6, 4, 26, 8, METAL_CLA)
    for fy in range(20, H, 24):
        for x in range(6, 26):
            stripe = ((x + fy) // 4) % 2
            p(x, fy, AMARELO if stripe == 0 else K_METAL)
            p(x, fy + 1, AMARELO if stripe == 0 else K_METAL)
    r(5, 0, 7, H, K_METAL); r(25, 0, 27, H, K_METAL)
    r(4, H - 4, 28, H, K_METAL); r(6, H - 8, 26, H - 4, METAL_ESC)
    return img

def i_barril_metal():
    img = novo()
    cx = 16
    for y in range(4, T - 2):
        meia = 11 if 10 <= y <= 24 else 9
        for x in range(cx - meia, cx + meia):
            r = nrand(x, y, 150)
            c = METAL_CLA if x < cx - meia + 4 else METAL_ESC if x > cx + meia - 5 or r > 0.9 else METAL_MED
            put(img, x, y, c)
        put(img, cx - meia - 1, y, K_METAL); put(img, cx + meia, y, K_METAL)
    for yo in (8, 16, 24):
        for x in range(cx - 11, cx + 11):
            put(img, x, yo, FERRUGEM[0]); put(img, x, yo + 1, FERRUGEM[1])
    manchas_ferrugem(img, 162, n=2, raio=3)
    rect(img, cx - 9, T - 4, cx + 9, T - 2, K_METAL)
    rect(img, cx - 9, 2, cx + 9, 4, K_METAL)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if abs(dx) + abs(dy) <= 3:
                put(img, cx + dx, 16 + dy, VERMELHO)
    return img

# ---------- cerca e engrenagem ----------
def i_cerca_tela_h():
    # contorno K + malha em tom claro: sem isso a malha some contra pisos cinza-metal
    img = novo()
    rect(img, 0, 4, T, 7, K_METAL); rect(img, 0, 5, T, 6, METAL_MED)
    rect(img, 0, 25, T, 28, K_METAL); rect(img, 0, 26, T, 27, METAL_MED)
    for y in range(7, 25):
        for x in range(T):
            if (x + y) % 6 == 0 or (x - y) % 6 == 0:
                put(img, x, y, METAL_CLA)
    for px in (2, T - 2):
        rect(img, px - 3, 0, px - 2, T, K_METAL); rect(img, px + 2, 0, px + 3, T, K_METAL)
        rect(img, px - 2, 0, px + 2, T, METAL_CLA)
    return img

def i_cerca_tela_v():
    img = novo()
    rect(img, 4, 0, 7, T, K_METAL); rect(img, 5, 0, 6, T, METAL_MED)
    rect(img, 25, 0, 28, T, K_METAL); rect(img, 26, 0, 27, T, METAL_MED)
    for y in range(T):
        for x in range(7, 25):
            if (x + y) % 6 == 0 or (x - y) % 6 == 0:
                put(img, x, y, METAL_CLA)
    for py in (2, T - 2):
        rect(img, 0, py - 3, T, py - 2, K_METAL); rect(img, 0, py + 2, T, py + 3, K_METAL)
        rect(img, 0, py - 2, T, py + 2, METAL_CLA)
    return img

def i_engrenagem():
    cx, cy = 16, 16
    r_out, r_in, r_hole, dentes = 13, 9, 4, 8
    def dentro(x, y):
        dx, dy = x - cx, y - cy
        d = (dx * dx + dy * dy) ** 0.5
        if d < r_hole:
            return False
        ang = math.atan2(dy, dx)
        raio_local = r_out if math.cos(ang * dentes) > 0.3 else r_in
        return d <= raio_local
    img = novo()
    for y in range(T):
        for x in range(T):
            if dentro(x, y):
                dy = y - cy
                c = METAL_CLA if dy < -2 else METAL_ESC if dy > 2 else METAL_MED
                put(img, x, y, c)
    for y in range(T):
        for x in range(T):
            if not dentro(x, y) and any(dentro(x + ddx, y + ddy)
                    for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                put(img, x, y, K_METAL)
    return img

# ---------- montagem ----------
def main():
    os.makedirs(OUT, exist_ok=True)
    maq = maquina_64()
    maquina_TL = maq.crop((0, 0, T, T)); maquina_TR = maq.crop((T, 0, 2 * T, T))
    maquina_BL = maq.crop((0, T, T, 2 * T)); maquina_BR = maq.crop((T, T, 2 * T, 2 * T))
    cham = chamine_96()
    chamine_T = cham.crop((0, 0, T, T)); chamine_M = cham.crop((0, T, T, 2 * T))
    chamine_B = cham.crop((0, 2 * T, T, 3 * T))

    industrial = [
        ("piso_metal", i_piso_metal()), ("piso_xadrez", i_piso_xadrez()),
        ("piso_metal_oleo", i_piso_metal_oleo()), ("piso_rachado", i_piso_rachado()),
        ("concreto", i_concreto()), ("concreto_faixa", i_concreto_faixa()),
        ("parede_topo", i_parede_topo()), ("parede_face", i_parede_face()),

        ("parede_base", i_parede_base()), ("fachada_janela", i_fachada_janela()),
        ("porta_L", i_porta_L()), ("porta_R", i_porta_R()),
        ("cano_h", i_cano_h()), ("cano_v", i_cano_v()),
        ("cano_curva_NE", i_cano_curva_NE()),

        ("cano_curva_NW", i_cano_curva_NW()), ("cano_curva_SE", i_cano_curva_SE()),
        ("cano_curva_SW", i_cano_curva_SW()),
        ("maquina_TL", maquina_TL), ("maquina_TR", maquina_TR),
        ("maquina_BL", maquina_BL), ("maquina_BR", maquina_BR),

        ("esteira_1", i_esteira_1()), ("esteira_2", i_esteira_2()),
        ("tanque_T", i_tanque_T()), ("tanque_B", i_tanque_B()),
        ("chamine_T", chamine_T), ("chamine_M", chamine_M), ("chamine_B", chamine_B),
        ("barril_metal", i_barril_metal()),

        ("cerca_tela_h", i_cerca_tela_h()), ("cerca_tela_v", i_cerca_tela_v()),
        ("engrenagem", i_engrenagem()),
        (None, None), (None, None), (None, None), (None, None),
        (None, None), (None, None), (None, None),
    ]
    folha, ti = montar(industrial, 8)
    salvar(folha, "tileset_industrial")

    # ponytail: checagem minima — todo tile nomeado tem pixels visiveis
    for nome, tile in ti.items():
        assert tile.getbbox() is not None, f"tile vazio: {nome}"

    # --- preview 16x10 tiles ---
    W, H = 16, 10
    cena = Image.new("RGBA", (W * T, H * T))
    for y in range(H):
        for x in range(W):
            if x < 3 and 3 <= y <= 5:
                nome = "piso_xadrez"
            elif (x, y) in [(0, 6), (1, 6)]:
                nome = "piso_rachado"
            elif (x, y) in [(2, 6), (3, 6)]:
                nome = "piso_metal_oleo"
            elif (x, y) in [(6, 8), (7, 8)]:
                nome = "concreto_faixa"
            elif (x, y) in [(6, 9), (7, 9)]:
                nome = "concreto"
            else:
                nome = "piso_metal"
            cena.alpha_composite(ti[nome], (x * T, y * T))

    for x in range(2, 14):  # parede ao fundo
        cena.alpha_composite(ti["parede_topo"], (x * T, 0 * T))
        nome_face = "fachada_janela" if x == 5 else "parede_face"
        if x == 8:
            nome_face = "porta_L"
        elif x == 9:
            nome_face = "porta_R"
        cena.alpha_composite(ti[nome_face], (x * T, 1 * T))
        cena.alpha_composite(ti["parede_base"], (x * T, 2 * T))

    cena.alpha_composite(ti["tanque_T"], (1 * T, 3 * T))     # tanque 1x2
    cena.alpha_composite(ti["tanque_B"], (1 * T, 4 * T))

    cena.alpha_composite(ti["chamine_T"], (14 * T, 3 * T))   # chamine 1x3
    cena.alpha_composite(ti["chamine_M"], (14 * T, 4 * T))
    cena.alpha_composite(ti["chamine_B"], (14 * T, 5 * T))

    for i, x in enumerate(range(4, 6)):  # maquina 2x2
        cena.alpha_composite(ti["maquina_TL" if i == 0 else "maquina_TR"], (x * T, 7 * T))
        cena.alpha_composite(ti["maquina_BL" if i == 0 else "maquina_BR"], (x * T, 8 * T))

    for i, x in enumerate(range(8, 11)):  # trecho de esteira
        cena.alpha_composite(ti["esteira_1" if i % 2 == 0 else "esteira_2"], (x * T, 6 * T))

    for x in range(8, 12):  # cano horizontal + curva + cano vertical
        cena.alpha_composite(ti["cano_h"], (x * T, 5 * T))
    cena.alpha_composite(ti["cano_curva_SW"], (12 * T, 5 * T))
    for y in range(6, 9):
        cena.alpha_composite(ti["cano_v"], (12 * T, y * T))

    cena.alpha_composite(ti["barril_metal"], (13 * T, 7 * T))  # 2 barris
    cena.alpha_composite(ti["barril_metal"], (13 * T, 8 * T))

    for x in range(4, 7):  # pedaco de cerca
        cena.alpha_composite(ti["cerca_tela_h"], (x * T, 9 * T))

    cena.alpha_composite(ti["engrenagem"], (15 * T, 7 * T))    # prop solto

    cena.resize((cena.width * 4, cena.height * 4), Image.NEAREST).save(
        os.path.join(OUT, "preview_industrial.png"))
    print("ok:", sorted(n for n in os.listdir(OUT) if "industrial" in n))

if __name__ == "__main__":
    main()
