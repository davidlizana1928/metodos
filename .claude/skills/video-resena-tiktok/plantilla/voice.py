import os, sys, json
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

# REGLA: voz por defecto del proyecto = Kokoro "em_alex" (voz masculina de español de Kokoro),
# SIEMPRE con fonemas de español latino neutro (espeak es-419, con seseo). Nunca voces inglesas
# ni pronunciación de España (θ).
KDIR = os.path.expanduser("~/kokoro")
VOICE = os.environ.get("VOICE", "em_alex")
LANG = "es-419"
assert VOICE.startswith("em_") or VOICE.startswith("ef_"), "Solo voces de español de Kokoro (em_/ef_)"
k = Kokoro(os.path.join(KDIR, "kokoro-q8.onnx"), os.path.join(KDIR, "voices_es.npz"))
SPEED = float(sys.argv[1]) if len(sys.argv) > 1 else 1.05
SR = 24000
# Pronunciación de títulos en inglés como la diría un hablante latino
FIX = {"Resident Evil": "Résident Ívil"}
P=["Imagina que la ciudad a la que viajas se llena de monstruos esta noche…",
"y tú no eres un héroe: eres el repartidor que debe cruzarla.",
"Llevas órganos y material médico entre hospitales. No eres soldado ni policía, y nunca has disparado un arma de verdad.",
"Tu novia está embarazada, y cada vez que te llama para hablarlo, esquivas el tema.",
"Pero esta noche, con tu turno ya terminado, te ofrecen un último encargo que paga el doble:",
"llevar un paquete al hospital de una ciudad en las montañas. En plena tormenta de nieve.",
"Y lo peor es que, en la carretera helada, una mujer aparece frente a tu auto y no alcanzas a frenar.",
"Un policía se ofrece a llevarlos a ambos al hospital… pero algo sale terriblemente mal.",
"Lo que no sabes es que un virus escapó del laboratorio de una poderosa empresa y transforma a la gente de la zona en criaturas.",
"Un perro deforme te persigue hasta una granja aislada… y el dueño también está infectado.",
"Llegaste para hacer una entrega y volver a casa, y terminas consiguiendo armas y aprendiendo a disparar sobre la marcha, solo para seguir vivo.",
"Y justo cuando crees que lo peor pasó, algo te muerde el brazo… y tu cuerpo empieza a cambiar.",
"Entonces aparecen dos empleados de la empresa que provocó todo esto.",
"Se trata de Resident Evil: Noche Cero…",
"Si fueras tú, ¿seguirías adelante para entregar el paquete… o lo dejarías todo para volver con tu novia?"]
def synth(t):
    for a, r in FIX.items():
        t = t.replace(a, r)
    ph = k.tokenizer.phonemize(t, LANG)
    assert "θ" not in ph, "Pronunciación de España detectada"
    a, _ = k.create(ph, voice=VOICE, speed=SPEED, is_phonemes=True)
    return a

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
        g=0.15 if i in (1,14) else GAP
        out.append(np.zeros(int(g*SR),np.float32)); t+=g
    segs.append({'i':i+1,'start':round(t,3),'end':round(t+len(a)/SR,3),'text':p})
    out.append(a.astype(np.float32)); t+=len(a)/SR
y=np.concatenate(out); y=y/np.abs(y).max()*0.89
sf.write('voice.wav',y,SR)
json.dump(segs,open('segments.json','w'),ensure_ascii=False,indent=1)
for s in segs: print(s['i'],s['start'],s['end'],round(s['end']-s['start'],2))
print('total',t)
