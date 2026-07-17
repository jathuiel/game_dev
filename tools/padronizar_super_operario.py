"""Padroniza as poses extraidas do Super Operario (assets/personagem2/*.png,
produzidas por extrair_super_operario.py) para o MESMO canvas 336x380 com pes
na base usado pelo heroi principal — assim os scripts de animacao existentes
(gerar_ciclos_verticais.py, gerar_idle_respiracao.py, gerar_ciclo_caminhada.py,
W,H=336,380 hardcoded) funcionam sem alteracao ao apontar para esta pasta.

Diferente de padronizar_frames.py (canvas auto-calculado a partir do maior
frame): aqui o canvas e FIXO (336x380, igual ao heroi 1) e cada pose e
ESCALADA por um fator unico antes de colar, porque a folha de referencia do
Super Operario foi desenhada numa resolucao bem menor (~100x177px por pose)
que a do heroi 1 (~311x375px) — sem escalar, o Super Operario ficaria minusculo
dentro do canvas comparado ao heroi 1 no jogo.
"""
from pathlib import Path

from PIL import Image

IN_DIR = Path(r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\assets\personagem2")
CANVAS_W, CANVAS_H = 336, 380
REF_POSE = "costas"       # pose "reta" usada para calibrar o fator de escala
REF_ALTURA_ALVO = 375     # altura do sprite do heroi 1 dentro do canvas 336x380

POSES = ["frente", "lado", "costas", "tres_quartos", "idle", "andando", "comemorando", "vitoria"]


def main():
    ref_img = Image.open(IN_DIR / f"{REF_POSE}.png")
    ref_bbox = ref_img.split()[3].getbbox()
    ref_altura = ref_bbox[3] - ref_bbox[1]
    fator = REF_ALTURA_ALVO / ref_altura
    print(f"Pose de referencia '{REF_POSE}': altura={ref_altura}px -> fator de escala={fator:.3f}")

    for nome in POSES:
        img = Image.open(IN_DIR / f"{nome}.png").convert("RGBA")
        bbox = img.split()[3].getbbox()
        trimmed = img.crop(bbox)

        novo_w = max(1, round(trimmed.width * fator))
        novo_h = max(1, round(trimmed.height * fator))
        escalado = trimmed.resize((novo_w, novo_h), Image.LANCZOS)

        if novo_w > CANVAS_W or novo_h > CANVAS_H:
            raise ValueError(f"{nome}: {novo_w}x{novo_h} nao cabe no canvas {CANVAS_W}x{CANVAS_H}")

        canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        x = (CANVAS_W - novo_w) // 2
        y = CANVAS_H - novo_h - 2   # pes na base, mesma convencao do heroi 1
        canvas.paste(escalado, (x, y), escalado)

        out_path = IN_DIR / f"pad_{nome}.png"
        canvas.save(out_path)
        print(f"  {nome}: trimmed={trimmed.size} -> escalado={novo_w}x{novo_h} @ ({x},{y}) -> {out_path.name}")


if __name__ == "__main__":
    main()
