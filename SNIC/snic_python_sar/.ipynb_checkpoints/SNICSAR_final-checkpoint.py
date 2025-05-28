#--------------------------------------------------------------
# This is a demo file intended to show the use of the SNIC algorithm
# Please compile the C files of snic.h and snic.c using:
# "python snic.c" on the command prompt prior to using this file.
#
# To see the demo use: "python SNICdemo.py" on the command prompt
#------------------------------------------------------------------

#------------------------------------------------------------------

#-------------------------------------------------------------------

import os
import rasterio
import subprocess
from PIL import Image
from skimage.io import imread,imshow
import numpy as np
from timeit import default_timer as timer
from _snic.lib import SNIC_main
from cffi import FFI


def segment(imgname,numsuperpixels,compactness,doRGBtoLAB):
	#--------------------------------------------------------------
	# read image and change image shape from (h,w,c) to (c,h,w)
	#--------------------------------------------------------------
	if isinstance(imgname, np.ndarray):
		img = imgname
	else:
		img = np.asarray(Image.open(imgname))

	#img = Image.open(imgname)
	# img = imread(imgname)
	#img = np.asarray(img)
	print(img.shape)

	dims = img.shape
	h,w,c = dims[0],dims[1],1
	if len(dims) > 1:
	#if len(dims) == 2:
		#h,w = dims
		#c = 1
		#img = img[np.newaxis, :, :] # (H,W) -> (1, H, W)
	#elif len(dims) == 3:
		#h,w,c = dims
		c = dims[2]
		img = img.transpose(2,0,1) # check this and change to np.transpose
		print(c, "channels")

	#-------------------------------------------------------------- 
	# Reshape image to a single dimensional vector
	#--------------------------------------------------------------
	img = img.reshape(-1).astype(np.double)
	labels = np.zeros((h,w), dtype = np.int32)
	numlabels = np.zeros(1,dtype = np.int32)
	#--------------------------------------------------------------
	# Prepare the pointers to pass to the C function
	#--------------------------------------------------------------
	ffibuilder = FFI()
	pinp = ffibuilder.cast("double*", ffibuilder.from_buffer(img))
	plabels = ffibuilder.cast("int*", ffibuilder.from_buffer(labels.reshape(-1)))
	pnumlabels = ffibuilder.cast("int*", ffibuilder.from_buffer(numlabels))

	
	start = timer()
	SNIC_main(pinp,w,h,c,numsuperpixels,compactness,doRGBtoLAB,plabels,pnumlabels)
	end = timer()

	#--------------------------------------------------------------
	# Collect labels
	#--------------------------------------------------------------
	print("number of superpixels: ", numlabels[0])
	print("time taken in seconds: ", end-start)

	return labels.reshape(h,w),numlabels[0]


	# lib.SNICmain.argtypes = [np.ctypeslib.ndpointer(dtype=POINTER(c_double),ndim=2)]+[c_int]*4 +[c_double,c_bool,ctypes.data_as(POINTER(c_int)),ctypes.data_as(POINTER(c_int))]


def drawBoundaries(imgname,labels,numlabels):

	if isinstance(imgname, np.ndarray):
		img = imgname
	else:
		img = Image.open(imgname)	
		img = np.array(img)
	
	print(img.shape)

	ht,wd = labels.shape

	for y in range(1,ht-1):
		for x in range(1,wd-1):
			if labels[y,x-1] != labels[y,x+1] or labels[y-1,x] != labels[y+1,x]:
				img[y,x,:] = 0

	return img
	
# Before calling this function, please compile the C code using
# "python compile.py" on the command line
def snicdemo():
	#--------------------------------------------------------------
	# Set parameters and call the C function
	#--------------------------------------------------------------
	numsuperpixels = 500
	compactness = 20.0
	doRGBtoLAB = False # only works if it is a three channel image
	# imgname = "/Users/achanta/Pictures/classics/lena.png"
	#imgname = 'bee.png'
	#imgname = ("../../Data/drone_large.png")
	#imgname = ("../../Data/kakumaa.tif")
	with rasterio.open("../../Data/Bangladeshtest.tif") as src:
		imgname = src.read()
		sar = src.read()
		sar = np.transpose(sar, (1, 2, 0))
		imgname = sar.astype(np.uint8)

	labels,numlabels = segment(imgname,numsuperpixels,compactness,doRGBtoLAB)
	print("Unique segment labels:", np.unique(labels))
	print("Total segments:", len(np.unique(labels)))
	#--------------------------------------------------------------
	# Display segmentation result
	#------------------------------------------------------------
	segimg = drawBoundaries(imgname,labels,numlabels)

	# Optional debug
	print("Segmentation result shape:", segimg.shape)

	# Image.fromarray(segimg).show()
	Image.fromarray(segimg).save("sar_snic.png")

	#Save outputs before returning
	np.save('labels.npy', labels)
	np.save('img.npy', imgname)
	print('Saved labels.npy abd img.npy for classification')
	return

snicdemo()



