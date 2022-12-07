#!/usr/bin/env python3

import sys
import os
import numpy as np
import imageio.v2 as iio
import h5py
import pprint as pp

# constants
VIDEOS = ['files/movies/mnms.mp4', 'files/movies/helmholtz.mov']
FORMATS = ['mp4', 'mov', 'hdf5', 'avi']

FILE = 'files/movies/katrina.mov'
FILE_FORMATS = ['hdf5', 'avi', 'mov']


# display frames in iio imread frames
def disp(frames):
    for fram in frames:
        print(frame.shape, frame.dtype)


# write dataset frames to hdf5 file in path
def write_movie_ndarray(path, reader, meta):
    with h5py.File(path, 'w') as f:
        g = f.create_group('video_frames')
        # copy over metadata
        g.attrs.update(meta.copy())
        print('Copied over metadata to g.attrs:')
        pp.pprint(g.attrs)
        
        count = 1
        print(reader.get_length())
        frames = np.empty(0)
        for im in reader:
            frames = np.append(frames, im)
            if count == 50:
                print(f'Adding first 50 frames...           ')
                dset = g.create_dataset('video', data=frames, chunks=True, compression='gzip', shuffle=True, maxshape=(None,))
                print('fdset shape: ', end='')
                print(dset.shape)
                frames = np.empty(0)
            elif count%50 == 0:
                print(f'Adding next 50 frames...            ')
                print(f'frames.shape = ', end='')
                print(frames.shape)
                dset.resize(dset.shape[0]+frames.shape[0], axis=0)
                dset[-frames.shape[0]:] = frames
            print(f'Copying frame {count} shape ', end='\r')
            count += 1

        # add the last couple frames
        if len(frames) > 0:
            dset.resize(dset.shape[0]+frames.shape[0], axis=0)
            dset[-frames.shape[0]:] = frames
            print(f'Added additional {len(frames)} frames')
                

        print('Done.\n')


# traverse hdf5 file and print structure
def tree(f, shapes, chunks):
    for dataset in f.keys():
        n = f.get(dataset)
        if isinstance(n, h5py.Group):
            tree(n, shapes, chunks)
        else:
            if n.name == '/video_frames/video':
                shapes.append(str(n.shape))
                #print(f'dataset {n.name} shape: ', end='')
                #print(n.shape)
                chunks.append(str(n.chunks))
                #print(f'dataset {n.name} chunks: ', end='')
                #print(n.chunks)
            #else:
                #print(f'skipping metadata {n.name}')

    return shapes, chunks


def compare_formats(mp4_video, avi_video, hdf_video):
    # TODO: decide if it's necessary to read in the data? can you get it from meta?
    mp4_reader = iio.get_reader(mp4_video)
    avi_reader = iio.get_reader(avi_video)
    mp4 = mp4_reader.get_meta_data()
    avi = avi_reader.get_meta_data()
    # TODO: get size and fps from meta 
    #print(mp4)
    #print(avi)
    hdf_file   = h5py.File(hdf_video, 'r')

    shapes, chunks = tree(hdf_file, [], [])
    
    hdf_chunks = ' '.join(chunks)
    hdf_shape = ' '.join(shapes)
    mp4_shape = str(mp4['size'])
    avi_shape = str(avi['size'])

    # collect size data
    mp4_size = os.path.getsize(mp4_video)
    avi_size = os.path.getsize(avi_video)
    hdf_size = os.path.getsize(hdf_video)

    # calculate compression ratio: CR = original file size / compressed file size
    sizes = [mp4_size, avi_size, hdf_size]
    sizes.sort(reverse=True) # take 'original' file to be largest file
    
    # display results
    print(f'{"Path":<30}: {"(x, y, z)":<17}   {"size (b)":>11}   {"fps":<5}  {"chunks":<10}')
    print(f'{mp4_video:<30}: {mp4_shape:<17}   {mp4_size:>11}  {mp4["fps"]:<5}')
    print(f'{avi_video:<30}: {avi_shape:<17}   {avi_size:>11}  {avi["fps"]:<5}')
    print(f'{hdf_video:<30}: {hdf_shape:<17}   {hdf_size:>11}   {"N/A":<5}  {hdf_chunks:<10}')
    print('')
    print(f'{sizes[0]} : {sizes[1]:<10} = {sizes[0]/sizes[1]}')
    print(f'{sizes[0]} : {sizes[2]:<10} = {sizes[0]/sizes[2]}')


def video_test():
    for video in VIDEOS:
        print(f'\n\nOriginal video: {video}')
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
                    
                    # get metadata on video
                    reader = iio.get_reader(video)
                    meta = reader.get_meta_data()
                    fps = int(meta['fps'])
                    print(f'Missing file: {path+fm}, writing from {video} with {fps} fps...')

                    # hdf5 files must be written specially
                    if fm == 'hdf5':
                        print(f'Missing file: {path+fm}, writing from {video}...')
                        pp.pprint(meta)
                        

                        write_movie_ndarray(path+fm, reader, meta)
                    # non-hdf5 files can all be writen with the writer
                    else:
                        writer = iio.get_writer(path+fm, fps=meta['fps'])
                        for im in reader:
                            writer.append_data(im[:,:,:])
                        writer.close()

                else:
                    print(f'ERROR: cannot start w/ original file {video}')
            else:
                print(f'Exists: {path+fm}')

        print('')
        compare_formats(mp4_path, avi_path, hdf_path)

def write_video(source, destination):
    if destination.endswith('hdf5'):
        print(f'ERROR: cannot write to {destination} with iio.')
        sys.exit(1)

    reader = iio.get_reader(source)
    meta   = reader.get_meta_data()
    writer = iio.get_writer(destination, fps=meta['fps'])
    
    print(f'Converting: {source} --> {destination}')
    for im in reader:
        writer.append_data(im[:,:,:])
    writer.close()
    return destination


# convert one frame of the video to an mp4 for manual gzip tests
def write_frames(source):
    reader = iio.get_reader(source)

    i = 0
    totalsize = 0
    for im in reader:
        path = f'files/frames/katrina_frame{i}.jpeg'
        writer = iio.get_writer(path)
        writer.append_data(im[:,:,:])
        writer.close()

        size = os.path.getsize(path)
        totalsize += size

        i += 1
        print(f'Frame {i}: {size}')
    print(f'Saved frames 0-{i}')
    print(f'Total size: {totalsize}')


def main():
    if not os.path.exists(FILE):
        print(f'ERROR: {FILE} does not exist.')
        sys.exit(1)

    write_frames(FILE)
    sys.exit(0)
    
    videos = []
    path = FILE[:-3]

    for fm in FILE_FORMATS:
        if not os.path.exists(path+fm):
            videos.append(write_video(FILE, path+fm))
        else:
            videos.append(path+fm)

    print(f'{"Path":<25}  {"size (b)":>13}')
    for video in videos:
        size = os.path.getsize(video)
        print(f'{video:<25}  {size:>13}')
        if not video.endswith('hdf5'):
            reader = iio.get_reader(video)
            meta = reader.get_meta_data()
            pp.pprint(meta)
        print('')
        



if __name__ == '__main__':
    main()
