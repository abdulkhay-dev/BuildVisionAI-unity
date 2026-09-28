import sys, json; sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent/'lib'))
import numpy as np, tr, inks, track
from PIL import Image, ImageDraw
from scipy import ndimage
which=sys.argv[1]
if which=='twig':
    PANE=(141.5,0,277,2000); files=['p014_gleys-1-twig__3d-cappuccino.jpg','p014_gleys-1-twig__3d-wenge.jpg']
else:
    PANE=(272.0,0,518.0,2000); files=['p014_gleys-2-twig__3d-cappuccino.jpg','p014_gleys-2-twig__3d-wenge.jpg']
W,H=PANE[2]-PANE[0],PANE[3]-PANE[1]
views=[];darks=[]
for f in files:
    rgb,g,bg,dark,white=inks.satin_ink(f, level=150, win=41)
    v=tr.View(f,PANE,np.clip(dark,0,1),psf=0.5)
    v.weight=inks.box_weight(dark.shape, v, [(-30,900,70,1060)])
    views.append(v); darks.append(dark)
    print(f, tr.leaf_of(f)['sx'])
grid=tr.Grid(W,H,4.0)
D=tr.field_from_views(grid,views,darks)
np.save(which+'_D.npy',D)
im=Image.fromarray(np.uint8(255-np.clip(D,0,1)*230)).convert('RGB')
d=ImageDraw.Draw(im)
for y in range(0,2001,50):
    r=(H-y)*4; d.line([(0,r),(8 if y%100 else 20,r)],fill=(255,0,0)); 
    if y%100==0: d.text((22,r-5),str(y),fill=(255,0,0))
for x in range(0,int(W)+1,10):
    d.line([(x*4,0),(x*4,6 if x%50 else 14)],fill=(0,0,255))
im.save(which+'_D.png')
