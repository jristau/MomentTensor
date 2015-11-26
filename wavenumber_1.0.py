#! /home/jristau//scratch/anaconda/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 08:50:26 2015

@author: jristau

Python script to run Bob Herrmann's code for calculating Green's functions
by wavenumber integration (Computer Programs in Seismology, Version 3.30,
http://www.eas.slu.edu/eqc/eqccps.html). It requires an input file which lists
the velocity model, name of the distance file to create, minimum, maximum, and
increment for the distance and depth. The script creates the distance file
with the appropriate format, then uses that file plus the velocity model to
calculate the Green's functions while looping over depth. The Green's functions
are moved to an appropriate directory for storage. The directory 'MainPath + 
ModelPath' must exist in order to create the appropriate directory for storing
the Green's functions.

NOTE: This script is set up for calculating Green's functions with a sampling
rate of 1.0 s (1.0 Hz). The number of points (npts) must be set up to work with
the appropriate distance to ensure that the entire record is captured. It takes
about 1/3 as long to run this script as the script using a sampling rate
of 0.5 s (2.0 Hz).
"""

import numpy as np
from os import system

# Path to where the Green's functions will be saved.
MainPath='/home/jristau/scratch/PROGRAMS.330/TEST/WAVENUMBER/'

# Read in the input file which contains all of the necessary parameters.
InFile=(np.genfromtxt('InputFile.txt',usecols=(0),dtype=['S100']))
Model=InFile[0][0]
DistFile=InFile[1][0]
DistMin=int(InFile[2][0])
DistMax=int(InFile[3][0])
DistInc=int(InFile[4][0])
DepthMin=int(InFile[5][0])
DepthMax=int(InFile[6][0])
DepthInc=int(InFile[7][0])
GreenType=InFile[8][0]

# Create the distance file using the minimum distance, maximum distance, and
# distance increment. The code to calculate the Green's functions can only
# handle one value for npts. Therefore, three distance files are created for
# the varying values of npts.
OutFile1=open(DistFile+'_Near','w')
OutFile2=open(DistFile+'_Med','w')
OutFile3=open(DistFile+'_Far','w')
for Dist in xrange(DistMin,DistMax+1,DistInc):
  dt=1.0 # set sampling rate
  T0=-5.0 # leave this values as is
  VRED=8.0 # leave this values as is
  if (Dist<450):
    DistFile1=DistFile+'_Near'
    npts=256 # set number of points to 256 for distances < 450 km
    OutFile1.write('{0:<4}  {1:>4.2f}  {2:>4}  {3:>5.1f}  {4:>4.1f}\n'\
    .format(Dist,dt,npts,T0,VRED))
  elif (Dist>=450 and Dist<=1000):
    DistFile2=DistFile+'_Med'
    npts=512 # set number of points to 512 for distances >= 450 km
    OutFile2.write('{0:<4}  {1:>4.2f}  {2:>4}  {3:>5.1f}  {4:>4.1f}\n'\
    .format(Dist,dt,npts,T0,VRED))
  elif (Dist>1000):
    DistFile3=DistFile+'_Far'
    npts=1024 # set number of points to 1024 for distances >= 450 km
    OutFile3.write('{0:<4}  {1:>4.2f}  {2:>4}  {3:>5.1f}  {4:>4.1f}\n'\
    .format(Dist,dt,npts,T0,VRED))
OutFile1.close()
OutFile2.close()
OutFile3.close()

# Create an array of depths to be looped over based on the minimum depth,
# maximum depth, and depth increment.
Depth=[]
for i in xrange(DepthMin,DepthMax+1,DepthInc):
  Depth=np.append(Depth,i)

# Loop over depth to calculate Green's functions. Green's functions are moved
# to an appropriate directory based on the velocity model and depth. This needs
# to be run for each distance file.
# E.g. for Green's functions calculated at 5 km depth using the North Island
# velocity model, a directory called 5.km is created under NORTH_ISLAND and the
# Green's functions are moved there.
for h in Depth:
  if (Model=='NorthIsland'):
    ModelPath='NORTH_ISLAND'
  elif (Model=='SouthIsland'):
    ModelPath='SOUTH_ISLAND'
  ModelDir=MainPath+ModelPath+'/'+str(int(h))+'.km'
  print ModelDir
  system ('mkdir {0}'.format(ModelDir))
  system ('hprep96 -M {0} -d {1} -EQEX -HS {2}'.format(Model,DistFile1,h))
  system ('hspec96')
  system ('hpulse96 -{0} -p -l 1 | f96tosac -G'.format(GreenType))
  system ('hprep96 -M {0} -d {1} -EQEX -HS {2}'.format(Model,DistFile2,h))
  system ('hspec96')
  system ('hpulse96 -{0} -p -l 1 | f96tosac -G'.format(GreenType))
  system ('hprep96 -M {0} -d {1} -EQEX -HS {2}'.format(Model,DistFile3,h))
  system ('hspec96')
  system ('hpulse96 -{0} -p -l 1 | f96tosac -G'.format(GreenType))
  system ('mv *.R?? {0}'.format(ModelDir))
  system ('mv *.T?? {0}'.format(ModelDir))
  system ('mv *.Z?? {0}'.format(ModelDir))
