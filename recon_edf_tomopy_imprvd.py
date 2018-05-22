

from __future__ import print_function
import tomopy
import dxchange
import numpy as np
import fnmatch
import os
from matplotlib import pyplot as plt
import argparse
import math

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-f",
                        "--filepath",
                        help="absolut path to the edf-files",
                        type=str)
    parser.add_argument("-s",
                        "--StartSlice",
                        help="start slice of the reconstruction",
                        default=0,
                        type=int)
    parser.add_argument("-e",
                        "--number_recon_slices",
                        help="number of slices that are to be reconstructed ",
                        default=0,
                        type=int)
    parser.add_argument("-r",
                        "--rotation_center",
                        help="absolut path to the edf-files",
                        default=0,
                        type=int)
    parser.add_argument("-a",
                        "--algorithm",
                        help="absolut path to the edf-files",
                        default='gridrec',
                        type=str)
    # parser.add_argument("-o","--filepath where the files are to be saved", help="absolut path to the edf-files", type=str)
    args = parser.parse_args()

    fname = args.filepath
    StartSlice = args.StartSlice
    number_recon_slices = args.number_recon_slices
    rot_center = args.rotation_center
    alg = args.algorithm

    dirpath = os.path.dirname(fname)
    number_of_files = len(fnmatch.filter(os.listdir(dirpath), '*.edf'))
    filename = fnmatch.filter(os.listdir(dirpath), '*.edf')[0]

    List_names = []

    # chose alg from 'fbp', 'gridrec'....
    print("Preparing: ")
    for i in range(number_of_files):

        loopnames = ""

        if (i < 10):
            loopnames = fname[:-5] + str(i) + '.edf'

        elif (i < 100):
            loopnames = fname[:-6] + str(i) + '.edf'

        elif (i < 1000):
            loopnames = fname[:-7] + str(i) + '.edf'

        elif (i < 10000):
            loopnames = fname[:-8] + str(i) + '.edf'

        List_names.append(loopnames)
        assert loopnames != ""

    measure_file = dxchange.reader.read_edf(List_names[1], slc=None)

    proj_ar = np.zeros((number_of_files, number_recon_slices, measure_file.shape[2]))

    for i in range( len(List_names)):

        loopfile=dxchange.reader.read_edf(name, slc=None)

        proj_ar[i]=loopfile[StartSlice:(number_recon_slices + StartSlice), :]



