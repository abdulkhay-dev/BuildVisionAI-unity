import sys, pickle; sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent/'lib'))
import numpy as np, track
from PIL import Image, ImageDraw
which=sys.argv[1]
D=np.load(which+'_D.npy'); res=4.0; H=2000.0; W=D.shape[1]/res
M=np.clip(D,0,1); M[-int(8*res):]=0
trs=track.track(M,res,H,thr=0.22,step_mm=1.0,max_jump_mm=1.5,max_gap_mm=25,min_len_mm=40,smooth_mm=1.2)
print(len(trs))
im=Image.fromarray(np.uint8(255-M*200)).convert('RGB'); d=ImageDraw.Draw(im)
cols=[(255,0,0),(0,160,0),(0,0,255),(200,0,200),(0,150,150),(200,120,0)]
for i,a in enumerate(trs):
    c=cols[i%len(cols)]
    d.line([(x*res,(H-y)*res) for x,y,_ in a],fill=c,width=2)
    x,y,_=a[0]; d.text((x*res+3,(H-y)*res),str(i),fill=c)
    print(i,'top',a[0,:2].round(0),'bot',a[-1,:2].round(0),'n',len(a),'pk %.2f'%a[:,2].mean())
h=im.height//4
s=Image.new('RGB',(im.width*4+30,h),'white')
for k in range(4): s.paste(im.crop((0,k*h,im.width,(k+1)*h)),(k*(im.width+10),0))
s.save(which+'_tracks.png')
pickle.dump(trs,open(which+'_tracks.pkl','wb'))
