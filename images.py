#!/usr/local/bin/python3.10

import os
import h5py
import numpy as np
import cv2

# write numpy array d to hdf5 file path
def write_contiguous(path, d):
    with h5py.File(path, 'w') as f:
        dset = f.create_dataset('image', data=d)
        print(f'Created dataset: {dset.name}')
        print(f'Chunks: {dset.chunks}')

    hdfsize = os.path.getsize(path)
    return hdfsize

# write numpy array d to hdf5 file path
def write_chunked(path, d, chunk, comp=None, shuffle=False):
    with h5py.File(path, 'w') as f:
        dset = f.create_dataset('image', data=d, chunks=chunk, compression=comp, shuffle=shuffle)
        #dset = f.create_dataset('image', data=d, chunks=True)
        print(f'Created dataset: {dset.name}')
        print(f'Chunks: {dset.chunks}')

    hdfsize = os.path.getsize(path)
    return hdfsize


# returns jpg image as a numpy array
def readjpg(path, rgb=True):
    img = cv2.imread(path)
    jpgsize = os.path.getsize(path)
    # BGR -> RGB
    if rgb:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    print(f'Image dimensions: {img.ndim}')
    return img, jpgsize

def main():
    chunks = [(225, 180, 1)]
    chunked_sizes = []
    gzipped_sizes = []
    shuffled_sizes = []

    print('Processing images:')
    img, jpgsize = readjpg('files/turtles.jpg')
    hdfsize = write_contiguous('files/turtles.hdf5', img)
    chunks.append(img.shape)

    print('Chunking image...')
    for chunk in chunks:
        path = 'files/turtles'
        path += str(chunk[1]) + 'x' + str(chunk[2])
        chunked_sizes.append(write_chunked(path+'.hdf5', img, chunk))
        gzipped_sizes.append(write_chunked(path+'gzip.hdf5', img, chunk, comp='gzip'))
        shuffled_sizes.append(write_chunked(path+'shuff.hdf5', img, chunk, comp='gzip', shuffle=True))
    
    print(f'JPG size:   {jpgsize}')
    print(f'HDF5 size:  {hdfsize}')
    print('')
    print('CHUNKED:')
    for size, chunk in zip(chunked_sizes, chunks):
        print(f'\t{chunk}: {size}')
    
    print('')
    print('GZIP:')
    for size, chunk in zip(gzipped_sizes, chunks):
        print(f'\t{chunk}: {size}')
    
    print('')
    print('GZIP & SHUFFLE:')
    for size, chunk in zip(shuffled_sizes, chunks):
        print(f'\t{chunk}: {size}')

if __name__ == '__main__':
    main()
