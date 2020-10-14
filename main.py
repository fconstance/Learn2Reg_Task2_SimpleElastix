#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  Constance Fourcade                                      #
#  Keosys Medical Imaging                                  #
#  LS2N, Ecole Centrale de Nantes                          #
#  15/09/2020 16:18                                        #
#  SimpleElastix.py                                        #
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


import glob
import os
import logging
from argparse import ArgumentParser
import time

from registration_functions import applyRegistration, applyTransformation

LOG_FORMAT = ('%(asctime)s %(levelname) -5s %(message)s')
LOGGER = logging.getLogger(__name__)


def runSimpleElastix(pathData):
    # Load images
    LOGGER.info('Load images')
    modes = ['training_cropped']
    for mode in modes:
        pathImages = os.path.join(pathData, mode, 'scans')
        pathSegs = os.path.join(pathData, mode, 'lungMasks')

        pathMovingImages = glob.glob(os.path.join(pathImages, 'case_*_insp.nii.gz'))
        pathFixedImages = glob.glob(os.path.join(pathImages, 'case_*_exp.nii.gz'))

        pathMovingSegs = glob.glob(os.path.join(pathSegs, 'case_*_insp.nii.gz'))
        pathFixedSegs = glob.glob(os.path.join(pathSegs, 'case_*_exp.nii.gz'))

        # Check fixed and moving images and segmentation lists are the same length
        assert (len(pathFixedImages) == len(pathMovingImages)), \
            'pathFixedImages and pathMovingImages are not the same length'
        assert (len(pathFixedImages) == len(pathFixedSegs)), \
            'pathFixedImages and pathFixedSegs are not the same length'
        assert (len(pathMovingImages) == len(pathMovingSegs)), \
            'pathMovingImages and pathMovingSegs are not the same length'

        for i in range(3):  # range(len(pathMovingImages)):
            LOGGER.info('Image ' + pathFixedImages[i][-14:-11])

            # Perform non rigid registration between exhale (fixed) and inhale images (moving)
            # Set the variables and paths
            name = 'Perform non rigid registration between exhale (fixed) and inhale images (moving)'
            regType = 'nonrigid'
            pathFixedImage = pathFixedImages[i]
            pathMovingImage = pathMovingImages[i]
            pathResultedImage = pathMovingImages[i][:-7] + '_reg_bending.nii.gz'  # _bending1
            # Registration between the cropped images
            if not os.path.isfile(pathResultedImage):
                LOGGER.info(name)
                start = time.time()
                applyRegistration(pathFixedImage, pathMovingImage, pathResultedImage, regType)
                LOGGER.info('It took {} seconds\n'.format(time.time() - start))
            # Clean the variables
            del regType, pathFixedImage, pathMovingImage, pathResultedImage, name

            # Apply non rigid registration between exhale (fixed) and inhale images (moving) to the segmentations
            # Set the variables and paths
            name = 'Apply non rigid registration between exhale (fixed) and inhale images (moving) to the segmentations'
            regType = 'nonrigid'
            pathMovingSeg = pathMovingSegs[i]
            pathResultedSeg = pathMovingSegs[i][:-7] + '_reg_bending.nii.gz'
            pathTransformParamTxt = os.path.join(pathMovingImages[i][:-7] + '_reg_bending_tmp', 'TransformParameters.0.txt')
            if not os.path.isfile(pathResultedSeg):
                LOGGER.info(name)
                start = time.time()
                applyTransformation(pathMovingSeg, pathResultedSeg, pathTransformParamTxt, mask=True)
                LOGGER.info('It took {} seconds\n'.format(time.time() - start))
            # Clean the variables
            del regType, pathMovingSeg, pathResultedSeg, \
                pathTransformParamTxt, name
    return


if __name__ == '__main__':
    pathData = 'C:\\Users\\cfo\\Documents\\Data\\learn2reg_task2'

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    parser = ArgumentParser()

    parser.add_argument("--pathData",
                        type=str,
                        dest="pathData",
                        default=pathData,
                        help="path to the data files")
    runSimpleElastix(**vars(parser.parse_args()))
