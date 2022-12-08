# Background on HDF5

[HDF5](https://www.hdfgroup.org/solutions/hdf5/) is a file format structured like a file system; data is stored in arbitrary NxN datasets, which are organized in a hierarchy in groups and sub-groups. 

# Tests
### Access time & file size with different chunking methods 
The `chunk.py` program converts an MOV or AVI video into HDF5 files with the following chunking methods:
* Default h5py chunking method
* One chunk for the entire video
* One chunk per frame in the video
* One chunk per frame and color channel in the video 

As well as converting it to an uncompressed, contiguous (non-chunked) HDF5 file. 

Multiple compression algorithms are available for the chunked HDF5 files, including 3rd party compression algorithms, and can be specified with the `-c [algorithm]` option.

```python
# Available compression algorithms & their names
ALGS = {'gzip'      : 'gzip',
        'lzf'       : 'lzf',
        'bitshuffle': hdf5plugin.Bitshuffle(),
        'blosc'     : hdf5plugin.Blosc(),
        'bzip2'     : hdf5plugin.BZip2(),
        'lz4'       : hdf5plugin.LZ4(),
        'sz'        : hdf5plugin.SZ(absolute=0.1),
        'zfp'       : hdf5plugin.Zfp(reversible=True),
        'zstd'      : hdf5plugin.Zstd()}
```

# Results
![access_time](./access_time.png)
![access_time](./file_format.png)
