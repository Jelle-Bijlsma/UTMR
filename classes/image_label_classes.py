import os
import time
import cv2
from PyQt5 import QtWidgets, QtGui
import QT_Gui.listbox
from functions.process import change_qpix as cqpx
import pickle

class PointWindow(QtWidgets.QWidget, QT_Gui.listbox.Ui_Form):
    def __init__(self, form,scrollclass, label:QtWidgets.QLabel):
        super().__init__()
        self.setupUi(form)
        self.clicklist = []
        self.rescaled_x = 0
        self.rescaled_y = 0
        self.scrollclass = scrollclass
        self.progress = label
        # self.__repr__ = "jemo"

        self.pushButton.clicked.connect(self.delete_entry)
        self.pushButton_2.clicked.connect(self.delete_all_entry)
        self.pushButton_3.clicked.connect(self.prev_image)
        self.pushButton_4.clicked.connect(self.next_image)
        # self.textEdit.keyPressEvent =
        self.loadem(production=False)

    def delete_entry(self):
        # cursor = QtGui.QTextCursor(self.textEdit.document())
        # cursor.movePosition(self.textEdit.textCursor().position())
        # cursor.movePosition(cursor.StartOfLine)
        # cursor.movePosition(cursor.EndOfLine,cursor.KeepAnchor)
        # print(cursor.selectedText())
        #self.textEdit.setTextCursor(cursor)
        #self.textEdit.insertPlainText("jej")
        linenumber = 0
        txtE = self.textEdit
        cursor = txtE.textCursor()
        cursor.movePosition(cursor.StartOfLine)

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

        #print(self.textEdit.cursor().pos().y())

    def savepoints(self):
        try:
            name = QtWidgets.QFileDialog.getSaveFileName()
        except FileNotFoundError:
            return

        print(str(name[0]))
        f = open(name[0], 'wb')
        pickle.dump((self.clicklist,self.image_number),f)
        f.close()

    def loadpoints(self):
        try:
            name = QtWidgets.QFileDialog.getOpenFileName()
        except FileNotFoundError:
            return

        f = open(name[0],'rb')
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
        self.textEdit.setText("")
        for element in self.clicklist[self.image_number]:
            self.textEdit.append(f"x = {element[0]}, y = {element[1]}")
        points = len(self.clicklist[self.image_number])
        self.label_5.setText(str(points))
        self.label_2.setText("..." + self.image_path_list[self.image_number][-53:-49] + "..." + self.image_path_list[self.image_number][-20:])



    def click(self, event: QtGui.QMouseEvent):
        # left or right?
        if event.button() == 1:
            self.clicklist[self.image_number].append((self.rescaled_x, self.rescaled_y))
        self.update_text()

    def update_coords(self):
        self.lineEdit.setText(str(self.rescaled_x))
        self.lineEdit_2.setText(str(self.rescaled_y))

    def go_30_forward(self):
        for ii in range(10):
            self.next_image()

    def go_30_backward(self):
        for ii in range(10):
            self.prev_image()


    def next_image(self):
        if self.image_number >= len(self.image_list)-1:
            self.image_number = 0
        else:
            self.image_number += 1
        image = self.image_list[self.image_number]
        self.scrollclass.change_img(image)
        # print(type(image))
        self.progress.setText(f"image {self.image_number} of {len(self.image_list)-1}")
        self.update_text()

        # get image name
        # get image iterator number
        # load in clicklist[image iterator]

    def prev_image(self):
        if self.image_number == 0:
            self.image_number = len(self.image_list)-1
        else:
            self.image_number -= 1
        image = self.image_list[self.image_number]
        self.scrollclass.change_img(image)
        self.progress.setText(f"image {self.image_number} of {len(self.image_list)-1}")
        self.update_text()

    def loadem(self, production = True):
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
        self.progress.setText(f"image {self.image_number} of {len(self.image_list)-1}")
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
        self.image = label
        self.ctrl_pressed = False
        self.hbar = hbar
        self.vbar = vbar
        label.setPixmap(self.qpix)

        self.rel_v = 0
        self.rel_h = 0

        self.labelsize = (self.qpix_og.width(), self.qpix_og.height())

    def change_img(self,img):
        self.qpix_og = cqpx(img)
        self.change_size(42069, override=True)
        print("nextim")

    def change_size(self, ch_s,override = False):
        if self.ctrl_pressed or (override is True):
            if ch_s == 0:
                pass
            elif ch_s == 42069:
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
            #print(f"pos_h = {pos_h}")
            self.rel_h = (pos_h / max_h)
            self.rel_v = (pos_v / max_v)
            #print(self.rel_v, self.rel_h)

    def set_scroll(self, diff):
        # min_h = self.hbar.minimum() <- its always 0!
        max_h = self.hbar.maximum()
        max_v = self.vbar.maximum()
        #print(diff)

        if (max_h > 0) & (max_v > 0):
            self.hbar.setValue(int(max_h * self.rel_h + diff[0] / 2))
            self.vbar.setValue(int(max_v * self.rel_v + diff[1] / 2))
