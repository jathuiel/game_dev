# Gera tilesets pixel art 16-bit (tiles 32x32) no estilo da imagem de referência:
# paleta saturada, contorno escuro, dithering leve. Regeneravel: python tools/gerar_tilesets.py
from PIL import Image
import os

T = 32
S = 2  # escala vs. arte original (era T=16)
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

# --- paleta (estetica industrial/mineracao: terrosa, contorno seletivo por material) ---
K = (26, 20, 16, 255)            # contorno geral (terra/madeira) — marrom quase-preto
K_FOLHA = (14, 20, 9, 255)       # contorno de folhagem — verde quase-preto
K_METAL = (20, 24, 23, 255)      # contorno de pedra/metal — cinza-azulado quase-preto
GRASS = [(38, 56, 23, 255), (89, 101, 43, 255), (136, 146, 69, 255)]           # deep_green/olive_green/light_moss
GRASS_SOMBRA = [(24, 36, 16, 255), (34, 48, 20, 255), (48, 64, 28, 255)]
DIRT = [(60, 38, 22, 255), (120, 69, 29, 255), (179, 120, 41, 255)]           # deep_brown/medium_brown/ochre
WATER = [(40, 90, 110, 255), (86, 164, 191, 255), (150, 210, 222, 255)]        # baseado em sky_cyan
FOAM = (228, 216, 153, 255)       # warm_cream
STONE = [(52, 59, 57, 255), (104, 112, 106, 255), (150, 156, 150, 255)]       # dark_metal/medium_metal/claro
SAND = [(179, 120, 41, 255), (209, 167, 85, 255), (228, 216, 153, 255)]       # ochre/sand/warm_cream
WOOD = [(50, 32, 18, 255), (120, 69, 29, 255), (209, 167, 85, 255)]           # marrom escuro/medium_brown/sand
LEAF = [(30, 48, 18, 255), (70, 96, 38, 255), (110, 140, 60, 255)]
METAL = [(52, 59, 57, 255), (170, 176, 170, 255)]                            # dark_metal / metal claro
SPIKE = [(104, 112, 106, 255), (192, 196, 190, 255)]
RED = (180, 25, 11, 255)          # red_accent
YELLOW = (255, 210, 46, 255)      # impact_yellow

def nrand(x, y, s):
    n = (x * 374761393 + y * 668265263 + s * 1442695041) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) % 1000) / 1000.0

def novo():
    return Image.new("RGBA", (T, T), (0, 0, 0, 0))

def put(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), c)

def speckle(img, cores, seed, pd=0.12, pl=0.12):
    for y in range(T):
        for x in range(T):
            r = nrand(x, y, seed)
            c = cores[2] if r < pl else cores[0] if r > 1 - pd else cores[1]
            put(img, x, y, c)

def jag(i, seed):
    return int(nrand(i, 7, seed) * 3) * S - S

# ---------- tiles de terreno ----------
def t_grass(seed=1):
    img = novo(); speckle(img, GRASS, seed); return img

def t_grass_tufos():
    img = t_grass(2)
    for tx, ty in [(3, 4), (10, 3), (6, 10), (12, 11)]:
        tx, ty = tx * S, ty * S
        put(img, tx, ty, GRASS[0]); put(img, tx + 1, ty, GRASS[0])
        put(img, tx, ty - 1, GRASS[2]); put(img, tx + 2, ty - 1, GRASS[2])
    return img

def t_grass_flores():
    img = t_grass(3)
    for fx, fy, c in [(4, 5, RED), (11, 4, YELLOW), (7, 11, RED)]:
        fx, fy = fx * S, fy * S
        miolo = YELLOW if c == RED else RED
        for dx, dy in [(-S, 0), (S, 0), (0, -S), (0, S)]:
            put(img, fx + dx, fy + dy, c)
        put(img, fx, fy, miolo); put(img, fx + 1, fy, miolo)
        put(img, fx, fy + 1, miolo); put(img, fx + 1, fy + 1, miolo)
    return img

def t_grass_alta():
    img = t_grass(4)
    for x in range(S, T, 2 * S):
        h = (5 + int(nrand(x, 0, 5) * 5)) * S
        for y in range(T - 1 - h, T - 1):
            put(img, x, y, LEAF[1] if y > T - 1 - h + 2 * S else LEAF[2])
        put(img, x, T - 1 - h, GRASS[2])
    return img

def t_terra(seed=6):
    img = novo(); speckle(img, DIRT, seed); return img

def t_terra_pedras():
    img = t_terra(7)
    for px_, py in [(3, 4), (11, 6), (6, 11), (13, 12)]:
        px_, py = px_ * S, py * S
        put(img, px_, py, STONE[1]); put(img, px_ + 1, py, STONE[2])
        put(img, px_, py + 1, STONE[0])
    return img

def t_areia():
    img = novo(); speckle(img, SAND, 8)
    for x, y in [(4, 3), (12, 8), (7, 13)]:
        put(img, x * S, y * S, SAND[0])
    return img

def t_piso_pedra():
    img = novo(); speckle(img, STONE, 9, pd=0.08, pl=0.08)
    c1, c2 = 7 * S, 8 * S
    for i in range(T):
        for k in range(S):
            put(img, i, c1 + k, STONE[0]); put(img, c1 + k, i, STONE[0])
        for k in range(S):
            cor = STONE[2] if (i // S) % 3 else STONE[1]
            put(img, i, c2 + k, cor); put(img, c2 + k, i, cor)
    return img

def t_caminho(lados):
    """Tile de caminho de terra com grama nos lados indicados ('N','E','S','W')."""
    img = novo(); speckle(img, DIRT, 10)
    grama = set()
    d = 4 * S
    for y in range(T):
        for x in range(T):
            if ("N" in lados and y < d + jag(x, 11)) or \
               ("W" in lados and x < d + jag(y, 12)) or \
               ("S" in lados and y > T - 1 - d - jag(x, 13)) or \
               ("E" in lados and x > T - 1 - d - jag(y, 14)):
                grama.add((x, y))
    for (x, y) in grama:
        r = nrand(x, y, 15)
        put(img, x, y, GRASS[2] if r < 0.12 else GRASS[0] if r > 0.88 else GRASS[1])
    for y in range(T):
        for x in range(T):
            if (x, y) not in grama and any((x + dx, y + dy) in grama
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                put(img, x, y, DIRT[0])
    return img

def t_agua(lados):
    """Tile de agua com margem de grama nos lados indicados; sem lados = centro."""
    img = novo(); speckle(img, WATER, 20, pd=0.10, pl=0.10)
    grama = set()
    d = 4 * S
    for y in range(T):
        for x in range(T):
            if ("N" in lados and y < d + jag(x, 21)) or \
               ("W" in lados and x < d + jag(y, 22)) or \
               ("S" in lados and y > T - 1 - d - jag(x, 23)) or \
               ("E" in lados and x > T - 1 - d - jag(y, 24)):
                grama.add((x, y))
    for (x, y) in grama:
        r = nrand(x, y, 25)
        put(img, x, y, GRASS[2] if r < 0.12 else GRASS[0] if r > 0.88 else GRASS[1])
    for y in range(T):
        for x in range(T):
            if (x, y) not in grama:
                viz = any((x + dx, y + dy) in grama
                          for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)])
                if viz:
                    put(img, x, y, WATER[0])
                elif any((x + dx, y + dy) in grama
                         for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)) \
                        and nrand(x, y, 26) < 0.35:
                    put(img, x, y, FOAM)
    if not lados:  # ondas no centro
        for y in (6, 16, 26):
            for x in range(T):
                if nrand(x, y, 27) < 0.22:
                    put(img, x, y, WATER[2]); put(img, (x + 1) % T, y, WATER[2])
    return img

def t_agua_brilho():
    img = t_agua("")
    for x, y in [(3, 4), (10, 7), (6, 12), (13, 2)]:
        x, y = x * S, y * S
        put(img, x, y, FOAM); put(img, x + 1, y, FOAM)
    return img

def t_penhasco_topo():
    img = novo(); speckle(img, GRASS, 30)
    for x in range(T):
        borda = 9 * S + jag(x, 31)
        for k in range(S):
            put(img, x, borda + k, K_METAL)
        for y in range(borda + S, T):
            r = nrand(x, y, 32)
            put(img, x, y, STONE[2] if y < borda + 2 * S else
                (STONE[0] if r > 0.85 else STONE[1]))
    return img

def t_penhasco_face():
    img = novo(); speckle(img, STONE, 33, pd=0.15, pl=0.10)
    for x in range(T):  # estratos horizontais
        for k in range(S):
            put(img, x, 4 * S + jag(x, 34) + k, STONE[0])
            put(img, x, 11 * S + jag(x, 35) + k, STONE[0])
    for y in range(2 * S, 14 * S):  # rachaduras verticais (esparsas — testar cada
        # linha com prob. alta vira ruido continuo em vez de rachadura fina)
        if nrand(0, y, 36) < 0.15:
            for k in range(S):
                put(img, 5 * S + jag(y, 37) + k, y, K_METAL)
        if nrand(1, y, 38) < 0.15:
            for k in range(S):
                put(img, 11 * S + jag(y, 39) + k, y, K_METAL)
    return img

def t_penhasco_base():
    img = novo(); speckle(img, STONE, 40, pd=0.15, pl=0.08)
    for x in range(T):
        for k in range(S):
            put(img, x, 15 * S + k, K_METAL)
            put(img, x, 14 * S + k, STONE[0])
        if nrand(x, 0, 41) < 0.3:
            for k in range(S):
                put(img, x, 13 * S + k, STONE[0]); put(img, x, 12 * S + k, STONE[2])
    return img

def t_penhasco_ao():
    """Grama com faixa de sombra suave no topo (base de penhascos/paredes)."""
    img = t_grass(44)
    faixa = 5 * S
    for y in range(faixa):
        peso = 1 - y / faixa
        for x in range(T):
            if nrand(x, y, 45) < peso * 0.8:
                put(img, x, y, GRASS_SOMBRA[1] if peso > 0.5 else GRASS_SOMBRA[2])
    return img

def t_ponte(horizontal=True):
    img = novo(); speckle(img, WOOD, 42, pd=0.15, pl=0.15)
    for i in range(T):
        if horizontal:
            for k in range(S):
                put(img, i, k, K); put(img, i, T - 1 - k, K)
                put(img, i, S + k, WOOD[2]); put(img, i, T - 2 * S + k, WOOD[0])
            for x in range(3 * S, T, 4 * S):
                for k in range(S):
                    put(img, x + k, i, WOOD[0])
        else:
            for k in range(S):
                put(img, k, i, K); put(img, T - 1 - k, i, K)
                put(img, S + k, i, WOOD[2]); put(img, T - 2 * S + k, i, WOOD[0])
            for y in range(3 * S, T, 4 * S):
                for k in range(S):
                    put(img, i, y + k, WOOD[0])
    return img

def t_grama_sombra():
    img = novo(); speckle(img, GRASS_SOMBRA, 43); return img

def arvore_64():
    """Arvore 64x64 (canopy + tronco), fundo transparente; vira 4 tiles de T px."""
    img = Image.new("RGBA", (32 * S, 32 * S), (0, 0, 0, 0))
    cx = 16 * S
    # tronco: silhueta reaproveita a formula original mapeada por y//S (upscale
    # fiel), com espessura das linhas estruturais ja em escala S
    for y in range(18 * S, 32 * S):
        yo = y // S
        wo = 3 if yo < 29 else 4 + (yo - 29)
        w = wo * S
        for x in range(cx - w, cx + w):
            c = WOOD[2] if x < cx - S else WOOD[1] if x < cx + S else WOOD[0]
            put(img, x, y, c)
        put(img, cx - w - 1, y, K); put(img, cx + w, y, K)
    for x in range(10 * S, 22 * S):
        put(img, x, 32 * S - 1, K)
    # copa: uniao de circulos (centros/raios x2)
    lobos = [(16 * S, 10 * S, 10 * S), (9 * S, 13 * S, 6 * S), (23 * S, 13 * S, 6 * S), (16 * S, 6 * S, 7 * S)]
    def na_copa(x, y):
        return any((x - cx_) ** 2 + (y - cy_) ** 2 <= r * r for cx_, cy_, r in lobos)
    for y in range(32 * S):
        for x in range(32 * S):
            if na_copa(x, y):
                r = nrand(x, y, 50)
                if (x - 11 * S) ** 2 + (y - 6 * S) ** 2 <= (5 * S) ** 2 and r < 0.75:
                    c = LEAF[2]
                elif y > 15 * S or r > 0.8:
                    c = LEAF[0]
                else:
                    c = LEAF[1]
                put(img, x, y, c)
    for y in range(32 * S):  # contorno da copa
        for x in range(32 * S):
            if not na_copa(x, y) and any(na_copa(x + dx, y + dy)
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                put(img, x, y, K_FOLHA)
    return img

def t_arbusto(espinhoso=False):
    img = novo()
    lobos = [(8 * S, 10 * S, 5 * S), (5 * S, 11 * S, 4 * S), (11 * S, 11 * S, 4 * S), (8 * S, 7 * S, 4 * S)]
    def dentro(x, y):
        return y <= 14 * S and any((x - cx) ** 2 + (y - cy) ** 2 <= r * r for cx, cy, r in lobos)
    pal = [LEAF[0], LEAF[0], LEAF[1]] if espinhoso else LEAF
    for y in range(T):
        for x in range(T):
            if dentro(x, y):
                r = nrand(x, y, 60)
                c = pal[2] if (x < 8 * S and y < 10 * S and r < 0.6) else pal[0] if r > 0.8 else pal[1]
                put(img, x, y, c)
    for y in range(T):
        for x in range(T):
            if not dentro(x, y) and any(dentro(x + dx, y + dy)
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                put(img, x, y, K_FOLHA)
    if espinhoso:
        for tx, ty in [(2, 7), (14, 8), (8, 2), (4, 14), (12, 14), (1, 12)]:
            put(img, tx * S, ty * S, SPIKE[1])
    return img

# ---------- obstaculos ----------
def o_pedra(raio=4, cy=9):
    img = novo()
    raio *= S; cy *= S
    cx = T // 2
    def dentro(x, y):
        return (x - cx) ** 2 + ((y - cy) * 1.2) ** 2 <= raio * raio
    for y in range(T):
        for x in range(T):
            if dentro(x, y):
                r = nrand(x, y, 70)
                c = STONE[2] if (x < cx and y < cy and r < 0.7) else \
                    STONE[0] if (x > cx and y > cy) or r > 0.85 else STONE[1]
                put(img, x, y, c)
    for y in range(T):
        for x in range(T):
            if not dentro(x, y) and any(dentro(x + dx, y + dy)
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                put(img, x, y, K_METAL)
    for i in range(6):  # highlight especular fino e intenso
        x = int(nrand(i, cy, 74) * T)
        y = int(nrand(i, cx, 75) * T)
        if dentro(x, y):
            put(img, x, y, STONE[2])
    return img

def o_toco():
    img = novo()
    for y in range(5 * S, 13 * S):  # corpo
        for x in range(3 * S, 13 * S):
            r = nrand(x, y, 71)
            put(img, x, y, WOOD[2] if x < 5 * S else WOOD[0] if x > 10 * S or r > 0.85 else WOOD[1])
    for y in range(2 * S, 7 * S):  # topo eliptico com aneis
        for x in range(3 * S, 13 * S):
            d = ((x - 8 * S) / (5.0 * S)) ** 2 + ((y - 4 * S) / (2.2 * S)) ** 2
            if d <= 1:
                put(img, x, y, WOOD[0] if 0.35 < d < 0.6 else WOOD[2])
    for k in range(S):
        for j in range(S):
            put(img, 8 * S + k, 4 * S + j, WOOD[0])
    for x in range(2 * S, 14 * S):
        for k in range(S):
            put(img, x, 13 * S + k, WOOD[0]); put(img, x, 14 * S + k, K)
    for y in range(3 * S, 14 * S):
        for k in range(S):
            put(img, 2 * S + k, y, K); put(img, 13 * S + k, y, K)
    for x in range(3 * S, 13 * S):
        row = S * (1 + (0 if 4 * S < x < 11 * S else 1))
        for k in range(S):
            put(img, x, row + k, K)
    return img

def o_espinhos():
    img = novo()
    for x in range(T):  # base de pedra
        for k in range(S):
            put(img, x, 13 * S + k, STONE[2])
            put(img, x, 14 * S + k, STONE[1])
            put(img, x, 15 * S + k, K_METAL)
    for s in range(4):
        cx = (2 + s * 4) * S
        for dy in range(6):
            meia = max(0, 2 - dy // 2) * S
            for yy in range(S):
                y = 12 * S - dy * S - yy
                for x in range(cx - meia, cx + meia + 1):
                    put(img, x, y, SPIKE[1] if x <= cx else SPIKE[0])
    return img

def o_caixote():
    img = novo()
    for y in range(S, 15 * S):
        for x in range(S, 15 * S):
            r = nrand(x, y, 72)
            put(img, x, y, WOOD[0] if r > 0.88 else WOOD[1])
    for i in range(S, 15 * S):
        for k in range(S):
            put(img, i, S + k, WOOD[2]); put(img, i, 14 * S + k, WOOD[0])
            put(img, S + k, i, WOOD[2]); put(img, 14 * S + k, i, WOOD[0])
    for i in range(2 * S, 14 * S):  # cruz diagonal
        for k in range(S):
            put(img, i + k, i, WOOD[0]); put(img, (T - 1) - i - k, i, WOOD[0])
    for i in range(T):
        for k in range(S):
            put(img, i, k, K); put(img, i, T - 1 - k, K)
            put(img, k, i, K); put(img, T - 1 - k, i, K)
    return img

def o_barril():
    img = novo()
    cx = 8 * S
    for y in range(S, 15 * S):
        yo = y // S
        meia = (6 if 4 <= yo <= 11 else 5 if yo in (2, 3, 12, 13) else 4) * S
        for x in range(cx - meia, cx + meia):
            r = nrand(x, y, 73)
            c = WOOD[2] if x < cx - meia + 2 * S else WOOD[0] if x > cx + meia - 3 * S or r > 0.9 else WOOD[1]
            put(img, x, y, c)
        for k in range(S):
            put(img, cx - meia - 1 - k, y, K); put(img, cx + meia + k, y, K)
    for yo in (3, 8, 13):  # aros de metal
        meia = (6 if 4 <= yo <= 11 else 5) * S
        for k in range(S):
            y = yo * S + k
            for x in range(cx - meia, cx + meia):
                put(img, x, y, METAL[1] if x < cx else METAL[0])
    for x in range(4 * S, 12 * S):
        for k in range(S):
            put(img, x, k, K); put(img, x, 15 * S + k, K)
    return img

def o_cerca(horizontal=True):
    img = novo()
    if horizontal:
        for y0 in (5, 9):  # travessas
            y = y0 * S
            for x in range(T):
                for k in range(S):
                    put(img, x, y + k, WOOD[2])
                    put(img, x, y + S + k, WOOD[1])
                    put(img, x, y + 2 * S + k, WOOD[0])
        for cx0 in (2, 11):  # mouroes
            cx = cx0 * S
            for y in range(2 * S, 14 * S):
                for k in range(S):
                    put(img, cx + k, y, WOOD[2])
                    put(img, cx + S + k, y, WOOD[1])
                    put(img, cx + 2 * S + k, y, WOOD[0])
            for k in range(S):
                for j in range(3 * S):
                    put(img, cx + j, 1 * S + k, K)
            for x in range(cx, cx + 3 * S):
                for k in range(S):
                    put(img, x, 14 * S + k, K)
    else:
        for x0 in (5, 9):
            x_ = x0 * S
            for y in range(T):
                for k in range(S):
                    put(img, x_ + k, y, WOOD[2])
                    put(img, x_ + S + k, y, WOOD[1])
        for cy0 in (2, 11):
            cy = cy0 * S
            for x in range(2 * S, 14 * S):
                for k in range(S):
                    put(img, x, cy + k, WOOD[2])
                    put(img, x, cy + S + k, WOOD[1])
                    put(img, x, cy + 2 * S + k, WOOD[0])
    return img

def o_placa():
    img = novo()
    for y in range(S, 9 * S):  # tabua
        yo = y // S
        for x in range(S, 15 * S):
            put(img, x, y, WOOD[2] if yo == 1 else WOOD[0] if yo == 8 else WOOD[1])
    for y0 in (3, 5):  # "texto"
        for x0 in range(3, 13, 2):
            for dy in range(S):
                for dx in range(S):
                    put(img, x0 * S + dx, y0 * S + dy, WOOD[0])
    for i in range(S, 15 * S):
        for k in range(S):
            put(img, i, k, K); put(img, i, 9 * S + k, K)
    for y in range(0, 10 * S):
        for k in range(S):
            put(img, k, y, K); put(img, T - 1 - k, y, K)
    for y in range(10 * S, 15 * S):  # poste
        for k in range(S):
            put(img, 7 * S + k, y, WOOD[1])
            put(img, 8 * S + k, y, WOOD[0])
            put(img, 6 * S + k, y, K)
            put(img, 9 * S + k, y, K)
    for x in range(6 * S, 10 * S):
        for k in range(S):
            put(img, x, 15 * S + k, K)
    return img

# ---------- montagem ----------
def montar(grade, cols):
    linhas = (len(grade) + cols - 1) // cols
    folha = Image.new("RGBA", (cols * T, linhas * T), (0, 0, 0, 0))
    tiles = {}
    for i, (nome, tile) in enumerate(grade):
        if tile is None:
            continue
        folha.alpha_composite(tile, ((i % cols) * T, (i // cols) * T))
        tiles[nome] = tile
    return folha, tiles

def salvar(img, nome):
    img.save(os.path.join(OUT, nome + ".png"))
    img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(
        os.path.join(OUT, nome + "@4x.png"))

def main():
    os.makedirs(OUT, exist_ok=True)
    arv = arvore_64()

    cenario = [
        ("grama", t_grass()), ("grama_tufos", t_grass_tufos()),
        ("grama_flores", t_grass_flores()), ("grama_alta", t_grass_alta()),
        ("terra", t_terra()), ("terra_pedras", t_terra_pedras()),
        ("areia", t_areia()), ("piso_pedra", t_piso_pedra()),

        ("caminho_NW", t_caminho("NW")), ("caminho_N", t_caminho("N")),
        ("caminho_NE", t_caminho("NE")), ("agua_NW", t_agua("NW")),
        ("agua_N", t_agua("N")), ("agua_NE", t_agua("NE")),
        ("penhasco_topo", t_penhasco_topo()), ("ponte_h", t_ponte(True)),

        ("caminho_W", t_caminho("W")), ("caminho_C", t_caminho("")),
        ("caminho_E", t_caminho("E")), ("agua_W", t_agua("W")),
        ("agua_C", t_agua("")), ("agua_E", t_agua("E")),
        ("penhasco_face", t_penhasco_face()), ("ponte_v", t_ponte(False)),

        ("caminho_SW", t_caminho("SW")), ("caminho_S", t_caminho("S")),
        ("caminho_SE", t_caminho("SE")), ("agua_SW", t_agua("SW")),
        ("agua_S", t_agua("S")), ("agua_SE", t_agua("SE")),
        ("penhasco_base", t_penhasco_base()), ("agua_brilho", t_agua_brilho()),

        ("arvore_TL", arv.crop((0, 0, T, T))), ("arvore_TR", arv.crop((T, 0, 2 * T, T))),
        ("arbusto", t_arbusto()), ("grama_sombra", t_grama_sombra()),
        ("penhasco_ao", t_penhasco_ao()), (None, None), (None, None), (None, None),

        ("arvore_BL", arv.crop((0, T, T, 2 * T))), ("arvore_BR", arv.crop((T, T, 2 * T, 2 * T))),
        (None, None), (None, None), (None, None), (None, None), (None, None), (None, None),
    ]
    folha_c, tc = montar(cenario, 8)
    salvar(folha_c, "tileset_cenario")

    obstaculos = [
        ("pedra", o_pedra(4)), ("pedregulho", o_pedra(6, 8)),
        ("toco", o_toco()), ("espinhos", o_espinhos()), ("caixote", o_caixote()),
        ("barril", o_barril()), ("cerca_h", o_cerca(True)), ("cerca_v", o_cerca(False)),
        ("placa", o_placa()), ("arbusto_espinhoso", t_arbusto(espinhoso=True)),
    ]
    folha_o, to = montar(obstaculos, 5)
    salvar(folha_o, "tileset_obstaculos")

    # ponytail: checagem minima — todo tile nomeado tem pixels visiveis
    for nome, tile in list(tc.items()) + list(to.items()):
        assert tile.getbbox() is not None, f"tile vazio: {nome}"

    # --- cena de preview 20x12 ---
    W, H = 20, 12
    cena = Image.new("RGBA", (W * T, H * T))
    for y in range(H):
        for x in range(W):
            r = nrand(x, y, 99)
            base = "grama" if r < 0.7 else "grama_tufos" if r < 0.85 else "grama_flores"
            cena.alpha_composite(tc[base], (x * T, y * T))
    for x in range(W):  # cordilheira no topo
        cena.alpha_composite(tc["penhasco_face"], (x * T, 0))
        cena.alpha_composite(tc["penhasco_base"], (x * T, T))
    for x in range(W):  # estrada horizontal
        cena.alpha_composite(tc["caminho_N"], (x * T, 6 * T))
        cena.alpha_composite(tc["caminho_S"], (x * T, 7 * T))
    lago = {(14, 2): "agua_NW", (15, 2): "agua_N", (16, 2): "agua_N", (17, 2): "agua_NE",
            (14, 3): "agua_W", (15, 3): "agua_C", (16, 3): "agua_brilho", (17, 3): "agua_E",
            (14, 4): "agua_SW", (15, 4): "agua_S", (16, 4): "agua_S", (17, 4): "agua_SE"}
    for (x, y), nome in lago.items():
        cena.alpha_composite(tc[nome], (x * T, y * T))
    for ax, ay in [(2, 2), (7, 3), (4, 9)]:  # arvores 2x2
        cena.alpha_composite(tc["arvore_TL"], (ax * T, ay * T))
        cena.alpha_composite(tc["arvore_TR"], ((ax + 1) * T, ay * T))
        cena.alpha_composite(tc["arvore_BL"], (ax * T, (ay + 1) * T))
        cena.alpha_composite(tc["arvore_BR"], ((ax + 1) * T, (ay + 1) * T))
    cena.alpha_composite(tc["arbusto"], (11 * T, 4 * T))
    cena.alpha_composite(tc["arbusto"], (10 * T, 9 * T))
    obst = {(5, 5): "pedra", (12, 3): "toco", (8, 10): "espinhos", (13, 9): "caixote",
            (14, 9): "barril", (11, 5): "placa", (16, 10): "pedregulho",
            (1, 9): "cerca_h", (2, 9): "cerca_h", (17, 8): "arbusto_espinhoso"}
    for (x, y), nome in obst.items():
        cena.alpha_composite(to[nome], (x * T, y * T))
    cena.resize((cena.width * 4, cena.height * 4), Image.NEAREST).save(
        os.path.join(OUT, "preview_cena.png"))
    print("ok:", sorted(os.listdir(OUT)))

if __name__ == "__main__":
    main()
