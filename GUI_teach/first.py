# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'first.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QColor
import sys
from PyQt5.QtWidgets import QMessageBox
import cv2
import numpy as np

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600, 1200)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

# vertical slider
        self.verticalSlider = QtWidgets.QSlider(self.centralwidget)
        self.verticalSlider.setGeometry(QtCore.QRect(480, 190, 16, 191))
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setObjectName("verticalSlider")
        self.verticalSlider.setMinimum(-255)
        self.verticalSlider.setMaximum(255)
        self.verticalSlider.setValue(0)
        self.verticalSlider.valueChanged.connect(self.sliderchange)

# scroll bar
        self.horizontalScrollBar = QtWidgets.QScrollBar(self.centralwidget)
        self.horizontalScrollBar.setGeometry(QtCore.QRect(180, 430, 160, 16))
        self.horizontalScrollBar.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalScrollBar.setObjectName("horizontalScrollBar")

# checkbox
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(370, 430, 92, 23))
        self.checkBox.setObjectName("checkBox")

        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(130, 160, 301, 231))
        self.graphicsView.setObjectName("graphicsView")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(460, 390, 67, 17))
        self.label.setObjectName("label")

        self.label1 = QtWidgets.QLabel(self.centralwidget)
        self.label1.setGeometry(QtCore.QRect(220, 90, 67, 17))
        self.label1.setObjectName("label1")

# image to the right
        self.label2 = QtWidgets.QLabel(self.centralwidget)
        # x, y, size
        self.label2.setGeometry(QtCore.QRect(520, 170, 500, 500))
        self.label2.setObjectName("label2")
        self.label2.setPixmap(QtGui.QPixmap("../dicom/png/IM_0011.png"))
        self.label2.setScaledContents(True)

# trigger popup
        self.button1 = QtWidgets.QPushButton(self.centralwidget)
        self.button1.setGeometry(QtCore.QRect(470, 90, 89, 25))
        self.button1.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.button1.setObjectName("button1")
        self.button1.clicked.connect(self.show_popup)


        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menuBar.setObjectName("menuBar")

        self.menuFunctions = QtWidgets.QMenu(self.menuBar)
        self.menuFunctions.setObjectName("menuFunctions")
        self.menuEdits = QtWidgets.QMenu(self.menuBar)
        self.menuEdits.setObjectName("menuEdits")
        MainWindow.setMenuBar(self.menuBar)

        self.actionVideo_Maker = QtWidgets.QAction(MainWindow)
        self.actionVideo_Maker.setObjectName("actionVideo_Maker")

        self.actionVideo_Viewer = QtWidgets.QAction(MainWindow)
        self.actionVideo_Viewer.setObjectName("actionVideo_Viewer")

        self.actionVideo_Loader = QtWidgets.QAction(MainWindow)
        self.actionVideo_Loader.setObjectName("actionVideo_Loader")

        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")

        self.actionCopy = QtWidgets.QAction(MainWindow)
        self.actionCopy.setObjectName("actionCopy")

        self.actionPaste = QtWidgets.QAction(MainWindow)
        self.actionPaste.setObjectName("actionPaste")

        self.menuFunctions.addAction(self.actionVideo_Maker)
        self.menuFunctions.addAction(self.actionVideo_Viewer)
        self.menuFunctions.addAction(self.actionVideo_Loader)

        self.menuEdits.addAction(self.actionSave)
        self.menuEdits.addAction(self.actionCopy)
        self.menuEdits.addAction(self.actionPaste)

        self.menuBar.addAction(self.menuFunctions.menuAction())
        self.menuBar.addAction(self.menuEdits.menuAction())

        self.actionPaste.triggered.connect(self.refreshing)
        self.actionSave.triggered.connect(lambda: self.bitte("u pressed save"))
        self.actionCopy.triggered.connect(lambda: self.bitte("u pressed copy"))
        self.actionVideo_Loader.triggered.connect(lambda: self.bitte("u pressed vid loader"))


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  THE INIT STOPS HERE
    def bitte(self,text):
        self.label1.setText(text)
        self.label1.adjustSize()

    def refreshing(self):
        active_figure = cv2.imread("../dicom/png/IM_0011.png", 0)
        w, h = active_figure.shape
        qim = QtGui.QImage(active_figure.data, h, w, h, QtGui.QImage.Format_Indexed8)
        self.label2.setPixmap(QPixmap.fromImage(qim))
        self.verticalSlider.setValue(0)


    def sliderchange(self):
        size = self.verticalSlider.value()
        size2 = int(size/10)
        self.label1.setFont(QtGui.QFont("Arial",size2))
        self.label1.adjustSize()
        rtrn_img = self.brightness_check(size)
        self.label2.setPixmap(rtrn_img)

    # popup box
    def show_popup(self):
        msg = QMessageBox()
        msg.setWindowTitle("A fkn box")
        msg.setText("this is a text")
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Cancel|QMessageBox.Retry)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.setInformativeText("hehehehe")

        msg.setDetailedText("hahahhahahahahhahahahahahha")
        msg.buttonClicked.connect(self.popoep)

        x = msg.exec_()

    # check which value was passed by the popup
    def popoep(self,i):
        # i being a value parsed
        print(i.text())

    # some weird multi text tingg
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.checkBox.setText(_translate("MainWindow", "Play"))
        self.label.setText(_translate("MainWindow", "Brightness"))
        self.button1.setText(_translate("MainWindow", "Reset"))
        self.label1.setText(_translate("MainWindow", "TextLabel"))
        self.menuFunctions.setTitle(_translate("MainWindow", "Functions"))
        self.menuEdits.setTitle(_translate("MainWindow", "Edits"))
        self.actionVideo_Maker.setText(_translate("MainWindow", "Video Maker"))
        self.actionVideo_Viewer.setText(_translate("MainWindow", "Video Viewer"))
        self.actionVideo_Loader.setText(_translate("MainWindow", "Video Loader"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setStatusTip(_translate("MainWindow", "This is save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionCopy.setText(_translate("MainWindow", "Copy"))
        self.actionCopy.setStatusTip(_translate("MainWindow", "This is copy"))
        self.actionPaste.setText(_translate("MainWindow", "Paste"))

    active_figure = cv2.imread("../dicom/png/IM_0011.png",0)

    # CV
    def brightness_check(self,size):
        # hv = cv2.cvtColor(self.active_figure, cv2.COLOR_BGR2HSV)
        # h,s, v = cv2.split(hv)
        # s = size
        # final_hsv = cv2.merge(h,s)
        # img = cv2.cvtColor(final_hsv,cv2.COLOR_HSV2BGR)

        img = self.active_figure
        size = int(size)
        print(size)

        if size > 0:
            newim = np.where((255-img)< size,255,img+size)
        else:
            newim= np.where((img+size)<0,0,img+size)
            newim=newim.astype('uint8')
            print(newim.dtype)
            print("minimum =", newim.min())
            print("max =", newim.max())

        img =newim
        img = img[58:428,143:513]

        # hv_im = cv2.cvtColor(img,cv2.COLOR_)
        # if size < 125:
        #     img2 = img*(1-(size/125))
        #     img = img-img2
        #     img = np.uint8(img)
        #     print(img.dtype)
        #     print("hi")
        #
        # else:
        #     img2 = img * (size / 250)
        #     img = img + img2
        #     img = np.uint8(img)
        #     print(img.dtype)
        #     print("hi")


        w,h = img.shape
        qim = QtGui.QImage(img.data.tobytes(),h,w,h,QtGui.QImage.Format_Indexed8)

        return QPixmap.fromImage(qim)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    # create an instance of Ui_MainWindow
    # fill in the instance into the setup function ?
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
