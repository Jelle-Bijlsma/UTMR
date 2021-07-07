# GUI

Gui is made in QT designer 5.
Output file is `gui_full.ui`
use terminal command 
`$ pyuic5 -x gui_full.ui -o gui_full.py

or just run ./scrip.sh
which is the command on line 6. 

## using exotic classes in Qt designer
In Designer
* create a QGraphicsView widget
(“Graphics View” under the “Display Widgets” category)
* Right-click on the QGraphicsView and select “Promote To…”.
* under “Promoted class name”, enter the class name you wish to use (“PlotWidget”, “GraphicsLayoutWidget”, etc).
* Under “Header file”, enter “pyqtgraph”.
* Click “Add”, then click “Promote”