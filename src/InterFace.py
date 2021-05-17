# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 18:45:40 2021

@author: User
"""

from tkinter import *
from tkinter import filedialog
from Main import *
import tkinter as tk
from tkinter import ttk

import ntpath
import os
import sys
import glob


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
    
    def file_opener1(self):
        
        self.e1.delete(0, 'end')
        filename = filedialog.askopenfilename(initialdir=os.getcwd())
        self.e1.insert(END, filename)

    def file_opener2(self):
        
        self.e2.delete(0, 'end')
        filepath = filedialog.askdirectory(initialdir=os.getcwd())
        self.e2.insert(0, filepath)
    
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
                
            self.textFrame()
            self.main=Main(path,self.Input,self.root,self.text,self.progress,lines)
            
            # if self.main.tstep!=0:
            label2      = tk.Label(self.root,text="Time Steps : Desired")
            label3      = tk.Label(self.root,text=f"Total Available :  {self.main.tstep}")
            self.e3     = Entry(self.root,width=35,borderwidth=5)
            
            self.e3.insert(0, 0)
            label3.grid(row=8,column=3,columnspan=1,padx=50,pady=10)
            label2.grid(row=8,column=0,columnspan=1,padx=10,pady=10)
            self.e3.grid(row=8,column=1,columnspan=1,padx=10,pady=10)
                
        except IOError:
            # 'File not found' error message.
            print(f'{self.Input["filename"]} keyword file not found')
    
    def Submitbutton(self):
        
        Input_t=0
        if self.main.time_flag==True:
            Input_t=int(self.e3.get())
            
            if Input_t==0:
                self.main.time_flag=False
                self.e1.insert(tk.END,'Time step not selected\n')
  
        self.main.getBezierPoints(Input_t)
        
        
    def textFrame(self):
        
        self.progress= ttk.Progressbar(self.root,orient=HORIZONTAL,length=290,
                                       mode='determinate')
        label1       = tk.Label(self.root,text="Progress:")
        chat_space   = tk.Frame(self.root, bg="blue")
        self.text    = tk.Text(chat_space,width=65,height=10,borderwidth=2)
        submitButton =Button(self.root, text ='submit', command = self.Submitbutton)
        
        
        self.progress.grid(row=7,column=1,padx=10,pady=10)
        label1.grid(row=7,column=0,columnspan=1,padx=10,pady=10)
        submitButton.grid(row=8,column=4,columnspan=1,padx=10,pady=10)
        chat_space.grid(row=9,column=0,columnspan=5,padx=0,sticky=NSEW)
        self.text.pack(fill="both", expand=True)
        self.text.tag_configure('big2', font=('Arial', 8,'bold'))
        self.text.tag_configure('big', font=('Verdana', 10, 'bold'))
        self.root.grid_columnconfigure(0, uniform="uniform", weight=1)
        self.root.grid_rowconfigure(8, weight=1)
        
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
        
        button_quit=Button(self.root,text="Quit",command=self.root.destroy)
        button_accept=Button(self.root,text="Check",command=self.CheckButton)
        
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
            opt5=Checkbutton(self.root,text="Enable ParaView Simple",\
                             variable=self.a,onvalue=True,offvalue=False)
            
            opt4.deselect()
            opt5.deselect()
            
            opt4.grid(row=5,column=0,columnspan=2,sticky="W")
            opt5.grid(row=6,column=0,columnspan=2,sticky="W")
    
        button_accept.grid(row=6,column=3,padx=10,pady=10)
        button_quit.grid(row=6,column=4,padx=10,pady=10)
        
        self.root.mainloop()
    
if __name__=='__main__':
    
    root=Tk()
    inter           =   InterFace(root)
    try:
        os.remove('temp.k')
    except:
        print('no temp file created')
    root.mainloop()