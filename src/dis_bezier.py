import numpy as np
import Mesh
import full_Elem_Extraction_Operator
import BezierCoord
import Directional_Extract_Op

def state_variable(ndm,patch_info,knot_r,knot_s,knot_t,conn,\
                   w,temp_tnel,u,ixbez):

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
    ne=1
    'x being the coordinate matrix'
    if ndm==2:
        tnel=nel
    if ndm==2:
        tnel=nel*mel
    elif ndm==3:
        tnel=nel*mel*lel
        
    temp_tnel-=tnel
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
    u_local=np.zeros((nen,3))
    w_local=np.zeros(nen)
    IXloc=[0 for i in range(nen)]
    
    ubez=np.zeros((patch_info['Bezier_points'],3))
    
    # ubez[0:len(temp_ubez), 0:3] = temp_ubez
        
    #numpbez=0       
    for ne in range(0,tnel):
        
        ne_bez = ne+1
        i=C_num[ne][1]
        j=C_num[ne][2]
                
        for k in range(0,nen):
            
            IXloc[k]=IX[ne][k]
            w_local[k]=w[ne][k]
            'IEN should be with nel: required as it is single patch information' 
        #print(IENloc)
        for mi in range(0,nen):# nen = number of element nodes
            if IXloc[mi]>0:
                
                for n in range(0,3):
                    u_local[mi,n]=u[(IXloc[mi]-1)][n]
                # w_local[mi]=w[IENloc[mi]-1]
                    
            else:
            
                for n in range(0,ndm):
                    u_local[mi,n]=0
                # w_local[mi]=1
      
        if ndm==1:
        
            i=C_num[ne]
            
            C=full_Elem_Extraction_Operator.ful_Ce(ndm,C_e1[i,:,:],0,0,p)
            
            ubezloc,wbezloc=BezierCoord.Bezier_loc(w_local,IXloc,C,u_local,\
                                                   nen,ne_bez,ndm,p,q,r)
            
        if ndm==2:
        
            i=C_num[ne][1]
            j=C_num[ne][2]
            
            C=full_Elem_Extraction_Operator.ful_Ce(ndm,C_e1[i,:,:],C_e2[j,:,:]\
                                                   ,0,p,q)

            ubezloc,wbezloc=BezierCoord.Bezier_loc(w_local,IXloc,C,u_local,nen\
                                                   ,ne_bez,ndm,p,q,r)
            
        if ndm==3:
        
            i=C_num[ne][1]
            j=C_num[ne][2]
            k=C_num[ne][3]
            
            C=full_Elem_Extraction_Operator.ful_Ce(ndm,C_e1[i,:,:],C_e2[j,:,:]\
                                                   ,C_e3[k,:,:],p,q,r)
            
            ubezloc,wbezloc=BezierCoord.Bezier_loc(w_local,IXloc,C,u_local,nen\
                                                   ,ne_bez,ndm,p,q,r)
        
        'we need to store this'
        
        for i in range(0,nen,1):
            for j in range(0,3,1):
                
                k=ixbez[temp_tnel+ne][i]-patch_info['numpbez']
                
                # if k>=len(temp_ubez):
                ubez[k-1][j]=ubezloc[i][j]

                    
        
        '''
        j2 = sorted(i for i in j if i >= 5)
        why didn't i use the entire temp displacement
        '''
                
    return ubez


