import os
import glob
import numpy as np
from BinaryBuffer import*
import Headers

path=[]

filepath = glob.glob(os.getcwd() + "/*")
for filename in filepath:
    if os.path.basename(filename).startswith('d3plot'):
        path.append(os.path.basename(filename))

_header = {}
bb = BinaryBuffer(path)

#assunming double precision
char_size = 1
word=8
int_type=np.int64
float_type=np.float64

def _get_n_parts(header):
    n_parts = header["nummat4"]
    return n_parts
def find_EOF(position):
    temp_position=position
    
    while temp_position<bb.memorysize:
        n=bb.read_number(temp_position, float_type)
        if n==-999999.0:
            EOF=temp_position
            print('EOF is',(temp_position-position))
        temp_position+=8

    return EOF
		
def _read_geometry_data(header,geometry_section_size):
    
    position = geometry_section_size
    
    section_word_length = header['ndim'] * header['numnp']
    #calculation of word length for reding node coordinates
 
    position += section_word_length * word 
    #update the position after reading the node coordinates
        
    # shells
    section_word_length = 5 * header['nel4']
    
    position += section_word_length * word

    geometry_section_size = position
    return geometry_section_size

def _read_words( words_to_read: dict, storage_dict: dict = None):
    if storage_dict is None:
        storage_dict = {}

    for name, data in words_to_read.items():
        if data[1] == int_type:
            storage_dict[name] = bb.read_number(data[0], data[1])
        elif data[1] == float_type:
            storage_dict[name] = bb.read_number(data[0], data[1])
        elif data[1] == char_size:
            storage_dict[name] = bb.read_text(data[0], data[1] * data[2])

        else:
            print("Encountered unknown dtype")

    return storage_dict        

def _compute_n_bytes_per_state(header, wordsize):
#81600
    if not header:
        return 0
    # timestep
    timestep_offset = 1 * wordsize
    # global vars
    global_vars_offset = header["nglbv"] * wordsize
    # node vars
    n_node_vars = (header["iu"] +header["iv"] +header["ia"]) * header["ndim"]
    node_data_offset = int(n_node_vars) * int(header["numnp"]) * int(wordsize)
        # solids
    solid_offset = header["nel8"] * header["nv3d"] * wordsize
        # shells
    shell_offset = (header["nel4"]) * header["nv2d"] * wordsize
    #     # deleted nodes and elems ... or nothing
    elem_deletion_offset = 0
    if header["mdlopt"] == 1:
        elem_deletion_offset = header["numnp"] * wordsize
    elif header["mdlopt"] == 2:
        elem_deletion_offset = (header["nel4"] +header["nel8"]) * wordsize
    elif header["mdlopt"] == 0:
        pass
    else:
        err_msg = "Unexpected value of mdlop: {}, expected was 0, 1 or 2."
        raise RuntimeError(err_msg.format(header["mdlopt"]))

    n_bytes_per_state = timestep_offset + global_vars_offset + \
                        node_data_offset + solid_offset+ shell_offset + \
                        elem_deletion_offset
    var_offset=1+header["nglbv"]
    
    return n_bytes_per_state,var_offset
#########S###############################################
def read_d3plot(ndf=3,n=5,m=5,l=1):
    
    head,geometry_section_size=Headers._read_header(bb)
    geometry_section_size=_read_geometry_data(head,geometry_section_size)
    geometry_section_size=Headers._read_user_ids(head,geometry_section_size,bb)

    bytes_per_state,var_offset=_compute_n_bytes_per_state(head, word)

    position=bb.sizes_[0]
    EOF=find_EOF(position)
    
    array_length=EOF-position
    no_of_states=(EOF-position)/bytes_per_state
    numnp=n*m*l
    index_per_state=int(bytes_per_state/8)-var_offset-(numnp*ndf)
    nparts=_get_n_parts(head)
    nnodes=head['numnp']
    
    print('offset',var_offset,index_per_state)
    
    i,state=0,0
    x_disp=([]) 
    
    state_data = bb.read_ndarray(position, array_length, 1, float_type)
    
    while state!=int(no_of_states):
        
        print(state_data[i])
        i+=var_offset #(1+'nlgbv')
        for j in range(numnp):
            for k in range(ndf):
                x_disp.append(state_data[i])
                i+=1
        state+=1
        i+=index_per_state #10104
    
    i=i-2744
    
    i+=var_offset
    for j in range(numnp):
        for k in range(ndf):
            x_disp.append(state_data[i])
            i+=1
            
    x_disp=np.reshape(x_disp,(-1,ndf))
    x_disp=np.around(x_disp,decimals=5)
    
    return x_disp,no_of_states