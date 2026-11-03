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

## Estado / pendientes
- [ ] Correr `ELEGIR_VOZ.bat` (elige el mejor tramo de 15 s de ENTRENAR_VOZ → `MUESTRA_VOZ.wav` y genera `PRUEBA_VOZ_opcion1-3.wav`). Escuchar y elegir.
- [ ] Bajar en `voz_ia.json`: exaggeration 0.55→0.4, temperature 0.8→0.7.
- [ ] Regrabar/regenerar Luz Mala Parte 2 (`LM_P2V`, marcada REGRABAR).
- [ ] Al terminar cada sesión: actualizar esta sección.
