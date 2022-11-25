#!/usr/local/bin/python3.10

import h5py
import pprint as pp
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


# traverse hdf5 file and print structure
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
    f = h5py.File('files/TempData.hdf5', 'a')
    tree(f)
    d = file2dict(f)
    pp.pprint(d)


if __name__ == '__main__':
    main()
