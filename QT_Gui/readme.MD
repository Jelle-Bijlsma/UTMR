# GUI

Gui is made in QT designer 5.

To get QT-designer, simply enter into a terminal:

`sudo apt-get install qtcreator`

This adds **Qt Designer** to Launchpad and allows for easy GUI editing.

Output file is `gui_full.ui`

Use terminal command:

`$ pyuic5 -x gui_full.ui -o gui_full.py`

To convert from *.ui* to *.py*

## Tips
### Automatically check for updates:
Set `script.sh` to execute as program and run without terminal. This will check the *.ui* file every 10 seconds and monitor if it has been updated.
If it has, it will run the conversion command, and recheck every 10 seconds. Due to it being written in bash, it is not resource intensive and put little to no additional stress on the machine.


### Using exotic classes in Qt designer
In Designer
* create a QGraphicsView widget
(“Graphics View” under the “Display Widgets” category)
* Right-click on the QGraphicsView and select “Promote To…”.
* under “Promoted class name”, enter the class name you wish to use (“PlotWidget”, “GraphicsLayoutWidget”, etc).
* Under “Header file”, enter “pyqtgraph”.
* Click “Add”, then click “Promote”
