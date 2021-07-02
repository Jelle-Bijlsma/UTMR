from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QColor
import sys
from PyQt5.QtWidgets import QMessageBox
import cv2
import numpy as np
import gui1

class buildup(gui1.Ui_MainWindow):
    def __init__(self):
        super().__init__()

    def setupUi2(self):
        self.slider_brightness.setMinimum(-255)
        self.slider_brightness.setMaximum(255)
        self.slider_brightness.setValue(0)
        self.slider_brightness.valueChanged.connect(self.sliderchange)

        #initialize image
        self.mr_image.setPixmap(QtGui.QPixmap("./dicom/png/IM_0011.png"))
        self.mr_image.setScaledContents(True)

        #button return
        self.button_reset.clicked.connect(self.resetB)
        self.button_play.clicked.connect(self.playB)
        self.button_pause.clicked.connect(self.pauseB)

        #video
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)


    def nextFrameSlot(self):
        rval, frame = self.vc.read()
        if not rval:
            self.pauseB()

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        print(frame.dtype)
        print(type(frame))
        print(type(frame))
        print("max = ", np.max(frame), "min =", np.min(frame))
        print(frame.shape)
        w, h = frame.shape
        valz = self.slider_brightness.value()
        eyo = self.brightness_check(valz, frame)
        # qim = QtGui.QImage(frame.data.tobytes(), h, w, h, QtGui.QImage.Format_Indexed8)
        # pixmap = QPixmap.fromImage(qim)
        self.mr_image.setPixmap(eyo)
        self.active_figure = eyo

# variables
    active_figure = cv2.imread("./dicom/png/IM_0011.png",0)

    def playB(self):
        self.vc = cv2.VideoCapture("video.avi")
        self.timer.start(100)

    def pauseB(self):
        self.timer.stop()
        self.vc.release()

    def resetB(self):
        self.slider_brightness.setValue(0)
        self.sliderchange()

    def sliderchange(self):
        size = self.slider_brightness.value()
        rtrn_img = self.brightness_check(size)
        self.mr_image.setPixmap(rtrn_img)

    def brightness_check(self,size,img=active_figure):
        size = int(size)

        if size > 0:
            newim = np.where((255-img)< size,255,img+size)
        else:
            newim= np.where((img+size)<0,0,img+size)
            newim=newim.astype('uint8')

        img = newim[58:428,143:513]

        w,h = img.shape
        print(type(img))
        print(img.shape)
        qim = QtGui.QImage(img.data.tobytes(),h,w,h,QtGui.QImage.Format_Indexed8)

        return QPixmap.fromImage(qim)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = buildup()
    # create an instance of Ui_MainWindow
    # fill in the instance into the setup function ?
    ui.setupUi(MainWindow)
    ui.setupUi2()
    MainWindow.show()
    sys.exit(app.exec_())

