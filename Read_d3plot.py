import os
import glob
import numpy as np
from BinaryBuffer import*
import Headers
import mmap

path=[]

filepath = glob.glob(os.getcwd() + "/*")
for filename in filepath:
    if os.path.basename(filename).startswith('d3plot'):
        path.append(os.path.basename(filename))

_header = {}
bb = BinaryBuffer([path[0]])

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
		
def read_geometry_data(header,geometry_section_size):
    
    position = geometry_section_size
    
    section_word_length = header['ndim'] * header['numnp']
    #calculation of word length for reding node coordinates
    position += section_word_length * word 
    #update the position after reading the node coordinates
    # shells
    section_word_length = 5 * header['nel4']
    position += section_word_length * word
    
    #solids 
    section_word_length = 9 * header['nel8']
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

def compute_n_bytes_per_state(header, wordsize):
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
        print("Unexpected value of mdlop expected was 0, 1 or 2.")

    n_bytes_per_state = timestep_offset + global_vars_offset + \
                        node_data_offset + solid_offset+ shell_offset + \
                        elem_deletion_offset#+therm_data_offset
                        
    var_offset=1+header["nglbv"]
    
    return n_bytes_per_state,var_offset
###############################################################
def collect_file_infos(path,geometry_section_size: int,size_per_state: int):
    
    mv=[]
    last_nz=0
    bb = BinaryBuffer([path[0]])
    
    last_byte=bb.get_size()[0]
    mv=bb.get_mv()
    mview_inv_arr = np.asarray(mv[::-1])
    
    block_size=2048
    
    for i in range(0,last_byte,block_size):
        
        nz,=np.nonzero(mview_inv_arr[i:i+block_size])
        
        if len(nz):
            last_nz=last_byte-(i+nz[0])
            break
    state_after_geo=(last_nz-geometry_section_size)//size_per_state
    
    memory_infos = [{
            "start": geometry_section_size,
            "length": state_after_geo * size_per_state,
            "offset": 0,
            "filepath": path[0],
            "n_states": state_after_geo
        }]
    
    
    'need a for loop to loop through files'
    for file in path[1:]:

        with open(file,'rb') as f:
        
            last_nonzero_byte_index = -1
            file_size=os.path.getsize(file)
            
            n_blocks = file_size // mmap.ALLOCATIONGRANULARITY
            rest_size = file_size % mmap.ALLOCATIONGRANULARITY
            block_length = mmap.ALLOCATIONGRANULARITY
            
            if rest_size:
                
                start=n_blocks*block_length
                mview = memoryview(mmap.mmap(f.fileno(),offset=start,length=rest_size,
                                             access=mmap.ACCESS_READ).read())
                nz_indexes, = np.nonzero(mview[::-1])
                if len(nz_indexes):
                    last_nonzero_byte_index = start + rest_size - nz_indexes[0]
                
            n_states_in_file = last_nonzero_byte_index // size_per_state
            rest=last_nonzero_byte_index % size_per_state
                
            memory_infos.append({
            "start": 0,
            "length": n_states_in_file * size_per_state,
            "offset": 0,
            "filepath": file,
            "n_states": n_states_in_file
            })
                      
    return memory_infos
##########################################################
def displacement(u,numnp,node_displacement,x,n_states):

    uloc = [[0 for i in range(3)] for j in range(numnp)]
    
    for i in range(n_states):
        for j in range(numnp):
            for k in range(3):
                uloc[j][k]=node_displacement[j+(numnp*i)][k]-x[j][k]
    
        u.append(np.pad(uloc,((0, 0), (0, 0))))
    
    return u
#########S###############################################
def read_state_data(memory_infos: dict,var_offset: int,numnp: int,x,ndf=3):
    
    n_states = sum(map(lambda x: x["n_states"], memory_infos))
    u=[]
    
    memory_required = 0
    offset = 0
    bb_states = BinaryBuffer()
    '''
    load the files one by one
    and read the array here itself
    '''
    for minfo in memory_infos:
        x_disp=[]
        start = minfo["start"]
        length = minfo["length"]
        filepath = minfo["filepath"]
        n_states_per_file=int(minfo["n_states"])
        
        if n_states_per_file>0:
            
            with open(filepath, "br") as fp:
                fp.seek(start)
                mview = memoryview(bytearray(length))
                fp.readinto(mview[offset:offset + length])
            
            bb_states.set_mv(length,mview)
            
            state_data = bb_states.read_ndarray(0, length, 1, np.float64)
            state_data = state_data.reshape((n_states_per_file, -1))
            
            for i in range(n_states_per_file):
                index=var_offset #(1+'nlgbv')
                for j in range(numnp):
                    for k in range(ndf):
                        x_disp.append(state_data[i][index])
                        index+=1
                
            
            x_disp=np.reshape(x_disp,(-1,ndf))
            x_disp=np.around(x_disp,decimals=5)
            
            u=displacement(u,numnp,x_disp,x,n_states_per_file)
            
    u = np.stack(u)
    
    return u,n_states
#########################################################
def read_d3plot(ndf,numnp,x):
    
    head,geometry_section_size=Headers._read_header(bb)
    geometry_section_size=read_geometry_data(head,geometry_section_size)
    geometry_section_size=Headers._read_user_ids(head,geometry_section_size,bb)
    
    bytes_per_state,var_offset=compute_n_bytes_per_state(head, word)
    
    memory_infos=collect_file_infos(path,geometry_section_size,bytes_per_state)
    
    u,n_states=read_state_data(memory_infos,var_offset,numnp,x,ndf)
            
    return u,n_states