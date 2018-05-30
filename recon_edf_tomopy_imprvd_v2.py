

from __future__ import print_function
import tomopy
import dxchange
import numpy as np
import fnmatch
import os
from matplotlib import pyplot as plt
from PIL import Image

import math

if __name__ == '__main__':
  
    fname = str(raw_input('Please paste the absolut path to the edf-files here: '))
    assert fname != "", "Your filepath cannot be empty!"
    
    StartSlice = int(input('At which Slice do you wish to start' + 
                       ' the reconstruction?' + '\n The first one is 0: '))
    
    number_recon_slices = int(input('How many slices do you want to reconstruct '
                                'after the first one?: '))
    
    rot_center = int(input('Where is the center of rotation? \nType 0 if you dont know: '))
    
    alg = str(raw_input('Which algorithm do you wish to use? \nSome choises are "gridrec" "fbp": '))
    
    print("so your files are here?: ")
    print(fname)
    
    print("you start at slice: " + str(StartSlice))
    print("and you want: "+ str(number_recon_slices)+ " Slices")
    
    
    
    number_of_files = len(fnmatch.filter(os.listdir(fname), '*.edf'))
    filename = fname + '/' + fnmatch.filter(os.listdir(fname), '*.edf')[0]
    
    print("---" + filename + "---")
    
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

   #measure_file = dxchange.reader.read_edf(List_names[1], slc=None)
    
    measure_file = dxchange.reader.read_edf(List_names[0], slc=None)
    height = measure_file.shape[1]
    width = measure_file.shape[2]
    
    measure_file = measure_file.reshape(height,width)
    
    if number_recon_slices==0:
        number_recon_slices=len(measure_file[0])-StartSlice

    proj_ar = np.zeros((number_of_files, number_recon_slices, measure_file.shape[2]))

    for i in range( len(List_names)):

        #loopfile=dxchange.reader.read_edf(List_names[i], slc=None)
        
        loopfile = dxchange.reader.read_edf(List_names[1], slc=None)
        
        resl_loopfile = loopfile.resize(nwidth, nheight, Image.LANCZOS)

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
