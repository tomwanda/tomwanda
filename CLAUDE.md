# Historias De La Noche — memoria del proyecto

Responder siempre en español rioplatense. El usuario no programa: explicar simple y darle pasos concretos.

## El proyecto
- **Canal A — Terror "Historias De La Noche"** (principal): leyendas de terror latinoamericanas (y alguna extranjera) en episodios cortos de 3 partes.
  Calendario: 33 episodios del 10-11 al 11-12 (Charro Negro, Luz Mala, Novia de la Ruta 40, Silbón, Familiar, Kuchisake-onna, Lobizón, Hombre Gato, Salamanca, Enterrada viva de la Recoleta, Pisadeira).
  Códigos: `H01_P1` = historia 01 parte 1; `LM_P2` = Luz Mala parte 2.
- **Canal B — Supervivencia** (nuevo, recién arrancando): demo "El Búnker", texto Día 1.
- La vieja "biblia" de *El Archivo del Monte* (archivista, 14 de marzo) **ya no va**.

## Dónde está todo
- Google Drive → `Leyenda videos/`
  - `A - VIDEOS DE TERROR (Historias De La Noche)/` y `B - VIDEOS DE SUPERVIVENCIA (canal nuevo)/`, cada uno con
    `0 - Mi voz (notas de voz)`, `1 - Para revisar`, `2 - Aprobados`, `3 - Publicados`, `Configuración (no tocar)`.
  - `Configuración (no tocar)/Generador PC/`: scripts que corre la PC, `voz_ia.json`, `ENTRENAR_VOZ` (11 min de voz del usuario).
- PC: Windows, `D:\HistoriasIA`, Python 3.11, GPU **AMD RX 6700 XT 12 GB** (torch-directml, no CUDA).
- Este repo: copia de scripts nuevos (`generador_pc/`) y esta memoria.

## Pipeline
1. `generar.py`: imágenes con SDXL rápido (8 pasos). Tarea programada de Windows "HDN Generar Escenas" cada 20 min.
2. `voz_ia.py`: narración con **Chatterbox Multilingual** (MIT, por CPU) clonando `MUESTRA_VOZ.*` de "Generador PC".
   Parámetros en `voz_ia.json` (exaggeration, cfg_weight, temperature, lista de episodios).
3. `rvc_voz.py`: RVC (descartado: suena robótico y corta mal porque convierte una voz TTS base).
4. `armar_pc.py` / `stickman_pc.py`: arman el .mp4 con imágenes + voz + subtítulos.

## Decisiones
- Voz **gratis** hasta monetizar en YouTube; después pasar a **ElevenLabs** (el plan gratis de ElevenLabs no permite uso comercial).
- Siempre revisar los videos antes de subirlos. Declarar contenido IA en YouTube Studio.

## Fábrica multicanal (visto en Drive el 11-11)
- Carpeta `Generador PC/Fabrica multicanal/` (`worker.py`, `monitor.py`, `LEEME.md`, `estado.json`). En la PC: `D:\HistoriasIA-dev\fabrica`.
  Monitor en la PC: `http://127.0.0.1:8789/` o `VER_FABRICA.cmd`. Tarea "Fabrica audiovisual - Procesar pedidos" cada 10 min.
- Canales nuevos en Drive: `C - OTRA VIDA` (códigos `OV01`, `OV02`) y `D - CURIOSIDADES (canal nuevo)` (códigos `CUR01`…`CUR07`).
- La fábrica solo deja videos en `1 - Para revisar`; nunca los pasa a Aprobados/Publicados.
- Cada video publicado tiene un `.json` al lado en `3 - Publicados` con título, fecha `publishAt` y link de YouTube.

## Estado / pendientes (actualizado 11-11)
- Voces automáticas de terror **pausadas el 11-11** por sonar robóticas: los `*_IA.wav` se movieron a `Voces automaticas roboticas (11-11)`;
  `voz_ia.json` quedó solo con `H01_P1` y 19 episodios en `episodios_en_espera`. Voz de referencia aprobada: `9B - OFICIAL corregida`.
- [ ] Decidir la voz: escuchar `COMPARAR - 9B aprobada vs fabrica (11-11).mp3`.
- [ ] Terror, para revisar: H01_P2, H01_P3, H03_P2, H03_P3, H04_P1, H05_P1, H05_P2, H05_P3.
- [ ] Curiosidades, para revisar: CUR01_flamencos_v2, CUR02_pulpo_v1 y v3 (elegir una), CUR03_mariposa, CUR04_venus, CUR05_arcoiris, CUR06_luna, CUR07_wombat.
- [ ] Otra Vida, para revisar: OV02_GUIA_ABUELO_v1 (revisión final), OV01_PILOTO_v1, OV01_SHORT_v1.
- [ ] `LM_P2` quedó programado en YouTube para el 11-11 21:00 (hora Argentina); confirmar que la voz esté bien.
- [ ] Correr `ELEGIR_VOZ.bat` si todavía hace falta elegir muestra de voz.
- [ ] Al terminar cada sesión: actualizar esta sección.
