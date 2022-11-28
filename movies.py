#!/usr/bin/env python3

import os
import numpy as np
import imageio.v2 as iio
import h5py

# constants
MOV_VIDEO = 'files/helmholtz.mov'
MP4_VIDEO = 'files/helmholtz.mp4'
HDF_VIDEO = 'files/helmholtz.hdf5'

# saved code: display each frame with iio
    #for frame in mov_frames:
    #    print(frame.shape, frame.dtype)
# saved code: write movie data to hdf5 w/ default chunks
    #with h5py.File(HDF_VIDEO, 'w') as f:
    #    dset = f.create_dataset('helmholtz', data=mp4_frames, chunks=True, compression='gzip', shuffle=True)
    #    hdf_shape = str(dset.chunks)


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
    # read in mp4, mov, and hdf data
    mp4_frames = iio.imread(MP4_VIDEO, format='pyav')
    mov_frames = iio.imread(MOV_VIDEO, format='pyav')
    hdf_file   = h5py.File(HDF_VIDEO, 'r')

    # convert hdf5 data to np ndarray, gather metadata
    shapes = []
    chunks = []
    hdf_frames = np.empty(0)
    for dname in hdf_file.keys():
        dset = hdf_file[dname]
        hdf_frames = np.append(hdf_frames, dset)
        shapes.append(str(dset.shape))
        chunks.append(str(dset.chunks))
    
    # collect shape data as str for alignment in printing
    hdf_shape = ' '.join(shapes)
    hdf_chunks = ' '.join(chunks)
    mp4_shape = str(mp4_frames.shape)
    mov_shape = str(mov_frames.shape)
    
    # ensure equality of audio/video data
    if mp4_frames.all() != mov_frames.all():
        print('MP4 frames do not match MOV frames')
    if mp4_frames.all() != hdf_frames.all():
        print('HDF frames do not match MP4 frames')
    if mov_frames.all() != hdf_frames.all():
        print('MOV frames do not match HDF frames')

    # collect size data
    mp4_size = os.path.getsize(MP4_VIDEO)
    mov_size = os.path.getsize(MOV_VIDEO)
    hdf_size = os.path.getsize(HDF_VIDEO)

    # calculate compression ratio: CR = original file size / compressed file size
    sizes = [mp4_size, mov_size, hdf_size]
    sizes.sort(reverse=True) # take 'original' file to be largest file
    
    # display results
    print(f'{"Path":<20}: {"(x, y, z)":<17}   {"size (b)":>8}   {"chunks":<10}')
    print(f'{MP4_VIDEO:<20}: {mp4_shape:<17}   {mp4_size:>8}')
    print(f'{MOV_VIDEO:<20}: {mov_shape:<17}   {mov_size:>8}')
    print(f'{HDF_VIDEO:<20}: {hdf_shape:<17}   {hdf_size:>8}   {hdf_chunks:<10}')
    print('')
    print(f'{sizes[0]} : {sizes[1]:<10} = {sizes[0]/sizes[1]}')
    print(f'{sizes[0]} : {sizes[2]:<10} = {sizes[0]/sizes[2]}')


if __name__ == '__main__':
    main()
