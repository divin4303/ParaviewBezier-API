# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 10:11:43 2020

@author: User
"""
def uparaview(ndm,nump,nel,nen,w,x,ixbez,global_order,filename,u,nstep=0,timefl=True,ufl=True):
    
    # set extender name
    parext='.vtu'
    
    if not timefl:
        # Filename to write
        filename = filename+"_paraview"
    #file naming for mutliple file outputs current time step=nstep
    
    else:
        if nstep<9:
            filename=filename+"_paraview"+"00"+str(nstep)
        elif nstep<99:
            filename=filename+"_paraview"+"0"+str(nstep)
        elif nstep<999:
            filename=filename+"_paraview"+str(nstep)
    
    filename=filename+parext
    
    # Open the file with writing permission
    myfile = open(filename, 'w')
    
    # Write a line to the file  1000
    myfile.write('<?xml version="1.0"?>\n')
    myfile.write('<VTKFile type="UnstructuredGrid" version="2.2">\n')
    myfile.write('<UnstructuredGrid>\n')
    
    #write #1020
    myfile.write('<Piece NumberOfPoints="%s" NumberOfCells="%s">\n' % (nump, nel))
    
    #1060
    myfile.write('<CellData HigherOrderDegrees="HigherOrderDegrees">')
    
    myfile.write('\n<DataArray type="%s" Name="%s" NumberOfComponents=" %s" format="ascii">'%('Float64','HigherOrderDegrees',3))
    
    for i in range(0,nel):
        myfile.write('\n%8d %8d %8d'%(global_order[i][0],global_order[i][1],global_order[i][2]))
    myfile.write('\n</DataArray>')
    
    myfile.write('</CellData>')
    myfile.write('\n<Points>')
    
    myfile.write('\n<DataArray type="%s" Name="%s" NumberOfComponents="%s" format="ascii">'%('Float64','Points',3))
    if ndm==1:
            for i in range(0,nump):
                myfile.write('\n%14.5E %14.5E %14.5E'%(x[i][0],0,0))
    
    if ndm==2:
            for i in range(0,nump):
                myfile.write('\n%14.5E %14.5E %14.5E'%(x[i][0],x[i][1],0))
    
    if ndm==3:
            for i in range(0,nump):
                myfile.write('\n%14.5E %14.5E %14.5E'%(x[i][0],x[i][1],x[i][2]))

    myfile.write('\n</DataArray>')
    
    myfile.write('\n</Points>')
    myfile.write('\n<Cells>')
    
    myfile.write('\n<DataArray type="%s" Name="%s" NumberOfComponents="%s" format="ascii">'%('Int32','connectivity',1))
    
    el_ptr = [0 for i in range(nel)]
    el_ptr[0] = 0
    for i in range(0,nel):
        el_ptr[i]= el_ptr[i-1]
        myfile.write('\n')
        for ii in range(0,nen):
            node = ixbez[i][ii]
            if node > 0:
                myfile.write('%8d'%(node-1))
                el_ptr[i] = el_ptr[i] + 1
                             
    myfile.write('\n</DataArray>')
    
    myfile.write('\n<DataArray type="%s" Name="%s" NumberOfComponents="%s" format="ascii">'%('Int32','offsets',1))
    
    myfile.write('\n')
    for i in range(nel):
        myfile.write('%8d'%(el_ptr[i]))
        
    myfile.write('\n</DataArray>')
    
    myfile.write('\n<DataArray type="%s" Name="%s" NumberOfComponents=" %s" format="ascii">'%('UInt8','types',1))
    for i in range(0,nel):
        if(ndm==1):
            myfile.write('\n%8d'%(75))
        elif(ndm==2):
            myfile.write('\n%8d'%(77))
        elif(ndm==3):
            myfile.write('\n%8d'%(79))
        else:
            myfile.write('UNSUPPORTED ELEMENT TYPE')
    
    myfile.write('\n</DataArray>')
    
    myfile.write('\n</Cells>')
    
    myfile.write('\n<PointData>')

# ======================================================================
    myfile.write('\n<DataArray type="%s" Name="%s" format="ascii">'%('Float64', 'RationalWeights'))
    
    #2000
    for i in range(0,nump):
        myfile.write('\n%14.5E'%(w[i]))
    
    myfile.write('\n</DataArray>')
# Displacement==========================================================
    if ufl:
        myfile.write('\n<DataArray type="%s" Name="%s" NumberOfComponents="%s" format="ascii">'%('Float64','Displacements',3))
        for i in range(0,nump):
            for j in range(0,3):
                myfile.write('%14.5E'%(u[i][j]))
            myfile.write('\n')

            
        myfile.write('\n</DataArray>')                 # Close Displ.
    myfile.write('\n</PointData>')
    myfile.write('\n</Piece>')
    
    myfile.write('\n</UnstructuredGrid> </VTKFile>')
    
    
    # Close the file
    myfile.close()