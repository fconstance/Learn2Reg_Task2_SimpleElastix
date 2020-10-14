#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  Constance Fourcade                                      #
#  Keosys Medical Imaging                                  #
#  LS2N, Ecole Centrale de Nantes                          #
#  22/09/2020 11:20                                        #
#  registration_functions.py                               #
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


import logging
import os
import SimpleITK as sitk


from tools import getSITKImage, getSITKMetaInfo, saveFromSITKImage

LOGGER = logging.getLogger(__name__)


def registration(fixedImage, movingImage, pathElastixFiles, regType,
                 multiModalities=False, transformParmeterFile=None, inverseTransform=False, multiMetrics='bending'):
    """
    Register a moving image to a fixed one
    :param fixedImage:
    :param movingImage:
    :param pathElastixFiles:
    :param regType: 'Rigid', 'Affine' or 'Nonrigid'
    :param multiModalities:
    :param transformParmeterFile: If not None, set initial transform. txt Transformation file produced by SimpleElastix
    :param inverseTransform:
    :return: resultImage: Registered moving image
    """
    # Initialize the filter
    elastixImageFilter = sitk.ElastixImageFilter()

    elastixImageFilter.SetFixedImage(sitk.Cast(fixedImage, sitk.sitkFloat32))
    elastixImageFilter.SetMovingImage(sitk.Cast(movingImage, sitk.sitkFloat32))

    # Outputs (the output of the registration without table is written in a tmp folder)
    elastixImageFilter.SetOutputDirectory(pathElastixFiles)
    elastixImageFilter.SetLogToFile(True)
    elastixImageFilter.SetLogToConsole(False)

    # If given, set the transformed parameter map
    if transformParmeterFile:
        elastixImageFilter.SetInitialTransformParameterFileName(transformParmeterFile)

    # Defined the parameter map
    pathParameterMap = []
    parameterMapVector = sitk.VectorOfParameterMap()
    if not isinstance(regType, list):
        regType = [regType]
    for i, regType in enumerate(regType):
        # Personalized parameter map
        pathParameterMap.append(
            os.path.join('..', 'RegistrationParameters', 'parameters{}.txt').format(regType.title()))
    for p in pathParameterMap:
        paramMap = elastixImageFilter.ReadParameterFile(p)
        # Adapt some parameters in the parameters map
        shape = fixedImage.GetSize()[0] * fixedImage.GetSize()[1] * fixedImage.GetSize()[2]
        paramMap['NumberOfSpatialSamples'] = [str(int(0.0005 * shape))]  # TODO: adapt the %
        print('NumberOfSpatialSamples:  ' + str(int(0.0005 * shape)))
        if multiMetrics:
            paramMap['Registration'] = ['MultiMetricMultiResolutionRegistration']
            paramMap['Metric0Weight'] = ['1.0']
            paramMap['Metric1Weight'] = ['1.0']
            if multiModalities:
                paramMap['Metric'] = ['AdvancedMattesMutualInformation', 'TransformBendingEnergyPenalty']
            else:
                paramMap['Metric'] = ['AdvancedNormalizedCorrelation', 'TransformBendingEnergyPenalty']
            if inverseTransform:
                paramMap['Metric'] = ['DisplacementMagnitudePenalty', 'TransformBendingEnergyPenalty']
        else:
            if multiModalities:
                paramMap['Metric'] = ['AdvancedMattesMutualInformation']
            else:
                paramMap['Metric'] = ['AdvancedNormalizedCorrelation']

            if inverseTransform:
                paramMap['Metric'] = ['DisplacementMagnitudePenalty']
        parameterMapVector.append(paramMap)
    elastixImageFilter.SetParameterMap(parameterMapVector)

    # Execute Elastix and results
    resultImage = sitk.Cast(elastixImageFilter.Execute(), sitk.sitkFloat32)

    return resultImage


def applyTransformation(pathMovingImage, pathResultedImage, transformParmeterFile, mask=False):
    """
    Apply a transformation to an image
    :param pathMovingImage:
    :param pathResultedImage:
    :param transformParmeterFile: txt Transformation file produced by SimpleElastix
    :param mask: If True, the interpolation order is 0 and the image is saved in UInt32
    :return: Transformed moving image
    """
    # Set the files
    os.makedirs(os.path.dirname(pathResultedImage), exist_ok=True)
    pathTransformixFiles = pathResultedImage[:-7] + '_tmp'
    os.makedirs(pathTransformixFiles, exist_ok=True)

    # Define the transformix object
    transformixImageFilter = sitk.TransformixImageFilter()
    transformixImageFilter.SetMovingImage(getSITKImage(pathMovingImage))
    transformixImageFilter.SetLogToConsole(False)
    transformixImageFilter.SetLogToFile(True)
    transformixImageFilter.SetOutputDirectory(pathTransformixFiles)
    # if 'nonrigid' in pathResultedImage:
    transformixImageFilter.ComputeDeterminantOfSpatialJacobianOn()
    transformixImageFilter.ComputeDeformationFieldOn()

    # Load the transform parameter map
    parameterTransformMapVector = sitk.VectorOfParameterMap()
    if not isinstance(transformParmeterFile, list):
        pathTransformParameters = [transformParmeterFile]
    for p in pathTransformParameters:
        if mask:
            transfParamInv = transformixImageFilter.ReadParameterFile(p)
            transfParamInv['FinalBSplineInterpolationOrder'] = ['0']
            parameterTransformMapVector.append(transfParamInv)
        else:
            parameterTransformMapVector.append(transformixImageFilter.ReadParameterFile(p))
    transformixImageFilter.SetTransformParameterMap(parameterTransformMapVector)

    # Execute transformix
    resultImage = transformixImageFilter.Execute()

    # if 'nonrigid' in pathResultedImage:
    # Load and save the deformation field
    deformationField = transformixImageFilter.GetDeformationField()
    saveFromSITKImage(deformationField, os.path.join(pathTransformixFiles, 'deformationField.mhd'))

    # Save the resulting image
    if mask:
        resultImage = sitk.Cast(resultImage, sitk.sitkUInt32)
    saveFromSITKImage(resultImage, pathResultedImage)
    return resultImage


def applyRegistration(pathFixedImage, pathMovingImage, pathResultedImage, regType,
                      multiModalities=False, transformParmeterFile=False):
    """
    Apply a registration from a moving image to a fixed image
    :param pathFixedImage:
    :param pathMovingImage:
    :param pathResultedImage:
    :param regType: 'Rigid', 'Affine' or 'Nonrigid'
    :param multiModalities:
    :param transformParmeterFile: If not None, set initial transform. txt Transformation file produced by SimpleElastix
    :return: Registered sitk image resultImage
    """
    # Load the images
    fixedImage = getSITKImage(pathFixedImage)
    movingImage = getSITKImage(pathMovingImage)

    # Perform the registration
    pathElastixFiles = pathResultedImage[:-7] + '_tmp'
    os.makedirs(pathElastixFiles, exist_ok=True)
    resultImage = registration(fixedImage, movingImage, pathElastixFiles, regType, multiModalities,
                               transformParmeterFile)

    # Write results
    saveFromSITKImage(resultImage, pathResultedImage, getSITKMetaInfo(fixedImage))

    if regType == 'nonrigid':
        # Compute the deformation field and the det of the Jacobian
        transformParmeterFile = os.path.join(pathElastixFiles, 'TransformParameters.0.txt')
        applyTransformation(pathMovingImage, pathResultedImage, transformParmeterFile)
    return resultImage
