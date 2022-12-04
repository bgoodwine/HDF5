#!/usr/local/bin/python3.10

import time
import sys
import os
import h5py
import numpy as np
import imageio as iio
import pprint as pp

FILE  = 'files/movies/katrina.MOV'

# traverse hdf5 file and print structure
def tree(f, prefix='  ', structure={}, group='/', verbose=True):
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

    return structure

# walk hdf5 file and yield datasets
def walk(f):
    for dataset in f.keys():
        n = f.get(dataset)
        if isinstance(n, h5py.Group):
            walk(n)
        else:
            yield(n)

# write dataset frames from source in chunks to hdf5 destination
def write_chunked(source):
    # hdf5 path -> replace format extension with hdf5
    hdf5_path = source[:-3]+'hdf5'
    if os.path.exists(hdf5_path):
        print(f'File: {hdf5_path} already exists')
        return None

    # get metadata on video
    reader = iio.get_reader(source)
    meta = reader.get_meta_data()
    fps = int(meta['fps'])
    print(f'Metadata for {source}')
    pp.pprint(meta)
    print('')

    # convert video into np array of frames
    count = 1
    frames_list = []
    for im in reader:
        frames_list.append(im)
        '''
        if count == 1:
            # create np array with shape (num_frames, height, width, channel)
            # expand on axis 0 so frames will be stacked first element of the shape
            frames = np.expand_dims(im, axis=0)
            print(f'Image shape:  {im.shape}')
            print(f'Frames shape: {frames.shape}')
        else:
            # stack onto existing frames np array
            frames = np.stack(axis=0)
            print(f'Image shape:  {im.shape}')
            print(f'Frames shape: {frames.shape}')
        '''
        count += 1
        #print(f'Frame shape: {im.shape}')
        print(f'Reading frame: {count}', end='\r')

    frames = np.stack(frames_list, axis=0)
    print(f'Frames shape: {frames.shape}')
    return

'''
    #with h5py.File(hdf5_path, 'w') as f:

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

'''


# write random data to an hdf5 file
def write_rand(file_name):
    # get metadata on video
    reader = iio.get_reader(video)
    meta = reader.get_meta_data()
    print(meta)
    fps = int(meta['fps'])

    for im in reader:
        
        writer.append_data(im[:,:,:])
    writer.close()

    d1 = np.random.random(size = (100, 20))
    d2 = np.random.random(size = (100, 200))
    d3 = np.random.random(size = (100, 2))

    with h5py.File(file_name, 'w') as f:
        dset = f.create_dataset('data1', data=d1)
        print(f'Created dataset: {dset.name}')
        dset2 = f.create_dataset('data2', data=d2)
        print(f'Created dataset: {dset2.name}')
        grp = f.create_group('subgroup')
        print(f'Created group: {grp.name}')
        dset3 = grp.create_dataset('data3', data=d3)
        print(f'Created dataset: {dset3.name}')
    

def main():
    if not os.path.exists(FILE):
        print(f'ERROR: {FILE} does not exist')
        sys.exit(1)

    write_chunked(FILE)

    #f = h5py.File(FILE, 'a')
    #structure = tree(f)
    #pp.pprint(structure)
    #readtime = testread(f)
    #print(f'Time to read {FILE}: {readtime}')
    #f.close()


if __name__ == '__main__':
    main()
