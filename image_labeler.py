import cv2
from PyQt5 import QtWidgets, QtGui, QtCore
import QT_Gui.image_labeler
import QT_Gui.listbox
import sys

from functions.process import change_qpix as cqpx


class PointWindow(QtWidgets.QWidget, QT_Gui.listbox.Ui_Form):
    def __init__(self, Form):
        super().__init__()
        self.setupUi(Form)
        self.clicklist = []
        # self.__repr__ = "jemo"

    def append_text(self):
        self.textEdit.setText("")
        for element in self.clicklist:
            self.textEdit.append(f"x = {element[0]}, y = {element[1]}")

    def click(self,event: QtGui.QMouseEvent):
        # left or right?
        if event.button() == 1:
            self.clicklist.append((event.pos().x(), event.pos().y()))
        self.append_text()

    def __repr__(self):
        return "jemo"




class ScrollClass():
    def __init__(self, img, label: QtWidgets.QLabel, hbar: QtWidgets.QScrollArea.horizontalScrollBar,
                 vbar: QtWidgets.QScrollArea.verticalScrollBar):
        self.sizevar = 1
        self.qpix = cqpx(img)
        self.qpix_og = cqpx(img)
        self.image = label
        self.ctrl_pressed = False
        self.hbar = hbar
        self.vbar = vbar
        label.setPixmap(self.qpix)

        self.rel_v = 0
        self.rel_h = 0

    def change_size(self, ch_s):
        if self.ctrl_pressed == True:
            if ch_s == 0:
                pass
            elif ch_s > 0:
                self.sizevar += 0.5
            elif ch_s < 0:
                self.sizevar -= 0.5
                if self.sizevar == 0:
                    self.sizevar = 0.5
            # print(self.sizevar)
            w = int(self.sizevar * self.qpix_og.width())
            h = int(self.sizevar * self.qpix_og.height())
            wold = int(self.qpix.width())
            hold = int(self.qpix.height())
            self.qpix = self.qpix_og.scaled(w, h)
            w = int(self.qpix.width())
            h = int(self.qpix.height())

            diff = (w - wold, h - hold)

            self.get_scroll()
            self.image.setPixmap(self.qpix)
            self.set_scroll(diff)
            return True
        return False

    def get_scroll(self):
        max_h = self.hbar.maximum()
        max_v = self.vbar.maximum()

        pos_h = self.hbar.sliderPosition()
        pos_v = self.vbar.sliderPosition()
        if (pos_h != 0) & (pos_v != 0):
            print(f"pos_h = {pos_h}")
            self.rel_h = (pos_h / max_h)
            self.rel_v = (pos_v / max_v)
            print(self.rel_v, self.rel_h)

    def set_scroll(self, diff):
        # min_h = self.hbar.minimum() <- its always 0!
        max_h = self.hbar.maximum()
        max_v = self.vbar.maximum()
        print(diff)

        if (max_h > 0) & (max_v > 0):
            self.hbar.setValue(int(max_h * self.rel_h + diff[0] / 2))
            self.vbar.setValue(int(max_v * self.rel_v + diff[1] / 2))


class MainWindowz(QtWidgets.QMainWindow, QT_Gui.image_labeler.Ui_MainWindow):
    def __init__(self, form):
        # form should be instance of QMainWindow
        super().__init__()
        self.setupUi(form)

        image = cv2.imread("./data/png/mri31/RLI_JB_RAM_CATH_TRACKING.MR.ABDOMEN_LIBRARY."
                           "0031.0041.2021.09.02.15.32.11.998847.16889705.IMA.png")

        self.ScrCls = ScrollClass(image, self.label, self.scrollArea.horizontalScrollBar(),
                                  self.scrollArea.verticalScrollBar())
        # self.PntC = PointCollect()

        self.drawing = False
        self.lastPoint = QtCore.QPoint()

        #self.statusbar = QtWidgets.QStatusBar()
        self.statusbar.showMessage("my G",20000)
        self.setStatusBar(self.statusbar)

        self.image = cqpx(image)
        self.label.setPixmap(self.image)

        # scroll override
        self.scrollArea.keyPressEvent = self.keyPressEvent_custom
        self.scrollArea.keyReleaseEvent = self.keyReleaseEvent_custom
        self.scrollArea.wheelEvent = self.wheelEvent_custom

        # mouse press override
        self.label.mousePressEvent = self.new_mouse
        self.label.mouseMoveEvent = self.mouseMoveEvent
        #self.label.mouseMoveEvent = self.move_mouse
        # self.label.keyPressEvent = self.keyPressEvent

        # brush

    def wheelEvent_custom(self, a0: QtGui.QWheelEvent):
        scr_val = a0.angleDelta().y()
        skp = self.ScrCls.change_size(scr_val)
        if skp == False:
            super(QtWidgets.QScrollArea, self.scrollArea).wheelEvent(a0)

    def keyPressEvent_custom(self, a0: QtGui.QKeyEvent) -> None:
        if not a0.isAutoRepeat():
            print(f"{a0.text()} is pressed")
            if a0.key() == 16777249:
                self.ScrCls.ctrl_pressed = True
        super(QtWidgets.QScrollArea, self.scrollArea).keyPressEvent(a0)

    def keyReleaseEvent_custom(self, a0: QtGui.QKeyEvent) -> None:
        if not a0.isAutoRepeat():
            print(f"{a0.text()} is released")
            if a0.key() == 16777249:
                self.ScrCls.ctrl_pressed = False
        super(QtWidgets.QScrollArea, self.scrollArea).keyReleaseEvent(a0)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(self.rect(), self.image)

    def mouseMoveEvent(self, event):
        if event.buttons() and QtCore.Qt.LeftButton and self.drawing:
            painter = QtGui.QPainter(self.image)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 3, QtCore.Qt.SolidLine))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()
    #
    # def mouse_press(self, event: QtGui.QMouseEvent):
    #     self.PntC.click(event)

    def new_mouse(self, event):
        # self.label.setText(f"u used {str(event.button())}")
        print(f"u used {str(event.button())}")
        self.PtWin.click(event)
        # self.PtWin.append_text(self.PntC.clicklist)

    def create_ting(self, mainwin):
        w = mainwin.width()

        # 'form' is the window'
        self.Form = QtWidgets.QWidget()
        self.Form.show()
        self.Form.move(w + 200, 125)
        # 'ui' is the class which can interact.
        self.PtWin = PointWindow(self.Form)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    sshFile = "./QT_Gui/Dtor.qss"
    # its not dtor. It is from https://github.com/GTRONICK/QSS/blob/master/Aqua.qss
    with open(sshFile, 'r') as fh:
        app.setStyleSheet(fh.read())
    MainWindow = QtWidgets.QMainWindow()
    ui = MainWindowz(MainWindow)
    MainWindow.show()
    ui.create_ting(MainWindow)
    sys.exit(app.exec_())
