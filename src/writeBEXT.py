# -*- coding: utf-8 -*-
"""
Created on Thu May 27 11:58:12 2021

@author: User
"""

import os
import h5py
import numpy as np
import ast
class WriteBEXT:
    
    def __init__(self,patchInfo,fileInfo,w,x):
        
        self.ndm    =fileInfo['dimensions']
        self.nump   =fileInfo['Total control points']
        self.tnel   =fileInfo['total number of elements']
        self.neb    =fileInfo['Number of patches']
        self.x      =x
        self.pid    =patchInfo['Part ID']
        self.WFL    =patchInfo['weight flag']
        self.ncv    =patchInfo['ncv']
    
    def writeKeyword(self,path):
        
        'varaible intialization'
        
        keywordfile=open(path+'\\'+self.filename+'.k','w')
        
        keywordfile.write('*KEYWORD memory=40000000\n')
        keywordfile.write('*TITLE\n\n')
        keywordfile.write('*IGA_INCLUDE_BEZIER\n')
        keywordfile.write(self.filename+'.v2')
        
        keywordfile.write('*PART\n\n')
        keywordfile.write('%d,%d,%d\n'%(1,1,1))
        
        if self.ndm==2:
            
            keywordfile.write('*SECTION_SHELL\n')
            keywordfile.write('%d,%d'%(1,201))
            keywordfile.write('%d\n'%(0.1))
            
        else:
            keywordfile.write('*SECTION_SOLID\n')
            keywordfile.write('%d,%d\n'%(1,201))
        
        keywordfile.write('*MAT_ELASTIC\n')
        keywordfile.write('%d,%2.2E,%d,%d\n'%(1,7.8E-9,200000,0.3))
        
        keywordfile.write('*CONTROL_IMPLICIT_GENERAL\n')
        keywordfile.write('%d,%d\n'%(1,1.))
        
        keywordfile.write('*CONTROL_IMPLICIT_EIGENVALUE\n')
        keywordfile.write('%d\n'%(20))
        
        keywordfile.write('*END\n')
        
        keywordfile.close()
    def uparaview(self,filename):
        
        
        c_dir = os.getcwd()
        path = os.path.join(c_dir, r'out')
        if not os.path.exists(path):
            os.makedirs(path)
            
        # set extender name
        fileExt='.v2'
        self.filename=os.path.splitext(filename)[0]
        filename=self.filename+fileExt
        self.writeKeyword(path)
        # Open the files with writing permission
        hf = h5py.File('PatchInfo.h5', 'r')
        v2file = open(path+'\\'+filename, 'w')
        
        # Write a line to the file
        v2file.write('B E X T 2.0')
        
        # PID NN(Number of nodes/control points) NE(Number of elements) NCV WFL
        numCoeffVec=0
        for i in range(self.neb):
            C=np.array(hf.get('C_{}'.format(i+1)))
            numCoeffVec+=C.shape[0]*C.shape[1]
        v2file.write('\n%8d %7d %7d %7d %7d'%(self.pid,self.nump,\
                                              self.tnel,numCoeffVec,
                                              self.WFL))
        
        # Xi, Yi, Zi, Wi
        for i in range(0,self.nump):
            
             v2file.write('\n%24.16E%24.16E%24.16E%24.16E'%(self.x[i][0],
                                                            self.x[i][1],
                                                            self.x[i][2],
                                                            self.x[i][3]))
        
        # NEB Number of sorted element sub-blocks
        v2file.write('\n%8d'%(self.neb))
        # ETYPE NE NN NCV PRP PS PT
        i=0
        for i in range(self.neb):
            self.Etype=1
            patchInfo=hf.get('patchInfo{}'.format(i+1))
            self.nel    =patchInfo['number of elements'][()]
            self.nen    =patchInfo['number of element nodes'][()]
            
            v2file.write('\n%8d %7d %7d %7d %7d %7d %7d'%(self.Etype,self.nel,
                                                          self.nen,self.nen,
                                                          patchInfo['p'][()],
                                                          patchInfo['q'][()],
                                                          patchInfo['r'][()]))
            
        #  N1	 N2 	N3 	N4 	N5 	N6 	N7 	N8	N9	N10
        coeffVecID=0
        for i in range(self.neb):
            
            self.ix=np.array(hf.get('Conn_{}'.format(i+1)))
            patchInfo=hf.get('patchInfo{}'.format(i+1))
            self.nel    =patchInfo['number of elements'][()]
            self.nen    =patchInfo['number of element nodes'][()]
            
            for j in range(0,self.nel):
                v2file.write('\n')
                fixedInputLimit=0
                for jj in range(0,self.nen):
                    nodeID = self.ix[j][jj]
                    if fixedInputLimit >= 10:
                        v2file.write('\n')
                        fixedInputLimit=0
                    if nodeID > 0:
                        v2file.write('%8d'%(nodeID))
                    fixedInputLimit+=1
                v2file.write('\n')
                fixedInputLimit=0
                
                'Need some different ID naming concept'
                for k in range(0,self.nen):
                    coeffVecID+=1
                    if fixedInputLimit >= 10:
                        v2file.write('\n')
                        fixedInputLimit=0
                    if nodeID > 0:
                        v2file.write('%8d'%(coeffVecID))
                    fixedInputLimit+=1
        
        # CVID - coefficient vector ID defining the element       
        #NDCVB NSCVB
        self.NDCVB=self.neb
        self.NSCVB=0
        v2file.write('\n%8d %7d'%(self.NDCVB,self.NSCVB))
        
        #   NCVs     NCVCs
        for i in range(self.neb):
            C=np.array(hf.get('C_{}'.format(i+1)))
            v2file.write('\n%8d %7d'%(C.shape[0]*C.shape[1],C.shape[2]))
        # CV1 CV2 ..................
        # for i in range(self.neb):
        for i in range(self.neb):
            C=np.array(hf.get('C_{}'.format(i+1)))
            for j in range(C.shape[0]):
                for k in range(0,C.shape[1]):
                    v2file.write('\n')
                    limit=0
                    for l in range(0,C.shape[1]):
                        if limit >= 5:
                            v2file.write('\n')
                            limit=0
                        limit+=1
                        v2file.write('%24.16E'%(C[j][l][k]))
                    
        hf.close()
        v2file.close()