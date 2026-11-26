# Instrucciones del proyecto

## Videos de reseñas (TikTok)

### Voz de la narración (obligatorio)
- La voz siempre debe ser **neural, nativa de español latino neutro** (espeak `es-419`).
- Voz por defecto: Piper `es_MX-claude-high` (en `~/piper/es_MX-claude-high.onnx`). Alternativa: `es_MX-ald-medium`.
- **Nunca** usar voces entrenadas en otro idioma con fonemas en español (por ejemplo, voces de Kokoro en inglés), ni voces de España (`es-ES`, con «z/c» como θ).
  Tampoco usar MBROLA ni espeak puro como voz final.
- Si la voz no está disponible, descargarla desde
  `https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/claude/high/es_MX-claude-high.onnx` (y su `.onnx.json`).
  Si la red lo bloquea, pedir acceso a Hugging Face antes de seguir; no sustituirla por otra voz.
- Los títulos en inglés se escriben para que suenen como los diría un hablante latino
  (ej.: «The Discovery» → «De Discóveri»), con el diccionario `FIX` de `the-discovery/src/voice.py`.
- La voz se genera en una sola pista continua (sin silencios > 0,4 s) y la imagen se ajusta a sus tiempos.

### Plantilla
`the-discovery/src/` contiene el flujo completo: `voice.py` (voz), `music.py` (música 100 BPM),
`scenes.py` + `render.py` (imagen 1080×1920, 30 fps). `voice.py` falla si la voz no es `es-419`.
