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
from multiprocessing import Pool
import time

import mesh_bezier
import File_Info
import Mesh
import unstructured_paraview as upar
import read
import Read_d3plot
import dis_bezier


t0=[]

wbez=[]
numpbez=0
global_ixbez=[[]]
global_order=np.zeros((0,3))

tnel=0
tnumnp=0
Num_patch=0
X, Y, Z=([],[],[])     


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


Node_info,df,ndm,coord_info,nnode,patch_info_end=read.read_keywordfile(lines)

print(coord_info,'*******',nnode)
BezPoints=np.zeros((0,ndm))

for i in range(len(coord_info)):
    X+=list(df.iloc[coord_info[i]:nnode[i],1].to_numpy(dtype=float))
    Y+=list(df.iloc[coord_info[i]:nnode[i],2].to_numpy(dtype=float))
    Z+=list(df.iloc[coord_info[i]:nnode[i],3].to_numpy(dtype=float))
    
no_of_nodes=len(X)
x = [[0 for i in range(3)] for j in range(no_of_nodes)]

for i in range(no_of_nodes):
    
    x[i][0]=X[i]
    x[i][1]=Y[i]
    x[i][2]=Z[i]
  
u,tstep=Read_d3plot.read_d3plot(3,no_of_nodes,x)
uglobal=np.zeros((tstep,0,3))

for i in range(len(Node_info)):
    
    print(Node_info[i],u.shape)
    
    while patch_info_end[i]!=Node_info[i]:
        
        temp_uglobal=[]
        Num_patch+=1
        
        patch_info,knot_r,knot_s,knot_t,conn,wght,Node_info[i]=\
        File_Info.NodeInfo(df,Node_info[i],ndm,filename)
        
        
        BezPoints,wbez,numpbez,ixbez,nen,temp_tnel=\
        mesh_bezier.bez_patch(ndm,patch_info,knot_r,knot_s,\
                                    knot_t,conn,wght,x,BezPoints,wbez,numpbez)
        tnel+=temp_tnel
        patch_info.update({
            'Bezier_points':len(BezPoints)})
        
        'try multiprocessing' 
        for t in range(tstep):
            ubez=dis_bezier.state_variable(ndm,patch_info,knot_r,\
                                   knot_s,knot_t,conn,wght,u[t,:,:],uglobal[t,:,:],wbez,\
                                       ixbez)
            temp_uglobal.append(np.pad(ubez,((0, 0), (0, 0))))
        temp_uglobal = np.stack(temp_uglobal)
        
        uglobal=temp_uglobal
            
        global_ixbez,global_order,nen=\
        Mesh.Bezier_IX(ndm,nen,tnel,ixbez,global_ixbez,global_order,patch_info)
        

for i in range(tstep):
    
    upar.uparaview(ndm,numpbez,tnel,nen,wbez,BezPoints,global_ixbez,\
                    global_order,filename,uglobal[i,:,:],i)
    
os.remove('temp.k')
print('Done :)')    
        
