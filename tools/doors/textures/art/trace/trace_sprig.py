"""Глейс-1 SPRIG: three shaded buds on thin stems (traced from p014 big photos, 3D Cappuccino + 3D Wenge)."""
import sys, json, os; sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent/'lib'))
import finalize
import numpy as np, tr, inks, track, curves as cv
from PIL import Image
from scipy import ndimage
REPO=str(__import__('pathlib').Path(__file__).resolve().parents[5])
PANE=(141.5, 0.0, 277.0, 2000.0)
W,H=PANE[2]-PANE[0], PANE[3]-PANE[1]
LEVEL=150.0
views=[]; darks=[]; rgbs=[]
for f in ['p014_gleys-1-sprig__3d-cappuccino.jpg','p014_gleys-1-sprig__3d-wenge.jpg']:
    rgb,g,bg,dark,white=inks.satin_ink(f, level=LEVEL)
    v=tr.View(f, PANE, np.clip(dark,0,1), psf=0.5)
    v.weight=inks.box_weight(dark.shape, v, [(-10,860,60,1040)])
    views.append(v); darks.append(dark); rgbs.append(rgb)
grid=tr.Grid(W,H,4.0)
D=tr.field_from_views(grid,views,darks)
G=tr.field_from_views(grid,views,[r@inks.LUMA for r in rgbs])
samp=tr.sampler(grid,D)
M=np.clip(D,0,1)
tracks=track.track(M,grid.res,H,thr=0.18,step_mm=0.5,max_jump_mm=1.0,max_gap_mm=8,min_len_mm=15,smooth_mm=0.8)
stems=sorted([a for a in tracks if a[0,1]-a[-1,1]>300], key=lambda a:-a[0,1])
# buds: grey body outlines (mm), read off the ink fields; base = where the stem enters
BUDS={
 'top': dict(base=(50.5,1873.0), body=[(50.5,1873.0),(57,1877.5),(63.1,1883.6),(67.5,1892),(68.7,1899),(68.2,1907.9),(66.5,1914.9),(63.9,1923.6),(62.4,1933.5),
                                    (58.8,1922.7),(53.6,1921.3),(49.2,1918.5),(45.8,1913),(43.4,1904.4),(43.0,1895),(44.9,1884),(47.5,1877)],
             white=[[(46.3,1914.5),(49.5,1920.3),(54.5,1923.8),(59.5,1925.2),(62.2,1925.6),(59.2,1922.9),(53.9,1921.4),(49.6,1918.6),(46.6,1914)]]),
 'mid': dict(base=(54.8,1320.6), body=[(54.8,1320.6),(59.2,1325.8),(64.4,1337),(66.1,1350),(66.1,1367.3),(64.4,1380.3),(60.9,1388.1),(55.7,1390.7),(47.9,1390.2),(40.0,1389.6),(35.8,1388.1),
                                    (33.0,1380.3),(31.8,1367.3),(32.4,1354.4),(34.6,1343.1),(39.3,1332.7),(47.1,1324.9)],
             white=[[(35.2,1388.4),(37.3,1400),(40.4,1414.2),(44.5,1406.5),(50.5,1398.5),(56.4,1392.0),(47.9,1391.0),(40.0,1390.4)]]),
 'low': dict(base=(80.6,683.0), body=[(80.6,683.0),(88.4,686.4),(95.3,695.1),(101.4,703.7),(105.7,714.1),(107.4,726.3),(107.0,738.4),(104.8,747.1),(101.4,754.0),(99.6,757.0),
                                    (96.2,751.4),(90.1,741.9),(84.1,733.2),(79.8,724.5),(78.0,717.6),(78.0,708.1),(78.9,697.7),(79.6,689.0)],
             white=[[(98.6,756.8),(98.3,761.5),(100.6,758.2)]]),
}
white_items=[]; body_items=[]; edge_items=[]; stem_items=[]
for name,b in BUDS.items():
    ring=cv.catmull(b['body'],closed=True,n_per=10)
    body_items.append(cv.poly(ring))
    white_items.append(cv.poly(cv.ring_offset(ring,1.1)))           # thin white outline around the bud
    for wr in b['white']:
        white_items.append(cv.poly(cv.catmull(wr,closed=True,n_per=8)))
    # darker shading line along the right-hand edge (base -> tip), inside the outline
    n=len(ring); pts=np.asarray(b['body']); 
    k_tip=int(np.argmax(pts[:,1]))
    edge=cv.catmull(pts[:k_tip+1],n_per=10)
    edge=cv.ring_offset(np.vstack([edge,edge[::-1]]),0)[:len(edge)]   # (no offset, keeps order)
    # move the line 0.8 mm inside: towards the bud centre
    c=pts.mean(0); d=c-edge; d/=np.maximum(np.hypot(d[:,0],d[:,1])[:,None],1e-9); edge=edge+d*0.8
    edge_items.append(cv.stroke(edge, cv.taper(len(edge),1.4,0.5,wmid=2.0,ends=(0.15,0.25))))
for a,(name,b) in zip(stems,BUDS.items()):
    bx,by=b['base']
    a=a[a[:,1]<by-6.0]
    xy=track.fit_track(a,s_mm=0.22,step=1.0)
    # join the bud base smoothly: spline through the base and the traced line every 8 mm
    head=cv.catmull(np.vstack([[bx,by],xy[4:40:8]]),n_per=8)
    xy=np.vstack([head[:-1],xy[36:]])
    d=np.r_[0,np.cumsum(np.hypot(*np.diff(xy,axis=0).T))]
    s_=np.arange(0,d[-1],1.0); xy=np.stack([np.interp(s_,d,xy[:,0]),np.interp(s_,d,xy[:,1])],1)
    ts=np.arange(-2.5,2.5001,0.1)
    X=xy[:,0:1]+ts[None,:]; Y=np.repeat(xy[:,1:2],len(ts),1)
    wh=np.clip(samp(X,Y),0,None).sum(1)*0.1
    dx=np.gradient(xy[:,0]); dy=np.gradient(xy[:,1])
    w=wh*np.abs(dy)/np.hypot(dx,dy)
    med=np.median(w)
    w=np.clip(ndimage.gaussian_filter1d(np.clip(w,0.6*med,1.4*med),20,mode='nearest'),0,None)*(235-LEVEL)/(235-120)
    n=len(xy); tl=min(60,n//3)
    w[-tl:]*=np.linspace(1,0.2,tl)
    w[:6]=np.maximum(w[:6],1.4)
    print(name,'stem %.0f mm, width median %.2f mm'%(xy[0,1]-xy[-1,1],np.median(w)))
    stem_items.append(cv.stroke(xy,w))
# tone of the bud fill: photo grey inside the buds, smoothed
inside=np.zeros_like(G,bool)
from PIL import ImageDraw
img=Image.new('L',(grid.nx,grid.ny),0); dr=ImageDraw.Draw(img)
for it in body_items:
    r=np.asarray(it['poly'][0]); dr.polygon([(x*grid.res,(H-y)*grid.res) for x,y in r],fill=1)
inside=ndimage.binary_erosion(np.asarray(img).astype(bool),iterations=5)
s=4.0
num=ndimage.gaussian_filter(np.where(inside,G,0),s); den=ndimage.gaussian_filter(inside.astype(float),s)
tone=np.where(den>0.01,num/np.maximum(den,1e-6),180.0)
tone=np.clip(tone*0.90,0,255)
os.makedirs(REPO+'/tools/doors/textures/art',exist_ok=True)
Image.fromarray(np.uint8(tone)).resize((int(round(W*2)),int(round(H*2))),Image.BILINEAR).save(REPO+'/tools/doors/textures/art/sprig_tone.png',optimize=True)
art={'id':'sprig','size':[W,H],'source':'Глейс-1 SPRIG, traced from the catalogue renders p014 (3D Cappuccino, 3D Wenge)',
     'layers':[{'role':'paint','color':'#fbfaf8','items':white_items},
               {'role':'paint','color':'#8f8a85','tone':'sprig_tone.png','items':body_items},
               {'role':'paint','color':'#6e6964','items':edge_items+stem_items}]}
finalize.save_art('sprig',art)
print('written')
