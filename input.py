#!/usr/local/bin/python3.10

import os
import h5py
import numpy as np
import cv2

# write numpy array d to hdf5 file path
def writearray(path, d):
    with h5py.File(path, 'w') as f:
        dset = f.create_dataset('image', data=d)
        print(f'Created dataset: {dset.name}')

    hdfsize = os.path.getsize(path)
    return hdfsize

# returns jpg image as a numpy array
def readjpg(path, rgb=True):
    img = cv2.imread(path)
    jpgsize = os.path.getsize(path)
    # BGR -> RGB
    if rgb:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img, jpgsize

def main():
    print('Processing images:')
    img, jpgsize = readjpg('files/turtles.jpg')
    hdfsize = writearray('files/turtles.hdf5', img)
    print(f'JPG size:   {jpgsize}')
    print(f'HDF5 size:  {hdfsize}')
    print(f'JPG : HDF5: 1 : {jpgsize/hdfsize}')

if __name__ == '__main__':
    main()
