import sys, wave, json, numpy as np
from piper import PiperVoice
from piper.config import SynthesisConfig
S=sys.argv[1]; ls=float(sys.argv[2])
F=["Imagina que la ciudad a la que viajas se llena de monstruos esta noche…",
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
"Se trata de Resident Evil: Noche Cero… Si fueras tú, ¿seguirías adelante para entregar el paquete… o lo dejarías todo para volver con tu novia?"]
v=PiperVoice.load(S+"/voz/es_MX-ald-medium.onnx")
cfg=SynthesisConfig(length_scale=ls, noise_scale=0.6, noise_w_scale=0.7)
sr=v.config.sample_rate; out=[]
for i,t in enumerate(F):
    a=np.concatenate([c.audio_float_array for c in v.synthesize(t,cfg)])
    # trim silence
    idx=np.where(np.abs(a)>0.01)[0]; a=a[max(0,idx[0]-200):idx[-1]+800]
    out.append(a)
durs=[len(a)/sr for a in out]
json.dump({"sr":sr,"durs":durs},open(S+"/build/voz.json","w"))
np.save(S+"/build/voz.npy",np.array(out,dtype=object),allow_pickle=True)
print(sr,[round(d,2) for d in durs],round(sum(durs),2))
