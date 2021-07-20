# UTMR

This is the code repository for my master thesis.
Currently it is a little bit less of a mess, and more information will be added.


### setup
UTMR_main.py is the main event handler. It imports:

(and a lot more, update this soon)

* PyQt5
* CV2
* sys (native)
* os (native)
* numpy (native)
* functions.auxillary & functions.classes

and `QT_Gui` which is the file 'built' in QTdesigner. It serves
as the template for the GUI.

`auxillary` and `classes` are used functions and classes which I dont want
to clog up the main script. 

### how does it work?
PyQt creates the event handler. For the video editor, the class `MovieClass` handles
the movie, it contains attributes such as
* current frame
* max frames
* video editing parameters such as brightness
* framelist

where `framelist` is a list of class instances of the `FrameClass` which 
contain the frames, in numpy format and qpix (for displaying). and have methods
such as `change_brightness`.

`MovieClass` also has methods such as `next_frame` and `return_frame` which can be 
called from the event handler to iterate through the `framelist`


## known issues
!! Using pycharm, whitin the virtual environment, the folder "./lib/python3.8/cv2/qt"
has to be renamed. I am not quite sure why, however this works. It seems  something breaks when using QT5
in conjuction with CV2.

If you dont have 4k resolution tough luck.

Menu buttons are suboptimal

video editor:
* 20% of the buttons do not work

## could be fixed:
dicom editor:d

* You can input an empty folder in dicom path and get no warning.