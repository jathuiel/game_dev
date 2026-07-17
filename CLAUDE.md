# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projeto

Jogo 2D de aventura top-down, pixel art. Plataforma atual: **HTML5/web mobile** (protótipo em `web/`). Projeto Godot 4 em `godot/` está **em espera**. Não é repositório git.

Escala oficial (dobrada de 16→32 na iteração de gameplay): tiles 32×32 px, personagem 64×72 px (~2,25 tiles), render 1× (canvas 1280×720 = mundo visível; mapa 40×24 = 1280×768, só ~48px de scroll vertical). Nos scripts de `tools/` a escala vem das constantes `T=32` e `S=2` (fator vs. arte original de 16px). Paleta com contorno escuro (33,28,30) — cores em `tools/gerar_tilesets.py`.

Objetivo do jogo: coletar bebidas espalhadas — chope, lata "Budwise" (vermelha) e "Hiniken" (verde). Nomes/rótulos são paródia genérica, **sem logotipos/tipografia/formas de marcas reais**. Mapa em 2 biomas: oeste verde, leste zona industrial (fábrica), ligados pela estrada.

## Comandos

Todos os assets são gerados por scripts Python (Pillow) em `tools/` — nunca editar os PNGs à mão; ajustar o script e regenerar:

- `python tools/gerar_tilesets.py` — tilesets de cenário e obstáculos + preview de cena
- `python tools/gerar_tileset_industrial.py` — tileset da zona industrial (importa helpers de `gerar_tilesets.py`) + preview
- `python tools/gerar_colecionaveis.py` — sprites das bebidas (strip de 6 células, 2 frames por tipo)
- `python tools/gerar_ciclo_caminhada.py` — frames walk_1..4 (lateral) a partir dos pads
- `python tools/gerar_ciclos_verticais.py` — frames walk_front_1..4 e walk_back_1..4 (frente/costas)
- `python tools/gerar_idle_respiracao.py` — frames idle_1..3 (respiração)
- `python tools/reduzir_16bit.py` — reduz TODOS os frames para 64×72 com paleta unificada (executar por último, após mudar qualquer frame do personagem)
- Testar o protótipo web: servir a **raiz do projeto** (o jogo usa `../assets/`), ex.: `python -m http.server 8123` e abrir `/web/index.html`

## Arquitetura

- `tools/` — pipeline de assets (Pillow). Fluxo do personagem: spritesheet de referência → `fatiar_spritesheet.py` → `padronizar_frames.py` (canvas 336×380, pés na base) → animações (`gerar_ciclo_caminhada.py` lateral, `gerar_ciclos_verticais.py` frente/costas por corte geométrico de pernas, `gerar_idle_respiracao.py`) → `reduzir_16bit.py` (64×72, paleta global de 64 cores; se o verde da lata sumir, cai para paleta em duas partes 8 verdes + 56 gerais).
- `assets/` — saída do pipeline. `assets/personagem/16bit/` só guarda os 4 strips (+`@8x` de conferência) — é o que o jogo carrega; `reduzir_16bit.py` processa os frames individuais em memória e não os salva (evita saída redundante). Os 336×380 em `assets/personagem/` são intermediários (inputs do pipeline). Strips (4 células de 64×72): idle (frontal, ordem 1-2-3-2), walk (lateral, olhando p/ direita — espelhar p/ esquerda), walk_front (descendo), walk_back (subindo).
- `assets/tileset_cenario.png` (8 colunas, lista `cenario`), `tileset_obstaculos.png` (5 colunas, lista `obstaculos`), `tileset_industrial.png` (8 colunas, lista `industrial`). **A ordem das listas é contrato com o `web/index.html`**, que mapeia célula por índice (`col=i%cols, row=i//cols`) — não reordenar, só preencher slots vazios. Obstáculos e estruturas industriais têm fundo transparente (camada desenhada por cima do piso).
- `web/` — protótipo jogável (`index.html` + vanilla JS em `web/js/`, sem build; joystick virtual por pointer events + WASD). Terreno pré-renderizado em canvas offscreen; estruturas industriais desenhadas em camada por cima do piso; entidades ordenadas por Y; sombras + vinheta. Assets referenciados como `../assets/` (servir a raiz do projeto).
  - `web/js/` — código do jogo, um arquivo por assunto, carregado via `<script src>` sequencial (sem módulos, sem build — mesmo esquema de `web/screens/*.js`). **A ordem das tags `<script>` no `index.html` é a ordem de dependência**: cada arquivo pode usar consts/funções só dos arquivos carregados antes dele. Ordem atual: `constantes.js` (tamanhos/escala/hash) → `tilesets.js` (posição de cada peça nos PNGs) → `mapa.js` (layout, colisão, colecionáveis) → `assets.js` (carregamento de imagens, terreno pré-renderizado) → `entidades.js` (estado/física do personagem) → `telas.js` (menu/config/personagem) → `input.js` (teclado/joystick) → `render.js` (desenho + HUD) → `main.js` (loop, resize, start). Ao adicionar um arquivo novo, encaixar na posição certa dessa cadeia.
- `godot/` — esqueleto Godot 4 configurado (GL Compatibility, 640×360, filtro nearest). Em espera.
- `assets/telas/` — mockups das telas de UI (menu, config, personagem), geradas por `tools/gerar_telas_menu.py`.

## Regras de trabalho

- Implementação de código é delegada a subagentes (modelo mais barato capaz); decisões de arquitetura, revisão e validação final ficam no modelo principal — validar SEMPRE visualmente assets/telas geradas (ler os PNGs) antes de dar por concluído.
- Responder sempre em português BR.
