import os
import numpy as np


class BinaryBuffer:
    memorysize=0

    def __init__(self, filepath=None):
        self.filepath_ = None #initialization of path'_'
        self.sizes_ = []  #initialization of size'_'
        self.load(filepath)#loading the file
		
    def read_number(self, start, dtype):
        return np.frombuffer(self.mv_,dtype=dtype,count=1,offset=start)[0]
    
    def read_ndarray(self, start, length, step, dtype):
        return np.frombuffer(self.mv_[start:start+length:step],dtype=dtype)

    def read_text(self, start, length, step=1, encoding='ascii'):
        return self.mv_[start:start+length:step].tobytes().decode(encoding)


    def load(self, filepath=None):

        filepath = filepath if filepath else self.filepath_

        if not filepath:
            return

        sizes = [os.path.getsize(path) for path in filepath]
        self.memorysize = sum(sizes)
        print(self.memorysize)
        # allocate memory
        buffer = memoryview(bytearray(b'0'*self.memorysize))

        sizes_tmp = [0] + sizes
        for i_path, path in enumerate(filepath):
            with open(path, "br") as fp:
                fp.readinto(buffer[sizes_tmp[i_path]:])

        self.filepath_ = filepath
        self.sizes_ = sizes
        self.mv_ = buffer