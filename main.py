from PIL import Image
import os
import sys
import math
import numpy
import heapq
import colorsys
import argparse
import matplotlib
from datetime import datetime

# http://stackoverflow.com/questions/1408171/thread-local-storage-in-python
import threading
threadlocal = threading.local()
threadlocal.callDepth = 0

def threadlocal_var(varname, factory, *args, **kwargs):
  v = getattr(threadlocal, varname, None)
  if v is None:
    v = factory(*args, **kwargs)
    setattr(threadlocal, varname, v)
  return v
# ===============================================================

def msg(aMsg, c='green'):
    if c == 'blue':
        print "\033[1;34m%s\033[m"%(aMsg)
    elif c == 'green':
        print "\033[1;32m%s\033[m"%(aMsg)
    elif c == 'pink':
        print "\033[1;35m%s\033[m"%(aMsg)
    elif c == 'yellow':
        print "\033[1;33m%s\033[m"%(aMsg)
    else:
        print "%s"%(aMsg)

#callDepth = 0

def printExecuteTime(func):
    """
    # TODO : need to check if thread safe
    """
    def func_wrapper(*args, **argd):
        #callDepth = threadlocal_var('callDepth', initInt)
        threadlocal.callDepth += 1
        strIndent = (threadlocal.callDepth-1) * "  "
        msg( strIndent + 'Enter : %s >>>>>'%(func.__name__), c='yellow')

        t1 = datetime.now()
        ret = func(*args, **argd)
        t2 = datetime.now()
        msg( strIndent + "[%s] exec %s (sec.)"%(str(func.__name__), str(t2-t1)), c='blue')
        msg( strIndent + 'Leave : %s <<<<<'%(func.__name__), c='yellow')
        threadlocal.callDepth -= 1
        return ret
    return func_wrapper

def PILToNumpyArray(img):
    return numpy.array(img.getdata(), numpy.uint8).reshape(img.size[1], img.size[0], 3)

def dict_nlargest(d, n):
    return heapq.nlargest(n, d, key = lambda k : d[k])

@printExecuteTime
def changeColor(filename):
    img = Image.open(filename)
    ld = img.load()
    width, height = img.size
    print "Image width, height = %d x %d"%(width, height)

    def colorQuantization(c, lv):
        nb = round(255.0 / lv);
        return int(math.floor((round(c/nb) * nb)))

    indexLevel = 2
    for y in range(height):
        for x in range(width):
            r,g,b = ld[x,y]
            h,s,v = colorsys.rgb_to_hsv(r/255., g/255., b/255.)
            s = min(1, s * 1.0)
            r,g,b = colorsys.hsv_to_rgb(h, s, v)
            nr = colorQuantization(int(r * 255.9999), indexLevel)
            ng = colorQuantization(int(g * 255.9999), indexLevel)
            nb = colorQuantization(int(b * 255.9999), indexLevel)
            ld[x,y] = nr, ng, nb

    downScaleFactor = 0.08
    newImg = resizeImage(img, downScaleFactor)
    newImg.show()

@printExecuteTime
def changeColorGPU(filename):

    img = Image.open(filename)

    from PixelArtCreator import PixelArtCreator
    pac = PixelArtCreator()
    print "original WH = %d x %d"%(img.size[0], img.size[1])
    imgSize = img.size[0] * img.size[1]

    t1 = datetime.now()
    buffIn = pac.createBufferData(PixelArtCreator.Pixel, lstData=img.getdata())
    buffOut = pac.createBufferData(PixelArtCreator.Pixel, imgSize)

    scaleFactor = 0.08
    resizedW = int(round(img.size[0] * scaleFactor))
    resizedH = int(round(img.size[1] * scaleFactor))
    print "resized WH = %d x %d"%(resizedW, resizedH)
    resizeImgSize = resizedW * resizedH
    buffTemp = pac.createBufferData(PixelArtCreator.Pixel, resizeImgSize)

    t2 = datetime.now()
    msg(" Prepare buffer for GPU takes %s (sec.)"%(str(t2-t1)), c='blue')

    factorSaturation = 1.0
    pac.rgb_to_hsl_adjust_saturation_and_to_rgb((img.size[0],img.size[1],),\
                                                None, img.size[0], img.size[1],\
                                                factorSaturation, buffIn, buffOut)

    indexLevel = 2
    pac.to_indexed_color((img.size[0],img.size[1],), None,\
                         img.size[0], img.size[1], indexLevel,\
                         buffOut, buffOut)

    pac.down_scale((resizedW, resizedH,), None, img.size[0], img.size[1],\
                   resizedW, resizedH, scaleFactor, buffOut, buffTemp)

    pac.up_scale((img.size[0],img.size[1],), None, resizedW, resizedH,\
                  img.size[0], img.size[1], scaleFactor, buffTemp, buffOut)

    outRS = buffOut.reshape(img.size[1], img.size[0]).get()
    im= Image.fromarray(outRS, 'RGB')
    im.show()

    """
    lstFileName = os.path.splitext(filename)
    fname = lstFileName[0] + '_gpu_to_hsv_rgb' + lstFileName[1]
    outRS = buffOut.reshape(img.size[1], img.size[0]).get()
    im= Image.fromarray(outRS, 'RGB')
    im.show()
    im.save(fname)
    """

@printExecuteTime
def resizeImage(img, factor=1.0):
    oriW, oriH = img.size
    newW, newH = int(oriW * factor), int(oriH * factor)
    tempImg = img.resize((newW,newH), Image.NEAREST)
    newImg = tempImg.resize((oriW, oriH), Image.NEAREST)
    return newImg

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Input image")
    parser.add_argument('-i', help="Path to your image")
    args = parser.parse_args()
    if args.i != None and os.path.isfile(args.i):
        filePath = os.path.abspath(args.i)

        changeColorGPU(filePath)

        changeColor(filePath)
    else:
        print "Not correct image path !! Bye ~"