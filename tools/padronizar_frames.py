#!/usr/bin/env python3
"""Padroniza frames de personagem com trimming e canvas unificado."""

from PIL import Image
import math
from pathlib import Path

input_dir = Path(r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\assets\personagem")
output_dir = input_dir
tools_dir = Path(r"C:\Users\JathuielCorrea\github\Meu projeto\Game_dev\tools")

# Carrega os 6 frames
frames = []
for i in range(1, 7):
    path = input_dir / f"frame_{i}.png"
    img = Image.open(path)
    frames.append(img)

# Re-trima cada frame pelo alpha channel
trimmed_frames = []
for i, frame in enumerate(frames, 1):
    if frame.mode != "RGBA":
        frame = frame.convert("RGBA")

    # getbbox() no alpha channel
    alpha = frame.split()[3]
    bbox = alpha.getbbox()

    if bbox:
        trimmed = frame.crop(bbox)
    else:
        trimmed = frame  # frame vazio

    trimmed_frames.append(trimmed)
    print(f"Frame {i}: original={frames[i-1].size}, trimmed={trimmed.size}")

# Calcula canvas único
max_width = max(f.width for f in trimmed_frames)
max_height = max(f.height for f in trimmed_frames)

# Largura e altura do canvas: maior + 4, arredondado para cima para número par
canvas_width = math.ceil((max_width + 4) / 2) * 2
canvas_height = math.ceil((max_height + 4) / 2) * 2

print(f"\nCanvas size: {canvas_width}x{canvas_height}")

# Cria canvases e salva
padded_frames = []
print("\nOffsets (x, y) onde cada frame foi colado:")

for i, trimmed in enumerate(trimmed_frames, 1):
    # Cria canvas transparente
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))

    # Posiciona: centralizado horizontalmente, alinhado pela base com 2px margem
    x = (canvas_width - trimmed.width) // 2
    y = canvas_height - trimmed.height - 2

    canvas.paste(trimmed, (x, y), trimmed)
    padded_frames.append(canvas)

    # Salva frame padronizado
    output_path = output_dir / f"pad_frame_{i}.png"
    canvas.save(output_path)
    print(f"Frame {i}: ({x}, {y}) -> {output_path.name}")

# Cria spritesheet horizontal 6x1
spritesheet_width = canvas_width * 6
spritesheet = Image.new("RGBA", (spritesheet_width, canvas_height), (0, 0, 0, 0))

for i, frame in enumerate(padded_frames):
    spritesheet.paste(frame, (i * canvas_width, 0))

spritesheet_path = output_dir / "personagem_strip.png"
spritesheet.save(spritesheet_path)
print(f"\nSpritesheet salvo: {spritesheet_path.name} ({spritesheet.size})")
