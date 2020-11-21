# -*- coding: utf-8 -*-
"""
==================================================================
input : XI                  :knot vector for 'r' dir.
        poly                :polynomial order of 'r' dir.
        
Output: stacked_array       :stacked 3D array (2D arrray per element).
==================================================================
"""
import numpy as np

def Operator(XI,poly):

    C=[]
    alphas=[]
    arrays=[]
    m=len(XI)-1;
    a=poly; 
    b=a+1;
    nb=1;
    C=np.identity(poly+1)
    C1=np.identity(poly+1)
    
    while b<m:
        alphas=[]
        C=C1
        C1=np.identity(poly+1)
       
        i=b
        
        while b<m and XI[b+1]==XI[b]:
            b=b+1
        mult=b-i+1
        
        
        if mult<poly:
            numerator=XI[b]-XI[a]
            for j in range(poly,mult,-1):
                alphas.append(round(numerator/(XI[a+j]-XI[a]),7))
            r=poly-mult
            #print('alpha',alphas)
           
            for j in range(0,r):
                save=r-j
                s=mult+j+1
                for k in range(poly+1,s,-1):
                    alpha=alphas[k-s-1]
                   
                    C[:,k-1]=alpha*C[:,k-1]+(1-alpha)*C[:,k-2]
                if b<m:
                    
                    C1[save-1:j+save+1,save-1]=C[poly-j-1:poly+1,poly]
                   

            nb=nb+1
            if b<m:
                a=b
                b=b+1
        elif mult==poly:
            nb=nb+1
            if b<m:
                a=b
                b=b+1
        arrays.append(np.pad(C,((0, 0), (0, 0))))
    stacked_array = np.stack(arrays)

    return stacked_array