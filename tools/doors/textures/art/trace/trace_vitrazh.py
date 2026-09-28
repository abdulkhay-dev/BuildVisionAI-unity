"""Белое сатинато «Витраж» (Тренд-14): black leaves in three clusters, outlined leaves, and a braid of thin dark
lines (two twisted double-line stems). Traced from the three small renders p012 (0.16 px/mm) averaged; the leaves
are almonds fitted to the averaged ink field, the lines row-tracked and joined across the crossings."""
import sys, json, pickle; sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent/'lib'))
import finalize
import numpy as np, track, almond, curves as cv, tr
REPO=str(__import__('pathlib').Path(__file__).resolve().parents[5])
D=np.load('vit_D.npy'); res=4.0; H=1593.5; W=198.0
trs=pickle.load(open('vit_tracks.pkl','rb'))
leaves=json.load(open('vit_leaves.json'))[:9]
items=[]
SHRINK=1.0        # the field is blurred by the photo pixels (~6 mm): fitted half widths shrunk
BASES=[(106,1371),(66,1121),(131,645)]
for f in leaves:
    B=np.array([f['Bx'],f['By']]); T=np.array([f['Tx'],f['Ty']])
    base=min(BASES,key=lambda b:np.hypot(b[0]-B[0],b[1]-B[1]))
    B=0.35*B+0.65*np.array(base)             # the three leaves of a cluster fan out from one point
    u=(T-B)/np.hypot(*(T-B)); B2=B+u*1.0; T2=T-u*1.0
    items.append(cv.poly(almond.almond(B2,T2,f['wmax']*SHRINK,skew=0.95,p=0.85,n=60)))
# outlined leaves: (base, tip, half width)
for B,T,w in [((139.0,1294),(163.0,1347),7.4),((24,1072),(79,1059),7.2),((140,569),(178,609),7.2)]:
    outer=almond.almond(B,T,w,skew=1.0,p=0.85,n=60)
    Bi=np.array(B)+ (np.array(T)-np.array(B))*0.07; Ti=np.array(T)-(np.array(T)-np.array(B))*0.07
    inner=almond.almond(Bi,Ti,w-3.0,skew=1.0,p=0.85,n=60)
    items.append(cv.poly(outer,inner))
samp=tr.sampler(tr.Grid(W,H,res),D)
def line(ids, top=None, bot=None, w=1.9, s_mm=0.8, taper_top=True, taper_bot=True):
    p=np.vstack([trs[i][:,:2] for i in ids])
    if top is not None: p=np.vstack([p,[top]])
    if bot is not None: p=np.vstack([p,[bot]])
    p=p[np.argsort(-p[:,1])]
    xy=track.fit_track(np.c_[p,np.zeros(len(p))],s_mm=s_mm,step=1.0)
    n=len(xy); ww=np.full(n,w)
    k=min(30,n//4)
    if taper_top: ww[:k]*=np.linspace(0.3,1,k)
    if taper_bot: ww[-k:]*=np.linspace(1,0.3,k)
    return cv.stroke(xy,ww)
# the braid: two double-line ribbons (A from the top cluster, B emerging from it at ~1040) twisting around each
# other; line positions read off the ink field every 25 mm (row peaks), then smoothed
A1=[(118,1336),(120.5,1300),(121,1270),(118.5,1235),(115.3,1200),(112,1175),(108.1,1150),(105.1,1125),(100.5,1100),(94.8,1075),
    (89.1,1050),(83.7,1025),(78.8,1000),(76.3,975),(72,950),(70.7,925),(69,900),(67.3,875),(66.8,850),(69.1,825),(70.3,800),
    (71.3,775),(74.9,750),(77.1,725),(80,700),(86,675),(92.4,650),(98.6,625),(105.3,600),(109.7,575),(117.4,550),(125.1,525),
    (132.6,500),(139.5,475),(143,464)]
A2=[(120.5,1300),(122.3,1250),(124.5,1225),(125.7,1200),(124.5,1175),(121.3,1150),(119,1125),(115.1,1100),(111.5,1075),
    (108.8,1050),(102.4,1025),(99.4,1000),(95.1,975),(90.5,950),(88.9,925),(85.3,900),(83.9,875),(83.7,850),(84,825),(84.4,800),
    (86.5,775),(88.9,750),(89.6,725),(92,700),(94.5,675),(96,650),(100,625),(105.3,600),(109.7,575),(98.7,550),(91.8,525),
    (86.7,500),(83.1,475),(81.5,450),(83.5,425),(89.3,400),(94.9,375),(98.5,350),(106.2,325),(115.3,300),(124.6,275),
    (132.9,250),(142.1,225),(146,214)]
B1=[(113,1052),(121,1025),(128.7,1000),(133.5,975),(138.2,950),(138.8,925),(139.9,900),(139.2,875),(137.1,850),(131.2,825),
    (122.5,800),(113.2,775),(102,750),(90,725),(79,700),(69.1,675),(59.1,650),(52.3,625),(46.6,600),(45.8,575),(45.9,550),
    (46.7,525),(51.7,500),(57.6,475),(62,450),(58.8,425),(54.5,400),(51.5,375),(47.8,350),(46.1,325),(46.1,300),(47.7,275),
    (51.5,250),(54.9,225),(59.6,200),(68,183),(76.5,165),(82,145),(88.1,125),(94,106),(99,93)]
B2=[(113,1052),(121,1025),(130,1000),(143.7,975),(150.9,950),(153.7,925),(157,900),(156.6,875),(152.4,850),(147,825),
    (139.4,800),(128.2,775),(116.3,750),(103.7,725),(93.1,700),(83.2,675),(70.8,650),(64.5,625),(58.9,600),(58.3,575),
    (58.5,550),(61.3,525),(65.1,500),(71.4,475),(75.5,450),(71,425),(67,400),(65.6,375),(64.5,350),(61.5,325),(61.3,300),
    (64.2,275),(65.4,250),(69.9,225),(72,200),(76.5,178),(81,160),(86,140),(90.5,122),(95.5,105),(99,93)]
from scipy import ndimage as ndi
def smooth_line(pts, sig=0.9, w=4.3, taper=(True,True)):
    p=cv.catmull(pts,n_per=10)
    d=np.r_[0,np.cumsum(np.hypot(*np.diff(p,axis=0).T))]
    s_=np.arange(0,d[-1],1.0); p=np.stack([np.interp(s_,d,p[:,0]),np.interp(s_,d,p[:,1])],1)
    q=np.stack([ndi.gaussian_filter1d(p[:,0],sig*3,mode='nearest'),ndi.gaussian_filter1d(p[:,1],sig*3,mode='nearest')],1)
    q[0]=p[0]; q[-1]=p[-1]
    n=len(q); ww=np.full(n,w); k=min(25,n//4)
    if taper[0]: ww[:k]*=np.linspace(0.35,1,k)
    if taper[1]: ww[-k:]*=np.linspace(1,0.35,k)
    return cv.stroke(q,ww)
def narrow(P,Q,k=0.8):
    # pulls the two lines of a ribbon towards their middle (the ink field is blurred by ~6 mm)
    P=np.array(P,float); Q=np.array(Q,float)
    qx=np.interp(P[:,1],Q[::-1,1],Q[::-1,0]); px=np.interp(Q[:,1],P[::-1,1],P[::-1,0])
    P2=P.copy(); Q2=Q.copy()
    P2[:,0]=(P[:,0]+qx)/2+k*(P[:,0]-qx)/2; Q2[:,0]=(Q[:,0]+px)/2+k*(Q[:,0]-px)/2
    return P2.tolist(),Q2.tolist()
A1,A2=narrow(A1,A2); B1,B2=narrow(B1,B2)
for L in (A1,A2,B1,B2):
    items.append(smooth_line(L))
# the stem under the top cluster, where both lines of ribbon A run together: one thick tapered stroke
top=cv.catmull([(106,1372),(112,1356),(118,1336),(120.5,1300),(121,1270),(120.5,1238)],n_per=10)
items.append(cv.stroke(top, cv.taper(len(top),3.2,5.2,ends=(0.12,0.35),lo=0.5)))
# short stalks into the clusters
items.append(smooth_line([(118,1336),(113,1352),(108,1366),(105,1375)],w=2.0,taper=(False,True)))
items.append(smooth_line([(94.8,1075),(82,1090),(72,1105),(66,1121)],w=1.8,taper=(False,True)))
items.append(smooth_line([(105.3,600),(113,612),(124,628),(132,644)],w=1.8,taper=(False,True)))
art={'id':'vitrazh','size':[W,H],'source':'Белое сатинато «Витраж» (Тренд-14), traced from the catalogue renders p012 (3D Cappuccino, Grey, Wenge)',
     'layers':[{'role':'paint','color':'#1d1b1a','smooth':0.55,'items':items}]}
finalize.save_art('vitrazh',art)
print('ok',len(items))
