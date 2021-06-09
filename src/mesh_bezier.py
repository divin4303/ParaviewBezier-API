"""
==================================================================
input : patch_info          :dict
        Node_info           : position of the pointer.
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

import time
import h5py
'from memory_profiler import profile'

def bez_patch(ndm,patch_info,knot_r,knot_s,knot_t,conn,w,x,numpbez):
    
    patch_numpbez=[numpbez,numpbez]
    BezPoints=np.zeros((0,ndm))
    wbez=[]
    nel=patch_info['nel']
    mel=patch_info['mel']
    
    p=patch_info['p']
    q=patch_info['q']
    if ndm==3:
        r=patch_info['r']
        lel=patch_info['lel']
    else:
        r=0
    
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
        
    IX,w=Mesh.Connectvity(ndm,conn,w,tnel,patch_info)
    
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
    
    
    arrays=[]
    hf = h5py.File('PatchInfo.h5', 'w')
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
        
        arrays.append(np.pad(C,((0, 0), (0, 0))))
        
        BezPoints,wbez,patch_numpbez,ixbez=uniqueBez.Unique(BezPoints,wbez,bezloc\
                                            ,wbezloc,ixbez,nen,ptol,ndm,nd_bez\
                                            ,ne_bez,patch_numpbez,p,q,r)
    stacked_Carray = np.stack(arrays)
    
    'Stores patch information in h5py files'
    hf.create_dataset('C_{}'.format(patch_info['numpatch']), data=stacked_Carray)
    hf.create_dataset('Conn_{}'.format(patch_info['numpatch']), data=IX)
    patchInfo=hf.create_group('patchInfo{}'.format(patch_info['numpatch']))
    
    patch_info.update({
                    'number of elements'     :tnel,
                    'number of element nodes':nen,
                    'ncv':stacked_Carray.shape[1]})
    
    for key,value in patch_info.items():
                patchInfo.create_dataset(key, data=value)
                
    
    
    return BezPoints,wbez,patch_numpbez[1],ixbez,nen,tnel,patch_info


