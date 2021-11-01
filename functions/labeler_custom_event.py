import numpy as np
from PyQt5 import QtWidgets, QtGui
from image_labeler import MainWindowz as Mainz

""""
WheelEvent_custom calls the scrollclass to zoom in, but also keeps a call to the original wheelevent
used by the scrollArea to be able to use the scrollwheel to navigate the vertical scrollbar
"""


def wheelEvent(self, event: QtGui.QWheelEvent):
    scr_val = event.angleDelta().y()
    skp = self.ScrCls.change_size(scr_val)
    if not skp:
        super(QtWidgets.QScrollArea, self.scrollArea).wheelEvent(event)

""""
Both Press and release events manage whether or not the user has pressed the ctrl key. If so,
it enables zooming in.
"""
def keyPressEvent(self: Mainz, event: QtGui.QKeyEvent) -> None:
    if not event.isAutoRepeat():
        print(f"{event.key()} is pressed")
        if event.key() == 16777249 or event.key() == 16777249:
            self.ScrCls.ctrl_pressed = True

    if (event.key() == 16777236) & self.ScrCls.ctrl_pressed:  # right arrow key
        self.PtWin.next_image()
        return
    elif (event.key() == 16777234) & self.ScrCls.ctrl_pressed:  # left arrow key
        self.PtWin.prev_image()
        return
    elif (event.key() == 16777235) & self.ScrCls.ctrl_pressed: # up key
        self.PtWin.go_30_backward()
        return
    elif (event.key() == 16777237) & self.ScrCls.ctrl_pressed: # up key
        self.PtWin.go_30_forward()
        return
    elif event.key() == 76:  # L
        self.PtWin.loadem()
    elif event.key() == 61: # plus
        self.ScrCls.change_size(10)
    elif event.key() == 45:
        self.ScrCls.change_size(-10)

    super(QtWidgets.QScrollArea, self.scrollArea).keyPressEvent(event)


def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
    if not event.isAutoRepeat():
        # print(f"{event.text()} is released")
        if event.key() == 16777249:
            self.ScrCls.ctrl_pressed = False
    super(QtWidgets.QScrollArea, self.scrollArea).keyReleaseEvent(event)

""""
Mouse tracking is on, meaning every time the mouse is moved over the label, a signal
is emitted. 
"""
def mouseMoveEvent(self, event: QtGui.QMouseEvent):
    x, y = self.ScrCls.labelsize  # ORIGINAL
    X, Y = self.ScrCls.w, self.ScrCls.h  # current
    xscale = x / X
    yscale = y / Y
    x_rescale = event.x() * xscale
    y_rescale = event.y() * yscale
    self.PtWin.rescaled_x = np.floor(x_rescale)
    self.PtWin.rescaled_y = np.floor(y_rescale)
    # QtWidgets.QToolTip.showText(event.pos(),str(x_rescale)+ str(y_rescale))
    self.PtWin.update_coords()


def mousePressEvent(self, event):
    # self.label.setText(f"u used {str(event.button())}")
    print(f"u used {str(event.button())}")
    self.PtWin.click(event)
    # self.PtWin.append_text(self.PntC.clicklist)
