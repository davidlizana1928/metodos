import numpy as np, soundfile as sf, json
SR=44100; seg=json.load(open('segments.json'))
D=seg[-1]['end']+1.0
n=int(D*SR); t=np.arange(n)/SR
beat=0.6; bar=2.4
rng=np.random.default_rng(3)
def note(f): return 440*2**((f-69)/12)
# chords (midi) Dm, Bb, F, C  -> moody
chords=[[50,57,62,65],[46,53,58,62],[41,48,57,60],[48,55,60,64]]
pad=np.zeros(n)
cl=2*bar
for ci in range(int(D/cl)+1):
    ch=chords[ci%4]; s=int(ci*cl*SR); e=min(n,int((ci+1)*cl*SR+0.6*SR))
    if s>=n: break
    tt=np.arange(e-s)/SR; env=np.minimum(1,tt/0.8)*np.minimum(1,np.maximum(0,(e-s)/SR-tt)/0.6)
    for m in ch:
        f=note(m)
        for det in (-0.12,0.12):
            ph=rng.uniform(0,6.28)
            pad[s:e]+=env*(np.sin(2*np.pi*f*(1+det/100)*tt+ph)+0.3*np.sin(4*np.pi*f*tt+ph))*0.05
    # bass
    f=note(ch[0]-12); pad[s:e]+=env*np.sin(2*np.pi*f*tt)*0.12
# soft low pulse every beat
kick=np.zeros(n)
kl=int(0.35*SR); kt=np.arange(kl)/SR
k=np.sin(2*np.pi*(50+70*np.exp(-kt*25))*kt)*np.exp(-kt*9)
for b in np.arange(0,D,beat):
    i=int(b*SR); acc=1.0 if round(b/beat)%4==0 else 0.55
    kick[i:i+kl]+=k[:n-i]*acc*0.35
# tick each half beat
tick=np.zeros(n); tl=int(0.05*SR)
noise=rng.standard_normal(tl); noise=np.diff(np.concatenate([[0],noise]))*np.exp(-np.arange(tl)/SR*80)
for b in np.arange(0,D,beat/2):
    i=int(b*SR); tick[i:i+tl]+=noise[:n-i]*0.035
# end: fade out last 2.5s
y=pad+kick+tick
y*=np.minimum(1,t/0.3)*np.minimum(1,(D-t)/2.5)
y=y/np.abs(y).max()*0.9
sf.write('music.wav',y.astype(np.float32),SR)
print(D)
