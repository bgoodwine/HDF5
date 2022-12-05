#!/usr/bin/env python3

import time
import sys
import os
import h5py
import numpy as np
import imageio as iio
import pprint as pp

FILE  = 'files/movies/katrina.mov'

def test_io(path, dset_name='video_frames'):
    with h5py.File(path, 'r+') as f:
        print(f'Opened file: {path}')
        if dset_name in f.keys():
            # display info on file
            print(f'Found dataset: {dset_name}')
            #dset = f[dset_name] 
            #print(f'Found dataset: {dset.name}')
            #print(f'\tShape:       {dset.shape}')
            #print(f'\tChunks:      {dset.chunks}')
            #print(f'\tCompression: {dset.compression}')

            # NOTE: using the notation f[dset][slice] instead of dset[slice] will let the
            # dset go "out of scope" (https://github.com/h5py/h5py/issues/1960)
            # and thus caching will NOT occur, which is what we want for this test

            # test read/write of the 0x0 pixel of the last frame for chanel 0
            start = time.time()
            val = f[dset_name][27,0,0,0]
            end = time.time()
            print(f'Pixel read time: {end-start}')
            start = time.time()
            f[dset_name][27,0,0,0] = 0
            end = time.time()
            print(f'Pixel write time:  {end-start}')
            f[dset_name][27,0,0,0] = val

            # test read/write of the last frame
            start = time.time()
            frame = f[dset_name][27,0:1919,0:1079,0:2]
            end = time.time()
            print(f'Frame read time: {end-start}')
            start = time.time()
            f[dset_name][27,0:1919,0:1079,0:2] = np.empty((1919,1079,2))
            end = time.time()
            print(f'Frame write time: {end-start}')
            f[dset_name][27,0:1919,0:1079,0:2] = frame

            # test multi-frame read/write
            start = time.time()
            frame = f[dset_name][25:27,0:1919,0:1079,0:2]
            end = time.time()
            print(f'Multi-frame (3) read time: {end-start}')
            start = time.time()
            f[dset_name][25:27,0:1919,0:1079,0:2] = np.empty((2,1919,1079,2))
            end = time.time()
            print(f'Multi-frame (3) write time: {end-start}')
            f[dset_name][25:27,0:1919,0:1079,0:2] = frame

            # test multi-frame read/write
            start = time.time()
            frame = f[dset_name][0:27,0:1919,0:1079,0:2]
            end = time.time()
            print(f'Whole file read time: {end-start}')
            start = time.time()
            f[dset_name][0:27,0:1919,0:1079,0:2] = np.empty((27,1919,1079,2))
            end = time.time()
            print(f'Whole file write time: {end-start}')
            f[dset_name][0:27,0:1919,0:1079,0:2] = frame

    print('')

''' 
    if f.name == '/':
        if verbose:
            print(f.name)
        structure[f.name] = {}
        structure[f.name]['groups'] = []
        structure[f.name]['datasets'] = []
        structure[f.name]['meta'] = {}

    for dataset in f.keys():
        n = f.get(dataset)

        # copy over attribute metadata
        for at in n.attrs.keys():
            if verbose:
                print(f'{prefix}\t{at}: {n.attrs[at]}')
            structure[group]['meta'][at] = n.attrs[at]

        if isinstance(n, h5py.Group):
            if verbose:
                print(prefix + n.name)
            structure[group]['groups'].append(n.name)
            # create group dictionary entry in structure
            structure[n.name] = {}
            structure[n.name]['groups'] = []
            structure[n.name]['datasets'] = []
            structure[n.name]['meta'] = {}
            tree(n, prefix=prefix+'  ', structure=structure, group=n.name)
        else:
            if verbose:
                print(prefix + dataset, end='')
                print(n[()])
                print(f'{prefix}\ttype: {n.dtype} size: {n.size} shape: {n.shape} chunked: {n.chunks}')
            structure[group]['datasets'].append(dataset)

    return structure'''


# convert frames to nd array for hdf5 writing
def get_frames(reader, verbose=False):
    # convert video into list of frames
    count = 1
    frames_list = []
    for im in reader:
        if count == 1:
            if verbose:
                print(f'Frame shape:  {im.shape}')
        frames_list.append(im)
        count += 1
        print(f'Reading frame: {count}', end='\r')

    # stack frames onto nparray with shape (num_frames, height, width, channel) 
    frames = np.stack(frames_list, axis=0)
    if verbose:
        print(f'Frames shape: {frames.shape}\n')

    return frames


# write dataset frames from source without chunks to hdf5 destination
def write_contiguous(source, overwrite=False, verbose=False):
    hdf5_path = source[:-4]+'_not_chunked_uncompressed'+'.hdf5'
    if not overwrite:
        if os.path.exists(hdf5_path):
            print(f'File: {hdf5_path} already exists')
            print(f'\tFile size: {os.path.getsize(hdf5_path)}')
            print('')
            return hdf5_path

    # get metadata on video
    reader = iio.get_reader(source)
    meta = reader.get_meta_data()
    frames = get_frames(reader)

    print(f'Created file: {hdf5_path}')
    with h5py.File(hdf5_path, 'w') as f:
        # write mov frames to hdf5 as a dataset
        dset = f.create_dataset('video_frames', data=frames)
        dset.attrs.update(meta.copy())
        dset.attrs['nframes'] = frames.shape[0]
        dset.attrs['original_format'] = source[-3:]
        dset.attrs['source_file'] = source
        print(f'\tCreated dataset: {dset.name}')
        print(f'\tChunks:          {dset.chunks}')
        print(f'\tCompression:     {dset.compression}')

    print(f'\tFile size: {os.path.getsize(hdf5_path)}')
    print('')
    return hdf5_path


# write dataset frames from source in chunks to hdf5 destination
def write_chunked(source, chunks=None, prefix=None, overwrite=False, compression='gzip', verbose=False):
    # create path name based on prefix that identifies chunking method
    if chunks is None:
        hdf5_path = source[:-4]+'_default'
        chunks=True
    else:
        if prefix is None or prefix == '':
            hdf5_path = source[:-4]+str(chunks)
        else:
            prefix = '_'+prefix
            hdf5_path = source[:-4]+prefix
    # add compression and hdf5 extention
    if compression is None:
        hdf5_path += '_uncompressed' + '.hdf5'
    else:
        hdf5_path += '_' + str(compression) + '.hdf5'
    
    if not overwrite:
        if os.path.exists(hdf5_path):
            print(f'File: {hdf5_path} already exists')
            print(f'\tFile size: {os.path.getsize(hdf5_path)}')
            print('')
            return hdf5_path

    # get video frames & metadata
    reader = iio.get_reader(source)
    frames = get_frames(reader)
    meta = reader.get_meta_data()

    print(f'Created file: {hdf5_path}')
    with h5py.File(hdf5_path, 'w') as f:
        # write mov frames to hdf5 as a dataset
        if compression is None:
            dset = f.create_dataset('video_frames', data=frames, chunks=chunks)
        else:
            dset = f.create_dataset('video_frames', data=frames, chunks=chunks, compression=compression)
        dset.attrs.update(meta.copy())
        dset.attrs['nframes'] = frames.shape[0]
        dset.attrs['original_format'] = source[-3:]
        dset.attrs['source_file'] = source
        print(f'\tCreated dataset: {dset.name}')
        print(f'\tChunks:          {dset.chunks}')
        print(f'\tCompression:     {dset.compression}')

    print(f'\tFile size: {os.path.getsize(hdf5_path)}')
    print('')

    return hdf5_path


def main():
    # command line argument: -o to overwrite
    overwrite = False
    compression = 'gzip'

    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == '-o':
                overwrite = True
            elif arg == '-c':
                compression = str(sys.argv[i+1])
                if compression == 'None':
                    compression = None
            elif arg == '-h':
                print('./chunks.py [-o] [-c compression]')
                print('\t -o - overwrite current files')
                print('\t -c - specify compression method (default: gzip)')

    if not os.path.exists(FILE):
        print(f'ERROR: {FILE} does not exist')
        sys.exit(1)

    files = []
    files.append(write_contiguous(FILE, overwrite=overwrite))
    files.append(write_chunked(FILE, overwrite=overwrite, compression=compression)) # write default chunked
    files.append(write_chunked(FILE, overwrite=overwrite, chunks=(28,1920,1080,3), compression=compression, prefix='chunked_whole'))
    files.append(write_chunked(FILE, overwrite=overwrite, chunks=(1,1920,1080,3), compression=compression, prefix='chunked_by_frame'))
    files.append(write_chunked(FILE, overwrite=overwrite, chunks=(1,1920,1080,1), compression=compression, prefix='chunked_by_frame_color'))
    
    for f in files:
        test_io(f)


if __name__ == '__main__':
    main()
