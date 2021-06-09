# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import filedialog
from Main import *
import tkinter as tk
from tkinter import ttk
import vtk

try:
    from paraview.simple import *
except ImportError:
    print('Could not find Paraview module so the compression \
          feature will not be enabled')

import ntpath
import os
import sys
import glob

intro_text='\
----------------------------------------------------------------------\n\
Author : Divin Xavier (divin.pulakudiyil@st.ovgu.de)\n\
         Otto von Guericke University Magdeburg\n\
         Germany\n\
-----------------------------------------------------------------------\n\
     Modification log                                Date (dd/mm/year)\n\
     Original version                                    02/04/2021\n\
-----------------------------------------------------------------------\n\
Browse or Enter the input and destination file location.\n\
Press \'Load Files\' button to load the input files\n\
-----------------------------------------------------------------------\n'
margin='-----------------------------------------------------------------------\n'
class InterFace:
    
    def __init__(self,root):
        
        self.root=root
        self.filepath="None"
        self.filename="None"
        self.destpath=os.getcwd()
        self.e1   = Entry(self.root,width=35,borderwidth=5)
        self.e2   = Entry(self.root,width=35,borderwidth=5)
        self.r    = StringVar()
        self.s    = StringVar()
        self.p    = StringVar()
        self.c    = StringVar()
        self.a    = StringVar()
        
        self.root.title("ParaViewBezier")
        self.root.iconbitmap("..\Image\geo.ico")
        
        self.dispFlag  =False
        self.strFlag   =False
        self.parFlag   =False
        self.compFlag  =False
        self.simpleFlag=False
        self.interface()
    
    'to get the path to file location'
    def file_opener1(self):
        
        self.e1.delete(0, 'end')
        filename = filedialog.askopenfilename(initialdir=os.getcwd())
        self.e1.insert(END, filename)
     
        
     
    'to get the destination path (by default it is cwd)'
    def file_opener2(self):
        
        self.e2.delete(0, 'end')
        filepath = filedialog.askdirectory(initialdir=os.getcwd())
        self.e2.insert(0, filepath)
    
    
    
    'to get the keyword file information and checkbox details'
    def CheckButton(self):
        
        self.filepath, self.filename = ntpath.split(self.e1.get())
        self.destpath                = self.e2.get()
        self.dispFlag=self.r.get()
        self.strFlag=self.s.get()
        self.parFlag=self.p.get()
        self.compFlag=self.c.get()
        self.simpleFlag=self.a.get()
        
        self.Input={
            "filename"               :self.filename,
            "filepath"               :self.filepath,
            "destination file path"  :self.destpath,
            "dispFlag"               :self.dispFlag,
            "strFlag"                :self.strFlag,
            "Parallel processing"    :self.parFlag,
            "compFlag"               :self.compFlag,
            "simple Flag"            :self.simpleFlag
            }
        path            =   []
        filepath        =   glob.glob(self.Input["filepath"] + "/*")
        
        for file in filepath:
            if os.path.basename(file).startswith('d3plot'):
                path.append(file)
                
        try:
            with open(self.Input["filepath"]+'/'+self.Input["filename"],'r') as f:
                lines   =   f.readline()
                temp    =   open("temp.k", "w")       
                for line in f:
                    
                    if not line.startswith('$#'):
                        temp.write(line)
                
                temp.close()
            
            self.text.insert(END,f'Input File  : {self.filename}\n')
            self.text.insert(END,f'Destination : {self.destpath}\n')
            self.main=Main(path,self.Input,self.root,self.text,self.progress,
                           lines)
            
            label3      = tk.Label(self.root,
                                   text=f"Total Available :  {self.main.tstep}")

            label3.grid(row=12,column=2,columnspan=1,padx=5)
            self.text.insert(END,'*FINISHED* reading input file(s)\n')
            self.text.insert(END,margin)
            self.text.insert(END,'Computing Bezier Coordinate(s)...\n')
                
        except IOError:
            # 'File not found' error message.
            print(f'{self.Input["filename"]} keyword file not found')
    
    
    
    'directs to the main routine for computation'
    def Submitbutton(self):
        
        Input_t=[]
        if self.main.time_flag==True:
            Input_t.append(int(self.e3.get()))
            Input_t.append(int(self.timeStepEnd.get()))
            if int(self.e3.get())==0 and int(self.timeStepEnd.get())==0:
                self.main.time_flag=False
                self.text.insert(tk.END,'Time step not selected\n')
            else:
                self.text.insert(tk.END,f'{Input_t[1]-Input_t[0]}sime step(s) selected\n')
        self.Input.update({
            'Compressor Type'  :self.CompressorType.get(),
            'Compression Level':int(self.CompressionLevel.get()),
            'Compressor Mode'  :self.CompressorMode.get()})
        self.main.getBezierPoints(Input_t)
    
    
    
    'open geometry from GUI'
    def open_Geomtery(self):
        
        filename = self.main.filename
        vtu_read = vtk.vtkXMLUnstructuredGridReader()
        vtu_read.SetFileName(filename)
        vtu_read.Update()
            
        ugrid2   = vtu_read.GetOutput()
        
        colors = vtk.vtkNamedColors()
        tess = vtk.vtkTessellatorFilter()
        tess.SetMaximumNumberOfSubdivisions(3);
        tess.SetInputData(ugrid2);
    
        mapper = vtk.vtkDataSetMapper()
        
        tessellate=True
        
        if tessellate:
            
            mapper.SetInputConnection(tess.GetOutputPort())
            
        else:
            
            mapper.SetInputData(ugrid2);
        
        actor=vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().EdgeVisibilityOn()
        
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renderer.ResetCamera()
        
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.SetWindowName("Bezier")
        renderWindow.AddRenderer(renderer)
        
        istyle = vtk.vtkInteractorStyleSwitch()
        istyle.SetCurrentStyleToTrackballCamera()
        
        interactor = vtk.vtkRenderWindowInteractor()
    
        interactor.SetRenderWindow(renderWindow)
        
        renderWindow.Render()
        interactor.Initialize()
        interactor.Start()
    
    def BEXTfile(self):
        
        self.main.BEXT.uparaview(self.Input["filename"])
        
    'interface design loaded from __init__ method'
    def interface(self):
        
        label1=Label(self.root,text="File Location :")
        label2=Label(self.root,text="Destination :")
        
        button_browse1=Button(self.root, text ='Browse', 
                              command = self.file_opener1,width=10)
        button_browse2=Button(self.root, text ='Browse', 
                              command = self.file_opener2,width=10)
        
        opt1=Checkbutton(self.root,text="Displacement",variable=self.r,
                         onvalue="True",offvalue="False")
        opt2=Checkbutton(self.root,text="Stress",variable=self.s,
                         onvalue="True",offvalue="False")
        opt3=Checkbutton(self.root,text="Parallel Processing",variable=self.p,
                         onvalue="True",offvalue="False")
        
        button_quit=Button(self.root,text=" Quit ",command=self.root.destroy,width=10)
        button_accept=Button(self.root,text="Read Data",
                             command=self.CheckButton,width=10)
        
        opt1.deselect()
        opt2.deselect()
        opt3.deselect()
        
        if paraview_module()== True:
            
            opt4=Checkbutton(self.root,text="Compress VTU",\
                             variable=self.c,onvalue="True",offvalue="False")
            opt5=Checkbutton(self.root,text="Enable ParaView Writing",\
                             variable=self.a,onvalue=True,offvalue=False)
            
            opt4.deselect()
            opt5.deselect()
            
            opt4.grid(row=6,column=0,padx=5,sticky="W")
            opt5.grid(row=5,column=0,padx=5,sticky="W")
        
        self.progress= ttk.Progressbar(self.root,orient=HORIZONTAL,length=300,
                                       mode='determinate')
        label3       = tk.Label(self.root,text="Progress :")
        chat_space   = tk.Frame(self.root, bg="blue")
        self.text    = tk.Text(chat_space,width=65,height=10,borderwidth=2)
        submitButton =Button(self.root, text ='Submit', 
                             command = self.Submitbutton,width=10)
        openGeomtery =Button(self.root, text ='Open Geometry', 
                             command = self.open_Geomtery)
        genBEXTButton =Button(self.root, text ='Generate BEXT File', 
                             command = self.BEXTfile,width=25)
        
        OPTIONS = list(range(1,10))
        variable = StringVar(self.root)
        variable.set(str(OPTIONS[0]))
        CompressorType_label= tk.Label(self.root,text="Compressor Type :")
        self.CompressorType = ttk.Combobox(self.root,state="readonly" ,
                                           value= ["LZ4", "ZLib", "LZMA"])
        CompressionLevel_label      = tk.Label(self.root,
                                               text="Compressor Level :")
        self.CompressionLevel = ttk.Combobox(self.root,state="readonly",
                                             value=list(map(str,OPTIONS)))
        CompressorMode_label      = tk.Label(self.root,
                                             text="Compressor Data Mode :")
        self.CompressorMode = ttk.Combobox(self.root,state="readonly",
                                           value= ["Ascii", "Binary"])
        self.CompressionLevel.current(8)
        self.CompressorType.current(2)
        self.CompressorMode.current(0)
        
        timeStepLabel      = tk.Label(self.root,text="Total Available :  0")
        NB_label= tk.Label(self.root,text=
        'NB : Compressor Type, Level and Data Mode options are acitvated only if Compress VTU button is enabled',
        width=80)
        
        gridframe = tk.Frame(self.root)
        label4      = tk.Label(gridframe,text="Desired Time Steps :     From-  ")\
            .pack(side=tk.LEFT)
        self.e3     = Entry(gridframe,width=7,borderwidth=5)
        self.e3.pack(side=tk.LEFT)
        self.e3.insert(0, 0)
        timestep_to_label=tk.Label(gridframe,text=' To-  ').pack(side=tk.LEFT)
        self.timeStepEnd     = Entry(gridframe,width=7,borderwidth=5)
        self.timeStepEnd.pack(side=tk.LEFT)
        self.timeStepEnd.insert(0, 0)
        
        canvas_1 = Canvas(self.root, width=80,height=2)
        canvas_1.create_line(0, 3, 10000,3, width = 2)
        canvas_2 = Canvas(self.root, width=80,height=2)
        canvas_2.create_line(0, 3, 10000,3, width = 2)

        label1.grid(row=0,column=0,columnspan=1,padx=5,pady=10,sticky="W")
        label2.grid(row=1,column=0,columnspan=1,padx=5,sticky="W")
        
        button_browse1.grid(row=0,column=4,columnspan=1,padx=5,pady=10,sticky="W")
        button_browse2.grid(row=1,column=4,columnspan=1,padx=5,sticky="W")
        
        self.e1.grid(row=0,column=1,columnspan=3,padx=5,sticky="EW")
        self.e2.grid(row=1,column=1,columnspan=3,padx=5,sticky="EW")
        
        opt1.grid(row=2,column=0,padx=5,sticky="W")
        opt2.grid(row=3,column=0,padx=5,sticky="W")
        opt3.grid(row=4,column=0,padx=5,sticky="W")
        # opt2.grid(row=2,column=1,padx=5,sticky="W")
        # opt3.grid(row=2,column=2,padx=5,sticky="W")
        
        button_accept.grid(row=6,column=4,padx=5,pady=10,sticky="W")
        canvas_1.grid(row=7, column=0,columnspan=6,sticky='NSEW')
        NB_label.grid(row=8,column=0,columnspan=6,padx=5,sticky="W")
        CompressorMode_label.grid(row=9,column=0,padx=5,pady=5,sticky="W")
        self.CompressorMode.grid(row=9,column=1,padx=5,pady=5,sticky="W")
        CompressorType_label.grid(row=10,column=0,padx=5,pady=5,sticky="W")
        self.CompressorType.grid(row=10,column=1,padx=5,pady=5,sticky="W")
        CompressionLevel_label.grid(row=11,column=0,padx=5,pady=5,sticky="W")
        self.CompressionLevel.grid(row=11,column=1,padx=5,pady=5,sticky="W")
        gridframe.grid(row=12,column=0,columnspan=2,padx=5,pady=5,sticky="W")
        # label4.grid(row=12,column=0,padx=5,pady=5,sticky="W")
        # self.e3.grid(row=12,column=1,padx=5,pady=5,sticky="W")
        # timestep_to_label.grid(row=12,column=2,padx=5,sticky="W")
        # self.timeStepEnd.grid(row=12,column=3,columnspan=1,padx=5,pady=5,sticky="W")
        timeStepLabel.grid(row=12,column=2,padx=5,sticky="w")
        submitButton.grid(row=12,column=4,columnspan=1,padx=5,pady=5,sticky="W")
        canvas_2.grid(row=14, column=0,columnspan=6,sticky='NSEW')
        genBEXTButton.grid(row=15,column=3,columnspan=2,padx=5,pady=5,sticky="W")
        self.progress.grid(row=15,column=1,columnspan=2,padx=5,sticky="EW")
        label3.grid(row=15,column=0,columnspan=1,padx=5,pady=5,sticky="W")
        openGeomtery.grid(row=16,column=3,columnspan=1,padx=5,pady=5,sticky="W")
        button_quit.grid(row=16,column=4,padx=5,pady=10,sticky="W")
        chat_space.grid(row=17,column=0,columnspan=6,padx=5,pady=5,sticky='NSEW')
        
        self.text.pack(fill="both", expand=True)
        self.root.grid_columnconfigure(2, uniform="uniform", weight=1)
        self.root.grid_rowconfigure(17, uniform="uniform", weight=1)
        # self.root.grid_rowconfigure(11, weight=1)
        # self.root.grid_columnconfigure(4, weight=100)
        self.text.insert(tk.END,intro_text)
        self.text.see(tk.END)
        self.root.mainloop()

        
    
if __name__=='__main__':
    
    root=Tk()
    inter           =   InterFace(root)
    try:
        os.remove('temp.k')
        os.remove('temp1.k')
        os.remove('PatchInfo.h5')
    except:
        print('no temp file created')
    root.mainloop()