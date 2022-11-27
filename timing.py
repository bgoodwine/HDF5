#!/usr/local/bin/python3.10

import time
import h5py
import numpy as np

# traverse hdf5 file and print structure
def tree(f, prefix='  '):
    if f.name == '/':
        print(f.name)
    for dataset in f.keys():
        n = f.get(dataset)
        if isinstance(n, h5py.Group):
            print(prefix + n.name)
            tree(n, prefix=prefix+'  ')
        else:
            print(prefix + dataset)
            print(n[()])

# walk hdf5 file and yield datasets
def walk(f):
    for dataset in f.keys():
        n = f.get(dataset)
        if isinstance(n, h5py.Group):
            walk(n)
        else:
            yield(n)

# traverse hdf5 file and access all data (chunk cache irrelevant)
def dump(f):
    for dataset in f.keys():
        n = f.get(dataset)
        if isinstance(n, h5py.Group):
            dump(n)
        else:
            n = n[()]

# returns time in seconds to read entire dataset
def testread(f):
    start = time.time()
    dump(f)
    end = time.time()
    return end-start


def repack(f, n1, n2):
    # TODO: loop through all datasets, rechunk
    gen = walk(f)
    while True:
        try:
            dataset = next(gen)
            print(dataset.name)
        except StopIteration:
            print('Iteration stopped.')
            break

# traverse hdf5 file and convert to dictionary
def file2dict(f, d={}, prefix=[]):
    if f.name == '/':
        d = {}
    else:
        for p in prefix:
            d = d[p]

    for dataset in f.keys():
        n = f.get(dataset)
        if isinstance(n, h5py.Group):
            d[n.name] = {}
            file2dict(n, d=d, prefix=[n.name])
        else:
            d[n.name] = n

    return d

# write random data to an hdf5 file
def write_rand(file_name):
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
    filename = 'files/TempData.hdf5'
    f = h5py.File(filename, 'a')
    readtime = testread(f)
    print(f'Time to read {filename}: {readtime}')
    repack(f, 1, 1)


if __name__ == '__main__':
    main()
