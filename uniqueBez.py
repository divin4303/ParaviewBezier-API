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

def Unique(xbez,wbez,bezloc,wb,ixbez,nen,ptol,ndm,nd_bez,ne_bez,patch_numpbez,p,q,r):
      
    xb3= 0
    save=0
    d=0
    
    for j in range (0,nen): ##for parsing through each point
    
        pflag=True
        bol=np.all(np.isclose(bezloc[j,:], xbez, atol=ptol),axis=1)

        if True in bol: #store the point in an array
            save=patch_numpbez[0]+np.where(bol)[0][0]
            pflag=False
            
        if pflag==True:
            
            patch_numpbez[1] = patch_numpbez[1] + 1
            xbez=np.row_stack((xbez,bezloc[j,:]))
                
            wbez.append(wb[j])
            
            #print(j)
            ixbez[ne_bez-1][j]   = patch_numpbez[1]
 
        else:
            
          ixbez[ne_bez-1][j]   = save+1
      
    return xbez,wbez,patch_numpbez,ixbez