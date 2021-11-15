import pydicom
from pydicom.data import get_testdata_file

scan1 = "./data/dicom/MRI_techmed/CINE_TF2D15_0313/" \
        "TEST_INTERVENTION_PACKAGE_RLI.MR.INTERVENTION_THERM.0313.0001.2021.07.27.14.57.17.728926.15673481.IMA"

scan2 = "./data/dicom/MRI_techmed/CINE_TF2D15_0315/" \
        "TEST_INTERVENTION_PACKAGE_RLI.MR.INTERVENTION_THERM.0315.0001.2021.07.27.14.57.17.728926.15678605.IMA"

scan3 = "./data/dicom/ABDOMEN_LIBRARY_20210902_132126_886000/TF2D_RT_1SLICE_NONTRIG_0031/" \
       "RLI_JB_RAM_CATH_TRACKING.MR.ABDOMEN_LIBRARY.0031.0001.2021.09.02.15.32.11.998847.16888985.IMA"
scan4 = "./data/dicom/ABDOMEN_LIBRARY_20210902_132126_886000/TF2D_RT_1SLICE_NONTRIG_0033/" \
       "RLI_JB_RAM_CATH_TRACKING.MR.ABDOMEN_LIBRARY.0033.0001.2021.09.02.15.32.11.998847.16897977.IMA"

ds = pydicom.dcmread(scan1)

print(ds)

"""" SCAN 1
 (0018, 0020) Scanning Sequence                   CS: 'GR'
(0018, 0050) Slice Thickness                     DS: '8.0'
(0018, 0080) Repetition Time                     DS: '45.0'
(0018, 0081) Echo Time                           DS: '1.26'
(0018, 1314) Flip Angle                          DS: '67.0'
(0028, 0030) Pixel Spacing                       DS: [1.25, 1.25]
(0051, 100c) [Unknown]                           LO: 'FoV 165*240'
"""


"""" SCAN 4
(0018, 0020)    Scanning Sequence:      Gradient Recalled
(0018, 0050)    Slice Thickness:        20mm
(0018, 0080)    Repetition Time:        216.84ms 
(0018, 0081)    Echo time:              1.22ms
(0018, 1314)    Flip Angle              75.0
(0028, 0030)    Pixel Spacing           1.3461538553238mm2
(0051, 100c)    Field of View           210*280mm2
"""

print("\n",ds[('0018', '0020')])
print(ds['0018', '0050'])
print(ds['0018', '0080'])
print(ds['0018', '0081'])
print(ds['0018', '1314'])
print(ds['0028', '0030'])
print(ds['0051', '100c'])