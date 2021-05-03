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
import tkinter as tk
from tkinter import ttk


import mesh_bezier
import File_Info
import Mesh
from writeVTU import *
import read
import Read_d3plot
import dis_bezier
from InterFace import *
import fnmatch


    
def main(path,Input,root,e1,progress,lines):
    
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
     
    e1.insert(END,f"{len(Node_info)} parts(s) with {len(X)} NURBS Control points\n",'big')
    
    root.update()
    no_of_nodes  =    len(X)
    x            =    [[0 for i in range(3)] for j in range(no_of_nodes)]
    timeCounter1 =    time.perf_counter()
    for i in range(no_of_nodes):
        
        x[i][0]=X[i]
        x[i][1]=Y[i]
        x[i][2]=Z[i]
    
    if not path:
        e1.insert(END,"no d3plot files given\n")
    elif Input["dispFlag"]== "False" and Input["strFlag"]=="False":
        e1.insert(END,"No displacement results or stress results are selected\n")
    else:
        u,tstep=Read_d3plot.read_d3plot(path,3,no_of_nodes,x)
        e1.insert(END,f"{len(path)} d3plot file(s) with {tstep} timestep(s)\n",'big')
        
        if u.size:
            u_flag=True
        if tstep!=0:
            time_flag=True
    
    progress['value']=30
    root.update()
    
    uglobal=np.zeros((tstep,0,3))
      
    for i in range(len(Node_info)):
        
        while patch_info_end[i]!=Node_info[i]:
            
            temp_uglobal =   []
            Num_patch   +=   1
            
            patch_info,knot_r,knot_s,knot_t,conn,wght,Node_info[i]=\
            File_Info.NodeInfo(df,Node_info[i],ndm)
            
            patch_info.update({
                'numpbez'   :numpbez,
                'numpatch'  :Num_patch})
            
            patch_BezPoints,patch_wbez,numpbez,ixbez,nen,temp_tnel=\
            mesh_bezier.bez_patch(ndm,patch_info,knot_r,knot_s,\
                                        knot_t,conn,wght,x,numpbez)
            
            e1.insert(END,"====================================\n")
            e1.insert(END,'Processing patch     :%d\n'%(Num_patch))
            e1.insert(END,'Number of elements   :%d\n'%(temp_tnel))
            tnel+=temp_tnel
            patch_info.update({
                'Bezier_points':len(patch_BezPoints)})
            
            temp_uglobal=np.zeros((tstep,numpbez,3))
            
            if Input["dispFlag"]== "True":
                progress['value']+=(20/len(Node_info))
                e1.insert(END,'====Extracting displacement information====\n',
                          'big2')
                root.update()
                e1.insert(END,'Total number of timesteps     :%d\n'%(tstep))
                for t in range(tstep):
                    patch_ubez=uglobal[t,:,:]
                    ubez=dis_bezier.state_variable(ndm,patch_info,knot_r,\
                                           knot_s,knot_t,conn,wght,u[t,:,:],patch_wbez,\
                                               ixbez)
                    patch_ubez          =   np.row_stack((patch_ubez,ubez))
                    temp_uglobal[t,:,:] =   patch_ubez
                    
                    
                    progress['value']+=(20/tstep)
                    root.update()
            else:
                progress['value']+=(40/len(Node_info))
                root.update()                
            
            BezPoints   =   np.row_stack((BezPoints,patch_BezPoints))
            wbez        =   np.hstack((wbez,patch_wbez))
            uglobal     =   temp_uglobal
                
            global_ixbez,global_order,nen=\
            Mesh.Bezier_IX(ndm,nen,tnel,ixbez,global_ixbez,global_order,patch_info)
            
    
    vtu=writeVTU(ndm,numpbez,tnel,nen,wbez,BezPoints,global_ixbez,\
                 global_order,Input)
    
    timeCounter2 = time.perf_counter()
    if time_flag:
        e1.insert(END,'====Writing VTK files====\n','big2')
        root.update()
        
        tstep=list(range(0,tstep,1))
        vtu.Set(Input["filename"],time_flag,u_flag,uglobal)
        
        
        if Input["Parallel processing"]=="True":
            e1.insert(END,"Parallel processing enabled\n")
            root.update()
            with concurrent.futures.ProcessPoolExecutor() as executor:  
                executor.map(vtu.uparaview,tstep)
            progress['value']+=30
            root.update()
        
        else:
            e1.insert(END,"Parallel processing not enabled\n")
            root.update()
            for i in tstep:
                vtu.uparaview(i)
                progress['value']+=(30/len(tstep))
                root.update()
            
    else:
        vtu.Set(Input["filename"],time_flag,u_flag)
        vtu.uparaview()
        progress['value']+=30
    
    timeCounter3 = time.perf_counter()
 
    e1.insert(END,"==========\n")
    e1.insert(END,"***FINISHED***\n",'big2')
    e1.insert(END,f'Read and process the file in {timeCounter2-timeCounter1} second(s)\n')
    e1.insert(END,f'Output file writen in {timeCounter3-timeCounter2} second(s)\n')
    e1.insert(END,"VTU files written to paraview folder in {}\n"\
              .format(Input["destination file path"])) 
    root.update()