import json, os, sys
import numpy as np, soundfile as sf
from piper import PiperVoice, SynthesisConfig

# REGLA: la narración se hace SOLO con una voz neural nativa de español latino neutro (espeak es-419).
# Nunca usar voces entrenadas en otro idioma (p. ej. Kokoro en inglés) ni voces de España.
MODEL = os.environ.get("VOICE_MODEL", os.path.expanduser("~/piper/es_MX-claude-high.onnx"))
cfg = json.load(open(MODEL + ".json"))
assert cfg["espeak"]["voice"] == "es-419", "La voz debe ser nativa de español latino (es-419)"
v = PiperVoice.load(MODEL)
LENGTH = float(sys.argv[1]) if len(sys.argv) > 1 else 0.82
SR = v.config.sample_rate
# Pronunciación de títulos en inglés como la diría un hablante latino
FIX = {"The Discovery": "De Discóveri"}
P=["Imagina que un científico demuestra que existe una vida después de la muerte… y que ese científico es tu padre.",
"Pero en vez de traer paz, la noticia trae algo terrible: millones de personas deciden quitarse la vida para llegar antes al otro lado.",
"En las calles, pantallas gigantes llevan la cuenta.",
"Para ti, tu padre no es un héroe: es el culpable.",
"Y quieres obligarlo a decir en público que su descubrimiento es falso.",
"Pero un día, en el ferry a la isla donde él vive escondido, conoces a una mujer que te mira como si ya te conociera.",
"Ella habla de la muerte como una salida fácil.",
"Poco después la encuentras en la playa, a punto de rendirse… y la salvas.",
"Y lo peor es que tu padre ya no está solo.",
"Vive en una mansión aislada, rodeado de seguidores que alguna vez quisieron morir y ahora lo obedecen.",
"Lo que no sabes es que está construyendo una máquina capaz de mostrar lo que una persona ve después de morir.",
"Y para probarla necesita un cuerpo.",
"Tú, que llegaste a desenmascararlo, terminas de noche en una morgue, robando un cadáver junto a tu hermano y la mujer que salvaste.",
"Ya no eres el hijo que vino a detenerlo… eres su cómplice.",
"Y justo cuando la pantalla de la máquina, que parecía muerta, empieza a mostrar algo…",
"Se trata de The Discovery.",
"Si fueras tú, ¿querrías saber qué hay del otro lado… aunque eso cambie cómo vives esta vida?"]
def synth(t):
    for k, r in FIX.items():
        t = t.replace(k, r)
    ch = list(v.synthesize(t, SynthesisConfig(length_scale=LENGTH)))
    return np.concatenate([c.audio_float_array for c in ch])

def compress(a,maxs=0.30,th=0.015):
    w=int(SR*0.02); keep=[]; run=[]
    for i in range(0,len(a),w):
        c=a[i:i+w]
        if np.abs(c).max()<th: run.append(c)
        else:
            keep+=run[:int(maxs*SR/w)]; run=[]; keep.append(c)
    keep+=run[:int(maxs*SR/w)]
    return np.concatenate(keep)
def trim(a,th=0.01):
    idx=np.where(np.abs(a)>th)[0]
    return a[max(idx[0]-int(SR*0.01),0):idx[-1]+int(SR*0.02)]
segs=[];t=0.0;out=[]
GAP=0.18
for i,p in enumerate(P):
    a=synth(p)
    a=compress(trim(a))
    if i>0:
        g=0.15 if i in (15,) else GAP
        out.append(np.zeros(int(g*SR),np.float32)); t+=g
    segs.append({'i':i+1,'start':round(t,3),'end':round(t+len(a)/SR,3),'text':p})
    out.append(a.astype(np.float32)); t+=len(a)/SR
y=np.concatenate(out); y=y/np.abs(y).max()*0.89
sf.write('voice.wav',y,SR)
json.dump(segs,open('segments.json','w'),ensure_ascii=False,indent=1)
for s in segs: print(s['i'],s['start'],s['end'],round(s['end']-s['start'],2))
print('total',t)
