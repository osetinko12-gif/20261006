import random, math
from PIL import Image, ImageDraw
W,H,FPS,SEC=320,180,12,5
random.seed(3)
stars=[(random.randrange(W),random.randrange(120)) for _ in range(60)]
SIL=(12,14,28)
def bike(d,x,y,f):
    # wheels
    for cx in (x,x+16):
        d.ellipse([cx-5,y-5,cx+5,y+5],outline=SIL)
        a=f*0.8
        d.line([cx+int(4*math.cos(a)),y+int(4*math.sin(a)),cx-int(4*math.cos(a)),y-int(4*math.sin(a))],fill=SIL)
    d.line([x,y,x+7,y-6,x+16,y],fill=SIL); d.line([x+7,y-6,x+14,y-7],fill=SIL)
    d.line([x+14,y-7,x+16,y],fill=SIL); d.line([x+14,y-7,x+15,y-11],fill=SIL)
    # boy
    d.rectangle([x+6,y-16,x+10,y-7],fill=SIL); d.rectangle([x+7,y-21,x+11,y-17],fill=SIL)
    d.line([x+10,y-14,x+15,y-11],fill=SIL); d.line([x+8,y-7,x+9+(f%2),y-2],fill=SIL)
    # basket + ET head with cloak
    d.rectangle([x+15,y-12,x+21,y-8],fill=SIL); d.ellipse([x+15,y-17,x+21,y-11],fill=SIL)
for f in range(FPS*SEC):
    im=Image.new('RGB',(W,H),(18,24,56)); d=ImageDraw.Draw(im)
    for i in range(6): d.rectangle([0,120+i*4,W,124+i*4],fill=(18+i*4,24+i*5,56+i*6))
    for x,y in stars:
        if (x*7+y+f)%11: d.point((x,y),fill=(220,220,255))
    mx,my,r=200,72,46
    d.ellipse([mx-r,my-r,mx+r,my+r],fill=(245,240,215))
    for cx,cy,cr in [(185,60,6),(215,85,8),(205,55,3),(180,90,4)]:
        d.ellipse([cx-cr,cy-cr,cx+cr,cy+cr],fill=(225,220,195))
    # pine treeline
    for tx in range(-4,W,9):
        h=26+((tx*37)%17)
        d.polygon([(tx,H),(tx+5,H-h),(tx+10,H)],fill=SIL)
    d.rectangle([0,H-12,W,H],fill=SIL)
    t=f/(FPS*SEC)
    bx=int(110+t*190); by=int(110-t*55+math.sin(t*math.pi)*-8)
    bike(d,bx,by,f)
    im.resize((1920,1080),Image.NEAREST).save(f'f{f:04d}.png')
