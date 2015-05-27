import os
import numpy
from oclConfigurar import OCLConfigurar, PREFERRED_GPU
from threading import Lock

class PixelArtCreator:
    lk = Lock()
    Pixel = numpy.dtype([('blue', 'u1'), ('green', 'u1'), ('red', 'u1')])
    def __init__(self):
        self.oclConfigurar = OCLConfigurar()
        self.oclConfigurar.setupContextAndQueue(PREFERRED_GPU)
        dirPath = os.path.dirname(__file__)
        path = os.path.join(dirPath, 'pixel_art_creator.c')
        PixelArtCreator.lk.acquire()
        try:
            dicRetDS = self.oclConfigurar.setupProgramAndDataStructure(path, [dirPath], { 'Pixel' : PixelArtCreator.Pixel,})
        finally:
            PixelArtCreator.lk.release()
        self.Pixel = dicRetDS.get('Pixel', None)

        pass

    def createBufferData(self, dataStructure, nSize=0, lstData=[]):
        OCLFunc = self.oclConfigurar.createOCLArrayForInput if nSize == 0 else self.oclConfigurar.createOCLArrayEmpty
        input = lstData if nSize == 0 else nSize
        dataBuffer = OCLFunc(dataStructure, input)
        return dataBuffer

    def rgb_to_hsl_adjust_saturation_and_to_rgb(self, gWorkSize, lWorkSize, aWidth, aHeight, aSaturationWeight, aBufferIn, aBufferOut):
        evt = self.oclConfigurar.callFuncFromProgram('rgb_to_hsl_adjust_saturation_and_to_rgb', gWorkSize, lWorkSize, numpy.int32(aWidth), numpy.int32(aHeight), numpy.float32(aSaturationWeight), aBufferIn.data, aBufferOut.data)
        return evt
        pass

    def up_scale(self, gWorkSize, lWorkSize, aInWidth, aInHeight, aOutWidth, aOutHeight, aScaleFactor, aBufferIn, aBufferOut):
        evt = self.oclConfigurar.callFuncFromProgram('up_scale', gWorkSize, lWorkSize, numpy.int32(aInWidth), numpy.int32(aInHeight), numpy.int32(aOutWidth), numpy.int32(aOutHeight), numpy.float32(aScaleFactor), aBufferIn.data, aBufferOut.data)
        return evt
        pass

    def to_indexed_color(self, gWorkSize, lWorkSize, aWidth, aHeight, aLevel, aBufferIn, aBufferOut):
        evt = self.oclConfigurar.callFuncFromProgram('to_indexed_color', gWorkSize, lWorkSize, numpy.int32(aWidth), numpy.int32(aHeight), numpy.int32(aLevel), aBufferIn.data, aBufferOut.data)
        return evt
        pass

    def down_scale(self, gWorkSize, lWorkSize, aInWidth, aInHeight, aOutWidth, aOutHeight, aScaleFactor, aBufferIn, aBufferOut):
        evt = self.oclConfigurar.callFuncFromProgram('down_scale', gWorkSize, lWorkSize, numpy.int32(aInWidth), numpy.int32(aInHeight), numpy.int32(aOutWidth), numpy.int32(aOutHeight), numpy.float32(aScaleFactor), aBufferIn.data, aBufferOut.data)
        return evt
        pass

