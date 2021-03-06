import cv2
from PyQt5 import QtWidgets
import QT_Gui.image_labeler
import sys

from functions.process import change_qpix as cqpx
from classes.image_label_classes import PointWindow as PointWindow
from classes.image_label_classes import ScrollClass as ScrollClass
import functions.labeler_custom_event as custom

"""
Image labeler is a program used to determine the true location of magnetic marker points in a list of images. 
CTRL + scroll is zoom
CTRL + right/left arrow key is goto next/previous picture. 
Left click in the picture to select a point.
left click the point in the pointwindow and press delete to delete the selected point. 

The selected keypoints can be saved as:
[[(x01,y01,b01) , (x02,y02,b02) .... ]
[(x11,y11,b11) , (x12,y12,b12) ...]
...
]]

first index is the frame, second index is the point. b= brightness value.
The points are ordered in increasing y value.
"""

class MainWindowz(QtWidgets.QMainWindow, QT_Gui.image_labeler.Ui_MainWindow):
    def __init__(self, form):
        # form should be instance of QMainWindow
        super().__init__()
        self.setupUi(form)
        self.image_list = []

        image = cv2.imread("./data/png/mri31/RLI_JB_RAM_CATH_TRACKING.MR.ABDOMEN_LIBRARY."
                           "0031.0041.2021.09.02.15.32.11.998847.16889705.IMA.png")

        # Scrollclass is responsible for allowing image zooming & scrolling
        self.ScrCls = ScrollClass(image, self.label, self.scrollArea.horizontalScrollBar(),
                                  self.scrollArea.verticalScrollBar())
        # Creates the PointWindow, which hosts all the selected points for each image.
        self.create_ting(MainWindow, self.ScrCls)

        self.actionLoad_New.triggered.connect(lambda: self.PtWin.loadem(production=True))
        self.actionSave_Keypoints.triggered.connect(self.PtWin.savepoints)
        self.actionLoad_Keypoints.triggered.connect(self.PtWin.loadpoints)

        self.image = cqpx(image)
        self.label.setPixmap(self.image)
        self.label.setMouseTracking(True)

        # scroll override
        self.scrollArea.keyPressEvent = lambda event: custom.keyPressEvent(self, event)
        self.scrollArea.keyReleaseEvent = lambda event: custom.keyReleaseEvent(self, event)
        self.scrollArea.wheelEvent = lambda event: custom.wheelEvent(self, event)

        # mouse press override
        self.label.mousePressEvent = lambda event: custom.mousePressEvent(self,event)
        self.label.mouseMoveEvent = lambda event: custom.mouseMoveEvent(self,event)

        a_warning = QtWidgets.QMessageBox()
        a_warning.setText("The coordinate transform fails if there are purple boundaries. \n"
                          "Please zoom in until no purple is visible")
        a_warning.exec()


    def create_ting(self, mainwin, scrollclass):
        """"This function creates the secondary window, but only the frame. The pointwindow
        Is responsible for filling it in. """
        w = mainwin.width()
        self.Kp_Window = QtWidgets.QWidget()
        self.Kp_Window.show()
        self.Kp_Window.move(w + 200, 125)  # offset so they dont overlap.
        # 'ui' is the class which can interact.
        self.PtWin = PointWindow(self.Kp_Window, scrollclass, self.label_2)  # label_2 is from the GUI


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    sshFile = "./QT_Gui/Dtor.qss"
    # its not dtor. It is from https://github.com/GTRONICK/QSS/blob/master/Aqua.qss
    with open(sshFile, 'r') as fh:
        app.setStyleSheet(fh.read())
    MainWindow = QtWidgets.QMainWindow()
    ui = MainWindowz(MainWindow)
    MainWindow.show()
    #ui.create_ting(MainWindow)
    sys.exit(app.exec_())
