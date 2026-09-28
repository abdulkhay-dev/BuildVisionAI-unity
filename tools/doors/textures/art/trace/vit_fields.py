import sys; sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent/'lib'))
import numpy as np, tr, inks
from PIL import Image, ImageDraw
PANE=(290.5,199.0,488.5,1792.5)
W,H=PANE[2]-PANE[0],PANE[3]-PANE[1]
files=['p012_trend-14__3d-cappuccino.jpg','p012_trend-14__3d-grey.jpg','p012_trend-14__3d-wenge.jpg']
views=[];darks=[]
for f in files:
    L=tr.leaf_of(f); print(f,{k:round(L[k],2) for k in ('x0','x1','y0','y1','sx','sy')})
    rgb,g,bg,dark,white=inks.satin_ink(f, level=25, win=31, pct=90)
    v=tr.View(f,PANE,np.clip(dark,0,1),psf=0.5)
    views.append(v); darks.append(dark)
grid=tr.Grid(W,H,4.0)
D=tr.field_from_views(grid,views,darks)
np.save('vit_D.npy',D)
im=Image.fromarray(np.uint8(255-np.clip(D,0,1)*255)).convert('RGB')
d=ImageDraw.Draw(im)
for y in range(0,int(H)+1,50):
    r=(H-y)*4; d.line([(0,r),(8 if y%100 else 20,r)],fill=(255,0,0))
    if y%100==0: d.text((22,r-5),str(y),fill=(255,0,0))
for x in range(0,int(W)+1,10):
    d.line([(x*4,0),(x*4,6 if x%50 else 14)],fill=(0,0,255))
h=im.height//3
s=Image.new('RGB',(im.width*3+20,h),'white')
for k in range(3): s.paste(im.crop((0,k*h,im.width,(k+1)*h)),(k*(im.width+10),0))
s.save('vit_D3.png'); print(s.size)
