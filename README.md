# pyppasearch
Simple python script for searching PPA

To use it one should install Python 3 packages using `sudo apt-get install python3-requests python3-bs4 python3-launchpadlib`.

## Description
This script will search from https://launchpad.net/ubuntu/+ppas, and then get packages information from each PPA, including package name, version and Ubuntu codename and CPU architecture.

## Usage
```
usage: pyppasearch.py [-h] [-c CODENAME] [-a ARCH] package

positional arguments:
  package               exact name of the package you want to search

optional arguments:
  -h, --help            show this help message and exit
  -c CODENAME, --codename CODENAME
                        First word of Ubuntu code name, e.g. Focal
  -a ARCH, --arch ARCH  CPU architecture, one of amd64, i386, armhf, arm64,
                        etc.
```
