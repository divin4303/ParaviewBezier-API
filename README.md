## ParaviewBezier- An API for post-processing IGA results [![Gitter](https://badges.gitter.im/ParaviewBezier-API/community.svg)](https://gitter.im/ParaviewBezier-API/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
*Latest version: v1.0(23 Spetember 2021)* 

Isogeometric analysis results are generally plotted on approximated linear FE-discretization, which causes loss in the visualization quality. Since ParaView supports splines in the form of Bézier cells, There is now a possibility to visualize geometrically exact results. 

This API is designed to post-process the results (currently only displacement) from NURBS-based IGA simulations performed on LS-DYNA, using the Bézier cells of ParaView.

This API includes the following features:

* Post-processing NURBS meshes using Bézier elements in ParaView
* Compress VTU file(s) on demand
* Parallel processing the task(s) on demand
* Inbuild *Open Geometry* button to view/interact with geometry
## How it Works
1. Excecute InterFace.py in python IDE or cmd
```
python InterFace.py
```
This results in following pop up GUI

<p align="left">
 <img src=https://user-images.githubusercontent.com/56837271/132837320-60d74e52-c0a9-4ae1-bed8-1003ebf2b228.png width="350">
</p>

2. a). Browse or enter the location of the `keyword` file  
   b). Browse or enter the desired location of the resultant `Visualization tool kit` file  
3. Check buttons  
   a). `Displacement` check button exctracts the displacement vector field information from the binary plot  
   b). `Stress` check button writes the stress vector field information  
   c). `Parallel processing` check button executes the timestep data asynchronously  
   d). `Compressed VTK` check button writes the `Visualization tool kit` file in binary format which otherwise is written in ASCII  
   e). `Enable ParaView Simple` check button
4. After selecting the desired options click on `Check` to load the input files  
   a). `Progress bar` shows the progress of the code  
   b). Desired number of `Time steps` from the `Total available` time steps can be entered into `entry box`  
       By default the results are written without the vector field information  
   c). The computation and writting file on clicking `Submit` button   
5. The necessary information(s) regarding thre model is written inside the text frame   
 
 ## What to expect
 The results are written in .VTU format and one could visualize the result file in ParaView  
 <p align="left">
 <img width="280" alt="Quarter_ring_model_subD_4" src="https://user-images.githubusercontent.com/56837271/132838146-222dff46-6f0e-47f6-9f50-ff6a371a075e.PNG">
 <img width="297" alt="vector_field_bivariate" src="https://user-images.githubusercontent.com/56837271/134482911-2d9807a0-af12-46c5-8bee-6c1e31266793.PNG">
</p>  


## Contact
For reporting bugs or suggesting new features, Contact divin.pulakudiyil@st.ovgu.de or resam.makvandi@ovgu.de  

## Version history

### v1.0
Release date: 23 Spetember 2021


## Notes
 
 The files are avaialable inside `paraview` folder on the destination. if the destination path is not given then the files are avaialble in `working directory`  
 Parallel processing is implimented using `cuncurrent.futures` module and is favourable if the number of time steps is more
