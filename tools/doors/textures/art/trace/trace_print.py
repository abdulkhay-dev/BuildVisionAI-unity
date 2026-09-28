"""S-13 PRINT / STAMP: light floral print on a black mirror, super-resolved from the catalogue render(s): the ink
(print coverage) is normalised by its local maximum (the print's shading goes to a smooth tone field), solved for a
near-binary coverage at `res` px/mm whose downsampled image matches the photo, then vectorised (smoothed contours)."""
import sys, json, time; sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent/'lib'))
import finalize
import numpy as np, tr, inks, shapes
from PIL import Image
from scipy import ndimage
REPO=str(__import__('pathlib').Path(__file__).resolve().parents[5])
which=sys.argv[1]
CFG={'print':dict(files=['p065_s-13-print__wenge-veralinga.jpg'],res=3.2,lam=0.25,level=195,size=9,psf=0.5,
                  blur=1.2,thr=0.5,smooth=0.5,step=0.25,min_area=1.2),
     'stamp':dict(files=['p065_s-13-stamp__wenge-veralinga.jpg'],res=2.5,lam=0.25,level=195,size=5,psf=0.5,
                  blur=1.5,thr=0.62,smooth=0.9,step=0.3,min_area=1.5)}[which]
PANE=(130.5,0.0,667.0,2000.0)
W,H=PANE[2]-PANE[0],PANE[3]-PANE[1]
views=[]; inkl=[]; greys=[]
for f in CFG['files']:
    rgb,g,bg,ink=inks.mirror_ink(f,level=CFG['level'],size=CFG['size'])
    ink=np.clip(ink,0,1.3)
    tone=ndimage.gaussian_filter(ndimage.maximum_filter(np.clip(ink,0,1.3),5),1.5)
    tone=np.clip(tone,0.35,1.0)
    mn=np.clip(ink/tone,0,1)
    v=tr.View(f,PANE,mn,psf=CFG['psf'])
    v.weight=inks.box_weight(ink.shape,v,[(-10,940,70,1060),(-10,-10,W+10,2),(-10,1998,W+10,2010)])
    views.append(v); inkl.append(ink); greys.append(g)
grid=tr.Grid(W,H,CFG['res'])
ops=[tr.Op(grid,v,margin=0.5) for v in views]
init=tr.init_from_views(grid,views)
t=time.time()
c=tr.solve(grid,ops,init,lam=CFG['lam'],mu=3,iters=220,lr=0.05,verbose=True)
print('solve',time.time()-t)
np.save(which+'_sr.npy',c)
b=ndimage.gaussian_filter(c,CFG['blur'])>CFG['thr']
items=shapes.mask_rings(b,grid.res,H,smooth_mm=CFG['smooth'],step_mm=CFG['step'],min_area_mm2=CFG['min_area'])
print('items',len(items))
art={'id':which,'size':[W,H],'source':'S-13 %s, super-resolved from the catalogue render %s'%(which.upper(),', '.join(CFG['files'])),
     'layers':[{'role':'print','color':'#cfcfcd','items':items}]}
finalize.save_art(which,art)
print('written', sum(len(r) for it in items for r in it['poly']),'points')
