"""Reduz os frames de um personagem (336x380) para a escala oficial 16-bit do
jogo: canvas 64x72 (tiles de 32x32, personagem ~2,25 tiles).

1. Resize cada frame para (64,72) com LANCZOS.
2. Binariza o alpha: >=96 -> 255, senao 0.
3. Junta os pixels opacos de TODOS os frames reduzidos numa paleta adaptativa
   unica (64 cores; sobe pra 80/96 se a checagem de cor falhar; ultimo
   recurso: paleta em duas partes 8+56, depois 12+52), e remapeia cada frame
   para essa MESMA paleta (mesma cor -> mesmo indice em todos os frames, pra
   animacao nao "ferver"). A checagem de cor e opcional (`check_frame`/
   `color_check`) — o heroi principal usa para garantir que a lata verde
   Hiniken nao suma da paleta; personagens sem essa regra de negocio passam
   check_frame=None e pulam a checagem.
4. Gera os strips (escala normal e @8x) + poses avulsas em `{out_dir}\\16bit\\`.
"""

from pathlib import Path

from PIL import Image

SIZE = (64, 72)
ALPHA_THRESHOLD = 96

# --- personagem principal (Ze da Lata) ---
ASSETS = Path(r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\assets\personagem")
OUT = ASSETS / "16bit"

FRAMES = (
    [f"pad_frame_{i}" for i in range(1, 7)]
    + [f"idle_{i}" for i in range(1, 4)]
    + [f"idle_lado_{i}" for i in range(1, 4)]
    + [f"walk_{i}" for i in range(1, 5)]
    + [f"walk_front_{i}" for i in range(1, 5)]
    + [f"walk_back_{i}" for i in range(1, 5)]
    + [f"comemorar_{i}" for i in range(1, 5)]
    + ["pad_view_3_4", "pad_vitoria"]
)
STRIPS = {
    "idle_strip": ["idle_1", "idle_2", "idle_3", "idle_2"],
    "idle_lado_strip": ["idle_lado_1", "idle_lado_2", "idle_lado_3", "idle_lado_2"],
    "walk_strip": ["walk_1", "walk_2", "walk_3", "walk_4"],
    "walk_front_strip": ["walk_front_1", "walk_front_2", "walk_front_3", "walk_front_4"],
    "walk_back_strip": ["walk_back_1", "walk_back_2", "walk_back_3", "walk_back_4"],
    "comemorar_strip": ["comemorar_1", "comemorar_2", "comemorar_3", "comemorar_4"],
    "vitoria_strip": ["pad_vitoria"],
}
# poses avulsas consumidas por gerar_telas_menu.py (mockups de UI) — nao
# entram em nenhum strip, mas load_sprite() espera acha-las em 16bit/
UI_POSES = ["pad_frame_1", "pad_frame_2", "pad_frame_5", "pad_frame_6", "pad_view_3_4"]


def is_green(r, g, b):
    return g > r + 30 and g > b + 30


def load_resized(assets_dir, name):
    img = Image.open(assets_dir / f"{name}.png").convert("RGBA").resize(SIZE, Image.LANCZOS)
    r, g, b, a = img.split()
    a = a.point(lambda v: 255 if v >= ALPHA_THRESHOLD else 0)
    return Image.merge("RGBA", (r, g, b, a))


def opaque_pixels(frames_rgba):
    pixels = []
    for img in frames_rgba.values():
        for r, g, b, a in img.getdata():
            if a == 255:
                pixels.append((r, g, b))
    if not pixels:
        raise RuntimeError("nenhum pixel opaco encontrado nos frames")
    return pixels


def quantize_pixels(pixels, n_cores):
    swatch = Image.new("RGB", (len(pixels), 1))
    swatch.putdata(pixels)
    return swatch.quantize(colors=n_cores)


def build_palette_from_colors(colors):
    """Monta uma imagem-paleta 'P' a partir de uma lista de cores RGB."""
    pal_img = Image.new("P", (1, 1))
    flat = []
    for c in colors:
        flat.extend(c)
    # ponytail: padding repete a ultima cor real para as 256 entradas do modo P
    # nao introduzirem uma cor extra (preto) fora da paleta
    flat.extend(list(colors[-1]) * (256 - len(colors)))
    pal_img.putpalette(flat)
    return pal_img


def palette_colors(pal_img, n):
    pal = pal_img.getpalette()
    return [tuple(pal[i * 3:i * 3 + 3]) for i in range(n)]


def has_green(img_rgba):
    return any(a == 255 and is_green(r, g, b) for r, g, b, a in img_rgba.getdata())


def remap_to_palette(img_rgba, palette_img):
    rgb = img_rgba.convert("RGB")
    mapped = rgb.quantize(palette=palette_img, dither=Image.Dither.NONE).convert("RGB")
    alpha = img_rgba.split()[3]
    return Image.merge("RGBA", (*mapped.split(), alpha))


def build_shared_palette(frames_rgba, check_frame=None, color_check=None):
    """Tenta paleta unica de 64/80/96 cores. Se `check_frame`/`color_check`
    forem dados, exige que o frame de checagem mantenha ao menos 1 pixel que
    passe em `color_check(r,g,b)` (regra de negocio especifica de um
    personagem, ex.: o heroi principal segura uma lata verde); sem checagem,
    aceita a primeira paleta unica (64 cores) direto. Fallback (so quando ha
    checagem): quantiza os pixels que passam separado do resto (8+56, depois
    12+52) e une."""
    pixels = opaque_pixels(frames_rgba)
    if check_frame is None or color_check is None:
        pal = quantize_pixels(pixels, 64)
        return pal, 64

    for n in (64, 80, 96):
        pal = quantize_pixels(pixels, n)
        test = remap_to_palette(frames_rgba[check_frame], pal)
        ok = any(a == 255 and color_check(r, g, b) for r, g, b, a in test.getdata())
        print(f"paleta unica com {n} cores: checagem de cor em {check_frame} -> {'PASSOU' if ok else 'falhou'}")
        if ok:
            return pal, n
    marcados = [p for p in pixels if color_check(*p)]
    resto = [p for p in pixels if not color_check(*p)]
    for n_marcados, n_resto in ((8, 56), (12, 52)):
        print(f"nenhuma paleta unica passou; tentando paleta em duas partes ({n_marcados}+{n_resto})")
        cores = palette_colors(quantize_pixels(marcados, n_marcados), n_marcados) + \
            palette_colors(quantize_pixels(resto, n_resto), n_resto)
        pal = build_palette_from_colors(cores)
        test = remap_to_palette(frames_rgba[check_frame], pal)
        ok = any(a == 255 and color_check(r, g, b) for r, g, b, a in test.getdata())
        total = n_marcados + n_resto
        print(f"paleta em duas partes ({total} cores): checagem de cor em {check_frame} -> {'PASSOU' if ok else 'FALHOU'}")
        if ok:
            return pal, total
    raise RuntimeError("checagem de cor falhou mesmo com paleta em duas partes (12+52)")


def make_strip(frames_rgba, names, cell_size):
    w, h = cell_size
    strip = Image.new("RGBA", (w * len(names), h), (0, 0, 0, 0))
    for i, name in enumerate(names):
        strip.paste(frames_rgba[name], (i * w, 0))
    return strip


def reduzir(assets_dir, out_dir, frames, strips, singles=(), check_frame=None, color_check=None):
    """Roda o pipeline completo (resize -> paleta compartilhada -> remap ->
    strips + poses avulsas) para um personagem. Retorna dict {nome: Image}
    dos frames finais (64x72), para o chamador validar o que quiser."""
    out_dir.mkdir(parents=True, exist_ok=True)

    resized = {name: load_resized(assets_dir, name) for name in frames}

    palette_img, n_cores = build_shared_palette(resized, check_frame, color_check)
    print(f"numero de cores da paleta usada = {n_cores}")

    final = {name: remap_to_palette(img, palette_img) for name, img in resized.items()}

    saved = []
    for nome, names in strips.items():
        strip = make_strip(final, names, SIZE)
        strip.save(out_dir / f"{nome}.png")
        strip.resize((strip.width * 8, strip.height * 8), Image.NEAREST).save(out_dir / f"{nome}@8x.png")
        saved += [out_dir / f"{nome}.png", out_dir / f"{nome}@8x.png"]

    for nome in singles:
        final[nome].save(out_dir / f"{nome}.png")
        saved.append(out_dir / f"{nome}.png")

    todas_cores = {(r, g, b) for img in final.values() for r, g, b, a in img.getdata() if a == 255}
    print("Arquivos gerados:")
    for p in saved:
        print(f"  {p}  {Image.open(p).size}")
    print(f"\nnumero de cores unicas finais (pixels opacos, todos os frames) = {len(todas_cores)}")

    if check_frame and color_check:
        ok = any(a == 255 and color_check(r, g, b) for r, g, b, a in final[check_frame].getdata())
        print(f"checagem final no frame {check_frame}: cor presente -> {'PASSOU' if ok else 'FALHOU'}")
        assert ok, f"cor de checagem ausente em 16bit/{check_frame}.png"

    return final


def main():
    reduzir(ASSETS, OUT, FRAMES, STRIPS, singles=UI_POSES, check_frame="idle_1", color_check=is_green)


if __name__ == "__main__":
    main()
