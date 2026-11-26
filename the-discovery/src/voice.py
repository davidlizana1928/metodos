import json, numpy as np, soundfile as sf, sys
from kokoro_onnx import Kokoro
S='/tmp/claude-0/-home-user-metodos/f6e0a16b-596d-57fc-bc23-6a586aa69e8d/scratchpad/'
k=Kokoro(S+'kokoro-q8.onnx',S+'voices.npz')
VOICE=sys.argv[1] if len(sys.argv)>1 else 'am_michael'
SPEED=float(sys.argv[2]) if len(sys.argv)>2 else 1.0
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
def ph(t):
    if 'The Discovery' in t:
        return k.tokenizer.phonemize('Se trata de','es-419')+' ðə dɪskˈʌvəɹi.'
    p=k.tokenizer.phonemize(t,'es-419')
    return p.replace('fˈeri','fˈeri')
SR=24000
def compress(a,maxs=0.30,th=0.015):
    w=480; keep=[]; run=[]
    for i in range(0,len(a),w):
        c=a[i:i+w]
        if np.abs(c).max()<th: run.append(c)
        else:
            keep+=run[:int(maxs*SR/w)]; run=[]; keep.append(c)
    keep+=run[:int(maxs*SR/w)]
    return np.concatenate(keep)
def trim(a,th=0.01):
    idx=np.where(np.abs(a)>th)[0]
    return a[max(idx[0]-240,0):idx[-1]+480]
segs=[];t=0.0;out=[]
GAP=0.18
for i,p in enumerate(P):
    a,sr=k.create(ph(p),voice=VOICE,speed=SPEED,is_phonemes=True)
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
