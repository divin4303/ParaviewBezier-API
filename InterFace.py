# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 18:45:40 2021

@author: User
"""

from tkinter import *
from tkinter import filedialog
import ntpath
from writeVTU import *
import os

class InterFace:
    
    def __init__(self):
        
        self.root=Tk()
        self.filepath="None"
        self.filename="None"
        self.destpath=os.getcwd()
        self.e1   = Entry(self.root,width=35,borderwidth=5)
        self.e2   = Entry(self.root,width=35,borderwidth=5)
        self.r    = StringVar()
        self.s    = StringVar()
        self.p    = StringVar()
        self.c    = StringVar()
        
        self.root.title("ParaViewBezier")
        self.root.iconbitmap(f"{os.getcwd()}\Image\geo.ico")
        
        self.dispFlag=False
        self.strFlag =False
        self.parFlag =False
        self.compFlag=False
        
    def button_click(self):
        
        self.filepath, self.filename = ntpath.split(self.e1.get())
        self.destpath                = self.e2.get()
        # self.filename=self.e2.get()
        # self.filepath=self.e1.get()
        self.dispFlag=self.r.get()
        self.strFlag=self.s.get()
        self.parFlag=self.p.get()
        self.compFlag=self.c.get()
        
    def file_opener1(self):
        
        
        filename = filedialog.askopenfilename(initialdir=os.getcwd())
        self.e1.insert(END, filename)

    def file_opener2(self):
        
        
        filepath = filedialog.askdirectory(initialdir=os.getcwd())
        self.e2.insert(0, filepath)        
        
    def interface(self):
        
        mylabel1=Label(self.root,text="File Location:")
        mylabel2=Label(self.root,text="Destination  :")
        
        mylabel1.grid(row=0,column=0,columnspan=1,padx=10,pady=10)
        mylabel2.grid(row=1,column=0,columnspan=1,padx=10,pady=10)
        
        button_browse1=Button(self.root, text ='Browse', command = self.file_opener1)
        button_browse2=Button(self.root, text ='Browse', command = self.file_opener2)
        
        button_browse1.grid(row=0,column=4,columnspan=1,padx=10,pady=10)
        button_browse2.grid(row=1,column=4,columnspan=1,padx=10,pady=10)
        
        opt1=Checkbutton(self.root,text="Displacement",variable=self.r,\
                         onvalue="True",offvalue="False")
        opt2=Checkbutton(self.root,text="Stress",variable=self.s,\
                         onvalue="True",offvalue="False")
        opt3=Checkbutton(self.root,text="Parallel Processing",variable=self.p,\
                         onvalue="True",offvalue="False")
        
        button_accept=Button(self.root,text="Accept",command=self.button_click)
        button_quit=Button(self.root,text="Submit",command=self.root.destroy)
        
        self.e1.grid(row=0,column=1,columnspan=3,padx=10,pady=10)
        self.e2.grid(row=1,column=1,columnspan=3,padx=10,pady=10)  
        
        opt1.deselect()
        opt2.deselect()
        opt3.deselect()
        
        opt1.grid(row=2,column=0,columnspan=2,sticky="W")
        opt2.grid(row=3,column=0,columnspan=2,sticky="W")
        opt3.grid(row=4,column=0,columnspan=2,sticky="W")
        
        if paraview_module()== True:
            
            opt4=Checkbutton(self.root,text="Compressed VTK",\
                             variable=self.c,onvalue="True",offvalue="False")
            opt4.deselect()
            opt4.grid(row=5,column=0,columnspan=2,sticky="W")
    
        button_quit.grid(row=6,column=2,padx=10,pady=10)
        button_accept.grid(row=6,column=1,padx=10,pady=10)
        
        self.root.mainloop()
        
        Input={
            "filename"               :self.filename,
            "filepath"               :self.filepath,
            "destination file path"  :self.destpath,
            "dispFlag"               :self.dispFlag,
            "strFlag"                :self.strFlag,
            "Parallel processing"    :self.parFlag,
            "compFlag"               :self.compFlag
            }
        
        return Input
    
    def display(self,patch_ID):
        
        status=Label(self.root,text="processing patch:"+str(patch_ID),bd=1,\
                     relief=SUNKEN,anchor=W)
        status.grid(row=1,column=1,columnspan=3,sticky=W+E)
        self.root.mainloop()
        return