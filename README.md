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

OPENCV:
opencv-python-headless
instead of opencv-python
If you still get this error:

_qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found. This application failed to_
_start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem._

run in terminal: `sudo apt-get install --reinstall libxcb-xinerama0`
> https://askubuntu.com/questions/308128/failed-to-load-platform-plugin-xcb-while-launching-qt5-app-on-linux-without

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

! qpix images are stored as RGB32, not as UINT8. This increases storage 4 fold.
However current RAM usage is 1.1Gb. I have not found the root of the problem yet.

sobel filter uses a shared memory array, if set to "copy" you get memory errors. 
I would expect the opposite. I dont know why this works. 

**focus**: there is a problem with keyboard input. keyPressEvent is not 
properly registered. I believe this has something to do with window focus..

If you dont have 4k resolution tough luck.

Menu buttons are suboptimal

video editor:
* 20% of the buttons do not work

## could be fixed:
dicom editor:d

* You can input an empty folder in dicom path and get no warning.