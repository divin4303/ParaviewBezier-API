## ISOGEOMETRIC ANALYSIS: POST-PROCESSING AND VISUALIZATION OF RESULTS USING BÉZIER CELLS

## How It Works
1. Excecute InterFace.py in python IDE or cmd.
```
python InterFace.py
```
This results in following pop up GUI

<p align="center">
  <img src="https://github.com/divin4303/Project_work/files/7143029/Interface.pdf" alt="GUI_1" width="304">
</p>

2. a). Browse or enter the location of the `keyword` file.  
   b). Browse or enter the desired location of the resultant `Visualization tool kit` file.  
3. Check buttons  
   a). `Displacement` check button exctracts the displacement vector field information from the binary plot.  
   b). `Stress` check button writes the stress vector field information.  
   c). `Parallel processing` check button executes the timestep data asynchronously.  
   d). `Compressed VTK` check button writes the `Visualization tool kit` file in binary format which otherwise is written in ASCII.  
   e). `Enable ParaView Simple` check button
4. After selecting the desired options click on `Check` to load the input files.  
<p align="center">
  <img src="https://user-images.githubusercontent.com/84045203/117939072-016d9080-b308-11eb-9192-e30ef1b4273f.jpg" alt="GUI_2" width="500">
</p>

   a). `Progress bar` shows the progress of the code  
   b). Desired number of `Time steps` from the `Total available` time steps can be entered into `entry box`.  
       By default the results are written without the vector field information.  
   c). The computation and writting file on clicking `Submit` button.   
5. The necessary information(s) regarding thre model is written inside the text frame.   
 
 ## Notes
 
 The files are avaialable inside `paraview` folder on the destination. if the destination path is not given then the files are avaialble in `working directory`.  
 Parallel processing is implimented using `cuncurrent.futures` module and is favourable if the number of time steps is more than --
