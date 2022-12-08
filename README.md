# HDF5

### Requirements
`python 3.10`
* [Windows 64-bit installer](https://www.python.org/downloads/release/python-3100/#:~:text=Windows%20installer%20(64%2Dbit))

* [MacOS 64-bit universal installer](https://www.python.org/downloads/release/python-3100/#:~:text=SIG-,macOS%2064%2Dbit%20universal2%20installer,-macOS)

* Linux: `sudo apt install software-properties-common -y` + `sudo add-apt-repository ppa:deadsnakes/ppa -y` + `sudo apt install python3.10 -y`

Check version: `python3 --version`

Locally install requirements with pip3: `./install.sh`
```
pip3 install --user numpy
pip3 install --user Pillow
pip3 install --user h5py
pip3 install --user hdf5plugin
pip3 install --user imageio
pip3 install --user av
pip3 install --user imageio[ffmpeg]
pip3 install --user opencv-python
```


### Files
* `files/TempData.hdf5` - default contiguous storage
* `files/TempData_100.hdf5` - 100x100 chunked storage
