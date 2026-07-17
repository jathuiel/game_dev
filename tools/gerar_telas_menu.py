"""Gera mockups pixel art (640x360) das telas de UI: menu, config, personagem.

Usa apenas assets existentes (tileset_cenario.png, sprites pad_frame_*) e Pillow.
Roda com: python tools/gerar_telas_menu.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUT_DIR = ASSETS / "telas"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 640, 360
TILE = 16
SCALE_BG = 2  # tiles de fundo desenhados a 32x32

# --- paleta -----------------------------------------------------------
CONTORNO = (33, 28, 30)
MADEIRA_ESCURA = (102, 68, 42)
MADEIRA = (150, 104, 60)
MADEIRA_CLARA = (196, 150, 94)
VERDE_FOLHA = (62, 130, 58)
VERDE_CLARO = (100, 172, 78)
DOURADO = (232, 200, 88)
CREME = (236, 222, 180)  # texto sobre madeira (contraste)
VERMELHO = (200, 60, 52)
AZUL_AGUA = (54, 104, 172)

FONT_CANDIDATES = [r"C:\Windows\Fonts\consolab.ttf", r"C:\Windows\Fonts\arialbd.ttf"]


def _font_path():
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return p
    raise FileNotFoundError("Nenhuma fonte bold encontrada (consolab.ttf / arialbd.ttf)")


FONT_PATH = _font_path()


# --- assets -------------------------------------------------------------
def load_tiles():
    ts = Image.open(ASSETS / "tileset_cenario.png").convert("RGBA")

    def cell(col, row, cw=1, ch=1):
        return ts.crop((col * TILE, row * TILE, (col + cw) * TILE, (row + ch) * TILE))

    return {
        "grama": cell(0, 0),
        "grama_tufos": cell(1, 0),
        "grama_flores": cell(2, 0),
        "arbusto": cell(2, 4),
        "arvore": cell(0, 4, 2, 2),  # cobre (0,4)(1,4)(0,5)(1,5) -> 32x32
    }


def load_sprite(name, char_dir="personagem"):
    return Image.open(ASSETS / char_dir / "16bit" / f"{name}.png").convert("RGBA")


def upscale(img, factor):
    return img.resize((img.width * factor, img.height * factor), Image.NEAREST)


def darken(img, factor=0.5):
    r, g, b, a = img.split()
    lut = [int(v * factor) for v in range(256)]
    return Image.merge("RGBA", (r.point(lut), g.point(lut), b.point(lut), a))


# --- texto pixelado -------------------------------------------------------
def render_text(text, size_half, fill, outline=None):
    """Renderiza texto na metade do tamanho e faz upscale 2x NEAREST (look pixelado)."""
    font = ImageFont.truetype(FONT_PATH, size_half)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bbox = probe.textbbox((0, 0), text, font=font)
    pad = 2
    w = bbox[2] - bbox[0] + pad * 2
    h = bbox[3] - bbox[1] + pad * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ox, oy = pad - bbox[0], pad - bbox[1]
    if outline:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            d.text((ox + dx, oy + dy), text, font=font, fill=outline)
    d.text((ox, oy), text, font=font, fill=fill)
    return upscale(img, 2)


def paste_text_centered(base, text, cx, y, size_half, fill, outline=None):
    txt = render_text(text, size_half, fill, outline)
    base.alpha_composite(txt, (cx - txt.width // 2, y))
    return txt


# --- fundo ----------------------------------------------------------------
TREE_SPOTS = [(0, 0), (576, 0), (0, 296), (576, 296)]
BUSH_SPOTS = [(96, 8), (480, 320), (8, 160), (600, 160), (280, 8), (280, 320)]


def draw_background(tiles):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    disp = TILE * SCALE_BG
    variants = [tiles["grama"], tiles["grama"], tiles["grama"],
                tiles["grama_tufos"], tiles["grama_tufos"], tiles["grama_flores"]]
    for y in range(0, H, disp):
        for x in range(0, W, disp):
            idx = ((x // disp) * 7 + (y // disp) * 13) % len(variants)
            t = variants[idx].resize((disp, disp), Image.NEAREST)
            img.paste(t, (x, y))

    tree = upscale(tiles["arvore"], SCALE_BG)  # 64x64
    for x, y in TREE_SPOTS:
        img.alpha_composite(tree, (x, y))
    bush = upscale(tiles["arbusto"], SCALE_BG)  # 32x32
    for x, y in BUSH_SPOTS:
        img.alpha_composite(bush, (x, y))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 90))
    img.alpha_composite(overlay)
    return img.convert("RGBA")


# --- paineis / botoes estilo madeira ---------------------------------------
def wood_rect(draw, box, border=2, gold_border=False):
    x0, y0, x1, y1 = box
    edge = DOURADO if gold_border else CONTORNO
    draw.rectangle([x0, y0, x1, y1], fill=MADEIRA)
    draw.rectangle([x0, y0, x1, y1], outline=edge, width=border)
    draw.line([(x0 + border, y0 + border), (x1 - border, y0 + border)], fill=MADEIRA_CLARA)
    draw.line([(x0 + border, y1 - border), (x1 - border, y1 - border)], fill=MADEIRA_ESCURA)


def draw_button(base, box, label, size_half=9):
    d = ImageDraw.Draw(base)
    wood_rect(d, box)
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    txt = render_text(label, size_half, CREME, CONTORNO)
    base.alpha_composite(txt, (cx - txt.width // 2, cy - txt.height // 2))


def draw_double_panel(draw, box, inset=6):
    wood_rect(draw, box)
    x0, y0, x1, y1 = box
    wood_rect(draw, (x0 + inset, y0 + inset, x1 - inset, y1 - inset))


# --- widgets de config ------------------------------------------------------
def draw_slider(base, x, y, width, pct, label):
    d = ImageDraw.Draw(base)
    lbl = render_text(label, 8, CREME, CONTORNO)
    base.alpha_composite(lbl, (x, y))
    track_x = x + 130
    track_y = y + lbl.height // 2 - 4
    track_w = width
    d.rectangle([track_x, track_y, track_x + track_w, track_y + 8], fill=MADEIRA_ESCURA, outline=CONTORNO)
    fill_w = int(track_w * pct)
    if fill_w > 2:
        d.rectangle([track_x + 1, track_y + 1, track_x + fill_w - 1, track_y + 7], fill=VERDE_CLARO)
    knob_x = track_x + fill_w
    d.rectangle([knob_x - 4, track_y - 3, knob_x + 4, track_y + 11], fill=DOURADO, outline=CONTORNO)


def draw_toggle(base, x, y, on, label):
    d = ImageDraw.Draw(base)
    lbl = render_text(label, 8, CREME, CONTORNO)
    base.alpha_composite(lbl, (x, y))
    tx = x + 130
    ty = y + lbl.height // 2 - 8
    d.rectangle([tx, ty, tx + 40, ty + 16], fill=(VERDE_FOLHA if on else MADEIRA_ESCURA), outline=CONTORNO)
    bx = tx + (40 - 15 if on else 3)
    d.rectangle([bx, ty + 2, bx + 12, ty + 14], fill=DOURADO, outline=CONTORNO)


def draw_choice(base, x, y, value, label):
    d = ImageDraw.Draw(base)
    lbl = render_text(label, 8, CREME, CONTORNO)
    base.alpha_composite(lbl, (x, y))
    arrow_l = render_text("<", 9, CREME, CONTORNO)
    arrow_r = render_text(">", 9, CREME, CONTORNO)
    val = render_text(value, 8, CREME, CONTORNO)
    ax = x + 130
    base.alpha_composite(arrow_l, (ax, y - 1))
    base.alpha_composite(val, (ax + 20, y))
    base.alpha_composite(arrow_r, (ax + 20 + val.width + 10, y - 1))


# --- telas -------------------------------------------------------------
def build_menu(tiles):
    img = draw_background(tiles)
    d = ImageDraw.Draw(img)

    paste_text_centered(img, "AVENTURA PIXEL", W // 2, 22, 17, DOURADO, CONTORNO)

    hero = upscale(load_sprite("pad_frame_5"), 5)  # 160x180
    img.alpha_composite(hero, (440, 110))

    labels = ["JOGAR", "OPÇÕES", "PERSONAGEM"]
    btn_w, btn_h, gap = 220, 44, 14
    bx = 60
    by = 100
    for i, label in enumerate(labels):
        box = (bx, by + i * (btn_h + gap), bx + btn_w, by + i * (btn_h + gap) + btn_h)
        draw_button(img, box, label)
    return img


def build_config(tiles):
    img = draw_background(tiles)
    d = ImageDraw.Draw(img)

    panel = (90, 30, 550, 320)
    draw_double_panel(d, panel, inset=8)

    paste_text_centered(img, "CONFIGURAÇÕES", W // 2, 44, 12, CREME, CONTORNO)

    row_x = 130
    row_y = 100
    row_gap = 44
    draw_slider(img, row_x, row_y, 150, 0.70, "MÚSICA")
    draw_slider(img, row_x, row_y + row_gap, 150, 0.50, "SOM")
    draw_toggle(img, row_x, row_y + row_gap * 2, True, "VIBRAÇÃO")
    draw_choice(img, row_x, row_y + row_gap * 3, "PT-BR", "IDIOMA")

    draw_button(img, (W // 2 - 90, 268, W // 2 + 90, 300), "VOLTAR")
    return img


def build_personagem(tiles):
    img = draw_background(tiles)
    d = ImageDraw.Draw(img)

    paste_text_centered(img, "ESCOLHA SEU HERÓI", W // 2, 18, 15, DOURADO, CONTORNO)

    # moldura central (destacada)
    cw, ch = 150, 170
    ccx = W // 2
    center_box = (ccx - cw // 2, 60, ccx + cw // 2, 60 + ch)
    wood_rect(d, center_box, border=3, gold_border=True)
    hero_c = upscale(load_sprite("pad_view_3_4"), 4)  # 128x144 -> cabe na moldura sem cobrir o titulo
    hx = ccx - hero_c.width // 2
    hy = 85  # fixo, abaixo da linha do titulo (sprite tem cabelo alto acima do "corpo" nominal)
    img.alpha_composite(hero_c, (hx, hy))

    # moldura lateral unica (escurecida, "nao selecionado") — so ha 2 herois
    # reais hoje (Ze da Lata + Super Operario), entao 1 lateral basta; a
    # vista 3/4 do Super Operario fica melhor aqui que uma pose reta
    sw, sh = 100, 120
    side_box = (center_box[2] + 40, 90, center_box[2] + 40 + sw, 90 + sh)
    wood_rect(d, side_box)

    side_op = darken(upscale(load_sprite("pad_tres_quartos", "personagem2"), 4))
    sb_cx = (side_box[0] + side_box[2]) // 2
    sb_cy = (side_box[1] + side_box[3]) // 2
    img.alpha_composite(side_op, (sb_cx - side_op.width // 2, sb_cy - side_op.height // 2))

    # setas grandes ao lado da moldura central
    arrow_l = render_text("<", 20, DOURADO, CONTORNO)
    arrow_r = render_text(">", 20, DOURADO, CONTORNO)
    acy = (center_box[1] + center_box[3]) // 2
    img.alpha_composite(arrow_l, (center_box[0] - 40 - arrow_l.width - 6, acy - arrow_l.height // 2))
    img.alpha_composite(arrow_r, (side_box[0] - arrow_r.width - 6, acy - arrow_r.height // 2))

    # painel do nome sob a moldura central
    name_box = (ccx - 90, center_box[3] + 10, ccx + 90, center_box[3] + 36)
    wood_rect(d, name_box)
    paste_text_centered(img, "ZÉ DA LATA", ccx, name_box[1] + 6, 9, CREME, CONTORNO)

    draw_button(img, (ccx - 90, 322, ccx + 90, 352), "CONFIRMAR")
    return img


def main():
    tiles = load_tiles()
    screens = {
        "menu.png": build_menu(tiles),
        "config.png": build_config(tiles),
        "personagem.png": build_personagem(tiles),
    }

    generated = []
    for name, img in screens.items():
        path = OUT_DIR / name
        img.convert("RGB").save(path)
        generated.append((path, img.size))

    gap = 8
    combo_h = H * 3 + gap * 2
    combo = Image.new("RGBA", (W, combo_h), (20, 20, 20, 255))
    for i, name in enumerate(["menu.png", "config.png", "personagem.png"]):
        combo.alpha_composite(screens[name], (0, i * (H + gap)))
    combo_path = OUT_DIR / "telas_todas.png"
    combo.convert("RGB").save(combo_path)
    generated.append((combo_path, combo.size))

    for path, size in generated:
        print(f"{path} -> {size[0]}x{size[1]}")


if __name__ == "__main__":
    main()
