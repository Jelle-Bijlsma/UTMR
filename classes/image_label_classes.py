import os
import cv2
from PyQt5 import QtWidgets, QtGui
import QT_Gui.listbox
from functions.process import change_qpix as cqpx
import pickle

"""
Classes used by the image labeler.
"""

class PointWindow(QtWidgets.QWidget, QT_Gui.listbox.Ui_Form):
    """"
    Pointwindow represents the secondary window used to log all the points per frame.
    It also serves to delete entry's, go to previous/next frames. Inherits visuals from the listbox,
    and calling super().__init__() and .setupUi
    """

    def __init__(self, form, scrollclass, label: QtWidgets.QLabel):
        super().__init__()
        self.setupUi(form)
        self.clicklist = []
        self.rescaled_x = 0
        self.rescaled_y = 0
        self.scrollclass = scrollclass
        self.progress = label

        self.pushButton.clicked.connect(self.delete_entry)
        self.pushButton_2.clicked.connect(self.delete_all_entry)
        self.pushButton_3.clicked.connect(self.prev_image)
        self.pushButton_4.clicked.connect(self.next_image)

        # loads in one standard image set, set to True if youre not developing anymore
        self.loadem(production=False)

    def delete_entry(self):
        """"Put the caret at the corresponding entry, then press this button."""
        linenumber = 0
        txtE = self.textEdit  # ? what? you might think. However, if you check, the PointWindow inherits from
        # QT_Gui.listbox, so then you can actually call it.

        cursor = txtE.textCursor()
        cursor.movePosition(cursor.StartOfLine)

        """"To find out at which line number the user was, we recursively
        go up until we are at the start of the QlineEdit"""
        while cursor.position() != 0:
            cursor.movePosition(cursor.Up)
            linenumber += 1

        try:
            self.clicklist[self.image_number].pop(linenumber)
        except IndexError:
            a_warning = QtWidgets.QMessageBox()
            a_warning.setText("Cant delete from empty list!")
            a_warning.exec()
        self.update_text()

    def savepoints(self):
        try:
            name = QtWidgets.QFileDialog.getSaveFileName()
        except FileNotFoundError:
            return

        print(str(name[0]))
        f = open(name[0], 'wb')
        pickle.dump((self.clicklist, self.image_number), f)
        f.close()

    def loadpoints(self):
        try:
            name = QtWidgets.QFileDialog.getOpenFileName()
        except FileNotFoundError:
            return

        f = open(name[0], 'rb')
        self.clicklist, self.image_number = pickle.load(f)
        f.close()
        self.scrollclass.change_img(self.image_list[self.image_number])
        self.update_text()

        a_warning = QtWidgets.QMessageBox()
        a_warning.setText("please press next and then previous for the changes to take effect.")
        a_warning.exec()

    def delete_all_entry(self):
        while len(self.clicklist[self.image_number]) != 0:
            self.delete_entry()

    def update_text(self):
        """ each time the update text is called, the entire block is redrawn."""
        self.textEdit.setText("")
        for element in self.clicklist[self.image_number]:
            self.textEdit.append(f"x = {element[0]}, y = {element[1]}, b = {element[2]}")
        points = len(self.clicklist[self.image_number])
        self.label_5.setText(str(points))
        self.label_2.setText(
            "..." + self.image_path_list[self.image_number][-53:-49] + "..." + self.image_path_list[self.image_number][
                                                                               -20:])

    def click(self, event: QtGui.QMouseEvent):
        """"kinda vague but trust me that self.rescaled_x is updated through the custom mousemove_event
         (in image_labeler) and you can see the update in this class ... 💀💀💀"""
        if event.button() == 1:  # if left click
            brightness = self.scrollclass.nparray[int(self.rescaled_y), int(self.rescaled_x)]
            self.clicklist[self.image_number].append((self.rescaled_x, self.rescaled_y, brightness))
            self.clicklist[self.image_number] = sorted(self.clicklist[self.image_number], key=lambda x: x[1])
        self.update_text()

    def update_coords(self):
        self.lineEdit.setText(str(self.rescaled_x))
        self.lineEdit_2.setText(str(self.rescaled_y))
        try:
            brightness = self.scrollclass.nparray[int(self.rescaled_y), int(self.rescaled_x)]
            self.label_8.setText(str(brightness))
        except IndexError:
            self.label_8.setText("")

    # it is not 30, but 10.
    def go_30_forward(self):
        for ii in range(10):
            self.next_image()

    def go_30_backward(self):
        for ii in range(10):
            self.prev_image()

    def next_image(self):
        if self.image_number >= len(self.image_list) - 1:
            self.image_number = 0
        else:
            self.image_number += 1
        image = self.image_list[self.image_number]
        self.scrollclass.change_img(image)
        # print(type(image))
        self.progress.setText(f"image {self.image_number} of {len(self.image_list) - 1}")
        self.update_text()

        # get image name
        # get image iterator number
        # load in clicklist[image iterator]

    def prev_image(self):
        if self.image_number == 0:
            self.image_number = len(self.image_list) - 1
        else:
            self.image_number -= 1
        image = self.image_list[self.image_number]
        self.scrollclass.change_img(image)
        self.progress.setText(f"image {self.image_number} of {len(self.image_list) - 1}")
        self.update_text()

    def loadem(self, production=True):
        # try and select folder. If user cancelled, return. Else, continue.
        if production is True:
            try:
                path = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'select folder'))
            except FileNotFoundError:
                return
        else:
            path = str("./data/png/mri31/")
        self.image_list = []  # clear it out
        self.clicklist = []

        image_path_list = os.listdir(path)
        self.image_path_list = sorted(image_path_list)
        for element in self.image_path_list:
            fp = path + '/' + element
            print(fp)
            self.image_list.append(cv2.imread(fp, 0))
            self.clicklist.append([])
        self.image_number = 0
        self.progress.setText(f"image {self.image_number} of {len(self.image_list) - 1}")
        self.scrollclass.change_img(self.image_list[self.image_number])
        self.update_text()

    def __repr__(self):
        return "jemo"


class ScrollClass:
    def __init__(self, img, label: QtWidgets.QLabel, hbar: QtWidgets.QScrollArea.horizontalScrollBar,
                 vbar: QtWidgets.QScrollArea.verticalScrollBar):
        self.sizevar = 1
        self.qpix = cqpx(img)
        self.w = self.qpix.width()
        self.h = self.qpix.height()
        self.qpix_og = cqpx(img)
        self.image: QtWidgets.QLabel = label
        self.ctrl_pressed = False
        self.hbar = hbar
        self.vbar = vbar
        label.setPixmap(self.qpix)
        self.nparray = img
        self.rel_v = 0
        self.rel_h = 0

        self.labelsize = (self.qpix_og.width(), self.qpix_og.height())

    def change_img(self, img):
        self.nparray = img
        self.qpix_og = cqpx(img)
        self.change_size(42069, override=True)
        print("nextim")

    def change_size(self, ch_s, override=False):
        if self.ctrl_pressed or (override is True):
            if ch_s == 0:
                pass
            elif ch_s == 42069:  # arbitrarily high value to recognize imchange
                self.sizevar += 0
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
            self.w = int(self.qpix.width())
            self.h = int(self.qpix.height())
            diff = (self.w - wold, self.h - hold)
            self.get_scroll()
            self.image.setPixmap(self.qpix)
            if not override:
                self.set_scroll(diff)
            return True
        return False

    def get_scroll(self):
        max_h = self.hbar.maximum()
        max_v = self.vbar.maximum()

        pos_h = self.hbar.sliderPosition()
        pos_v = self.vbar.sliderPosition()
        if (pos_h != 0) & (pos_v != 0):
            # print(f"pos_h = {pos_h}")
            self.rel_h = (pos_h / max_h)
            self.rel_v = (pos_v / max_v)
            # print(self.rel_v, self.rel_h)

    def set_scroll(self, diff):
        # min_h = self.hbar.minimum() <- its always 0!
        max_h = self.hbar.maximum()
        max_v = self.vbar.maximum()
        # print(diff)

        if (max_h > 0) & (max_v > 0):
            self.hbar.setValue(int(max_h * self.rel_h + diff[0] / 2))
            self.vbar.setValue(int(max_v * self.rel_v + diff[1] / 2))
