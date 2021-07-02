import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QColor
import sys
from PyQt5.QtWidgets import QMessageBox
import cv2
import numpy as np
import stackscreen

class buildup(stackscreen.Ui_MainWindow):
    def __init__(self):
        super().__init__()

    def setupUi2(self):
        self.actionpage1.triggered.connect(self.gotopage1)
        self.actionpage2.triggered.connect(self.gotopage2)

    def gotopage1(self):
        self.stackedWidget.setCurrentIndex(0)

    def gotopage2(self):
        self.stackedWidget.setCurrentIndex(1)


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

