

from __future__ import print_function
import tomopy
import dxchange
import numpy as np
import fnmatch
import os
from matplotlib import pyplot as plt
from scipy.misc import imresize
from scipy import ndimage
import time
import datetime
import math

if __name__ == '__main__':
    
    time_start = time.time()
  
    fname = str(raw_input('Please paste the absolut path to the edf-files here: '))
    assert fname != "", "Your filepath cannot be empty!"
    
    number_of_files = len(fnmatch.filter(os.listdir(fname), '*.edf'))
    filename = fname + '/' + fnmatch.filter(os.listdir(fname), '*.edf')[0]
    print("--- The first file: " + filename + " ---\n")
    
    List_names = []

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

    
    #getting the image dimensions
    measure_file = dxchange.reader.read_edf(List_names[0], slc=None)
    height = measure_file.shape[1]
    width = measure_file.shape[2]
    
    measure_file = measure_file.reshape(height,width)
    print("Your original images have the following size: ", measure_file.shape)
    
    #User chooses at which height the reconstruction should start
    StartSlice = int(input('At which Slice do you wish to start' + 
                       ' the reconstruction?' + '\nThe first one is 0: '))
    
    #User chooses how many slides he want to have after the StartSlice
    number_recon_slices = int(input('How many slices do you want to consider ' +
                                'after the first one? '+
                                '\n(Before resizing) '
                                '\nType 0 for all: '))
    
    rot_center = int(input('Where is the center of rotation? ' +
                           '\nType 0 if you dont know: '))
    
    alg = str(raw_input('Which algorithm do you wish to use? ' +
                        '\nSome choises are "gridrec" "fbp": '))
    
    resize_bool = False
    
    factor_question = str(raw_input('Do you wish to resize the image ' +
                                    '(to handle big datasets)? (y/n): '))
    
    if factor_question in ['y','Y','Yes','yes']:
        
        resize_bool = True
        resize_parameter = input('Please type the fraction of the size '+
                                 '\n(e.g. 0.5 for 50% smaller height and widths):  ')
       
    rotate_bool = False
        
    rotate_question = str(raw_input('Do you wish to rotate the image ' +
                                    '(to handle object movement)? (y/n): '))
    
    if rotate_question in ['y','Y','Yes','yes']:
        
        rotate_bool = True
        rotate_parameter = input('Please type the angle for the rotation '+
                                 '\n(e.g. 1.5 for a 1.5 degree rotation):  ')
        
    output_folder = str(raw_input('Where do you want to safe the resulting images'
                                  +' (a new folder gets created)?: '))
    
    print("\n so your files are here?: ")
    print(fname)
    
    print("you start at slice: " + str(StartSlice))
    print("and you want: "+ str(number_recon_slices)+ " Slices")
    
    sample_name = os.path.splitext(os.path.basename(filename[:-9]))[0]
    
    savename = output_folder + "/rec_" + sample_name + alg + "/" + sample_name
    
    savedirectory = os.path.dirname(savename)
    
    if not os.path.exists(savedirectory):
        os.makedirs(savedirectory)
    
    if number_recon_slices==0:
        number_recon_slices = len(measure_file[0])-StartSlice

    #proj_ar = np.zeros((number_of_files, number_recon_slices, measure_file.shape[1]))
    proj_ar=[]

    for i in range(len(List_names)):
        
        #if i == 0:
            
        loopfile = dxchange.reader.read_edf(List_names[i], slc=None)
        
        if resize_bool == True:
            
            resl_loopfile = ndimage.zoom(
                    loopfile[0,StartSlice:(number_recon_slices + StartSlice), :],
                    resize_parameter,
                    )

        if rotate_bool == True:
            
            resl_loopfile = ndimage.interpolation.rotate(resl_loopfile,rotate_parameter)

        proj_ar.append(resl_loopfile)
        
        print('\r' + "progress: " + str(i+1) + "/ " + str(number_of_files),end='')

    proj_ar = np.asarray(proj_ar)
    theta = tomopy.angles(number_of_files)

    if rot_center == 0:
        rot_center = math.floor(len(proj_ar[0, 0]) / 2)
        assert rot_center>0, "rot_center is probably wrong"
        assert rot_center<len(proj_ar[0, 0]), "Rotation center is outside of the image"

    proj = tomopy.minus_log(proj_ar)
    print("")
    print("begin reconstruction using ["+alg+ "] approach...")  
    rec = tomopy.recon(proj, theta, center=rot_center, algorithm=alg)
    
    print("applying a circular mask to the reconstructed data")
    # Mask each reconstructed slice with a circle.
    rec1 = tomopy.circ_mask(rec, axis=0, ratio=0.95)
    #plt.show(block=False)
    #plt.imshow(rec1[0])
    #plt.show
    
    print("writing the files as 'TIFF's to the output direction ")
    # Write data as stack of TIFs.
    dxchange.write_tiff_stack(rec1, savename+'recon')    
    
    duration = str(datetime.timedelta((time.time()-time_start)/(3600*24)))
    
    print("It took %s (hh:mm:ss) to finish reconstruction" %(duration))
    print("everything finished, find the results here: ",savename)
