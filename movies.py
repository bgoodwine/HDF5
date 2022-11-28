#!/usr/bin/env python3

import os
import numpy as np
import imageio.v2 as iio
import h5py

# constants
MOV_VIDEO = 'files/helmholtz.mov'
MP4_VIDEO = 'files/helmholtz.mp4'
HDF_VIDEO = 'files/helmholtz.hdf5'


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
        print(f'Created dataset: {dset.name}')
        print(f'Chunks: {dset.chunks}')

    hdfsize = os.path.getsize(path)
    return hdfsize

def main():

    mp4_frames = iio.imread(MP4_VIDEO, format='pyav')
    mov_frames = iio.imread(MOV_VIDEO, format='pyav')
    hdf_frames = h5py.File(HDF_VIDEO, 'r')

    shapes = []
    chunks = []
    for dname in hdf_frames.keys():
        dset = hdf_frames[dname]
        shapes.append(str(dset.shape))
        chunks.append(str(dset.chunks))

    hdf_shape = ' '.join(shapes)
    hdf_chunks = ' '.join(chunks)

    
    mp4_shape = str(mp4_frames.shape)
    mov_shape = str(mov_frames.shape)

    #for frame in mov_frames:
    #    print(frame.shape, frame.dtype)
    
    #with h5py.File(HDF_VIDEO, 'w') as f:
    #    dset = f.create_dataset('helmholtz', data=mp4_frames, chunks=True, compression='gzip', shuffle=True)
    #    hdf_shape = str(dset.chunks)

    mp4_size = os.path.getsize(MP4_VIDEO)
    mov_size = os.path.getsize(MOV_VIDEO)
    hdf_size = os.path.getsize(HDF_VIDEO)

    print(f'{"Path":<20}: {"(x, y, z)":<17} - {"size (b)":>8} - {"chunks":<10}')
    print(f'{MP4_VIDEO:<20}: {mp4_shape:<17} - {mp4_size:>8}')
    print(f'{MOV_VIDEO:<20}: {mov_shape:<17} - {mov_size:>8}')
    print(f'{HDF_VIDEO:<20}: {hdf_shape:<17} - {hdf_size:>8} - {hdf_chunks:<10}')


if __name__ == '__main__':
    main()
