# Learn2Reg_Task2_SimpleElastix

This code is made available in the context of the Learn2Reg 2020 challenge (https://learn2reg.grand-challenge.org/).
It corresponds to an Elastix-based [1] registration implementation for the second task. This task consists of intrasubject 3D HRCT inhale/exhale thorax images registration.

The corresponding dataset is publicaly available and downloadable: https://zenodo.org/record/3835682#.X4Vu5O06-Un.

### Requirements
Make sure that following python librarie is installed:
- SimpleITK with the SimpleElastix module (see https://simpleelastix.readthedocs.io/GettingStarted.html for introduction and installation)

### Running
To lauch the code, make sure the varaible `pathData` from `SimpleElastix.py` is adapted to the actual path of the downloaded data.
Then, launch `SimpleElastix.py`.

### Questions
If you have a question about the code, don't hesitate to raise an issue in the corresponding section. 

#### Author: Constance Fourcade


[1] Klein, S., Staring, M., Murphy, K., Viergever, M. a., & Pluim, J. (2010). elastix: A Toolbox for Intensity-Based Medical Image Registration. IEEE Transactions on Medical Imaging, 29(1), 196–205. https://doi.org/10.1109/TMI.2009.2035616
