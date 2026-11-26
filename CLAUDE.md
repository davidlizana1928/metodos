# Instrucciones del proyecto

## Videos de reseñas (TikTok)

### Voz de la narración (obligatorio)
- **Voz por defecto de todos los proyectos: «Alex»** = Kokoro `em_alex` (voz masculina de español de Kokoro),
  elegida por el usuario. Usarla siempre salvo que el usuario pida otra.
- Siempre con **pronunciación de español latino neutro**: fonemas espeak `es-419` (con seseo), velocidad 1.05.
  `the-discovery/src/voice.py` ya lo hace y falla si aparece pronunciación de España (θ).
- Archivos (los instala el script de preparación del entorno en `~/kokoro/`):
  - `kokoro-q8.onnx` ← `https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/onnx/model_quantized.onnx`
  - `em_alex.bin` ← `.../resolve/main/voices/em_alex.bin`, convertido a `voices_es.npz` (forma 510×1×256, float32).
  Si faltan, descargarlos; si la red lo bloquea, pedir acceso a Hugging Face antes de seguir. No sustituir Alex por otra voz sin preguntar.
- **Nunca** usar voces inglesas de Kokoro (`am_*`, `af_*`, `bm_*`…) con fonemas en español, ni voces de España (`es-ES`),
  ni MBROLA o espeak puro como voz final.
- Alternativas solo si el usuario las pide: Piper `es_MX-claude-high` / `es_MX-ald-medium` (nativas `es-419`).
- Los títulos en inglés se escriben como los diría un hablante latino
  (ej.: «The Discovery» → «De Discóveri»), con el diccionario `FIX` de `voice.py`.
- La voz se genera en una sola pista continua (sin silencios > 0,4 s) y la imagen se ajusta a sus tiempos.

### Plantilla
`the-discovery/src/` contiene el flujo completo: `voice.py` (voz), `music.py` (música 100 BPM),
`scenes.py` + `render.py` (imagen 1080×1920, 30 fps).
