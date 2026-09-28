import sys, json; sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent/'lib'))
import numpy as np, almond
from scipy import ndimage
D=np.load('vit_D.npy'); res=4; H=1593.5
Ds=ndimage.gaussian_filter(D,1.0)
core=ndimage.binary_opening(ndimage.gaussian_filter(D,1.5)>0.85, structure=np.ones((9,9)))
lab,n=ndimage.label(core)
fits=[]
for i in range(1,n+1):
    comp=lab==i
    if comp.sum()/16<200: continue
    region=ndimage.binary_dilation(comp,iterations=10) & (Ds>0.5)
    # keep only pixels closer to this core than to other cores
    others=(lab>0)&(lab!=i)
    dist_me=ndimage.distance_transform_edt(~comp); dist_o=ndimage.distance_transform_edt(~others)
    region&=dist_me<=dist_o
    rr,cc=np.nonzero(region)
    r0,r1,c0,c1=rr.min()-4,rr.max()+5,cc.min()-4,cc.max()+5
    m=region[r0:r1,c0:c1]
    y=H-(rr+0.5)/res; x=(cc+0.5)/res
    P=np.c_[x,y]; mu=P.mean(0); U,S,Vt=np.linalg.svd(P-mu,full_matrices=False); ax=Vt[0]
    proj=(P-mu)@ax; lo,hi=proj.min(),proj.max()
    A=mu+ax*lo; B=mu+ax*hi
    # base = the end nearer the cluster centre (lower end for these leaves: the lower one)
    if A[1]>B[1]: A,B=B,A
    wid=((P-mu)@np.array([-ax[1],ax[0]])).std()*2.2
    g=dict(Bx=A[0],By=A[1],Tx=B[0],Ty=B[1],wmax=wid,skew=1.0,p=0.8,bend=0.0,asym=0.0)
    x0=c0/res; ytop=H-r0/res
    f,l=almond.fit(m,res,ytop,x0,g)
    print('leaf',i,'IoU %.3f'%(1-l),{k:round(float(v),1) for k,v in f.items()})
    fits.append({k:float(v) for k,v in f.items()})
json.dump(fits,open('vit_leaves.json','w'),indent=1)
