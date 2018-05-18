#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TomoPy example script to reconstruct the ESRF tomography data as original edf
files.
"""

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
    parser.add_argument("-f","--filepath", help="absolut path to the edf-files", type=str)
    #parser.add_argument("-n","--number_of_files", help="number of edf files ", type=str) 
    parser.add_argument("-s","--StartSlice", help="start slice of the reconstruction",default=0, type=int)    
    parser.add_argument("-e","--number_recon_slices", help="number of slices that are to be reconstructed ",default=0, type=int) 
    parser.add_argument("-r","--rotation_center", help="absolut path to the edf-files", default=0, type=int)    
    parser.add_argument("-a","--algorithm", help="absolut path to the edf-files",default='gridrec', type=str)
    #parser.add_argument("-o","--filepath where the files are to be saved", help="absolut path to the edf-files", type=str)    
    args=parser.parse_args()
    
    # Set path to the micro-CT data to reconstruct.
    #fname1 = '/data-jwi/jwi-fs03/data/Tomo_tmp/Kai/1405_Bessy_BoneTissue/1405_set01_BlackDrum_17K_25mmPhC_0p8sec_0001a_norm_test/norm_1405_set01_BlackDrum_17K_25mmPhC_0p8sec_0001a__0000.edf'
    #fname2 = '/data-jwi/jwi-fs03/data/Tomo_tmp/Kai/1405_Bessy_BoneTissue/1405_set01_BlackDrum_17K_25mmPhC_0p8sec_0001a_norm_test/norm_1405_set01_BlackDrum_17K_25mmPhC_0p8sec_0001a__0001.edf'
    
    #fname = '/data-jwi/jwi-fs03/data/Tomo_tmp/Kai/1405_Bessy_BoneTissue/1405_set01_BlackDrum_17K_25mmPhC_0p8sec_0001a_norm/norm_1405_set01_BlackDrum_17K_25mmPhC_0p8sec_0001a__0000.edf'
    fname=args.filepath
    StartSlice=args.StartSlice
    number_recon_slices=args.number_recon_slices
    rot_center=args.rotation_center
    alg=args.algorithm
    
    dirpath=os.path.dirname(fname)
    number_of_files=len(fnmatch.filter(os.listdir(dirpath), '*.edf'))
    print("the data is this: "+fname)
    filename=os.path.splitext(os.path.basename(fname))[0]
    
    savename=fname[:-4]+"/"
    savedirectory=os.path.dirname(savename)
    if not os.path.exists(savename):
        os.makedirs(savename)
    
    #dirpath='/data-jwi/jwi-fs03/data/Tomo_tmp/Kai/1405_Bessy_BoneTissue/1405_set01_BlackDrum_17K_25mmPhC_0p8sec_0001a_norm/'
    
    List_names=[]

    # chose alg from 'fbp', 'gridrec'....
    print("Preparing: ")
    for i in range(number_of_files):
        
        loopnames=""
        
        if (i<10):
            loopnames=fname[:-5]+str(i)+'.edf'
            
            
        elif(i<100):
            loopnames=fname[:-6]+str(i)+'.edf'
            
        elif(i<1000):
            loopnames=fname[:-7]+str(i)+'.edf'
        
        elif(i<10000):
            loopnames=fname[:-8]+str(i)+'.edf'
        
        #print("schaust du hier:: "+loopnames)
        List_names.append(loopnames)
        assert loopnames!=""
        #print(" ")
    #print(List_names[0:5])
    print("OK. Now reading "+str(number_of_files)+" files... ")
    proj=[]
    
    for i in range(number_of_files):
        proj.append(dxchange.reader.read_edf(List_names[i], slc=None))
        #print(i)
    
    if number_recon_slices==0:
        number_recon_slices=len(proj[0][0])-StartSlice
    #plt.imshow(proj[1])
    
    print("Done. Now rearranging slices: ")    
    proj=np.asarray(proj[:])
    
    #proj_ar=np.zeros((number_of_files,proj[0].shape[1],proj[0].shape[2]))
    proj_ar=np.zeros((number_of_files,number_recon_slices,proj[0].shape[2]))
    
    for i in range(number_of_files):
        proj_ar[i]=proj[i,0,StartSlice:(number_recon_slices+StartSlice),:]
    print("Releasing memory... ")      
    del proj
    #plt.imshow(proj_ar[1])
    # Read the ESRF ID-19 raw data.
    #proj1 = dxchange.reader.read_edf(fname1, slc=None)
    #proj2 = dxchange.reader.read_edf(fname2, slc=None)
    #plt.imshow(proj_ar[:,0,:])
    #plt.show
    print("Now calculate center of rotation... ")   
    # Set data collection angles as equally spaced between 0-180 degrees.
    theta = tomopy.angles(number_of_files)
    
    # Find rotation center.
    #rot_center = tomopy.find_center(proj_ar, theta, init=1002,
                                    #ind=700, tol=0.5,mask=False,ratio=0.6)
    
    if rot_center==0:
        rot_center=math.floor(len(proj_ar[0,0])/2)

    print("Cool. Center of rotation is: ",rot_center)
    
    proj = tomopy.minus_log(proj_ar)
    
    # Reconstruct object using Gridrec algorithm.
    #rec = tomopy.recon(proj, theta, center=rot_center, algorithm='gridrec')
    print("begin reconstruction using ["+alg+ "] approach...")  
    rec = tomopy.recon(proj, theta, center=rot_center, algorithm=alg)
    
    # Mask each reconstructed slice with a circle.
    rec1 = tomopy.circ_mask(rec, axis=0, ratio=0.95)
    #plt.show(block=False)
    #plt.imshow(rec1[0])
    #plt.show
    
    # Write data as stack of TIFs.
    dxchange.write_tiff_stack(rec, savename+filename+'_recon_')    
    
    print("everything finished, find the results here: ",savename)
    
    
   
    
