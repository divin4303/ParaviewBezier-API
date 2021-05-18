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
        self.w      =w              #Bezier weights
        self.x      =x              #Bezier coordinates
        self.ix     =ixbez          #IX array
        self.order  =global_order   #order of each patch
        self.comp   =Input["compFlag"]
        self.path   =Input["destination file path"]
        self.CompressionLevel=Input['Compression Level']
        self.CompressorMode=Input['Compressor Mode']
        if Input['Compressor Type']=='fastest':
            self.CompressorType=1
        elif Input['Compressor Type']=='balanced':
            self.CompressorType=2
        else:
            self.CompressorType=3
        
    def Set(self,filename,timefl=False,ufl=False):
        
        self.filename=filename
        self.timefl=timefl
        self.ufl=ufl
        #if concurrent.futures is used else comment
        
    def compress(self,filename):
        
        print("Checking: ", filename)
        fline = open(filename).readline().rstrip()
        if ("compressor" in fline):
            print(self.filename, "is already compressed! skipping to the next file...")
            # if already compressed, skip the file
        else:
            print("Converting: ", filename)
        
            # if self.comp=="True":
                  
            vtu_read = XMLUnstructuredGridReader(FileName=[filename])
            writer = XMLUnstructuredGridWriter \
            (FileName=[filename],CompressorType=self.CompressorType,
             CompressionLevel=self.CompressionLevel) 
            writer.DataMode=self.CompressorMode # appended, ascii
            writer.UpdatePipeline()
                
    def uparaview(self,nstep=0,u=0):
        
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
        
        # Open the file with writing permission
        myfile = open(path+'\\'+filename, 'w')
        
        # Write a line to the file  1000
        myfile.write('<?xml version="1.0"?>\n')
        myfile.write('<VTKFile type="UnstructuredGrid" version="2.2">\n')
        myfile.write('<UnstructuredGrid>\n')
        
        #write #1020
        myfile.write('<Piece NumberOfPoints="%s" NumberOfCells="%s">\n' % (self.nump, self.nel))
        
        #1060
        myfile.write('<CellData HigherOrderDegrees="HigherOrderDegrees">')
        
        myfile.write('\n<DataArray type="%s" Name="%s" NumberOfComponents=" %s" format="ascii">'%('Float64','HigherOrderDegrees',3))
        
        for i in range(0,self.nel):
            myfile.write('\n%8d %8d %8d'%(self.order[i][0],self.order[i][1],self.order[i][2]))
        myfile.write('\n</DataArray>')
        
        myfile.write('</CellData>')
        myfile.write('\n<Points>')
        
        myfile.write('\n<DataArray type="%s" Name="%s" NumberOfComponents="%s" format="ascii">'%('Float64','Points',3))
        if self.ndm==1:
                for i in range(0,self.nump):
                    myfile.write('\n%14.5E %14.5E %14.5E'%(self.x[i][0],0,0))
        
        if self.ndm==2:
                for i in range(0,self.nump):
                    myfile.write('\n%14.5E %14.5E %14.5E'%(self.x[i][0],self.x[i][1],0))
        
        if self.ndm==3:
                for i in range(0,self.nump):
                    myfile.write('\n%14.5E %14.5E %14.5E'%(self.x[i][0],self.x[i][1],self.x[i][2]))
    
        myfile.write('\n</DataArray>')
        
        myfile.write('\n</Points>')
        myfile.write('\n<Cells>')
        
        myfile.write('\n<DataArray type="%s" Name="%s" NumberOfComponents="%s" format="ascii">'%('Int32','connectivity',1))
        
        el_ptr = [0 for i in range(self.nel)]
        el_ptr[0] = 0
        for i in range(0,self.nel):
            el_ptr[i]= el_ptr[i-1]
            myfile.write('\n')
            for ii in range(0,self.nen):
                node = self.ix[i][ii]
                if node > 0:
                    myfile.write('%8d'%(node-1))
                    el_ptr[i] = el_ptr[i] + 1
                                 
        myfile.write('\n</DataArray>')
        
        myfile.write('\n<DataArray type="%s" Name="%s" NumberOfComponents="%s" format="ascii">'%('Int32','offsets',1))
        
        myfile.write('\n')
        for i in range(self.nel):
            myfile.write('%8d'%(el_ptr[i]))
            
        myfile.write('\n</DataArray>')
        
        myfile.write('\n<DataArray type="%s" Name="%s" NumberOfComponents=" %s" format="ascii">'%('UInt8','types',1))
        for i in range(0,self.nel):
            if(self.ndm==1):
                myfile.write('\n%8d'%(75))
            elif(self.ndm==2):
                myfile.write('\n%8d'%(77))
            elif(self.ndm==3):
                myfile.write('\n%8d'%(79))
            else:
                myfile.write('UNSUPPORTED ELEMENT TYPE')
        
        myfile.write('\n</DataArray>')
        
        myfile.write('\n</Cells>')
        
        myfile.write('\n<PointData>')
    
    # ======================================================================
        myfile.write('\n<DataArray type="%s" Name="%s" format="ascii">'%('Float64', 'RationalWeights'))
        
        #2000
        for i in range(0,self.nump):
            myfile.write('\n%14.5E'%(self.w[i]))
        
        myfile.write('\n</DataArray>')
    # Displacement==========================================================
        if self.ufl:
            myfile.write('\n<DataArray type="%s" Name="%s" NumberOfComponents="%s" format="ascii">'%('Float64','Displacements',3))
            for i in range(0,self.nump):
                for j in range(0,3):
                    myfile.write('%14.5E'%(u[i][j]))
                myfile.write('\n')
            myfile.write('</DataArray>')                 # Close Displ.
        myfile.write('\n</PointData>')
        myfile.write('\n</Piece>')
        
        myfile.write('\n</UnstructuredGrid> </VTKFile>')
        
        
        # Close the file
        myfile.close()
        
        if self.comp=="True":
            self.compress(path+'\\'+filename)
            
    def paraviewSimple(self,nstep=0,u=0):
        
        tp=None
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
        # for i in range(ix_temp.shape[0]):
        #     for j in range(ix_temp.shape[1]):
        #         if ix_temp[i][j]>0:
        #             ix_temp[i][j]=ix_temp[i][j]-1
        # temp=[]
        # '''
        # format for cell connectivity is number of nodes/control points in an
        # element followed by the node ids
        # this then could handle multipatch problems
        # '''
        # for i in range(ix_temp.shape[0]):
        #     count=0
        #     for j in range(ix_temp.shape[1]):
                
        #         if ix_temp[i][j]>0:
        #             count+=1
        #     temp.append(count)
            
        # ix=np.zeros((ix_temp.shape[0],ix_temp.shape[1]+1),dtype=np.int64)
        
        # for i in range(len(temp)):
        #     ix[i][0]=temp[i]
        # for i in range(ix_temp.shape[0]):
        #     for j in range(ix_temp.shape[1]):        
        #         ix[i][j+1]=ix_temp[i][j]-1
        
        # cells = vtk.vtkCellArray()
        # cells.SetCells(ix_temp.shape[0], vnp.numpy_to_vtkIdTypeArray(ix))
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
        uGrid.SetPoints(points) # sets the points
        # uGrid.SetCells(elementType, cells) #sets connectivity buffer and cell type
        for i in range(ix_temp.shape[0]):
            temp=[]
            for j in range(ix_temp.shape[1]):
                if ix_temp[i][j]>0:
                    temp.append(ix_temp[i][j]-1)
            uGrid.InsertNextCell(elementType,len(temp),temp)
        uGrid.GetCellData().SetHigherOrderDegrees(degrees)
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
            
            writer = XMLUnstructuredGridWriter(Input=tp,
                                               CompressorType=self.CompressorType,
                                               CompressionLevel=self.CompressionLevel)
            writer.DataMode=self.CompressorMode
        else:
            writer = XMLUnstructuredGridWriter(Input=tp)
            writer.DataMode=self.CompressorMode
            
        writer.FileName=path+'\\'+filename
        writer.UpdatePipeline()
        
        return tp
    
def paraview_module():
    return par
    