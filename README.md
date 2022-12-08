# HDF5

### Install
Install `python 3.10`
* [Windows 64-bit installer](https://www.python.org/downloads/release/python-3100/#:~:text=Windows%20installer%20(64%2Dbit))

* [MacOS 64-bit universal installer](https://www.python.org/downloads/release/python-3100/#:~:text=SIG-,macOS%2064%2Dbit%20universal2%20installer,-macOS)

* Linux: `sudo apt install software-properties-common -y` + `sudo add-apt-repository ppa:deadsnakes/ppa -y` + `sudo apt install python3.10 -y`

Check version: `python3 --version`

Locally install requirements with pip3: `./install.sh`


### Run your own tests
`chunks.py` - convert a MOV or AVI video to hdf5, compare file sizes, access times for different chunking methods
```
USAGE: ./chunks [-f filepath] [-o] [-t] [-c compression] [-h]
	 -f - pass a path to a MOV of AVI file to analyze
	 -o - overwrite existing files (hdf5 file names built from properties)
	 -t - run I/O tests
	 -c - specify compression method (default: gzip)
	 -h - display this message
```

Chunk types tested
* no chunking
* h5py default
* entire file
* by frame
* by frame and color
