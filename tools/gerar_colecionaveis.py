# Gera sprites pixel art 16-bit dos colecionaveis (chope, budwise, hiniken).
# Regeneravel: python tools/gerar_colecionaveis.py
from PIL import Image
import os

W, H = 20, 24
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

# --- paleta ---
K = (33, 28, 30, 255)              # contorno
BRILHO = (245, 248, 250, 255)      # quase-branco (cintilar / especular)
BRANCO = (255, 255, 255, 255)

GOLD = (232, 180, 60, 255)
GOLD_CLARO = (255, 214, 100, 255)
GOLD_ESCURO = (196, 142, 40, 255)  # base do copo, mais escura

VERMELHO = (196, 40, 44, 255)
VERMELHO_CLARO = (230, 80, 80, 255)

VERDE = (44, 140, 60, 255)
VERDE_CLARO = (90, 190, 100, 255)
FAIXA_VERDE_CLARA = (214, 238, 214, 255)  # branca-esverdeada

TAMPA = (150, 148, 158, 255)       # cinza metalico
TAMPA_CLARA = (190, 188, 196, 255)


def novo():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def put(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), c)


def contorno(img):
    # contorno K de 1px em torno de toda a silhueta ja pintada (mesma ideia de o_pedra em gerar_tilesets.py)
    interior = {(x, y) for y in range(img.height) for x in range(img.width) if img.getpixel((x, y))[3] > 0}
    for x, y in interior:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) not in interior and 0 <= nx < img.width and 0 <= ny < img.height:
                put(img, nx, ny, K)


# ---------- 1. chope (copo americano, sem alca) ----------
def chope(brilho=False):
    img = novo()
    for y in range(7, 21):  # corpo, afunila levemente rumo a base
        t = (y - 7) / 13.0
        esq, dir_ = 5 + round(t), 14 - round(t)
        for x in range(esq, dir_ + 1):
            if y >= 18:
                cor = GOLD_ESCURO
            elif (x - esq) % 3 == 1:
                cor = GOLD_CLARO  # listra vertical de brilho
            else:
                cor = GOLD
            put(img, x, y, cor)
    for x in range(5, 15):  # espuma transbordando
        put(img, x, 6, BRANCO)
    for x in range(4, 16):
        put(img, x, 5, BRANCO); put(img, x, 4, BRANCO)
    for x in range(5, 15):
        put(img, x, 3, BRANCO)
    for x, y in [(7, 2), (7, 1), (10, 1), (13, 2), (14, 3)]:  # 3 bolhas transbordando
        put(img, x, y, BRANCO)
    if brilho:
        for x, y in [(6, 8), (6, 9), (7, 7)]:
            put(img, x, y, BRILHO)
    contorno(img)
    return img


# rotulos abstratos: sem logotipos/tipografia/formas registradas (paródia genérica)
def lata(cor, cor_clara, faixa, pixels_faixa, cor_pixel, brilho=False):
    img = novo()
    put_topo = [7, 8, 9, 10, 11, 12]
    for x in put_topo:
        put(img, x, 4, TAMPA)
    for x in range(6, 14):
        put(img, x, 5, TAMPA_CLARA)
    for y in list(range(6, 11)) + list(range(14, 19)):
        for x in range(6, 14):
            put(img, x, y, cor_clara if x == 7 else cor)
    for y in range(11, 14):  # faixa horizontal do rotulo
        for x in range(6, 14):
            put(img, x, y, faixa)
    for x, y in pixels_faixa:
        put(img, x, y, cor_pixel)
    for x in range(6, 14):
        put(img, x, 19, TAMPA)
    for x in put_topo:
        put(img, x, 20, TAMPA)
    if brilho:
        for x, y in [(6, 6), (6, 7), (6, 8)]:
            put(img, x, y, BRILHO)
    contorno(img)
    return img


def budwise(brilho=False):
    return lata(VERMELHO, VERMELHO_CLARO, BRANCO, [(8, 12), (11, 12)], VERMELHO, brilho)


def hiniken(brilho=False):
    return lata(VERDE, VERDE_CLARO, FAIXA_VERDE_CLARA, [(9, 12)], VERMELHO, brilho)


def montar(itens):
    folha = Image.new("RGBA", (W * len(itens), H), (0, 0, 0, 0))
    for i, img in enumerate(itens):
        folha.alpha_composite(img, (i * W, 0))
    return folha


def salvar(img, nome, escala=4):
    img.save(os.path.join(OUT, nome + ".png"))
    img.resize((img.width * escala, img.height * escala), Image.NEAREST).save(
        os.path.join(OUT, nome + f"@{escala}x.png"))


def checar(nome, f1, f2):
    assert f1.getbbox() is not None and f2.getbbox() is not None, f"{nome}: celula vazia"
    dif = sum(1 for y in range(H) for x in range(W) if f1.getpixel((x, y)) != f2.getpixel((x, y)))
    assert 2 <= dif <= 6, f"{nome}: frames diferem em {dif} pixels (esperado 2-6)"


def main():
    os.makedirs(OUT, exist_ok=True)

    itens = {
        "chope": (chope(False), chope(True)),
        "budwise": (budwise(False), budwise(True)),
        "hiniken": (hiniken(False), hiniken(True)),
    }
    for nome, (f1, f2) in itens.items():
        checar(nome, f1, f2)

    strip = montar([f for par in itens.values() for f in par])
    salvar(strip, "colecionaveis_strip")

    # --- teste de contraste sobre dois fundos ---
    pad, gap = 8, 8
    bloco_w = pad * 2 + 3 * W + 2 * gap
    bloco_h = pad * 2 + H
    teste = Image.new("RGBA", (bloco_w * 2 + gap, bloco_h), (0, 0, 0, 255))
    grama = Image.new("RGBA", (bloco_w, bloco_h), (84, 150, 70, 255))
    metal = Image.new("RGBA", (bloco_w, bloco_h), (120, 116, 126, 255))
    for fundo, ox in [(grama, 0), (metal, bloco_w + gap)]:
        for i, nome in enumerate(itens):
            fundo.alpha_composite(itens[nome][0], (pad + i * (W + gap), pad))
        teste.alpha_composite(fundo, (ox, 0))
    salvar(teste, "colecionaveis_teste")

    print("ok:", sorted(f for f in os.listdir(OUT) if f.startswith("colecionaveis")))


if __name__ == "__main__":
    main()
