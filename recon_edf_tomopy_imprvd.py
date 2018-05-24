

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

    #dirpath = os.path.dirname(fname)
    
    print("so your files are here?: ")
    print(fname + "/n")
    
    print("you start at slice: " + str(StartSlice))
    print("and you want: "+ str(number_recon_slices)+ " Slices")
    
    number_of_files = len(fnmatch.filter(os.listdir(fname), '*.edf'))
    filename = fnmatch.filter(os.listdir(fname), '*.edf')[0]
    
    savename = fname + "/rec_" +  filename[:-4]
    savedirectory = os.path.dirname(savename)
    if not os.path.exists(savedirectory):
        os.makedirs(savedirectory)

    List_names = []

    # chose alg from 'fbp', 'gridrec'....
    print("Preparing: ")
    
    for i in range(number_of_files):

        loopnames = ""

        if (i < 10):
            loopnames = filename[:-5] + str(i) + '.edf'

        elif (i < 100):
            loopnames = filename[:-6] + str(i) + '.edf'

        elif (i < 1000):
            loopnames = filename[:-7] + str(i) + '.edf'

        elif (i < 10000):
            loopnames = filename[:-8] + str(i) + '.edf'

        List_names.append(loopnames)
        assert loopnames != "", "no files are given to the edf.reader"

    measure_file = dxchange.reader.read_edf(List_names[1], slc=None)
    
    if number_recon_slices==0:
        number_recon_slices=len(measure_file[0])-StartSlice

    proj_ar = np.zeros((number_of_files, number_recon_slices, measure_file.shape[2]))

    for i in range( len(List_names)):

        loopfile=dxchange.reader.read_edf(List_names[i], slc=None)

        proj_ar[i]=loopfile[0,StartSlice:(number_recon_slices + StartSlice), :]
        
        print('\r'+"progress: " + str(i) + "/ " + str(number_of_files), end = '')

    theta = tomopy.angles(number_of_files)

    if rot_center == 0:
        rot_center = math.floor(len(proj_ar[0, 0]) / 2)
        assert rot_center>0, "rot_center is probably wrong"

    proj = tomopy.minus_log(proj_ar)
    print("")
    print("begin reconstruction using ["+alg+ "] approach...")  
    rec = tomopy.recon(proj, theta, center=rot_center, algorithm=alg)
    
    # Mask each reconstructed slice with a circle.
    rec1 = tomopy.circ_mask(rec, axis=0, ratio=0.95)
    #plt.show(block=False)
    #plt.imshow(rec1[0])
    #plt.show
    
    # Write data as stack of TIFs.
    dxchange.write_tiff_stack(rec1, savename+'_recon_')    
    
    print("everything finished, find the results here: ",savename)
