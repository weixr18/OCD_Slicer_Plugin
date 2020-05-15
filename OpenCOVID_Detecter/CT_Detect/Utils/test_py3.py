import sys
import time
import os
import socket
import logging
import argparse
import pickle


def unzip_file(zip_src, dst_dir):
    import zipfile
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        print('This is not zip')


if __name__ == "__main__":

    dirPath = '/'.join(os.path.realpath(__file__).split('\\')[:-1])

    if (sys.version.find('64 bit') > 0):
        include_path = dirPath + '/../../../Tools/required/required-amd64'
    else:
        include_path = dirPath + '/../../../Tools/required/required-win32'

    zip_path = include_path + '.zip'
    if not os.path.exists(include_path):
        os.mkdir(include_path)
        print("Unzip files...")
        unzip_file(zip_path, '/'.join(include_path.split('/')[:-1]))

    if (sys.version.find('64 bit') > 0):
        sys.path.insert(0, dirPath + '/../../../Tools/required/required-amd64')
        print("64 bit")
    else:
        sys.path.insert(0, dirPath + '/../../../Tools/required/required-win32')
        print("32 bit")

    if True:
        import numpy as np
        print("np:", np.__version__)
        import nibabel as nib
        print("nib:", nib.__version__)

    i = 0
    while True:
        print(i)
        i += 1
        time.sleep(1)
    pass
