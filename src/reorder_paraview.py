# -*- coding: utf-8 -*-
"""
===============================================
input : 
        bezloc              :local Bezier coordinates.
        nen                 :number of element nodes
        ndm                 :number of dimensions
        ne_bez              :current Bezier element
        p,q,r               :order of fn in p,q,r, dir.
output: 
        bezloc              :local Bezier coordinates(reorder).
================================================
"""
def _init_(bezloc,ne_bez,ndm,nen,p,q,r):
#def _init_(ndm=3,nen=27,p=2,q=2,r=2):
    
    conn=[0 for i in range(nen)]
    temp_bezloc=[0 for i in range(nen)]
    
    if ndm==1:
        #end CPS
        conn[0] = 1
        conn[1] = p+1
        
        #inner cps
        pc = 1
        for i in range(1, p):
            pc = pc + 1
            conn[pc] = i + 1
            
    elif ndm==2:# bivariate case
        #print(ndm)
        
        # vertices
        conn[0] = 1
        conn[1] = p+1
        conn[2] = (p+1)*(q+1)
        conn[3] = q*(p+1) + 1
        
        #edges
        pc = 3
        
        #edge 1
        for i in range(1, p):
            pc = pc + 1
            conn[pc] = i + 1
            
        #edge 2
        for i in range(1, q):
            pc = pc + 1
            conn[pc] = (p+1)*(i+1)
            
        #edge 3
        for i in range(1, p):
            pc = pc + 1
            conn[pc] = (p+1)*q + i + 1
            
        #edge 4
        for i in range(1, q):
            pc = pc + 1
            conn[pc] = (p+1)*i + 1
            
        #face
        for j in range(1, q):
            for i in range(1, p):
                pc = pc + 1
                conn[pc] = (p+1)*j + i + 1
                
    elif ndm==3:
        
        #vertices
        conn[0] = 1
        conn[1] = p+1
        conn[2] = (p+1)*(q+1)
        conn[3] = q*(p+1) + 1
        
        conn[4] = (p+1)*(q+1)*r+1
        conn[5] = (p+1)*(q+1)*r+p+1
        conn[6] = (p+1)*(q+1)*(r+1)
        conn[7] = (p+1)*(q+1)*r+q*(p+1) + 1
        
        pc=7
        
        #edge 1
        #print(p)
        for i in range(1, p):
            pc = pc + 1
            conn[pc] = i + 1
           
        #edge 2
        for i in range(1, q):
            pc = pc + 1
            conn[pc] = (p+1)*(i+1)
            
            
        #edge 3
        for i in range(1, p):
            pc = pc + 1
            conn[pc] = (p+1)*q+i+1
        
        #edge 4
        for i in range(1, q):
            pc = pc + 1
            conn[pc] = (p+1)*i+ 1
            
        #edge 5
        for i in range(1, p):
            pc = pc + 1
            conn[pc] = (p+1)*(q+1)*r+i + 1
        
        for i in range(1, q):
            pc = pc + 1
            conn[pc] = (p+1)*(q+1)*r+(p+1)*(i+1)
        
        
        # edge 7
        for i in range(1, p):
            pc = pc + 1
            conn[pc] = (p+1)*(q+1)*r+(p+1)*q+i+1

        
        # edge 8
        for i in range(1, q):
            pc = pc + 1
            conn[pc] = (p+1)*(q+1)*r + (p+1)*i+ 1
           
        # edge 9
        for i in range(1, r):
            pc = pc + 1
            conn[pc] = (p+1)*(q+1)*i + 1
 
        # edge 10
        for i in range(1, r):
            pc = pc + 1
            conn[pc] = (p+1)*(q+1)*i+(p+1)
        
        for i in range(1, r):
            pc = pc + 1
            conn[pc] = (p+1)*(q+1)*i+(p+1)*(q+1)
        # edge 12
        for i in range(1, r):
            pc = pc + 1
            conn[pc] = (p+1)*(q+1)*i+q*(p+1) + 1
        
        #face 1
        for j in range(1, r):
            for i in range(1, q):
                pc = pc + 1
                conn[pc] = (p+1)*(q+1)*j + (p+1)*i + 1
        
        #face 2
        for j in range(1, r):
            for i in range(1, q):
                pc = pc + 1
                conn[pc] = (p+1)*(q+1)*j + (p+1)* (i+ 1)
                
        #face 3
        for j in range(1, r):
            for i in range(1, p):
                pc = pc + 1
                conn[pc] = (p+1)*(q+1)*j+(i + 1)
                
        #face 4
        for j in range(1, r):
            for i in range(1, p):
                pc = pc + 1
                conn[pc] = (p+1)*(q+1)*j+((p+1)*q+i+1)
        
        #face 5
        for j in range(1, q):
            for i in range(1, p):
                pc = pc + 1
                conn[pc] = (p+1)*j + i + 1
                
        #face 6
        for j in range(1, q):
            for i in range(1, p):
                pc = pc + 1
                conn[pc] = ((p+1)*(q+1)*r)+(p+1)*j + i + 1
                # (p+1)*(r+1)*j + i + 1
                
        #print(conn[pc])
        
        #volume
        for k in range(1, r):
            for j in range(1, q):
                for i in range(1,p):
                    pc=pc+1
                    conn[pc]=((p+1)*(q+1)*k)+(p+1)*j + i + 1 
                
  
    #print(pc,'************','\n',conn)
    for i in range(0,nen):
        
        temp_bezloc[i]=bezloc[conn[i]-1]
        
    for i in range(0,nen):
        
        bezloc[i]=temp_bezloc[i]
    # print(conn)
        
    return bezloc