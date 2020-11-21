# -*- coding: utf-8 -*-
"""
======================================
input: number of dimensions,starting position for nodal information.

processing: temp file created exlcuding the lines starting with $
            information positions are noted and the values are taken to list using pandas
            the file is then processed to create bazier paravie file.
            
output: n,m,l: number of nodal points in r,s,t dir.
        p,q,r: order of the fn in r,s,t dir.
        Node_info: position of the pointer.
        nel,mel,lel: number of elements in r,s,t dir
        knot_r,knot_S,knot_t: number of elemtns in r,s,t dir.
======================================
"""

def NodeInfo(df,Node_info,ndm,filename):
    
    knot_r=[]
    knot_s=[]
    knot_t=[]
    p,q,r,n,m,l,wfl,i=(0,0,0,1,1,1,0,0)
    # x, y, z=([],[],[])
    rk,sk,tk=(0,0,0)
    
    npid= df.iloc[Node_info,0]
    pid = df.iloc[Node_info,1]
    n   = int(df.iloc[Node_info,2])
    p   = int(df.iloc[Node_info,3])
    rk=n+p+1   #length of knots vector
    
    #print(df.iloc[Node_info,:])
    if ndm==2:
        
        m   = int(df.iloc[Node_info,4])
        q   = int(df.iloc[Node_info,5])
        sk=m+q+1
    
    if ndm==3:
        
         m   = int(df.iloc[Node_info,4])
         q   = int(df.iloc[Node_info,5])
         l   = int(df.iloc[Node_info,6])
         r   = int(df.iloc[Node_info,7])
         sk=m+q+1
         tk=l+r+1
    
    Node_info=Node_info+1 #for wfl
    
    wfl = int(df.iloc[Node_info,0])
          
    Node_info=Node_info+1 #knot vector information start line
    i=0

    # print(rk)  
    
    for count in range(0,rk):
        
        if i>=8:
            
            Node_info=Node_info+1
            i=0
        
        #print(i)
        rknot=float(df.iloc[Node_info,i])
        knot_r.append(rknot) #since the numbers are written in odd widths
        i+=1
    if ndm > 1:    
        Node_info=Node_info+1 #knot vector along s information start line
        i=0
    
    for count in range(0,sk):
        
        if i>=8:
            
            Node_info=Node_info+1
            i=0
        
        sknot=float(df.iloc[Node_info,i])
        knot_s.append(sknot) #since the numbers are written in odd widths
        i+=1
    if ndm > 2:
        Node_info=Node_info+1 #knot vector along s information start line
        i=0
    
    for count in range(0,tk):
        
        if i>=8:
            
            Node_info=Node_info+1
            i=0
        
        tknot=float(df.iloc[Node_info,i])
        knot_t.append(tknot) #since the numbers are written in odd widths
        i+=1
    
    #number of knots (needs few more conditions)
    nel,mel,lel=(0,0,0)
    for i in range(p,rk-1):
        if knot_r[i]!=knot_r[i+1]:
            nel=nel+1
    
    for j in range(q,sk-1):
        if knot_s[j]!=knot_s[j+1]:
            mel=mel+1
    
    for k in range(r,tk-1):
        if knot_t[k]!=knot_t[k+1]:
            lel=lel+1
            # print(knot_t[k],lel)
      
    # if ndm==2:
    #     tnel=nel
    # if ndm==2:
    #     nel=nel*mel
    # elif ndm==3:
    #     nel=nel*mel*lel
    
    #print(nel,mel,lel)
    
    # reading connectivity information total rows to read
    '2D conn=m rows* n columns and for 3D l*m rows and n columns'
    Node_info=Node_info+1
    ncon=l*m
    conn = [[0 for i in range(n)] for j in range(ncon)]
    
    for k in range(0,ncon):
        i=0
        
        for j in range(0,n):
            
            if i>=8:
                Node_info=Node_info+1
                i=0
            t=int(df.iloc[Node_info,i])
            
            conn[k][j]=t #since the numbers are written in odd widths
            i+=1
        Node_info=Node_info+1
    
    if wfl !=0:
        wght = [[0 for i in range(n)] for j in range(ncon)]
        for k in range(0,ncon):
            i=0
            for j in range(0,n):
                
                if i>=8:
                    Node_info=Node_info+1
                    i=0
                    
                t=float(df.iloc[Node_info,i])
                wght[k][j]=t #since the numbers are written in odd widths
                i+=1
            Node_info=Node_info+1
    
    return n,m,l,p,q,r,knot_r,knot_s,knot_t,conn,wght,Node_info,nel,mel,lel