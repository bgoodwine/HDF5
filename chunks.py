#!/usr/bin/env python3

import time
import sys
import os
import h5py
import hdf5plugin
import numpy as np
import imageio as iio
import pprint as pp

FILE  = 'files/movies/katrina.mov'

ALGS = {'gzip'      : 'gzip',
        'lzf'       : 'lzf',
        'bitshuffle': hdf5plugin.Bitshuffle(),
        'blosc'     : hdf5plugin.Blosc(),
        'bzip2'     : hdf5plugin.BZip2(),
        'lz4'       : hdf5plugin.LZ4(),
        'sz'        : hdf5plugin.SZ(absolute=0.1),
        'zfp'       : hdf5plugin.Zfp(reversible=True),
        'zstd'      : hdf5plugin.Zstd()}


def usage(exit_status):
    print('USAGE: ./chunks [-o] [-t] [-c compression] [-h]')
    print('\t -o - overwrite current files')
    print('\t -t - run I/O tests')
    print('\t -c - specify compression method (default: gzip)')
    print('\t -h - display this message')
    sys.exit(exit_status)


def test_io(path, dset_name='video_frames'):
    with h5py.File(path, 'r+') as f:
        print(f'Opened file: {path}')
        if dset_name not in f.keys():
            return None
        else:
            dset = f[dset_name] 
            print(f'Found dataset: {dset.name}')
            print(f'\tShape:       {dset.shape}')
            print(f'\tChunks:      {dset.chunks}')
            print(f'\tCompression: {dset.compression}')

    # opening/closing to ensure data is flushed to the file and not just stored
    # test read/write of the 0x0 pixel of the last frame for chanel 0
    f = h5py.File(path, 'r+', rdcc_nbytes=0)
    start = time.time()
    val = f[dset_name][27,0,0,0]
    end = time.time()
    f.close()
    print(f'Pixel read time: {end-start}')
    f = h5py.File(path, 'r+', rdcc_nbytes=0)
    start = time.time()
    f[dset_name][27,0,0,0] = 0
    end = time.time()
    f.close()
    print(f'Pixel write time:  {end-start}')
    f = h5py.File(path, 'r+')
    f[dset_name][27,0,0,0] = val
    f.close()

    # test read/write of the last frame
    f = h5py.File(path, 'r+', rdcc_nbytes=0)
    start = time.time()
    frame = f[dset_name][27,0:1919,0:1079,0:2]
    end = time.time()
    f.close()
    print(f'Frame read time: {end-start}')
    f = h5py.File(path, 'r+', rdcc_nbytes=0)
    start = time.time()
    f[dset_name][27,0:1919,0:1079,0:2] = np.empty((1919,1079,2))
    end = time.time()
    f.close()
    print(f'Frame write time: {end-start}')
    f = h5py.File(path, 'r+')
    f[dset_name][27,0:1919,0:1079,0:2] = frame
    f.close()

    # test read/write of entire file
    f = h5py.File(path, 'r+', rdcc_nbytes=0)
    start = time.time()
    frame = f[dset_name][0:27,0:1919,0:1079,0:2]
    end = time.time()
    f[dset_name][0:27,0:1919,0:1079,0:2] = frame
    f.close()
    print(f'Whole file read time: {end-start}')
    f = h5py.File(path, 'r+', rdcc_nbytes=0)
    start = time.time()
    f[dset_name][0:27,0:1919,0:1079,0:2] = np.empty((27,1919,1079,2))
    end = time.time()
    f.close()
    print(f'Whole file write time: {end-start}')
    f = h5py.File(path, 'r+')
    f[dset_name][0:27,0:1919,0:1079,0:2] = frame
    f.close()

    print('')


# convert one frame of the video to an mp4 for manual gzip tests
def get_image(source):
    reader = iio.get_reader(source)
    writer = iio.get_writer('files/katrina_frame.mp4')

    for im in reader:
        writer.append_data(im[:,:,:])
        break
    writer.close()
    print('Saved first frame as an mp4 image...')


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
        print(f'Frames shape: {frames.shape}')
        print(f'Frames type:   {frames.dtype}\n')

    return frames


# write dataset frames from source without chunks to hdf5 destination
def write_contiguous(source, overwrite=False, verbose=False):
    hdf5_path = source[:-4]+'_not_chunked_uncompressed'+'.hdf5'
    if not overwrite:
        if os.path.exists(hdf5_path):
            print(f'File: {hdf5_path} already exists')
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
            print(f'File: {hdf5_path} exists')
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
            dset = f.create_dataset('video_frames', data=frames, dtype=frames.dtype, chunks=chunks, compression=ALGS[compression])
        dset.attrs.update(meta.copy())
        dset.attrs['nframes'] = frames.shape[0]
        dset.attrs['original_format'] = source[-3:]
        dset.attrs['source_file'] = source
        print(f'\tCreated dataset: {dset.name}')
        print(f'\tChunks:          {dset.chunks}')
        print(f'\tCompression:     {dset.compression}')
        print(f'\tType:            {dset.dtype}')

    print(f'\tFile size: {os.path.getsize(hdf5_path)}')
    print('')

    return hdf5_path


def main():
    # command line argument: -o to overwrite
    overwrite = False
    compression = 'gzip'
    io_test = False

    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == '-o':
                overwrite = True
            elif arg == '-c':
                compression = str(sys.argv[i+1])
                if compression == 'None':
                    compression = None
            elif arg == '-t':
                io_test = True
            elif arg == '-h':
                usage(0)

    if not os.path.exists(FILE):
        print(f'ERROR: {FILE} does not exist')
        sys.exit(1)

    print('Available 3rd party compression algorithms: ', end='')
    print(' '.join([key for key in ALGS.keys()]))
    print('')

    files = []
    files.append(write_contiguous(FILE, overwrite=overwrite))
    files.append(write_chunked(FILE, overwrite=overwrite, compression=compression)) # write default chunked
    files.append(write_chunked(FILE, overwrite=overwrite, chunks=(28,1920,1080,3), compression=compression, prefix='chunked_whole'))
    files.append(write_chunked(FILE, overwrite=overwrite, chunks=(1,1920,1080,3), compression=compression, prefix='chunked_by_frame'))
    files.append(write_chunked(FILE, overwrite=overwrite, chunks=(1,1920,1080,1), compression=compression, prefix='chunked_by_frame_color'))
    
    if io_test:
        print('\nRunning I/O tests...')
        for f in files:
            test_io(f)


if __name__ == '__main__':
    main()
