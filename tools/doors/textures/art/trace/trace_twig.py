"""Глейс-1 TWIG and Глейс-2 TWIG: grass blades with seed heads rising from a tuft (small catalogue photos p014,
0.16 px/mm: long blades from row tracking of the ink field, tuft and seeds placed by hand from the same fields)."""
import sys, json, pickle; sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent/'lib'))
import finalize
import numpy as np, track, curves as cv, almond
REPO=str(__import__('pathlib').Path(__file__).resolve().parents[5])
COLOR='#a9a5a0'

def pts_of(trs, idx, ylo=-1e9, yhi=1e9):
    out=[]
    for i in idx:
        a=trs[i]; a=a[(a[:,1]>=ylo)&(a[:,1]<=yhi)]
        out.append(a[:,:2])
    p=np.vstack(out); p=p[np.argsort(-p[:,1])]
    return p

def blade(points, w_base=3.0, w_tip=0.35, s_mm=1.2, extra_top=None, extra_bot=None, power=0.40, scale=3.1):
    """Blade from traced points (any order): smoothing spline x(y); optional hand points at the ends.
    Width w_base at the bottom tapering to w_tip at the top."""
    p=np.asarray(points,float); p=p[np.argsort(-p[:,1])]
    if extra_top is not None: p=np.vstack([extra_top, p])
    if extra_bot is not None: p=np.vstack([p, extra_bot])
    p=p[np.argsort(-p[:,1])]
    a=np.c_[p, np.zeros(len(p))]
    xy=track.fit_track(a, s_mm=s_mm, step=1.0)
    n=len(xy); t=np.linspace(1,0,n)          # 1 at the top (tip)
    w=w_tip+(w_base*scale-w_tip)*(1-t)**power
    return cv.stroke(xy,w)

def curve_blade(pts, w0, w1=0.3, n_per=14, power=0.6, scale=2.4):
    """Hand blade through points from its base (first) to its tip (last)."""
    xy=cv.catmull(pts,n_per=n_per)
    t=np.linspace(0,1,len(xy)); w=w1+(w0*scale-w1)*(1-t)**power
    return cv.stroke(xy,w)

def seed(c, length, angle_deg, width=2.4, stalk_to=None, k=1.6):
    """Grain-like seed head: almond centred at c, axis at angle (deg from +x), optional thin stalk to a point."""
    a=np.radians(angle_deg); u=np.array([np.cos(a),np.sin(a)])
    B=np.asarray(c)-u*length/2; T=np.asarray(c)+u*length/2
    items=[cv.poly(almond.almond(B,T,width*k,skew=0.85,p=0.8,n=40))]
    if stalk_to is not None:
        items.append(cv.stroke(np.array([stalk_to,B]),[0.9,0.7]))
    return items

def save(name, W, items, source):
    art={'id':name,'size':[W,2000.0],'source':source,'layers':[{'role':'paint','color':COLOR,'items':items}]}
    finalize.save_art(name,art)

# ---------------------------------------------------------------- Глейс-1 TWIG (pane 135.5 x 2000)
t1=pickle.load(open('twig_tracks.pkl','rb'))
items=[]
A=pts_of(t1,[1],ylo=1195); A2=pts_of(t1,[2],yhi=1190); A3=pts_of(t1,[4])
items.append(blade(np.vstack([A,A2,A3]), w_base=3.2, w_tip=0.35, s_mm=1.5, extra_top=[[46.5,1868]], extra_bot=[[94.8,123]]))
B=pts_of(t1,[2],ylo=1205)
items.append(blade(B, w_base=2.4, w_tip=0.35, s_mm=1.5, extra_top=[[21,1392]], extra_bot=[[70,1196]]))
items.append(blade(pts_of(t1,[5]), w_base=2.2, w_tip=0.3, s_mm=1.0, extra_top=[[106,300]], extra_bot=[[97,124]]))
items.append(curve_blade([(95,128),(92,148),(75.5,170),(53.5,189),(39.2,198)], 2.4))
items.append(curve_blade([(95,124),(92,137),(75.5,139.7),(53.5,137),(42,129),(39.5,124)], 2.2))
items.append(curve_blade([(95,124),(88,120),(80,117)], 1.6))
items.append(curve_blade([(96,126),(90,160),(80,205),(70,238)], 1.8))
items.append(curve_blade([(97,125),(101,150),(99,185),(93,215)], 1.8))
items += seed((63,225),22,-48,width=3.0,stalk_to=(82,200))
items += seed((83.5,1767),20,62,width=2.4,stalk_to=(63,1745))
items += seed((74,766),20,70,width=2.4,stalk_to=(54,742))
save('twig',135.5,items,'Глейс-1 TWIG, traced from the catalogue renders p014 (3D Cappuccino, 3D Wenge)')

# ---------------------------------------------------------------- Глейс-2 TWIG (pane 246 x 2000)
t2=pickle.load(open('twig2_tracks.pkl','rb'))
items=[]
items.append(blade(pts_of(t2,[7]), w_base=3.2, w_tip=0.35, s_mm=1.5, extra_top=[[113,1858]], extra_bot=[[140,122]]))       # 1: long arc
items.append(blade(pts_of(t2,[1]), w_base=2.6, w_tip=0.35, s_mm=1.5, extra_top=[[149,1522]], extra_bot=[[136,1106]]))      # 2
items.append(blade(pts_of(t2,[2]), w_base=2.4, w_tip=0.3, s_mm=1.2, extra_top=[[203,1128]], extra_bot=[[166,915]]))        # 3
A=np.vstack([pts_of(t2,[3]),pts_of(t2,[5]),pts_of(t2,[6],yhi=445)])
items.append(blade(A, w_base=3.0, w_tip=0.35, s_mm=1.5, extra_top=[[73,1040]], extra_bot=[[140,122]]))                     # A
B=np.vstack([pts_of(t2,[4]),pts_of(t2,[11],yhi=595)])
items.append(blade(B, w_base=3.0, w_tip=0.35, s_mm=1.5, extra_top=[[107,857]], extra_bot=[[132,118]]))                     # B
C=np.vstack([pts_of(t2,[6],ylo=455),pts_of(t2,[8])])
items.append(blade(C, w_base=2.8, w_tip=0.3, s_mm=1.5, extra_top=[[167,596]], extra_bot=[[134,118]]))                      # C
items.append(blade(pts_of(t2,[9]), w_base=2.0, w_tip=0.3, s_mm=1.0, extra_top=[[82,236]], extra_bot=[[128,118]]))          # tuft
items.append(blade(pts_of(t2,[10]), w_base=2.0, w_tip=0.3, s_mm=1.0, extra_top=[[132,232]], extra_bot=[[137,112]]))
items.append(curve_blade([(132,118),(124,110),(114,92),(106,68),(102,52)], 2.2))
items.append(curve_blade([(134,120),(128,150),(122,185),(112,215),(103,238),(92,244),(86,240)], 2.0))
items.append(curve_blade([(136,118),(146,108),(158,96),(166,84)], 1.8))
items.append(curve_blade([(130,120),(118,112),(100,110),(86,118)], 1.8))
items.append(curve_blade([(133,119),(122,140),(104,160),(90,168),(78,165)], 1.8))
items.append(curve_blade([(137,119),(150,140),(158,170),(160,205)], 1.8))
items.append(curve_blade([(135,118),(142,96),(146,70),(145,48)], 1.8))
items.append(curve_blade([(131,118),(110,125),(92,140),(84,158)], 1.6))
items += seed((103,1876),18,95,width=2.4)
items += seed((148,1506),16,95,width=2.2)
items += seed((200,1047),18,60,width=2.4,stalk_to=(186,1030))
items += seed((107,842),18,95,width=2.4)
items += seed((57,231),26,178,width=3.2,stalk_to=(84,232))
items += seed((65,134),24,-65,width=3.0)
items += seed((165,124),24,-20,width=3.0,stalk_to=(140,128))
save('twig-2',246.0,items,'Глейс-2 TWIG, traced from the catalogue renders p014 (3D Cappuccino, 3D Wenge)')
print('ok')
