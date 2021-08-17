import sys

import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui

import scrapyard.gui_morph
from scrapyard.image_process import change_qpix as cqpx


class MorphWindowClass(QtWidgets.QMainWindow, scrapyard.gui_morph.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MorphWindowClass, self).__init__(parent)
        self.setupUi(MainWindow)
        self.frame = cv2.imread("../data/screenshots/newting.png", 0)
        self.result = np.copy(self.frame)
        self.image.setPixmap(cqpx(self.frame))
        self.textEdit.placeholderText()

        self.valid_ops = ["dilate", "erosion", "m_grad", "blackhat", "whitehat"]

        # connect!
        self.dilation.clicked.connect(lambda: self.addstr2ting("dilate"))
        self.erosion.clicked.connect(lambda: self.addstr2ting("erosion"))
        self.m_grad.clicked.connect(lambda: self.addstr2ting("m_grad"))
        self.blackhat.clicked.connect(lambda: self.addstr2ting("blackhat"))
        self.white_hat.clicked.connect(lambda: self.addstr2ting("whitehat"))

        # checkbox + settings
        self.checkBox.pressed.connect(self.runfun)

        # minor
        self.image.mousePressEvent = self.getPixel

    """This part is left for reference reasons with respect to mousePress events"""

    #   self.textEdit.viewport().installEventFilter(self)
    #
    # def eventFilter(self, obj, event):
    # https://stackoverflow.com/questions/53294597/how-to-define-a-mousepressevent-function-for-a-qtextedit-widget-without-subclass
    #     if obj is self.textEdit.viewport() and event.type() == QtCore.QEvent.MouseButtonPress:
    #         if event.button() == QtCore.Qt.LeftButton:
    #             self.editfun()
    #     return super(MorphWindowClass, self).eventFilter(obj, event)
    #     # self.textEdit.mousePressEvent = self.editfun

    def getPixel(self, event):
        """Function which takes over the normal mousePressEvent from the qlabel. It gets the x,y coordinates of the
        label and resizes them to the matrix coordinates needed for FLOOD-filling"""
        x = event.pos().x()
        y = event.pos().y()
        print(f"clicked pos{x, y}")
        # Mask used to flood filling.
        # Notice the size needs to be 2 pixels than the image.
        h, w = self.result.shape[:2]
        xtot = self.image.width()
        ytot = self.image.height()
        print(f"xtot = {xtot}, ytot = {ytot}")
        x = int((x / xtot) * w)
        y = int((y / ytot) * h)
        print(f"rescaled x = {x}, rescaled y = {y}")

        self.beforefill = np.copy(self.result)
        self.afterfill = np.copy(self.result)
        mask = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(self.afterfill, mask, (x, y), 255)
        self.result = self.afterfill ^ self.beforefill
        self.image.setPixmap(cqpx(self.result))

    def runfun(self):
        """
        Main function which does error checking firs 'self.checker' and based on the result, continues with
        reading from the textEditor to determine which operations are used.

        --> Note:
        Checkboxes return False when checked and True when unchecked? Bizarre...."""
        # print(f"the setchecked returns: {self.checkBox.isChecked()}")
        # print(f"lets also try checkstate: {self.checkBox.checkState()}")

        error = self.checker()
        if error == 1:
            # if there is an error in the checker, uncheck the checkbox
            self.checkBox.setChecked(True)
        if self.checkBox.isChecked() is not False:
            # if the code is called when the checkbox is unchecked, return
            self.image.setPixmap(cqpx(self.frame))
            return

        cur_ele = np.copy(self.frame)
        if error == 0:
            # kernelsize = (self.spinBox.value(), self.spinBox.value())
            # kernel = cv2.getStructuringElement(shape=self.comboBox.currentIndex(), ksize=kernelsize)
            for element in self.textEdit.toPlainText().split('\n'):
                starter = element.split(' ')
                print(starter)
                kernelsize = (int(starter[2]), int(starter[2]))
                kernel = cv2.getStructuringElement(shape=int(starter[4]), ksize=kernelsize)
                if starter[0] == self.valid_ops[0]:  # dilate
                    cur_ele = cv2.dilate(cur_ele, kernel, iterations=1)
                elif starter[0] == self.valid_ops[1]:  # erosion
                    cur_ele = cv2.erode(cur_ele, kernel, iterations=1)
                elif starter[0] == self.valid_ops[2]:  # m_grad
                    cur_ele = cv2.morphologyEx(cur_ele, cv2.MORPH_GRADIENT, kernel)
                elif starter[0] == self.valid_ops[3]:  # blackhat
                    cur_ele = cv2.morphologyEx(cur_ele, cv2.MORPH_BLACKHAT, kernel)
                elif starter[0] == self.valid_ops[4]:  # whitehat
                    cur_ele = cv2.morphologyEx(cur_ele, cv2.MORPH_TOPHAT, kernel)
        self.result = cur_ele
        self.image.setPixmap(cqpx(self.result))

    def checker(self):
        a = 0
        marker = 0
        cursor = self.textEdit.textCursor()
        clrR = QtGui.QColor(255, 0, 0, 255)
        clrB = QtGui.QColor(0, 0, 0, 255)

        for element in self.textEdit.toPlainText().split('\n'):
            starter = element.split(' ')
            if starter[0] in self.valid_ops:
                cursor.setPosition(marker)
                cursor.movePosition(20, 1, 1)
                self.textEdit.setTextCursor(cursor)
                self.textEdit.setTextColor(clrB)
                marker += len(element) + 1
                print(marker)
                cursor.setPosition(0)
                self.textEdit.setTextCursor(cursor)
            else:
                cursor.setPosition(marker)
                cursor.movePosition(20, 1, 1)
                self.textEdit.setTextCursor(cursor)
                self.textEdit.setTextColor(clrR)
                print("something is wrong!!")
                a = 1
                marker += len(element) + 1
                cursor.setPosition(0)
                self.textEdit.setTextCursor(cursor)
        return a

    def addstr2ting(self, stringz):
        a = QtGui.QColor(0, 0, 0, 255)
        self.textEdit.setTextColor(a)
        stringz += f" kernel: {self.spinBox.value()} shape: {self.comboBox.currentIndex()}"
        self.textEdit.append(stringz)


if __name__ == "__main__":
    # chad no argument vs virgin sys.argv
    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()
    ui = MorphWindowClass()
    MainWindow.show()

    sys.exit(app.exec_())
