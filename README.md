# UTMR
This is the code repository for my master thesis. The project centres around creating a GUI for interventional MR imaging during endovascular intervention.
The program is able to detect a MR-compatible guidewire in the lower aorta in realtime on a low-end PC at a framerate of 4Hz. The program is able to measure the distance from wire to artery wall along the entire guidewire, and also measure the angle of the tip with respect to the wall. In higher end machines there is a possibility of adding more computational work. Tested on a Ryzen 3700x to run at 40Hz. The program is run on a single core, CPU only. 

### setup
Program confirmed to work in Python 3.9.5 with the following dependancies:

* PyQt5                   == 5.15.4
* matplotlib              == 3.4.3
* numpy                   == 1.21.2
* opencv-python-headless  == 4.5.3.56
* pydicom                 == 2.2.1
* pyqtgraph               == 0.12.2
* scipy                   == 1.7.1

If you get this error:

_qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found. This application failed to_
_start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem._

run in terminal: `sudo apt-get install --reinstall libxcb-xinerama0`
> https://askubuntu.com/questions/308128/failed-to-load-platform-plugin-xcb-while-launching-qt5-app-on-linux-without

Next, create a folder called `./data/dicom/` which can host different folders of dicom images.
Update the template matching (might be included in final release)
1. Create templates for template matching in `./data/dicom/templates/`. They should ideally be 14x14-16x16, different sizes require tweaking of parameters (tpz) in `./functions/line_find.py`
2. Edit filename in `./classes/movieclass_2.py'
3. ???
4. Run

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
