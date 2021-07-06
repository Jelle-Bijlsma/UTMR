# UTMR

This is the code repository for my master thesis.
Currently it is a mess, and more information will be added.


### setup
UTMR_main.py is the main event handler. It imports:

* PyQt5
* CV2
* sys (native)
* os (native)
* numpy (native)

and `QT_Gui` which is the file 'built' in QTdesigner. It serves
as the template for the GUI.

## known issues
If you dont have 4k resolution tough luck

Menu buttons are suboptimal

video editor:
* crash when no image is loaded
* 90% of the buttons do not work
* 10% of the buttons work poorly

## could be fixed:
dicom editor:

* You can input an empty folder in dicom path and get no warning.