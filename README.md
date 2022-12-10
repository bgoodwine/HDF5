# HDF5

### Install
Install `python 3.10`
* [Windows 64-bit installer](https://www.python.org/downloads/release/python-3100/#:~:text=Windows%20installer%20(64%2Dbit))

* [MacOS 64-bit universal installer](https://www.python.org/downloads/release/python-3100/#:~:text=SIG-,macOS%2064%2Dbit%20universal2%20installer,-macOS)

* Linux: `sudo apt install software-properties-common -y` + `sudo add-apt-repository ppa:deadsnakes/ppa -y` + `sudo apt install python3.10 -y`

Check version: `python3 --version`

Locally install the pip3 packages required: `./install.sh`

### Directory structure
* `chunks.py` - main test script
* `gzip_test.sh` - bash script to test speed of gzip 
* `install.sh` - bash script to install Python packages with pip3
* `tests/` - programs I wrote to figure out how to use h5py
* `results/` - my results from i/o tests on 3rd party compression algorithms

### Branches
* `main` - code
* `website` - has the `docs/` directory with the github pages website


### Run your own tests
`chunks.py` - convert a MOV or AVI video to hdf5, compare file sizes, access times for different chunking methods
```
USAGE: ./chunks [-f filepath] [-o] [-t] [-c compression] [-j] [-h]
	 -f - pass a path to a MOV of AVI file to analyze
	 -o - overwrite existing files (hdf5 file names built from properties)
	 -t - run I/O tests
	 -c - specify compression method (default: gzip)
	 -j - write all frames of selected video to JPEG images & report combined size
	 -h - display this message
```

Chunk types tested
* no chunking
* h5py default
* entire file
* by frame
* by frame and color

### Instructions 

1. Choose a MOV or AVI video (<= 40 frames recommended as it is processing intensive)
5. Ensure you've installed Python 3.10 and run `./install.sh` to install required `pip3` packages
6. Make a `files/` directory and copy your selected video into it
7. Run `./chunks.py -f files/[your_file.mov]` to convert your video to HDF5 files
8. Modify the dimensions of the I/O test as shown below
9. Run `./chunks.py -f files/[your_file.mov] -t` to run the I/O tests

The dimensions within the access time test may need to be modified, as the current dimensions are hardcoded to the dimensions of my test file; (28, 1920, 1080, 3), or a 28-frame 1920x1080 pixel 3-channel color video. 
```python
# test read of entire file
f = h5py.File(path, 'r+', rdcc_nbytes=0)
start = time.time()
frame = f[dset_name][0:27,0:1919,0:1079,0:2]
end = time.time()
f[dset_name][0:27,0:1919,0:1079,0:2] = frame
f.close()
```

The slices to read the entire file are from `0:number_of_frames`, `0:height_of_frame`, `0:width_of_frame`, and `0:number_of_color_channels`. For example, to modify this test to run for a 30 frame 3072x2304 color video, i.e. a video with dimensions (30, 3072, 2304, 3), the modified code would be:
```python
# test read of entire file
f = h5py.File(path, 'r+', rdcc_nbytes=0)
start = time.time()
frame = f[dset_name][0:29,0:3071,0:2303,0:2]
end = time.time()
f[dset_name][0:29,0:3071,0:2303,0:2] = frame
f.close()
```

The dimensions of your selected video's frames are displayed when running `./chunks.py`, after displaying the metadata on that video. For example, my video has a frame dimension of (1920, 1080, 3).
```
Path: files/movies/katrina.mov 
Size:       2125688

...

 'rotate': 0,
 'size': (1080, 1920),
 'source_size': (1080, 1920)}
Shape: (1920, 1080, 3)
```

The number of frames in your selected video can be discovered by running `./chunks.py -j` to write the frames as JPEG images. For example, my video has 28 frames. 
```
Writing JPEGs...
Frame 1: 127850
Frame 2: 129607

...

Frame 28: 126611
Saved frames 1-28
Total size: 3478752
```

Since the dimensions are (number of frames, height of frame, width of frame, number of color channels), my total video dimensions are: (28, 1920, 1080, 3), so my slices are as follows in the I/O test:
```python
# last frame's 0x0 pixel on color channel 0
pixel = f[dset_name][27,0,0,0]
# last frame's 1920x1080 image on all three channels
one_frame = f[dset_name][27,0:1919,0:1079,0:2]
# all frames of all 1920x1080 images on all three channels
all_frames = f[dset_name][0:29,0:3071,0:2303,0:2]
```

Note: Multiple compression algorithms are available for the chunked HDF5 files, including 3rd party compression algorithms. These can be specified with the `-c [algorithm]` option.

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
