"""
======================================
input: filename.

processing: temp file created exlcuding the lines starting with $
            information positions are noted and the values are taken to list using pandas
            the file is then processed to create bazier paraview file.
            
output: vtk file
======================================
"""
import numpy as np
import os
import sys
import mesh_bezier
import File_Info
import Mesh
import unstructured_paraview as upar
import read
import Read_d3plot
import dis_bezier

import time
t0=[]


wbez=[]
numpbez=0
global_ixbez=[[]]
global_order=np.zeros((0,3))
tnel=0
Num_patch=0
X, Y, Z=([],[],[])
patch_info_end=[]       


filename = sys.argv[1]
try:
    with open(filename+'.k','r') as f:
        lines=f.readline()
        temp=open("temp.k", "w")       
        for line in f:
            
            if not line.startswith('$#'):
                temp.write(line)
        
        temp.close()
except IOError:
    # 'File not found' error message.
    print('File not found')  

Node_info,df,ndm,coord_info,nnode=read.read_keywordfile(lines)
node_displacement,tstep=Read_d3plot.read_d3plot()

BezPoints=np.zeros((0,ndm))

vbez=np.zeros((0,ndm))
abez=np.zeros((0,ndm))

for i in range(len(coord_info)):
    X+=list(df.iloc[coord_info[i]:nnode[i],1].to_numpy(dtype=float))
    Y+=list(df.iloc[coord_info[i]:nnode[i],2].to_numpy(dtype=float))
    Z+=list(df.iloc[coord_info[i]:nnode[i],3].to_numpy(dtype=float))
    patch_info_end.append(coord_info[i]-1)

no_of_nodes=len(X)
x = [[0 for i in range(3)] for j in range(no_of_nodes)]
u = [[0 for i in range(3)] for j in range(no_of_nodes)]

for i in range(no_of_nodes):
    
    x[i][0]=X[i]
    x[i][1]=Y[i]
    x[i][2]=Z[i]
  

for i in range(len(Node_info)): 
    print('s',Node_info[i],patch_info_end[i])
    while patch_info_end[i]!=Node_info[i]:
        
        Num_patch+=1
        n,m,l,p,q,r,knot_r,knot_s,knot_t,conn,wght,Node_info[i],nel,mel,lel=\
        File_Info.NodeInfo(df,Node_info[i],ndm,filename)
        
        t0.append(time.time())
        
        BezPoints,wbez,numpbez,ixbez,nen,temp_tnel=\
        mesh_bezier.bez_patch(ndm,nel,mel,lel,n,m,l,p,q,r,knot_r,knot_s,\
                                    knot_t,conn,wght,x,BezPoints,wbez,numpbez)
        t0.append(time.time())
        
        tnel+=temp_tnel
        
        global_ixbez,global_order,nen=\
        Mesh.Bezier_IX(nen,tnel,ixbez,global_ixbez,global_order,p,q,r)
        
        t0.append(time.time())

ubez=np.zeros((len(BezPoints),3))
for i in range(22):
    'filtering the '
    'u=node_displacement - x'
    for j in range(no_of_nodes):
        for k in range(3):
            u[j][k]=node_displacement[j+(no_of_nodes*i)][k]-x[j][k]
    if i==1:
        print(j+(no_of_nodes*i),u)
    'just pass the global ixbez since the global ixbez has information about \
    all the nodes'
    
    ubez=dis_bezier.state_variable(ndm,nel,mel,lel,n,m,l,p,q,r,knot_r,knot_s,\
                                   knot_t,conn,wght,u,ubez,wbez,global_ixbez)
    
    upar.uparaview(ndm,numpbez,tnel,nen,wbez,BezPoints,global_ixbez,\
                   global_order,filename,ubez,i)


for i in range(1,len(t0)):
    print('time: ',t0[i]-t0[i-1])
    
os.remove('temp.k')
    
        