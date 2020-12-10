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
def multipl(XI,p):
    m=len(XI)-1 
    'for the array index other for end knot '
    b=p+1
    el_mult=[]
    
    while b<m:
        i=b
        while b<m and XI[b+1]==XI[b]:
            b=b+1
        el_mult.append(b-i+1)
        b=b+1
    
    return el_mult

def NodeInfo(df,Node_info,ndm,filename):
    
    knot_r=[]
    knot_s=[]
    knot_t=[]
    p,q,r,n,m,l,wfl,i=(0,0,0,1,1,1,0,0)
    # x, y, z=([],[],[])
    rk,sk,tk=(0,0,0)
    
    position=Node_info
    
    npid= df.iloc[position,0]
    pid = df.iloc[position,1]
    n   = int(df.iloc[position,2])
    p   = int(df.iloc[position,3])
    rk=n+p+1   #length of knots vector
    
    patch_infos = {
        "n": n,
        "p": p,
    }
    
    if ndm==2:
        
        m   = int(df.iloc[position,4])
        q   = int(df.iloc[position,5])
        sk=m+q+1
        
        patch_infos.update({
            "m": m,
            "q": q,
        })
    
    if ndm==3:
        
         m   = int(df.iloc[position,4])
         q   = int(df.iloc[position,5])
         l   = int(df.iloc[position,6])
         r   = int(df.iloc[position,7])
         sk=m+q+1
         tk=l+r+1
         
         patch_infos.update({
             "m": m,
             "q": q,
             "l": l,
             "r": r,
        })
    
    position=position+1 #for wfl
    
    wfl = int(df.iloc[position,0])
          
    position=position+1 #knot vector information start line
    i=0

    # print(rk)  
    
    for count in range(0,rk):
        
        if i>=8:
            
            position=position+1
            i=0
        
        rknot=float(df.iloc[position,i])
        knot_r.append(rknot) #since the numbers are written in odd widths
        i+=1
    if ndm > 1:    
        position=position+1 #knot vector along s information start line
        i=0
    
    for count in range(0,sk):
        
        if i>=8:
            
            position=position+1
            i=0
        
        sknot=float(df.iloc[position,i])
        knot_s.append(sknot) #since the numbers are written in odd widths
        i+=1
    if ndm > 2:
        position=position+1 #knot vector along s information start line
        i=0
    
    for count in range(0,tk):
        
        if i>=8:
            
            position=position+1
            i=0
        
        tknot=float(df.iloc[position,i])
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
      
    patch_infos.update({
        "nel": nel,
        "mel": mel,
        "lel": lel,
        })
    
    nel_mult=multipl(knot_r,p)
    mel_mult=multipl(knot_s,q)
    lel_mult=multipl(knot_t,r)
    
    patch_infos.update({
        "nel mult": nel_mult,
        "mel mult": mel_mult,
        "lel mult": lel_mult,
        })
            
    # reading connectivity information total rows to read
    '2D conn=m rows* n columns and for 3D l*m rows and n columns'
    position=position+1
    ncon=l*m
    conn = [[0 for i in range(n)] for j in range(ncon)]
    
    for k in range(0,ncon):
        i=0
        
        for j in range(0,n):
            
            if i>=8:
                position=position+1
                i=0
            t=int(df.iloc[position,i])
            
            conn[k][j]=t #since the numbers are written in odd widths
            i+=1
        position=position+1
    
    if wfl !=0:
        wght = [[0 for i in range(n)] for j in range(ncon)]
        for k in range(0,ncon):
            i=0
            for j in range(0,n):
                
                if i>=8:
                    position=position+1
                    i=0
                    
                t=float(df.iloc[position,i])
                wght[k][j]=t #since the numbers are written in odd widths
                i+=1
            position=position+1
    
    return patch_infos,knot_r,knot_s,knot_t,conn,wght,position