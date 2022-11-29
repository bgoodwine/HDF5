#!/usr/bin/env python3

import sys
import os
import numpy as np
import imageio.v2 as iio
import h5py

# constants
VIDEOS = ['files/movies/helmholtz.mov', 'files/movies/mnms.mp4']
#VIDEOS = ['files/movies/mnms.mp4']
FORMATS = ['mp4', 'mov', 'hdf5', 'avi']

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

def compare_formats(mp4_video, avi_video, hdf_video):
    # TODO: decide if it's necessary to read in the data? can you get it from meta?
    #print('Reading frames...')
    #print('MP4...')
    #mp4_frames = iio.imread(mp4_video, plugin='pyav')
    #print('AVI...')
    #avi_frames = iio.imread(avi_video, plugin='ffmpeg')
    #print('HDF5...')
    mp4_reader = iio.get_reader(mp4_video)
    avi_reader = iio.get_reader(avi_video)
    mp4_meta = mp4_reader.get_meta_data()
    avi_meta = avi_reader.get_meta_data()
    # TODO: get size and fps from meta 
    print(mp4_meta)
    print(avi_meta)
    hdf_file   = h5py.File(hdf_video, 'r')
    return

    # convert hdf5 data to np ndarray, gather metadata
    print('Converting HDF5 data to ndarray...')
    shapes = []
    chunks = []
    hdf_frames = np.empty(0)
    for dname in hdf_file.keys():
        dset = hdf_file[dname]
        hdf_frames = np.append(hdf_frames, dset)
        shapes.append(str(dset.shape))
        chunks.append(str(dset.chunks))
    
    # collect shape data as str for alignment in printing
    print('Gathering shape data...')
    hdf_shape = ' '.join(shapes)
    hdf_chunks = ' '.join(chunks)
    mp4_shape = str(mp4_frames.shape)
    mov_shape = str(mov_frames.shape)
    
    # ensure equality of audio/video data
    print('Comparing arrays...')
    if mp4_frames.all() != avi_frames.all():
        print('MP4 frames do not match AVI frames')
    if mp4_frames.all() != hdf_frames.all():
        print('HDF frames do not match MP4 frames')
    if avi_frames.all() != hdf_frames.all():
        print('AVI frames do not match HDF frames')

    # collect size data
    print('Collecting size data...')
    mp4_size = os.path.getsize(mp4_video)
    avi_size = os.path.getsize(avi_video)
    hdf_size = os.path.getsize(hdf_video)

    # calculate compression ratio: CR = original file size / compressed file size
    sizes = [mp4_size, avi_size, hdf_size]
    sizes.sort(reverse=True) # take 'original' file to be largest file
    
    # display results
    print(f'{"Path":<25}: {"(x, y, z)":<17}   {"size (b)":>8}   {"chunks":<10}')
    print(f'{mp4_video:<25}: {mp4_shape:<17}   {mp4_size:>8}')
    print(f'{avi_video:<25}: {mov_shape:<17}   {mov_size:>8}')
    print(f'{hdf_video:<25}: {hdf_shape:<17}   {hdf_size:>8}   {hdf_chunks:<10}')
    print('')
    print(f'{sizes[0]} : {sizes[1]:<10} = {sizes[0]/sizes[1]}')
    print(f'{sizes[0]} : {sizes[2]:<10} = {sizes[0]/sizes[2]}')


def main():
    for video in VIDEOS:
        print(f'Original video: {video}')
        # check for existing conversions of original video
        original_fm = video[-3:]
        print(f'Format: {original_fm}')
        path = video[:-3]
        mp4_path = path+'mp4'
        avi_path = path+'avi'
        hdf_path = path+'hdf5'
        # use mov files in place of mp4 files as both use mpeg4 compression
        if original_fm == 'mov':
            mp4_path = video

        for fm in FORMATS:
            if not os.path.exists(path+fm):
                if not video.endswith('hdf5'):
                    # mov and mp4 both use mpeg4 compression; not going to compare
                    if fm == 'mp4' and original_fm == 'mov':
                        continue
                    if fm == 'mov' and original_fm == 'mp4':
                        path_mp4 = video
                        continue
                    # hdf5 files must be written specially
                    if fm == 'hdf5':
                        print(f'Missing file: {path+fm}, writing from {video}...')
                        frames = iio.imread(video, plugin='pyav')
                        write_movie_ndarray(path+fm, frames)

                    # else possible to write with imageio
                    reader = iio.get_reader(video)
                    fps = int(reader.get_meta_data()['fps'])
                    writer = iio.get_writer(path+fm)
                    print(f'Missing file: {path+fm}, writing from {video} with {fps} fps...')

                    for im in reader:
                        writer.append_data(im[:,:,:])
                    writer.close()

                else:
                    print(f'ERROR: cannot start w/ original file {video}')
            else:
                print(f'Exists: {path+fm}')

        compare_formats(mp4_path, avi_path, hdf_path)





if __name__ == '__main__':
    main()
