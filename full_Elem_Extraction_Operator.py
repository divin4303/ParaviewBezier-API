# -*- coding: utf-8 -*-
"""
==================================================================
input : ndm                 : number of nodal points in r,s,t dir.
        ceta_T              : directional operator in eta dir.
        Cxi_T               : directional operator in xi dir.
        Cphi_T              : directional operator in phi dir.
        p,q,r               : order of fn in r,s,t dir.
        
        
Output: C_e                 :element extraction operator for ith element.
==================================================================
"""

def ful_Ce(ndm,Ceta_T=0,Cxi_T=0,Cphi_T=0,p=0,q=0,r=0):
    C_e=[]
    
    Ctemp_rows,Ctemp_cols = ((p+1)*(q+1), (p+1)*(q+1))
    C_rows,C_cols=((p+1)*(q+1)*(r+1), (p+1)*(q+1)*(r+1))
    #print(ndm,rows, cols,C_rows,C_cols)
    
    Ceta=[[0 for i in range(p+1)] for j in range(p+1)]
    Cxi=[[0 for i in range(q+1)] for j in range(q+1)] 
    Cphi=[[0 for i in range(r+1)] for j in range(r+1)]
    
    C_e=[[0 for i in range(C_cols)] for j in range(C_rows)]
    C_temp=[[0 for i in range(Ctemp_cols)] for j in range(Ctemp_rows)]
    
    if ndm==1:
        for i in range(0,p+1):
            for j in range(0,p+1):
                C_e[i,j]=Cxi_T[j,i]
        
    if ndm==2:
        
        for i in range(0,p+1):
            for j in range(0,p+1):
                Cxi[i][j]=Cxi_T[j][i]
        for i in range(0,q+1):
            for j in range(0,q+1):
                Ceta[i][j]=Ceta_T[j][i]
                
        #kronecker product
        for i in range(0,q+1): #for row a
            for k in range(0,p+1): #for row b
                for j in range(0,q+1):
                    for l in range(0,p+1):
                        mm=j*(p+1)+l
                        nn=i*(p+1)+k
                        C_e[nn][mm] = Ceta[k][l]*Cxi[i][j]
        
    if ndm==3:#trivariate case
    
        for i in range(0,q+1):
            for j in range(0,q+1):
                Cxi[i][j]=Cxi_T[j][i]
        for i in range(0,p+1):
            for j in range(0,p+1):
                Ceta[i][j]=Ceta_T[j][i]
        for i in range(0,r+1):
            for j in range(0,r+1):
                Cphi[i][j]=Cphi_T[j][i]
                
        #kronecker product between ceta and cxi=C_temp
        for i in range(0,q+1): #for row a
            for k in range(0,p+1): #for row b
                for j in range(0,q+1):
                    for l in range(0,p+1):
                        mm=j*(p+1)+l
                        nn=i*(p+1)+k
                        #print(mm,nn,i,j,k,l,Ceta[i][j],Cxi[k][l])
                        C_temp[nn][mm] = Ceta[k][l]*Cxi[i][j]
        
        
        #kronecker product between cphi and C_temp
        C_temp_ord=(p+1)*(q+1)
        for i in range(0,r+1): #for row a
            for k in range(0,C_temp_ord): #for row b
                for j in range(0,r+1):
                    for l in range(0,C_temp_ord):
                        qq=j*(C_temp_ord)+l
                        pp=i*(C_temp_ord)+k
                        C_e[pp][qq] = C_temp[k][l]*Cphi[i][j]
   
    return C_e