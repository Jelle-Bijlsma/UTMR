# UTMR

This is the code repository for my master thesis.
Currently it is a little bit less of a mess, and more information will be added.

## known issues
The readme is not up to date, documentation is a bit lacking and some parts are uncommented

### setup
UTMR_main.py is the main event handler. It imports:

(and a lot more, update this soon)
>implying
> >what
> >>stop

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


