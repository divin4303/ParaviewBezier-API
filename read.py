# -*- coding: utf-8 -*-
"""
======================================
input: line[0] (before deleting $#) to identify the file format.

output: patch_info           : patch information
        df                  :list with patch info and coordinate.
        ndm                 :Number of dimension from file.
        coord_info          :coordinate information
        nnode               :instead of calculting the number of nodes the last line number is noted and stored
======================================
"""
import pandas as pd

def read_keywordfile(lines):
    
    flag=False
    patch_flag=False
    line_no=0
    coord_info=[]
    nnode=[]
    patch_info=[]
    patch_info_end=[]
    
    
    with open('temp.k','r') as f:
            #print(lines)
        for line in f:
            line_no+=1
        
            if line.startswith('*KEYWORD'):
                if 'LONG=Y' in line:
                    
                    widths=[4,16,4,16,4,16,4,16,4,16,4,16,4,16,4,16]
                elif 'LONG=N' in line:
                    widths=[4,8,4,8,4,8,4,8,4,8,4,8,4,8,4,8]
                else:
                    print('width to create coordinate table not mentioned')
                
            if  line.startswith("*ELEMENT_SOLID_NURBS_PATCH"):
                
                patch_flag=True
                patch_info.append(line_no)
                ndm=3
                
            elif line.startswith("*ELEMENT_SHELL_NURBS_PATCH"):
                
                patch_flag=True
                patch_info.append(line_no)
                ndm=2
            
            elif line.startswith("*") and patch_flag==True:
                patch_flag=False
                patch_info_end.append(line_no-1)
                
            
            if line.startswith("*NODE") or line.startswith("*Node") :
                flag=True
                coord_info.append(line_no)
                
            elif line.startswith("*") and flag==True:
                flag=False
                nnode.append(line_no-1)

        if 'created by LS-PrePost' in lines:
            df = pd.read_fwf('temp.k', widths=widths,header=None)
            df.drop(df.columns[[0,2,4,6,8,10,12,14]],axis=1,inplace=True)
        
        elif 'created by Flowdiverter' in lines:
                    
            df = pd.read_csv('temp.k', header=None, sep='\n')
            df = df[0].str.split(',', expand=True)
    

        f.close()
        
        
            
        return patch_info,df,ndm,coord_info,nnode,patch_info_end