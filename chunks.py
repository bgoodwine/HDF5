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

    # convert video into list of frames
    count = 1
    frames_list = []
    for im in reader:
        if count == 1:
            print(f'Frame shape:  {im.shape}')
        frames_list.append(im)
        count += 1
        print(f'Reading frame: {count}', end='\r')

    # stack frames onto an np array on axis 0 for (num_frames,  
    frames = np.stack(frames_list, axis=0)
    print(f'Frames shape: {frames.shape}\n')

    with h5py.File(hdf5_path, 'w') as f:
        # write mov frames to hdf5 as a dataset
        dset = f.create_dataset('video_frames', data=frames)
        dset.attrs.update(meta.copy())
        dset.attrs['nframes'] = frames.shape[0]
        dset.attrs['original_format'] = source[-3:]
        dset.attrs['source_file'] = source
        print(f'Created dataset: {dset.name}')
        print('')

    return hdf5_path


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
