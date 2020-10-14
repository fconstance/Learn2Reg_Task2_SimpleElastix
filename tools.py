#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  Constance Fourcade                                      #
#  Keosys Medical Imaging                                  #
#  LS2N, Ecole Centrale de Nantes                          #
#  31/10/2019 11:17                                        #
#  tools.py                                                #
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import os
import logging

import SimpleITK as sitk


LOG_FORMAT = ('%(asctime)s %(levelname) -5s %(message)s')
LOGGER = logging.getLogger(__name__)


def getSITKMetaInfo(imageSITK):
    imageMetaInfo = {'direction': imageSITK.GetDirection(),
                     'spacing': imageSITK.GetSpacing(),
                     'origin': imageSITK.GetOrigin()}
    return imageMetaInfo


def setSITKMetaInfo(imageSITK, imageMetaInfo):
    imageSITK.SetDirection(imageMetaInfo['direction'])
    imageSITK.SetSpacing(imageMetaInfo['spacing'])
    imageSITK.SetOrigin(imageMetaInfo['origin'])
    return imageSITK


def getSITKImage(loadPath):
    reader = sitk.ImageFileReader()
    reader.SetFileName(loadPath)
    image = reader.Execute()
    return image


def saveFromSITKImage(image, savePath, meta_image=None):
    os.makedirs(os.path.dirname(savePath), exist_ok=True)
    if meta_image:
        image.SetDirection(meta_image['direction'])
        image.SetSpacing(meta_image['spacing'])
        image.SetOrigin(meta_image['origin'])
    writer = sitk.ImageFileWriter()
    writer.SetFileName(savePath)
    writer.UseCompressionOn()
    writer.Execute(image)