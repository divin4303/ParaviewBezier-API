# -*- coding: utf-8 -*-
'''=====================================
Creates the paraview file in folder named 
'''
try:
    from paraview.simple import *
    import paraview.vtk as vtk
    import paraview.vtk.util.numpy_support as vnp
    
    par=True
except ImportError:
    print('Could not find Paraview module so the compression \
          feature will not be enabled')
    par=False
import os
import numpy as np

class writeVTU:
    
    def __init__(self,ndm,nump,nel,nen,w,x,ixbez,global_order,Input):
        
        self.ndm    =ndm            #number of dimentions'
        self.nump   =nump           #number of bezier points'
        self.nel    =nel            #number of elements
        self.nen    =nen            #maximum number of nodes in element
        self.x      =x              #Bezier coordinates
        self.ix     =ixbez          #IX array
        self.w      =w              #Bezier weights
        self.order  =global_order   #order of each patch
        self.comp   =Input["compFlag"]
        self.path   =Input["destination file path"]
    
    def Set(self,filename,timefl=False,ufl=False,u=np.zeros((1,1,3))):
        
        self.filename=filename
        self.timefl=timefl
        self.ufl=ufl
        self.u=u #if concurrent.futures is used else comment
        
    def compress(self,filename):
        
        print("Checking: ", filename)
        fline = open(filename).readline().rstrip()
        if ("compressor" in fline):
            print(self.filename, "is already compressed! skipping to the next file...")
            # if already compressed, skip the file
        else:
            print("Converting: ", filename)
        
            if self.comp=="True":
                  
                vtu_read = XMLUnstructuredGridReader(FileName=[filename])
                writer = XMLUnstructuredGridWriter \
                (FileName=[filename],CompressorType=3,CompressionLevel=9) 
                writer.DataMode="Binary" # appended, ascii
                writer.UpdatePipeline()
                
    def uparaview(self,nstep=0):
        
        u=self.u[nstep,:,:] #comment this and add the u as input parameter
        
        # c_dir = os.getcwd()
        path = os.path.join(self.path, r'Paraview')
        if not os.path.exists(path):
            os.makedirs(path)
            
        # set extender name
        parext='.vtu'
        
        self.filename=os.path.splitext(self.filename)[0]
        if not self.timefl:
            # Filename to write
            filename = self.filename+"_paraview"
        #file naming for mutliple file outputs current time step=nstep
        
        else:
            if nstep<=9:
                filename=self.filename+"_paraview"+"00"+str(nstep)
            elif nstep<=99:
                filename=self.filename+"_paraview"+"0"+str(nstep)
            elif nstep<=999:
                filename=self.filename+"_paraview"+str(nstep)
        
        filename=filename+parext
        
        'CELL DATA HIGHER ORDER======================================='
        degrees = vtk.vtkDoubleArray()
        degrees.SetName("HigherOrderDegrees");
        degrees.SetNumberOfComponents(3);
        for i in range(0,self.nel):
            degrees.InsertNextTuple3(self.order[i][0],\
                                     self.order[i][1],self.order[i][2]);

        'POINTS======================================================='
        self.x=np.array(self.x, dtype=np.float)
        'adding a third column for ndm=2'
        if self.ndm==2:
            x_temp=self.x
            x=np.zeros((x_temp.shape[0],x_temp.shape[1]+1),dtype=np.float)
            for i in range(x_temp.shape[0]):
                x[i][x_temp.shape[1]]=0
            for i in range(x_temp.shape[0]):
                for j in range(x_temp.shape[1]):        
                    x[i][j]=x_temp[i][j]
        else:
            x=self.x
        
        points = vtk.vtkPoints()
        points.SetData(vnp.numpy_to_vtk(x))
        'CELL CONNECTIVITY============================================'
        ix_temp=np.array(self.ix, dtype=np.int64)
        temp=[]
        '''
        format for cell connectivity is number of nodes/control points in an
        element followed by the node ids
        this then could handle multipatch problems
        '''
        for i in range(ix_temp.shape[0]):
            count=0
            for j in range(ix_temp.shape[1]):
                
                if ix_temp[i][j]>0:
                    count+=1
            temp.append(count)
            
        ix=np.zeros((ix_temp.shape[0],ix_temp.shape[1]+1),dtype=np.int64)
        
        for i in range(len(temp)):
            ix[i][0]=temp[i]
        for i in range(ix_temp.shape[0]):
            for j in range(ix_temp.shape[1]):        
                ix[i][j+1]=ix_temp[i][j]-1
        
        cells = vtk.vtkCellArray()
        cells.SetCells(ix_temp.shape[0], vnp.numpy_to_vtkIdTypeArray(ix))
    # ======================================================================
        '''
        format for adding rational weights:
            node id followed by the weight
        '''
        rationalWeight = vtk.vtkDoubleArray()
        rationalWeight.SetName("RationalWeights")
        rationalWeight.SetNumberOfComponents(1)
        rationalWeight.SetNumberOfTuples(self.nump)
        
        for i in range(self.nump):            
            rationalWeight.SetValue(i,self.w[i])
        'Element Tyape ==============================================='
        if self.ndm==2:
            elementType=vtk.VTK_BEZIER_QUADRILATERAL
        elif self.ndm==3:
            elementType=vtk.VTK_BEZIER_HEXAHEDRON
        'SETTING INPUT FOR WRITER====================================='
        uGrid =vtk.vtkUnstructuredGrid()
        uGrid.GetCellData().SetHigherOrderDegrees(degrees)
        uGrid.SetPoints(points) # sets the points
        uGrid.SetCells(elementType, cells) #sets connectivity buffer and cell type
        uGrid.GetPointData().SetRationalWeights(rationalWeight)
        if self.ufl:
            # Displacement=====================================================
            disp = vtk.vtkDoubleArray()
            disp.SetName('Displacements')
            disp.SetNumberOfComponents(3)
            disp.SetNumberOfTuples(self.nump)
            for i in range(0,self.nump):
                  disp.InsertTuple3(i,u[i][0],u[i][1],u[i][2])
            uGrid.GetPointData().SetVectors(disp)
            # print(self.nump)
        

        'LINE FROM PARAVIEW PAGE======================================' 
        tp = TrivialProducer()
        tp.GetClientSideObject().SetOutput(uGrid)
        
        'write ascii data============================================='
        if self.comp=="True":
            
            writer = XMLUnstructuredGridWriter(Input=tp,CompressorType=3,CompressionLevel=9)
            writer.DataMode="Binary"
        else:
            writer = XMLUnstructuredGridWriter(Input=tp)
            writer.DataMode="Ascii"
            
        writer.FileName=path+'\\'+filename
        writer.UpdatePipeline()
        
        # self.compress(path+'\\'+filename)
    
def paraview_module():
    return par
    