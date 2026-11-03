# Elige automaticamente el mejor tramo de ENTRENAR_VOZ (11 min de tu voz) para usarlo
# como referencia de Chatterbox (voz_ia.py).
#
# Por que: voz_ia.py usaba los PRIMEROS 30 s de MUESTRA_VOZ.* tal cual. Si ese arranque tiene
# ruido, dudas, respiraciones o un tono distinto al del canal, la voz clonada sale rara.
# Este script escanea todo el audio, puntua cada tramo de ~15 s y guarda el mejor como
# MUESTRA_VOZ.wav en "Generador PC". Asi voz_ia.py lo usa sin cambiar nada mas.
#
# Uso (doble clic en ELEGIR_VOZ.bat):
#   elegir_voz.py            -> analiza, guarda el mejor tramo y genera 3 pruebas para escuchar
#   elegir_voz.py --opcion 2 -> usa el 2do mejor tramo (si el 1ro no te convence)
#   elegir_voz.py --sin-prueba -> solo elige el tramo, no genera audio de prueba
import os, sys, glob, json, wave, string, shutil, subprocess, datetime, traceback
import numpy as np

SEG = 15.0          # duracion del tramo de referencia (s)
SR = 24000          # Chatterbox trabaja a 24 kHz
HOP = 0.5           # paso entre tramos candidatos (s)
FR = 0.025          # frame de analisis (s)
TOP = 3             # cuantos candidatos guardar
FRASE_PRUEBA = ("Esa noche el camino estaba vacío. Entonces lo vi, al costado de la ruta: "
                "un jinete vestido de negro, quieto, esperándome. Y supe que no tenía que mirarlo a la cara.")

NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)
BASE = r"D:\HistoriasIA" if os.path.isdir(r"D:\HistoriasIA") else os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, "log.txt")


def log(*a):
    msg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + "[elegir voz] " + " ".join(str(x) for x in a)
    print(msg)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def drive_root():
    for letter in string.ascii_uppercase:
        for name in ("Mi unidad", "My Drive"):
            p = f"{letter}:\\{name}"
            if os.path.isdir(p):
                return p
    return None


def carpeta_generador():
    lv = os.path.join(drive_root() or "", "Leyenda videos")
    for c in sorted(glob.glob(os.path.join(lv, "Configuraci*", "Generador PC"))) + [os.path.join(lv, "Generador PC")]:
        if os.path.isdir(c):
            return c
    here = os.path.dirname(os.path.abspath(__file__))
    return here


def ffmpeg():
    for p in (os.path.join(BASE, "ffmpeg", "ffmpeg.exe"), shutil.which("ffmpeg") or ""):
        if p and os.path.exists(p):
            return p
    raise RuntimeError("No encuentro ffmpeg (esperaba " + os.path.join(BASE, "ffmpeg", "ffmpeg.exe") + ")")


def decodificar(src, dst, extra=()):
    subprocess.run([ffmpeg(), "-y", "-i", src, "-ac", "1", "-ar", str(SR), *extra, "-c:a", "pcm_s16le", dst],
                   check=True, capture_output=True, creationflags=NOWIN)


def leer_wav(path):
    with wave.open(path, "rb") as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    return x


def escribir_wav(path, x):
    y = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())


# ---------------- analisis ----------------
def frames_db(x):
    n = int(SR * FR)
    k = len(x) // n
    f = x[:k * n].reshape(k, n)
    rms = np.sqrt((f ** 2).mean(1) + 1e-12)
    peak = np.abs(f).max(1)
    return 20 * np.log10(rms), peak, f


def pitch_frames(f):
    # tono aproximado por autocorrelacion (80-300 Hz), 0 si no es sonoro
    lo, hi = int(SR / 300), int(SR / 80)
    out = np.zeros(len(f))
    for i, fr in enumerate(f):
        fr = fr - fr.mean()
        e = (fr ** 2).sum()
        if e < 1e-6:
            continue
        ac = np.correlate(fr, fr, "full")[len(fr) - 1:]
        seg = ac[lo:hi]
        j = int(seg.argmax())
        if seg[j] / ac[0] > 0.45:
            out[i] = SR / (lo + j)
    return out


def puntuar(db, peak):
    nf = int(round(SEG / FR))
    paso = int(round(HOP / FR))
    piso = np.percentile(db, 10)                 # ruido de fondo global
    umbral = max(piso + 6, db.max() - 45)       # por encima = habla
    voz = db > umbral
    res = []
    for s in range(0, len(db) - nf, paso):
        d, v, p = db[s:s + nf], voz[s:s + nf], peak[s:s + nf]
        ratio = v.mean()
        if ratio < 0.35:
            continue
        # silencio mas largo dentro del tramo
        run = mx = 0
        for b in v:
            run = 0 if b else run + 1
            mx = max(mx, run)
        sil_max = mx * FR
        ruido = np.percentile(d[~v], 50) if (~v).sum() > 5 else piso
        snr = d[v].mean() - ruido
        estab = d[v].std()                       # volumen parejo
        clip = (p > 0.98).mean()
        # que empiece y termine en silencio (no cortar palabras)
        bordes = (0 if v[:4].any() else 1) + (0 if v[-4:].any() else 1)
        score = (snr * 1.0 - estab * 0.8 - max(0, sil_max - 0.6) * 15 - clip * 400
                 - abs(ratio - 0.65) * 20 + bordes * 2)
        res.append((score, s, dict(snr=snr, estab=estab, sil_max=sil_max, ratio=ratio, clip=clip)))
    return res


def elegir(x):
    db, peak, f = frames_db(x)
    cands = sorted(puntuar(db, peak), reverse=True)
    if not cands:
        raise RuntimeError("No encontre tramos de habla continua en el audio")
    nf = int(round(SEG / FR))
    # reordenar los mejores 20 (sin solaparse) premiando tono grave y estable
    elegidos = []
    for sc, s, info in cands:
        if any(abs(s - e[1]) < nf for e in elegidos):
            continue
        elegidos.append([sc, s, info])
        if len(elegidos) >= 20:
            break
    for e in elegidos:
        pf = pitch_frames(f[e[1]:e[1] + nf])
        pv = pf[pf > 0]
        if len(pv) > 20:
            med, var = np.median(pv), np.std(pv) / np.median(pv)
            e[2].update(tono_hz=float(med), var_tono=float(var))
            e[0] += -max(0, med - 140) * 0.05 - max(0, var - 0.25) * 20
    elegidos.sort(key=lambda e: -e[0])
    return elegidos[:TOP]


def recortar(x, s_frame):
    a = int(s_frame * FR * SR)
    b = a + int(SEG * SR)
    y = x[a:b].copy()
    fade = int(0.05 * SR)
    y[:fade] *= np.linspace(0, 1, fade)
    y[-fade:] *= np.linspace(1, 0, fade)
    # normalizar a ~-18 dBFS RMS sin pasar -1 dB de pico
    rms = np.sqrt((y ** 2).mean() + 1e-12)
    y *= min(10 ** (-18 / 20) / rms, 10 ** (-1 / 20) / (np.abs(y).max() + 1e-9))
    return y


# ---------------- prueba con Chatterbox ----------------
def generar_pruebas(refs, gen):
    os.environ["HF_HOME"] = os.path.join(BASE, "hf_cache")
    os.environ["HF_HUB_DISABLE_XET"] = "1"
    import torch, torchaudio as ta
    _load = torch.load
    torch.load = lambda *a, **k: _load(*a, **{**k, "map_location": k.get("map_location") or "cpu"})
    torch.set_num_threads(max(2, (os.cpu_count() or 4) - 2))
    try:
        import perth
        if getattr(perth, "PerthImplicitWatermarker", None) is None:
            perth.PerthImplicitWatermarker = perth.DummyWatermarker
    except Exception:
        pass
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    cfg = json.load(open(os.path.join(gen, "voz_ia.json"), encoding="utf-8"))
    log("Cargando Chatterbox para generar pruebas (tarda unos minutos)...")
    model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    for i, ref in enumerate(refs, 1):
        torch.manual_seed(1234)
        w = model.generate(FRASE_PRUEBA, language_id="es", audio_prompt_path=ref,
                           exaggeration=cfg.get("exaggeration", 0.4), cfg_weight=cfg.get("cfg_weight", 0.5),
                           temperature=cfg.get("temperature", 0.7))
        out = os.path.join(gen, f"PRUEBA_VOZ_opcion{i}.wav")
        ta.save(out, w.cpu(), model.sr)
        log("Prueba lista:", out)


def main():
    opcion = 1
    if "--opcion" in sys.argv:
        opcion = int(sys.argv[sys.argv.index("--opcion") + 1])
    gen = carpeta_generador()
    src = next((p for p in [os.path.join(gen, "ENTRENAR_VOZ")] + glob.glob(os.path.join(gen, "ENTRENAR_VOZ.*"))
                if os.path.isfile(p)), None)
    if not src:
        raise RuntimeError("No encuentro ENTRENAR_VOZ en " + gen)
    tmp = os.path.join(BASE, "tmp", "elegir_voz")
    os.makedirs(tmp, exist_ok=True)
    wav = os.path.join(tmp, "entrenar_24k.wav")
    log("Leyendo", src)
    decodificar(src, wav, ["-af", "highpass=f=70"])
    x = leer_wav(wav)
    log(f"Audio de {len(x)/SR/60:.1f} min. Analizando tramos de {SEG:.0f} s...")
    top = elegir(x)
    refs, resumen = [], []
    for i, (sc, s, info) in enumerate(top, 1):
        y = recortar(x, s)
        p = os.path.join(tmp, f"candidato{i}.wav")
        escribir_wav(p, y)
        refs.append(p)
        t = s * FR
        resumen.append(f"opcion {i}: {int(t//60)}:{t%60:04.1f} a {int((t+SEG)//60)}:{(t+SEG)%60:04.1f}  "
                       f"puntaje {sc:.1f}  " + ", ".join(f"{k}={v:.2f}" for k, v in info.items()))
        log(resumen[-1])
    if opcion > len(refs):
        raise RuntimeError(f"Solo hay {len(refs)} opciones")
    # guardar la elegida como MUESTRA_VOZ.wav (las viejas quedan como .version-vieja)
    for old in glob.glob(os.path.join(gen, "MUESTRA_VOZ.*")):
        if not old.endswith(".version-vieja"):
            os.replace(old, old + ".version-vieja")
    shutil.copy(refs[opcion - 1], os.path.join(gen, "MUESTRA_VOZ.wav"))
    with open(os.path.join(gen, "voz_elegida.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"Usando opcion {opcion}\n" + "\n".join(resumen) + "\n")
    log(f"Listo: MUESTRA_VOZ.wav = opcion {opcion}")
    if "--sin-prueba" not in sys.argv:
        generar_pruebas(refs, gen)
        log("Escucha PRUEBA_VOZ_opcion1/2/3.wav en 'Generador PC'. Si preferis otra, corre: ELEGIR_VOZ.bat 2 (o 3)")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log("ERROR", traceback.format_exc())
        sys.exit(1)
