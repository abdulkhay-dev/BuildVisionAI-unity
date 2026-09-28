import sys, json, pickle; sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent/'lib'))
import numpy as np, track, almond
from PIL import Image, ImageDraw
from scipy import ndimage
D=np.load('vit_D.npy'); res=4.0; H=1593.5; W=198
M=np.clip(D,0,1)
# mask leaves
for f in json.load(open('vit_leaves.json'))[:9]:
    poly=almond.almond((f['Bx'],f['By']),(f['Tx'],f['Ty']),f['wmax']+2.5,f['skew'],f['p'])
    m=almond.raster(poly,M.shape,res,H,0)
    M[m]=0
trs=track.track(M,res,H,thr=0.3,step_mm=1.0,max_jump_mm=1.2,max_gap_mm=12,min_len_mm=25,smooth_mm=0.8)
print(len(trs))
im=Image.fromarray(np.uint8(255-M*200)).convert('RGB'); d=ImageDraw.Draw(im)
cols=[(255,0,0),(0,160,0),(0,0,255),(200,0,200),(0,150,150),(200,120,0)]
for i,a in enumerate(trs):
    c=cols[i%len(cols)]
    d.line([(x*res,(H-y)*res) for x,y,_ in a],fill=c,width=2)
    x,y,_=a[0]; d.text((x*res+3,(H-y)*res),str(i),fill=c)
    print(i,'top',a[0,:2].round(0),'bot',a[-1,:2].round(0),'n',len(a))
h=im.height//3
s=Image.new('RGB',(im.width*3+20,h),'white')
for k in range(3): s.paste(im.crop((0,k*h,im.width,(k+1)*h)),(k*(im.width+10),0))
s.save('vit_tracks.png')
pickle.dump(trs,open('vit_tracks.pkl','wb'))
