#!/usr/bin/env python3

import os
import numpy as np
import imageio.v3 as iio
import h5py

# constants
#VIDEOS = ['files/movies/helmholtz.mov', 'files/movies/mnms.mp4']
VIDEOS = ['files/movies/mnms.mp4']
FORMATS = ['mp4', 'mov', 'hdf5']

#MOV_VIDEO = 'files/movies/helmholtz.mov'
#MP4_VIDEO = 'files/movies/helmholtz.mp4'
#HDF_VIDEO = 'files/movies/helmholtz.hdf5'
#MP4_VIDEO = 'files/movies/mnms.mp4'
#MOV_VIDEO = 'files/movies/mnms.mov'
#HDF_VIDEO = 'files/movies/mnms.hdf5'


# display frames in iio imread frames
def disp(frames):
    for fram in frames:
        print(frame.shape, frame.dtype)

# write dataset frames to hdf5 file in path
def write_movie_ndarray(path, frames):
    with h5py.File(path, 'w') as f:
        dset = f.create_dataset('video', data=frames, chunks=True, compression='gzip', shuffle=True)

def compare_formats(mp4_video, mov_video, hdf_video):
    # read in mp4, mov, and hdf data
    mp4_frames = iio.imread(mp4_video, plugin='pyav')
    mov_frames = iio.imread(mov_video, plugin='pyav')
    if not os.path.exists(hdf_video):
        print(f'{HDF_VIDEO} does not exist- writing data from {MP4_VIDEO}...')
        write_movie_ndarray(hdf_video, mp4_frames)
    hdf_file   = h5py.File(hdf_video, 'r')

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
    mp4_size = os.path.getsize(mp4_video)
    mov_size = os.path.getsize(mov_video)
    hdf_size = os.path.getsize(hdf_video)

    # calculate compression ratio: CR = original file size / compressed file size
    sizes = [mp4_size, mov_size, hdf_size]
    sizes.sort(reverse=True) # take 'original' file to be largest file
    
    # display results
    print(f'{"Path":<25}: {"(x, y, z)":<17}   {"size (b)":>8}   {"chunks":<10}')
    print(f'{mp4_video:<25}: {mp4_shape:<17}   {mp4_size:>8}')
    print(f'{mov_video:<25}: {mov_shape:<17}   {mov_size:>8}')
    print(f'{hdf_video:<25}: {hdf_shape:<17}   {hdf_size:>8}   {hdf_chunks:<10}')
    print('')
    print(f'{sizes[0]} : {sizes[1]:<10} = {sizes[0]/sizes[1]}')
    print(f'{sizes[0]} : {sizes[2]:<10} = {sizes[0]/sizes[2]}')


def main():
    for video in VIDEOS:
        print(f'Original video: {video}')
        # check for existing conversions of original video
        path = video[:-3]
        for fm in FORMATS:
            if not os.path.exists(path+fm):
                print(f'Missing file: {path+fm}, writing from {video}...')
                if not video.endswith('hdf5'):
                    frames = iio.imread(video, plugin='pyav')
                    #frames = iio.imread(video, format='pyav')
                    print(frames[0].shape)
                    metadata = iio.immeta(video, plugin='pyav')
                    if fm == 'hdf5':
                        write_movie_ndarray(path+fm, frames) 
                    elif fm == 'mp4':
                        iio.imwrite(path+fm, frames, codec_name='mpeg4', fps=metadata['fps'])
                    elif fm == 'mov':
                        iio.imwrite(path+fm, frames, codec='mov', plugin='pyav', fps=metadata['fps'])
                else:
                    print(f'ERROR: cannot start w/ original file {video}')

        compare_formats(path+'mp4', path+'mov', path+'hdf5')





if __name__ == '__main__':
    main()
