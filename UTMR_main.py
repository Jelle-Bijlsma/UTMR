import sys
import os
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap

from GUI_teach import gui3


# date 22-05 21:19


class Build_Up(gui3.Ui_MainWindow):
    def __init__(self):
        super().__init__()

    # variablesq

    def setupUi2(self):
        self.stackedWidget.setCurrentIndex(0)
        self.label_logo_uni.setPixmap((QtGui.QPixmap("./UTlogo.png")))
        self.label_logo_uni.setScaledContents(True)
        self.slider_brightness.setMinimum(-255)
        self.slider_brightness.setMaximum(255)
        self.slider_brightness.setValue(0)
        self.slider_brightness.valueChanged.connect(self.sliderchange)


        # initialize image
        self.mr_image.setPixmap(QtGui.QPixmap("./dicom/png/IM_0011.png"))
        self.mr_image.setScaledContents(True)

        # button return
        self.button_reset.clicked.connect(self.resetB)
        self.button_play.clicked.connect(self.playB)
        self.button_pause.clicked.connect(self.pauseB)

        # video
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.base_image = cv2.imread("./dicom/png/IM_0011.png", 0)
        self.initial_figure = cv2.imread("./dicom/png/IM_0011.png", 0)

        # menu
        self.actionMain.triggered.connect(lambda: self.gotopage(0))
        self.actionImage_processing.triggered.connect(lambda: self.gotopage(1))
        self.actionDicom_Edit.triggered.connect(lambda: self.gotopage(2))

        self.button_2dicom.clicked.connect(lambda: self.gotopage(2))
        self.button_2editor.clicked.connect(lambda: self.gotopage(1))

        self.pb_convert.clicked.connect(self.convert)
        self.pb_browse_save.clicked.connect(lambda: self.filebrowse(1))
        self.pb_browse_dcm.clicked.connect(lambda: self.filebrowse(2))

    def gotopage(self, pagenum):
        self.stackedWidget.setCurrentIndex(pagenum)

    def filebrowse(self, dcmsave):
        path = str(QtWidgets.QFileDialog.getExistingDirectory(MainWindow, 'select folder'))
        if dcmsave == 1:
            self.lineEdit_save.setText(path)
            filelist = os.listdir(path)
            filelist.sort()
            self.save_contains.clear()
            for element in filelist:
                self.save_contains.append(element)
        else:
            self.lineEdit_dicom.setText(path)
            filelist = os.listdir(path)
            filelist.sort()
            self.txtbox_dcmcont.clear()
            for element in filelist:
                self.txtbox_dcmcont.append(element)

    def getallfiles(self,path):
        filelist = os.listdir(path)
        filelist.sort()
        img_array= []
        for element in filelist:
            #print(element)
            fp = path + element
            img = cv2.imread(fp)
            h, w, l = img.shape
            # notice the reversal of order ...
            size = (w, h)
            img_array.append(img)
        return

    def convert(self):
        fps = self.spinbox_fps.value()
        if fps == 0:
            pass
        savepath = self.lineEdit_save.text()
        dcmpath = self.lineEdit_dicom.text()

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
        rtrn_img = self.brightness_check()
        self.update_figure(rtrn_img)

    # buttons
    def playB(self):
        self.vc = cv2.VideoCapture("video.avi")
        self.timer.start(100)

    def pauseB(self):
        self.centralwidget2 = QtWidgets.QWidget()
        # self.centralwidget2.setObjectName("centralwidget2")
        # self.mr_image2 = QtWidgets.QLabel(self.centralwidget2)
        # self.mr_image2.setGeometry(QtCore.QRect(130, 100, 591, 731))
        # MainWindow.setCentralWidget(self.centralwidget2)
        # time.sleep(3)
        # MainWindow.setCentralWidget(self.centralwidget)

    def resetB(self):
        self.slider_brightness.setValue(0)
        self.update_figure(self.initial_figure)


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
