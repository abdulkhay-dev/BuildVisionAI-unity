"""Белое худож-е «Mystic» (Симпл-15.2 M): a frame of double lines with a spiral scroll in every corner (big pane)
and a centred double line (small pane). Pane sizes and line insets measured on the p061 renders (0.16 px/mm); the
scroll is drawn from the glass swatch of the SIMPLE page (catalogue p60, ~0.33 px/mm, top-left corner of the glass)."""
import sys, json; sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent/'lib'))
import finalize
import numpy as np, curves as cv
REPO=str(__import__('pathlib').Path(__file__).resolve().parents[5])
M=3.07                      # mm per swatch px
XO, TO = 45.75, 37.0       # outer vertical line from the side edge, outer horizontal line from the top edge (mm, design pane)
LW=1.9                      # line width, mm
COL='#8b8782'
def sw(c, r):               # swatch (col, row) continuous -> (mm from the left edge, mm from the top edge)
    return (XO+(c-16.0)*M, TO+(r-12.5)*M)
SCROLL=[(28.6,22.4),(27.3,21.2),(26.0,19.8),(24.8,18.3),(23.6,16.9),(22.0,15.4),(20.3,14.0),(18.4,12.4),(16.0,11.4),
        (13.4,11.3),(10.9,12.0),(9.0,13.5),(8.2,15.6),(8.5,17.8),(9.8,19.5),(12.0,20.5),(14.3,20.3),(16.0,18.9),
        (16.6,17.0),(15.8,15.6),(14.2,15.1),(12.7,15.7),(12.1,16.9),(12.8,17.8)]
SWOOSH=[(18.6,22.6),(19.4,21.3),(21.0,20.6),(23.0,20.7),(25.2,21.5),(27.6,22.6),(30.2,23.2),(33.0,22.9),(35.5,22.1)]
LEAF=((22.0,15.0),(28.6,16.3),1.25)       # small leaf beside the scroll: base, tip, half width (swatch px)

def corner_items():
    """Scroll of the top-left corner in (mm from the left, mm from the top)."""
    items=[]
    p=np.array([sw(*q) for q in SCROLL])
    xy=cv.catmull(p,n_per=10)
    n=len(xy); t=np.linspace(0,1,n)
    w=LW*(0.55+0.45*np.sin(np.pi*np.clip(t*1.15,0,1))**0.5)
    w[-8:]=np.linspace(w[-9],LW*1.6,8)          # the spiral ends in a dot
    items.append(('s',xy,w))
    q=np.array([sw(*q) for q in SWOOSH]); xy=cv.catmull(q,n_per=10)
    items.append(('s',xy,cv.taper(len(xy),LW*0.9,ends=(0.2,0.3),lo=0.3)))
    (b,tp,hw)=LEAF
    import almond
    B=np.array(sw(*b)); T=np.array(sw(*tp)); h=hw*M
    outer=almond.almond(B,T,h,skew=0.9,p=0.8,n=50); inner=almond.almond(B+(T-B)*0.12,T-(T-B)*0.1,h-LW,skew=0.9,p=0.8,n=50)
    items.append(('p',outer,inner))
    return items

def place(items, W, H):
    out=[]
    for sx in (0,1):
        for sy in (0,1):
            for it in items:
                def tf(a):
                    a=np.asarray(a,float)
                    x=a[:,0] if sx==0 else W-a[:,0]
                    y=H-a[:,1] if sy==0 else a[:,1]
                    return np.stack([x,y],1)
                if it[0]=='s': out.append(cv.stroke(tf(it[1]),it[2]))
                else: out.append(cv.poly(tf(it[1]),tf(it[2])))
    return out

def hline(y, x0, x1, taper_mm=10.0):
    n=max(20,int((x1-x0)/2)); xs=np.linspace(x0,x1,n)
    w=np.full(n,LW); k=max(2,int(taper_mm/((x1-x0)/(n-1))))
    w[:k]*=np.linspace(0.25,1,k); w[-k:]*=np.linspace(1,0.25,k)
    return cv.stroke(np.stack([xs,np.full(n,y)],1),w)

def vline(x, y0, y1, taper_mm=10.0):
    s=hline(x,y0,y1,taper_mm)['stroke']
    return {'stroke':[[p[1],p[0],p[2]] for p in s]}

W,H=508.0,935.0
items=place(corner_items(),W,H)
xa,xb=sw(33.8,0)[0],sw(37.0,0)[0]          # ends of the outer / inner horizontal lines (next to the scroll)
ta,tb=sw(0,30.0)[1],sw(0,33.0)[1]          # ends of the outer / inner vertical lines
yo,yi=TO,sw(0,16.4)[1]
xo,xi=XO,sw(20.3,0)[0]
for y,x0 in ((yo,xa),(yi,xb)):
    items.append(hline(H-y,x0,W-x0)); items.append(hline(y,x0,W-x0))
for x,t0 in ((xo,ta),(xi,tb)):
    items.append(vline(x,t0,H-t0)); items.append(vline(W-x,t0,H-t0))
art={'id':'mystic','size':[W,H],'source':'Белое худож-е «Mystic» (Симпл-15.2 M, big pane): p061 renders + the p60 glass swatch',
     'layers':[{'role':'paint','color':COL,'items':items}]}
finalize.save_art('mystic',art)
W2,H2=508.0,85.0
art2={'id':'mystic-small','size':[W2,H2],'source':'Белое худож-е «Mystic» (Симпл-15.2 M, small pane): p061 renders',
      'layers':[{'role':'paint','color':COL,'items':[hline(H2/2+6.25,47.0,W2-47.0,40),hline(H2/2-6.25,34.0,W2-34.0,40)]}]}
finalize.save_art('mystic-small',art2)
print('ok', 'lines x from %.1f/%.1f, y from %.1f/%.1f; outer %.1f/%.1f inner %.1f/%.1f'%(xa,xb,ta,tb,xo,yo,xi,yi))
