
import numpy as np

char_size = 1
word=8
int_type=np.int64
float_type=np.float64

def _read_words( bb,words_to_read: dict, storage_dict: dict = None):
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

def _read_header(bb):
    geometry_section_size=0
    header_words = {
        "title": [0 * word, char_size, 10 * word],
            "runtime": [10 * word, int_type],
            "filetype": [11 * word, int_type],
            "source_version": [12 * word, int_type],
            "release_version": [13 * word, char_size, 1 * word],
            "version": [14 * word, float_type],
            "ndim": [15 * word, int_type],
            "numnp": [16 * word, int_type],
            "icode": [17 * word, int_type],
            "nglbv": [18 * word, int_type],
            "it": [19 * word, int_type],
            "iu": [20 * word, int_type],
            "iv": [21 * word, int_type],
            "ia": [22 * word, int_type],
            "nel8": [23 * word, int_type],
            "nummat8": [24 * word, int_type],
            "numds": [25 * word, int_type],
            "numst": [26 * word, int_type],
            "nv3d": [27 * word, int_type],
            "nel2": [28 * word, int_type],
            "nummat2": [29 * word, int_type],
            "nv1d": [30 * word, int_type],
            "nel4": [31 * word, int_type],
            "nummat4": [32 * word, int_type],
            "nv2d": [33 * word, int_type],
            "neiph": [34 * word, int_type],
            "neips": [35 * word, int_type],
            "maxint": [36 * word, int_type],
            "nmsph": [37 * word, int_type],
            "ngpsph": [38 * word, int_type],
            "narbs": [39 * word, int_type],
            "nelth": [40 * word, int_type],
            "nummatt": [41 * word, int_type],
            "nv3dt": [42 * word, int_type],
            "ioshl1": [43 * word, int_type],
            "ioshl2": [44 * word, int_type],
            "ioshl3": [45 * word, int_type],
            "ioshl4": [46 * word, int_type],
            "ialemat": [47 * word, int_type],
            "ncfdv1": [48 * word, int_type],
            "ncfdv2": [49 * word, int_type],
            "nadapt": [50 * word, int_type],
            "nmmat": [51 * word, int_type],
            "numfluid": [52 * word, int_type],
            "inn": [53 * word, int_type],
            "npefg": [54 * word, int_type],
            "nel48": [55 * word, int_type],
            "idtdt": [56 * word, int_type],
            "extra": [57 * word, int_type],
        }
    header_extra_words = {
        "nel20": [64 * word, int_type],
        "nt3d": [65 * word, int_type],
        "nel27": [66 * word, int_type],
        "neipb": [67 * word, int_type],
    }

    # read data in header_words
    header = _read_words(bb,header_words)
    #print(header)

    if header["extra"] != 0:
        _read_words(bb,header_extra_words, header)

    # filetype
    if header["filetype"] > 1000:
        header["filetype"] -= 1000
        header["external_numbers_dtype"] = np.int64
    else:
        header["external_numbers_dtype"] = np.int32

    if header["filetype"] != 1 and header["filetype"] != 5:
        print("Wrong filetype %d != 1 (d3plot) or 5 (d3part) in \
                           header" % header["filetype"])

        # ndim
    if header["ndim"] == 5 or header["ndim"] == 7:
        header["mattyp"] = 1
        header["ndim"] = 3
            
    if header["ndim"] == 4:
        header["mattyp"] = 0
        header["ndim"] = 3

    if 5 < header["ndim"] < 8:
        header["mattyp"] = 0
        header['ndim'] = 3

    if header['ndim'] == 8 or header['ndim'] == 9:
        header["mattyp"] = 0
        header['ndim'] = 3

    if header["ndim"] != 3:
        print("Invalid header entry ndim: %d" % header["ndim"])

        # integration points
    if header["maxint"] >= 0:
        header["mdlopt"] = 0
    if header["maxint"] < -10000:
        header["mdlopt"] = 2
        header["maxint"] = abs(header["maxint"]) - 10000
    if header["maxint"] < 0:
        header["mdlopt"] = 1
        header["maxint"] = abs(header["maxint"])

    geometry_section_size = 64 * (1 + (header['extra'] != 0)) * word
    return header,geometry_section_size

def _read_user_ids(header,geometry_section_size,bb):

    if not bb:
        return

    if header['narbs'] <= 0:
        return

    position = geometry_section_size

    # safety
    original_position = position
    blocksize = header["narbs"] * word
    
    numbering_words = {
            'nsort': (position, int_type),
            'nsrh': (position + 1 * word, int_type),
            'nsrb': (position + 2 * word, int_type),
            'nsrs': (position + 3 * word, int_type),
            'nsrt': (position + 4 * word, int_type),
            'nsortd': (position + 5 * word, int_type),
            'nsrhd': (position + 6 * word, int_type),
            'nsrbd': (position + 7 * word, int_type),
            'nsrsd': (position + 8 * word, int_type),
            'nsrtd': (position + 9 * word, int_type),
        }
        
    numbering_header = _read_words(bb,numbering_words)
        
    position += len(numbering_words) * word
        
    header['numbering_header'] = numbering_header
    
############## node ids###################################
    array_length = numbering_header['nsortd'] * word
    node_ids = bb.read_ndarray(position, array_length, 1, int_type)
    position += array_length
        
############## shell ids###################################
    array_length = header['nel4'] * word
    shell_ids = bb.read_ndarray(position, array_length, 1, int_type)
    position += array_length
      
    position = original_position + blocksize

    # update position
    geometry_section_size = position
    return geometry_section_size

