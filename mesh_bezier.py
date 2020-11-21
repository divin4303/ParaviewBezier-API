"""
==================================================================
input : n,m,l               : number of nodal points in r,s,t dir.
        p,q,r               : order of the fn in r,s,t dir.
        Node_info           : position of the pointer.
        nel,mel,lel         : number of elements in r,s,t dir
        knot_r,knot_S,knot_t: number of elemtns in r,s,t dir.
        X,Y,z               : coordinates in x,y,z dir.
        BezPoints           : Bezpoints in x,y,z coordinates.
        wbez                : weight of bezier points.
        numpbez             : number of bezier points.
        w                   : weight of NURB points.
        
Output: BezPoints           : Bezpoints in x,y,z coordinates.
        wbez                : weight of bezier points.
        numpbez             : number of bezier points.
        tnel                : total number of elements of the patch.
        ixbez               : IX array of the patch.
        nen                 : number of elemental node of the patch.
==================================================================
"""

import numpy as np
import Mesh
import full_Elem_Extraction_Operator
import BezierCoord
import Directional_Extract_Op
import uniqueBez
import matplotlib.pyplot as plt
import unstructured_paraview as upar

import time
from memory_profiler import profile

def bez_patch(ndm,nel,mel,lel,n,m,l,p,q,r,knot_r,knot_s,knot_t,conn,w,x,\
              BezPoints,wbez,numpbez):

    elem_no=0
    ptol=1E-4
    ne=1
    'x being the coordinate matrix'
    if ndm==2:
        tnel=nel
    if ndm==2:
        tnel=nel*mel
    elif ndm==3:
        tnel=nel*mel*lel
        
    IX,w=Mesh.Connectvity(ndm,conn,w,tnel,nel,mel,lel,n,m,l,p,q,r)
    
    if ndm==1:
        'Initialization for directional operator'
            
        C_num = [0 for i in range(tnel)]
        
        nen = p+1 # number of local basis functions
        
        C_e1=Directional_Extract_Op.Operator(knot_r,p)
            
    elif ndm==2:          
        'Initialization for directional operator'

        nen = (p+1)*(q+1)
        
        C_num = [[0 for i in range(ndm+1)] for j in range(tnel)]
        
        # IEN=Mesh.ien(ndm,nel,nnp,nen,n,p,m,q)
        
        for i in range(0,nel):
            for j in range(0,mel):
                C_num[elem_no][0]=elem_no+1
                C_num[elem_no][1]=i
                C_num[elem_no][2]=j
                elem_no=elem_no+1
                
        C_e1=Directional_Extract_Op.Operator(knot_r,p)
        
        C_e2=Directional_Extract_Op.Operator(knot_s,q)
                
    elif ndm==3:
                  
        'Initialization for directional derivative'
                        
        nen = (p+1)*(q+1)*(r+1)
        
        
        C_num = [[0 for i in range(ndm+1)] for j in range(tnel)]
        
        # IEN=Mesh.ien(ndm,nel,nnp,nen,n,p,m,q,l,r)
        
        for i in range(0,nel):
                for j in range(0,mel):
                        for k in range(0,lel):
                                C_num[elem_no][0]=elem_no+1
                                C_num[elem_no][1]=i
                                C_num[elem_no][2]=j
                                C_num[elem_no][3]=k
                                elem_no=elem_no+1
                                    
        # C_num=[[1,0,0,0],[2,1,0,0],[3,2,0,0],[4,3,0,0]]
        
        C_e1=Directional_Extract_Op.Operator(knot_r,p)
        
        C_e2=Directional_Extract_Op.Operator(knot_s,q)
        
        C_e3=Directional_Extract_Op.Operator(knot_t,r)        
                        
        'C numbering for 3D is pending'
                        
    else:
            
        print("not valid number of dimension")
            
    'initialization of local variables'
    x_local=np.zeros((nen,ndm))
    w_local=np.zeros(nen)
    IXloc=[0 for i in range(nen)]
    nd_bez = tnel*nen
    # wbez=[]  
    ixbez = ([[0 for i in range(nen)] for j in range(tnel)])
    
    
    #numpbez=0      
    for ne in range(1,tnel+1):
        t0=time.time()
        ne_bez = ne
        i=C_num[ne-1][1]
        j=C_num[ne-1][2]
                
        for k in range(0,nen):
            
            IXloc[k]=IX[ne-1][k]
            w_local[k]=w[ne-1][k]
            'IEN should be with nel: required as it is single patch information' 
        #print(IENloc)
        for mi in range(0,nen):# nen = number of element nodes
            if IXloc[mi]>0:
                
                for n in range(0,ndm):
                    x_local[mi,n]=x[(IXloc[mi]-1)][n]
                # w_local[mi]=w[IENloc[mi]-1]
                    
            else:
            
                for n in range(0,ndm):
                    x_local[mi,n]=0
                # w_local[mi]=1
      
        if ndm==1:
        
            i=C_num[ne-1]
            
            C=full_Elem_Extraction_Operator.ful_Ce(ndm,C_e1[i,:,:],0,0,p)
            
            bezloc,wbezloc=BezierCoord.Bezier_loc(w_local,IXloc,C,x_local,nen,\
                                                  ne_bez,ndm,p,q,r)
            
        if ndm==2:
        
            i=C_num[ne-1][1]
            j=C_num[ne-1][2]
            
            C=full_Elem_Extraction_Operator.ful_Ce(ndm,C_e1[i,:,:],C_e2[j,:,:],\
                                                   0,p,q)

            bezloc,wbezloc=BezierCoord.Bezier_loc(w_local,IXloc,C,x_local,nen,\
                                                  ne_bez,ndm,p,q,r)
            
        if ndm==3:
        
            i=C_num[ne-1][1]
            j=C_num[ne-1][2]
            k=C_num[ne-1][3]
            
            C=full_Elem_Extraction_Operator.ful_Ce(ndm,C_e1[i,:,:],C_e2[j,:,:]\
                                                   ,C_e3[k,:,:],p,q,r)
            
            bezloc,wbezloc=BezierCoord.Bezier_loc(w_local,IXloc,C,x_local,nen,\
                                                  ne_bez,ndm,p,q,r)
        
        t1=time.time()
        BezPoints,wbez,numpbez,ixbez=uniqueBez.Unique(BezPoints,wbez,bezloc\
                                            ,wbezloc,ixbez,nen,ptol,ndm,nd_bez\
                                            ,ne_bez,numpbez,p,q,r)
        t2=time.time()
    
    return BezPoints,wbez,numpbez,ixbez,nen,tnel


