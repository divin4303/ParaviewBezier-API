"""
======================================
input: filename.
output: vtk file
======================================
"""
import numpy as np
import os
import sys
import glob
import concurrent.futures
import time


import mesh_bezier
import File_Info
import Mesh
from writeVTU import *
import read
import Read_d3plot
import dis_bezier
from InterFace import *
import fnmatch

# filename = sys.argv[1]
# filedir = sys.argv[2]

def main(path,Input):
    
    
    global_ixbez=       [[]]
    global_order=       np.zeros((0,3))
    X, Y, Z     =       ([],[],[])
    u           =       np.array([])
    
    tnel        =       0                       #total number of elements
    numpbez     =       0                       #total number of nodal points
    tstep       =       0                       #number of timesteps
    Num_patch   =       0                       #total number of patches
    
    time_flag   =   False                       #time flag
    u_flag      =   False                       #displacement flag 
    
    'Read_keyword routine read .k file'
    Node_info,df,ndm,coord_info,nnode,patch_info_end=read.read_keywordfile(lines)
    
    BezPoints   =   np.zeros((0,ndm))           #Bezier points per patch
    wbez        =   np.array([])                #Bezier weight per patch
    
    for i in range(len(coord_info)):
        X+=list(df.iloc[coord_info[i]:nnode[i],1].to_numpy(dtype=float))
        Y+=list(df.iloc[coord_info[i]:nnode[i],2].to_numpy(dtype=float))
        Z+=list(df.iloc[coord_info[i]:nnode[i],3].to_numpy(dtype=float))
    print(f"{len(Node_info)} components with {len(X)} NURB nodes")   
    no_of_nodes =    len(X)
    x           =    [[0 for i in range(3)] for j in range(no_of_nodes)]
    
    for i in range(no_of_nodes):
        
        x[i][0]=X[i]
        x[i][1]=Y[i]
        x[i][2]=Z[i]
    
    if not path:
        print('no d3plot files given')
    elif Input["dispFlag"]== "False" and Input["strFlag"]=="False":
        print("No displacement results or stress results are selected")
    else:
        u,tstep=Read_d3plot.read_d3plot(path,3,no_of_nodes,x)
        print(f"{len(path)} d3plot files with {tstep} timestep(s)")
        
        if u.size:
            u_flag=True
        if tstep!=0:
            time_flag=True
    
    uglobal=np.zeros((tstep,0,3))
    
    for i in range(len(Node_info)):
        
        while patch_info_end[i]!=Node_info[i]:
            
            temp_uglobal =   []
            Num_patch   +=   1
            print('====================================')
            print('Processing ptach     :%d'%(Num_patch))
            
            patch_info,knot_r,knot_s,knot_t,conn,wght,Node_info[i]=\
            File_Info.NodeInfo(df,Node_info[i],ndm)
            
            patch_info.update({
                'numpbez'   :numpbez,
                'numpatch'  :Num_patch})
            
            patch_BezPoints,patch_wbez,numpbez,ixbez,nen,temp_tnel=\
            mesh_bezier.bez_patch(ndm,patch_info,knot_r,knot_s,\
                                        knot_t,conn,wght,x,numpbez)
            print('number of elements   :%d'%(temp_tnel))
            tnel+=temp_tnel
            patch_info.update({
                'Bezier_points':len(patch_BezPoints)})
            
            temp_uglobal=np.zeros((tstep,numpbez,3))
            
            if Input["dispFlag"]== "True":
                for t in range(tstep):
                    patch_ubez=uglobal[t,:,:]
                    ubez=dis_bezier.state_variable(ndm,patch_info,knot_r,\
                                           knot_s,knot_t,conn,wght,u[t,:,:],wbez,\
                                               ixbez)
                    patch_ubez          =   np.row_stack((patch_ubez,ubez))
                    temp_uglobal[t,:,:] =   patch_ubez
            
            BezPoints   =   np.row_stack((BezPoints,patch_BezPoints))
            wbez        =   np.hstack((wbez,patch_wbez))
            uglobal     =   temp_uglobal
                
            global_ixbez,global_order,nen=\
            Mesh.Bezier_IX(ndm,nen,tnel,ixbez,global_ixbez,global_order,patch_info)
            
    
    vtu=writeVTU(ndm,numpbez,tnel,nen,wbez,BezPoints,global_ixbez,\
                 global_order,Input)
    
    t1 = time.perf_counter()
    if time_flag:
        
        tstep=list(range(0,tstep,1))
        vtu.Set(Input["filename"],time_flag,u_flag,uglobal)
        
        
        if Input["Parallel processing"]=="True":
            print("==========parallel processing enabled")

            with concurrent.futures.ProcessPoolExecutor() as executor:  
                executor.map(vtu.uparaview,tstep)
        
        else:
            print("==========parallel processing not enabled")
            for i in tstep:
                vtu.uparaview(i)
            
    else:
        vtu.Set(Input["filename"],time_flag,u_flag)
        vtu.uparaview()
    
    t2 = time.perf_counter()
 
    print("==========")
    print(f"***FINISHED*** in {t2-t1} second(s)")

if __name__=='__main__':
    
    
    path            =   []
    inter           =   InterFace()
    Input           =   inter.interface()
    filepath        =   glob.glob(Input["filepath"] + "/*")
    
    for file in filepath:
        if os.path.basename(file).startswith('d3plot'):
            path.append(file)
            
    try:
        with open(Input["filepath"]+'/'+Input["filename"],'r') as f:
            lines   =   f.readline()
            temp    =   open("temp.k", "w")       
            for line in f:
                
                if not line.startswith('$#'):
                    temp.write(line)
            
            temp.close()
        
        main(path,Input)
        os.remove('temp.k')
        print('====================================')
        print(f"VTU files written to paraview folder in {os.getcwd()}")    
        
    except IOError:
        # 'File not found' error message.
        print(f'{Input["filename"]} keyword file not found')
        