import numpy as np, wave, math, random
from PIL import Image, ImageDraw
W,H,FPS,SEC=320,180,12,6
random.seed(1)
stars=[(random.randrange(W),random.randrange(90)) for _ in range(40)]
SKY=[(20,16,48),(48,32,88),(120,60,110),(230,110,90),(250,180,90)]
for f in range(FPS*SEC):
    im=Image.new('RGB',(W,H)); d=ImageDraw.Draw(im)
    for i,c in enumerate(SKY): d.rectangle([0,i*20,W,i*20+20],fill=c)
    for x,y in stars:
        if y<40 and (x+f)%7: d.point((x,y),fill=(255,255,220))
    d.rectangle([140,82,180,100],fill=(255,210,80))  # sun
    d.rectangle([0,100,W,H],fill=(40,30,90))
    for y in range(102,H,4):
        for x in range((f*2+y*3)%16,W,16):
            if abs(x-160)<20+(y-100)//2: d.line([x,y,x+5,y],fill=(255,200,90))
            elif (x//16+y)%3==0: d.line([x,y,x+3,y],fill=(90,70,150))
    sx=int(-40+f*1.0); by=104+(1 if (f//3)%2 else 0)
    d.polygon([(sx,by),(sx+36,by),(sx+30,by+6),(sx+6,by+6)],fill=(30,20,30))
    d.rectangle([sx+17,by-22,sx+18,by],fill=(30,20,30))
    d.polygon([(sx+19,by-20),(sx+30,by-4),(sx+19,by-4)],fill=(240,230,210))
    im.resize((1920,1080),Image.NEAREST).save(f'f{f:04d}.png')
SR=44100
def sq(fr,dur,vol=.15):
    t=np.arange(int(SR*dur))/SR
    w=np.sign(np.sin(2*np.pi*fr*t))*vol if fr else t*0
    return w*np.clip(1-t/dur*1.2,0,1)
notes=[523,659,784,659,587,698,880,698,523,659,784,1047,988,784,659,0]
bass=[131,131,175,175,131,131,196,196]
mel=np.concatenate([sq(n,.375) for n in notes])
bs=np.concatenate([sq(b,.75,.1) for b in bass])
n=min(len(mel),len(bs)); a=mel[:n]+bs[:n]
with wave.open('m.wav','w') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
    w.writeframes((a*32767).astype(np.int16).tobytes())
