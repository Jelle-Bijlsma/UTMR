import sys
import os
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap

from QT_Gui import gui_full

# used only once


# why did i write this function if it is not used?
# too bad!

import functions.auxillary

# the whole thing is just existing within this class.


class Build_Up(gui_full.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # video
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.base_image = cv2.imread("./data/png/IM_0011.png", 0)
        self.initial_figure = cv2.imread("./data/png/IM_0011.png", 0)

        self.a = PopupInput()
        self.b = PopupWaring()

    # variablesq

    def setupUi2(self):
        # this is setting up the GUI more. I couldnt find't / couldn't be bothetered to set these options within
        # QT designer.
        self.stackedWidget.setCurrentIndex(0)
        self.label_logo_uni.setPixmap((QtGui.QPixmap("./QT_Gui/images/UTlogo.png")))
        self.label_logo_uni.setScaledContents(True)
        self.slider_brightness.setMinimum(-255)
        self.slider_brightness.setMaximum(255)
        self.slider_brightness.setValue(0)
        self.slider_brightness.valueChanged.connect(self.sliderchange)

        # a lot of it is linking, using the .connect() option. Here an 'action' gets linked to a function,
        # such as 'valueChanged' of the brightness slider to the function 'sliderchange'

        # initialize image
        self.mr_image.setPixmap(QtGui.QPixmap("./data/png/IM_0011.png"))
        self.mr_image.setScaledContents(True)

        # button return
        self.button_reset.clicked.connect(self.resetB)
        self.button_play.clicked.connect(self.playB)
        self.button_pause.clicked.connect(self.pauseB)



        # menu buttons
        self.actionMain.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.actionImage_processing.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.actionDicom_Edit.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(2))

        self.button_2dicom.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.button_2editor.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

        self.pb_convert.clicked.connect(self.convert)
        #self.pb_browse_save.clicked.connect(self.filebrowse)
        self.pb_browse_dcm.clicked.connect(self.filebrowse)

    def filebrowse(self):
        # this could definitely be done different, too bad!
        #
        path = str(QtWidgets.QFileDialog.getExistingDirectory(MainWindow, 'select folder'))
        try:
            self.lineEdit_dicom.setText(path)
            filelist = os.listdir(path)
            filelist.sort()
            self.txtbox_dcmcont.clear()
            for element in filelist:
                self.txtbox_dcmcont.append(element)
        except:
            self.txtbox_cmd.append("folder selection aborted")

    def convert(self):
        self.txtbox_cmd.append("starting conversion")
        fps = self.spinbox_fps.value()
        project_name = self.lineEdit_save.text()
        dcmpath = self.lineEdit_dicom.text()
        if fps <= 0:
            msg = QtWidgets.QMessageBox()
            msg.setText("FPS Cant be zero!")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            x = msg.exec_()
            self.txtbox_cmd.append("FPS cant be set, exiting")
            return
        self.txtbox_cmd.append("FPS =" + str(self.spinbox_fps.value()))

        if project_name == "" or dcmpath == "":
            msg = QtWidgets.QMessageBox()
            msg.setText("Project name & dcm folder cant be empty")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            x = msg.exec_()
            self.txtbox_cmd.append("Empty project name or dcm folder, exiting")
            return
        else:
            projectpath = "./data/png/" + project_name
            if os.path.exists(projectpath):
                msg = QtWidgets.QMessageBox()
                msg.setText("possibility of overwrite, continue?")
                msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                x = msg.exec_()
                bresult = (msg.clickedButton().text())
                if bresult != "&Yes":
                    self.txtbox_cmd.append("overwrite detected, exiting")
                    return
            else:
                os.mkdir(projectpath)

        # here we start calling functions

        filelist = os.listdir(dcmpath)
        filelist.sort()
        a = functions.auxillary.dicom2png(filelist,dcmpath +"/",project_name)
        if a < 2:
            self.txtbox_cmd.append("Less than two images processed")
            self.txtbox_cmd.append("Are you sure the right folder is selected?")
            self.txtbox_cmd.append("Exiting")
            return
        #

        functions.auxillary.png2avi(projectpath + "/",fps)



    def nextFrameSlot(self):
        rval, frame = self.vc.read()
        # if there are no more frames,movie is stopped.
        if not rval:
            self.pauseB()
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        frame = frame[58:428, 143:513]
        self.base_image = frame
        frame = self.brightness_check(frame)
        self.update_figure(frame)

    # edits brightness based on current slider position
    def brightness_check(self, img=None):
        if img is None:
            img = self.base_image

        b_val = self.slider_brightness.value()
        b_val = int(b_val)  # cast to make sure

        if b_val > 0:
            newim = np.where((255 - img) < b_val, 255, img + b_val)
        else:
            newim = np.where((img + b_val) < 0, 0, img + b_val)
            newim = newim.astype('uint8')
        return newim

    def update_figure(self, img):
        # slice and dice
        w, h = img.shape
        qim = QtGui.QImage(img.data.tobytes(), h, w, h, QtGui.QImage.Format_Indexed8)
        pmap = QPixmap.fromImage(qim)
        self.mr_image.setPixmap(pmap)

    def sliderchange(self):
        # this is bad and should be edited
        rtrn_img = self.brightness_check()
        self.update_figure(rtrn_img)

    # buttons
    def playB(self):
        # the play button in the videoplayer
        # works sort of
        self.vc = cv2.VideoCapture("./data/avi/video.avi")
        self.timer.start(100)

    def pauseB(self):
        # pause button, doesnt work!
        self.centralwidget2 = QtWidgets.QWidget()
        # self.centralwidget2.setObjectName("centralwidget2")
        # self.mr_image2 = QtWidgets.QLabel(self.centralwidget2)
        # self.mr_image2.setGeometry(QtCore.QRect(130, 100, 591, 731))
        # MainWindow.setCentralWidget(self.centralwidget2)
        # time.sleep(3)
        # MainWindow.setCentralWidget(self.centralwidget)

    def resetB(self):
        # yeaah doesnt work
        self.slider_brightness.setValue(0)
        self.update_figure(self.initial_figure)


class PopupInput(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

    def showdialog(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'input dialog', 'Is this ok?')
        if ok:
            return text
        else:
            return False

class PopupWaring(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("not that word")
        QtWidgets.QPushButton("a button")

    def showme(self):
        self.show()

if __name__ == "__main__":
    # chad no argument vs virgin sys.argv
    app = QtWidgets.QApplication([])
    MainWindow = QtWidgets.QMainWindow()
    # class creation
    ui = Build_Up()
    # create an instance of Ui_MainWindow
    # fill in the instance into the setup function ?
    ui.setupUi(MainWindow)
    ui.setupUi2()
    MainWindow.show()
    sys.exit(app.exec_())
