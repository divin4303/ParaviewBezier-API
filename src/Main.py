"""
======================================
input: filename.
output: vtk file
======================================
"""
import numpy as np
import concurrent.futures
import time
import tkinter as tk
from tkinter import ttk
import pandas as pd

import mesh_bezier
import File_Info
import Mesh
from writeVTU import *
import read
import Read_d3plot
import dis_bezier

    
class Main:
    
    def __init__(self,path,Input,root,e1,progress,lines):
        
        'Read_keyword routine read .k file'
        self.df,self.fileInfo =read.read_keywordfile(lines)
        
        self.global_ixbez=       [[]]
        self.global_order=       np.zeros((0,3))
        self.u           =       np.array([])
        self.tnel        =       0               #total number of elements
        self.numpbez     =       0               #total number of nodal points
        self.tstep       =       0               #number of timesteps
        self.Num_patch   =       0               #total number of patches
        self.time_flag   =   False               #time flag
        self.u_flag      =   False               #displacement flag
        self.rendObj     =   None
        self.wbez        =   np.array([])        #Bezier weight per patch
        self.Input       =   Input
        
        'parameters for tk'
        self.e1     	=   e1
        self.root       =   root
        self.progress   =   progress

        self.LoadCoordinates()
        self.timeCounter1 =    time.perf_counter()
        self.LoadDisplacement(path)
        # self.getBezierPoints()
        
    def TextEntry(self,text):
        
        self.e1.insert(tk.END,text)
        self.root.update()    
        
    def LoadCoordinates(self):
        
        x, y, z     =       ([],[],[])
        for i in range(len(self.fileInfo['Coordinate start'])):
            x+=list(self.df.iloc[self.fileInfo['Coordinate start'][i]:\
                            self.fileInfo['Coordinate end'][i],1]
                    .to_numpy(dtype=float))  
            y+=list(self.df.iloc[self.fileInfo['Coordinate start'][i]:\
                            self.fileInfo['Coordinate end'][i],2]
                    .to_numpy(dtype=float))
            z+=list(self.df.iloc[self.fileInfo['Coordinate start'][i]:\
                            self.fileInfo['Coordinate end'][i],3]
                    .to_numpy(dtype=float))
        self.x           =    np.zeros((len(x),3))
    
        for i in range(len(x)):
            
            self.x[i][0]=x[i]
            self.x[i][1]=y[i]
            self.x[i][2]=z[i]
         
        self.TextEntry(f"number of parts : {len(self.fileInfo['patch start'])}\n")
        self.TextEntry(f'NURBS Control points : {len(y)}\n')
                       
        self.no_of_nodes  =    len(y)
        self.timeCounter1 =    time.perf_counter()
    
    
    
    
    def LoadDisplacement(self,path):
        
        if not path:
            self.TextEntry("no d3plot files given\n")
        elif self.Input["dispFlag"]== "False" and self.Input["strFlag"]=="False":
            self.TextEntry("No displacement or")
            self.TextEntry(" stress results are selected\n")
        else:
            self.u,self.tstep=Read_d3plot.read_d3plot(path,3,
                                                      self.no_of_nodes,self.x)
            self.TextEntry(f"{len(path)} d3plot file(s) with \
                           {self.tstep} timestep(s)\n")
            
            if self.u.size:
                self.u_flag=True
            if self.tstep!=0:
                self.time_flag=True
        
        self.progress['value']=30
        self.root.update()
        
        
        
        
    def getBezierPoints(self,input_t):
        
        print(self.fileInfo)
        
        for i in range(len(self.fileInfo['patch start'])):
            s       = []
            self.patch   = {}
            
            EOP     =self.fileInfo['patch start'][i]
            ndm     =self.fileInfo['dimensions'][i]
            self.BezPoints   =   np.zeros((0,ndm))   #Bezier points per patch
            
            while self.fileInfo['patch end'][i]!=EOP:
                
                self.Num_patch   +=   1
                patch_info,knot_r,knot_s,knot_t,conn,wght,EOP=File_Info.NodeInfo(self.df
                                                                                 ,EOP
                                                                                 ,ndm)
                
                patch_info.update({
                    'numpbez'   :self.numpbez,
                    'numpatch'  :self.Num_patch})
                
                patch_BezPoints,patch_wbez,self.numpbez,ixbez,nen,temp_tnel=\
                mesh_bezier.bez_patch(ndm,patch_info,knot_r,knot_s,\
                                        knot_t,conn,wght,self.x,self.numpbez)
                    
                self.TextEntry("====================================\n")
                self.TextEntry('Processing patch     :%d\n'%(self.Num_patch))
                self.TextEntry('Number of elements   :%d\n'%(temp_tnel))
                self.tnel+=temp_tnel
                patch_info.update({
                    'Bezier_points':len(patch_BezPoints),
                    'patch_tnel':self.tnel})
                
                self.BezPoints   =   np.row_stack((self.BezPoints,patch_BezPoints))
                self.wbez        =   np.hstack((self.wbez,patch_wbez))
                
                
                self.global_ixbez,self.global_order,self.nen=Mesh.Bezier_IX(ndm,nen,self.tnel,
                                                             ixbez,self.global_ixbez,
                                                             self.global_order,patch_info)
                
                self.patch.update({'patch_info_{}'.format(self.Num_patch):patch_info})
            self.progress['value']+=(20/len(self.fileInfo['patch start']))
            self.root.update()
                
        
        self.vtu=writeVTU(self.fileInfo['dimensions'][0],self.numpbez,self.tnel,
                            self.nen,self.wbez,self.BezPoints,self.global_ixbez,
                            self.global_order,self.Input)
        self.vtu.Set(self.Input["filename"],self.time_flag,self.u_flag)
        self.TextEntry('====Extracting displacement information====\n')
        self.TextEntry('Total number of timesteps     :%d\n'%(self.tstep))
        self.timeCounter2 =    time.perf_counter()
        
        self.WithoutDisplacement()
        if self.time_flag==True:
          self.getDisplacement(input_t)
          
        self.TextEntry("==========\n")
        self.TextEntry("***FINISHED***\n")
        self.TextEntry(f'Read and process the file in {self.timeCounter2-self.timeCounter1}\
                       second(s)\n')
        self.TextEntry(f'Output file writen in {self.timeCounter3-self.timeCounter2} second(s)\n')
        self.TextEntry("VTU files written in {}/paraview\n"
                       .format(self.Input["destination file path"]))
        print("***FINISHED***\n")
        print(self.progress['value'])
            
    def getDisplacement(self,input_t):
        
        self.tstep=input_t[1]
        progress=self.progress
        root=self.root
        tstep   =list(range(input_t[0],self.tstep,1))
        s=sh(self.fileInfo,self.patch,self.df,self.u,
             self.global_ixbez,self.vtu,self.Input)
        # s.Set(self.e1,self.progress,self.root,self.tstep)
        
        self.TextEntry('====Calculating Bezier displacement====\n')
        self.TextEntry('====Writing VTK files====\n')
        
        if self.Input["Parallel processing"]=="True":
              self.TextEntry("Parallel processing enabled\n")
              self.root.update()
              with concurrent.futures.ProcessPoolExecutor() as executor:  
                  executor.map(s.calcDisp,tstep)
        else:
             self.TextEntry("Parallel processing not enabled\n")
             self.root.update()
             for i in tstep:
                s.calcDisp(i)
                
        self.timeCounter3 =    time.perf_counter() 
        progress['value']+=50
        root.update() 
                

        
    def WithoutDisplacement(self):
        
        temp1=self.vtu.ufl
        temp2=self.vtu.timefl
        self.vtu.ufl=False
        self.vtu.timefl=False
        
        if temp1==False or self.time_flag==False:
            self.progress['value']+=20
            self.root.update()
        
        if paraview_module()== True:
            self.rendObj=self.vtu.paraviewSimple()
        else:
            self.vtu.uparaview()
            
        if temp1==False or self.time_flag==False:
            self.progress['value']+=30
            self.root.update()
            
        self.vtu.ufl=temp1
        self.vtu.timefl=temp2
        
        self.timeCounter3 = time.perf_counter()

class sh:
    
    def __init__(self,fileInfo,patch,df,u,global_ixbez,vtu,Input):
        
        self.fileInfo=fileInfo
        self.patch=patch
        self.df=df
        self.global_ixbez=global_ixbez
        self.u=u
        self.vtu=vtu
        self.simpleFlag=Input["simple Flag"]
    def calcDisp(self,t):
        
        temp_Numpatch=0
        ubez    =np.zeros((0,3))
        for i in range(len(self.fileInfo['patch start'])):
            EOP=self.fileInfo['patch start'][i]
            ndm=self.fileInfo['dimensions'][i]
            
            while self.fileInfo['patch end'][i]!=EOP:
                
                temp_Numpatch+=1
                patch_info,knot_r,knot_s,knot_t,conn,wght,EOP=File_Info.NodeInfo(self.df
                                                                                ,EOP,ndm)
                patch_info=self.patch['patch_info_{}'.format(temp_Numpatch)]
                tnel=patch_info['patch_tnel']
                
                patch_ubez=dis_bezier.state_variable(ndm,patch_info,knot_r,
                                                knot_s,knot_t,conn,wght,tnel,
                                                self.u[t,:,:],self.global_ixbez)
                ubez          =   np.row_stack((ubez,patch_ubez))
        
        
        if self.simpleFlag==True:
            print(self.simpleFlag)
            self.vtu.paraviewSimple(t,ubez)
        else:
            self.vtu.uparaview(t,ubez)