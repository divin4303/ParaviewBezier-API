# -*- coding: utf-8 -*-
"""
==================================================================
input : wloc                :elemental weights.
        IENloc              :elemental IX array.
        c                   :extraction operator.
        xloc                :element coordinates.
        nen                 :number of elemtnal coordinates.
        ndm                 :number of dimensions.
        p,q,r               :order of fn in r,s,t dir.
        ne_bez              :
        
Output: Bezloc              :element bezier coordinates.
        wbez                :elemntal bezier weights.
==================================================================
"""
import numpy as np
import reorder_paraview

def Bezier_loc(wloc,IENloc,C,xloc,nen,ne_bez,ndm,p,q,r):
    
    wbez_diag=[[0 for i in range(nen)]for i in range(nen)]
    wbez=np.dot(C,wloc)
    
    for i in range(0,len(wbez)):
        for j in range(0,len(wbez)):
            if (i==j):
                wbez_diag[i][j]=wbez[i]
            else:
                wbez_diag[i][j]=0
    
    wbez_inv=[[0 for i in range(0,nen)] for j in range(0,nen)] 
    wloc_diag=[[0 for i in range(0,nen)] for j in range(0,nen)] 
    
    for i in range(0,len(IENloc)):
        for j in range(0,len(IENloc)):
            if (i==j):
                wloc_diag[i][j]=wloc[i]
            else:
                wloc_diag[i][j]=0    

    for i in range(0,nen):
        for j in range(0,nen):
            if i==j:
                wbez_inv[i][j]=1.0/wbez_diag[i][j]
            else:
                wbez_inv[i][j]=0.0
    
    Proj_C=np.dot(C,wloc_diag)
    
    Proj_back=np.dot(wbez_inv,Proj_C)
    
    bezloc=np.dot(Proj_back,xloc)
    
    for i in range(0,ndm):
        
        #print(bezloc[:,i])
        
        bezloc[:,i]=reorder_paraview._init_(bezloc[:,i],ne_bez,ndm,nen,p,q,r)
    
    wbez=reorder_paraview._init_(wbez,ne_bez,ndm,nen,p,q,r)
    
    return bezloc,wbez

def nbez(XI,n,p):
    
    b=p+1
    
    
    m=len(XI)-1
    
    while b<m:
        i=b
        
        while b<m and XI[b+1]==XI[b]:
            b=b+1
        mult=b-i+1
        
        if mult<p:
            n=n+(p-mult)
            
        b=b+1
    return n