# -*- coding: utf-8 -*-
"""
==================================================================
input : xbez                :global Bezier coordinates.
        wbez                :global Bezier weights
        bezloc              :local Bezier coordinates.
        wb                  :local Bezier weights
        ixbez               :global IX array.
        nen                 :number of element nodes
        ptol                :point tolerence.
        ndm                 :number of dimensions
        nd_bez
        ne_bez              :current Bezier element
        numpbez             :global number of unique Bezier points
        p,q,r               :order of fn in p,q,r, dir.
        
Output: xbez                :global Bezier coordinates(updated).
        wbez                :global Bezier weights(updated)
        ixbez               :global IX array(updated).
        numpbez             :global number of unique Bezier points(updated)
==================================================================
"""
import numpy as np

def Unique(xbez,wbez,bezloc,wb,ixbez,nen,ptol,ndm,nd_bez,ne_bez,numpbez,p,q,r):
      
    xb3= 0
    save=0
    d=0
    
    for j in range (0,nen): ##for parsing through each point
    
        pflag=True
        
        # for k in range(0,len(xbez)):
        #     ##each point is checked against all the other points and the unique values are stored in an array
        #     if ndm==3:
        #         xb3=abs(xbez[k,2]-bezloc[j,2])
        #         xb2=abs(xbez[k,1]-bezloc[j,1])
                
        #     if ndm==2:
        #         xb2=abs(xbez[k,1]-bezloc[j,1])
                
        #     xb1=abs(xbez[k,0]-bezloc[j,0])
        #     dist=max(xb1,xb2,xb3)
        bol=np.all(np.isclose(bezloc[j,:], xbez, atol=ptol),axis=1)

        if True in bol: #store the point in an array
            save=np.where(bol)[0][0]
            pflag=False
            # if numpbez==41:
                #print(dist,d)
        if pflag==True:
            
            numpbez = numpbez + 1
            
            
            # if (nd_bez<numpbez):
                
            #     print('Number of computed Bezier points too large')
                
            # for i in range(0,ndm):
            #     xbez[numpbez-1,i]=bezloc[j,i]
            xbez=np.row_stack((xbez,bezloc[j,:]))
                
            wbez.append(wb[j])
            
            #print(j)
            ixbez[ne_bez-1][j]   = numpbez
 
        else:
            
          ixbez[ne_bez-1][j]   = save+1
      
    return xbez,wbez,numpbez,ixbez