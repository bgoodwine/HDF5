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

## HDF5, MOV, and AVI

![file_format](./file_format.png)

![access_time](./access_time.png)

Chunking methods **whole** and **by frame** are larger chunks, and have higher compression ratios than **by frame+color**. However, **by frame+color** 

## Chunking methods

Read and write times for HDF5 video files with different chunking methods, all compressed with gzip. 
![](./read_time.png)

![](./write_time.png)

Note that gzip scales poorly, which is the cause of the inefficient write times for **by frame** but not **by frame+color**. 

### Compression ratio & chunk size
![](./chunk_size.png)
![](./chunk_sizes.png)

# Run these tests yourself

1. Cline the github <a href="https://github.com/bgoodwine/HDF5" class="downloads">
2. Choose a MOV or AVI video (<= 40 frames recommended as it is processing intensive)
3. 
