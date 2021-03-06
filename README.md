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

Tested to work on Ubuntu 20.04 and 21.4 only.

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


## How does it work?
The GUI is event driven. In QT terms, this means that specific actions can emit `signals`. These signals can be linked 
to specific actions. For example, pressing the **play** button will trigger a *button_press* event, which is linked
to the **Play** function. This will then start a timer, which will emit a signal every X milliseconds. This signal is 
picked up by the **next_frame** function, which will trigger a frame update, and redo all the image processing on
the newly acquired image. All the linking and connecting of signals and receiving functions, or `slots` as they are 
called, happens in the *\_\_init__* part of `UTMR_main2.py`.

In the main file, instances from the `./classes/` folder are created. `class_addition.py` extends current class
capabilites. `class_extra` contains the **SliderClass**, which is used to tie together parameter acquisition from the 
GUI to the main program. It also hosts classes that are used for multithreading. `movieclass_2.py` has one instance 
and is responsible for doing all the image processing. (All functions/classes etc. have extensive comments to describe
their functions and workings.)

In the folder `./functions/` all the additional functions are placed, and they are categorized according to their
purpose (all filtering related functions are found in `filter.py` for example). 

###additional
get qt-designer!
```sudo apt-get install qtcreator pyqt5-dev-tools```





