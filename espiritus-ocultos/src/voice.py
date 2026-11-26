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
FIX = {}
P=["Imagina que despiertas encerrada en el mismo psiquiátrico donde trabajas… acusada de asesinar brutalmente a tu esposo. Y no recuerdas absolutamente nada.",
"Tres días antes, tu vida es otra: trabajas como doctora en un psiquiátrico dentro de una cárcel de mujeres, y tu esposo dirige ese mismo hospital.",
"Pero una noche de tormenta, mientras manejas por la carretera, una joven aparece de pie en medio del camino. Giras el volante para no atropellarla… y chocas.",
"Bajas a ayudarla. Ella se enciende en llamas frente a ti. Y todo se apaga.",
"Y lo peor es que, cuando abres los ojos, ya no eres la doctora.",
"Eres una paciente más, encerrada junto a tus antiguas pacientes, y tu colega de trabajo ahora es tu médico.",
"Lo que no sabes es que esa joven no es de este mundo… y te está usando para algo que todavía no entiendes.",
"Te sigue apareciendo dentro del hospital, pero solo tú puedes verla. Cada vez que intentas explicarlo, todos se convencen más de que eres culpable.",
"Llegaste a ese lugar para decidir quién está cuerdo… y ahora eres tú la que tiene que demostrar que no perdió la razón.",
"Y justo cuando empiezas a creer que todo está en tu cabeza… ella vuelve a aparecer frente a ti, y esta vez parece querer decirte algo.",
"Se trata de Espíritus ocultos: En compañía del miedo…",
"Si fueras tú, ¿confiarías en las pruebas que todos ven… o en la aparición que solo tú puedes ver?"]
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
        g=0.15 if i==10 else GAP
        out.append(np.zeros(int(g*SR),np.float32)); t+=g
    segs.append({'i':i+1,'start':round(t,3),'end':round(t+len(a)/SR,3),'text':p})
    out.append(a.astype(np.float32)); t+=len(a)/SR
y=np.concatenate(out); y=y/np.abs(y).max()*0.89
sf.write('voice.wav',y,SR)
json.dump(segs,open('segments.json','w'),ensure_ascii=False,indent=1)
for s in segs: print(s['i'],s['start'],s['end'],round(s['end']-s['start'],2))
print('total',t)

# control: ningún silencio > 0,4 s
w=int(SR*0.02); run=0; mx=0
for i in range(0,len(y),w):
    if np.abs(y[i:i+w]).max()<0.015: run+=1; mx=max(mx,run)
    else: run=0
print('max silencio',round(mx*0.02,2))
