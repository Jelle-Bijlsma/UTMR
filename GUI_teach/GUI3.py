from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


# we inherit everything from QMainWindow Class.
class MyWindow(QMainWindow):
    # so when we initialize..
    def __init__(self):
        # calling parent constructor, i.e. QMainWindow
        super(MyWindow, self).__init__()
        # size
        width = 900
        height = 900
        # position
        x = 0
        y = 0
        self.setGeometry(x, y, width, height)
        self.setWindowTitle("cool title")
        self.init_ui()

    # here we put all the bs in our window
    def init_ui(self):
        # app = QApplication(sys.argv)
        # win = QMainWindow()
        # # size
        # width = 900
        # height = 900
        # # position
        # x = 0
        # y = 0
        # win.setGeometry(x, y, width, height)
        # win.setWindowTitle(title)

        # label
        self.label = QtWidgets.QLabel(self)
        self.label.setText("jemo")
        self.label.move(40, 40)

        # button
        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("this is a button")
        self.b1.move(90, 90)
        self.b1.clicked.connect(self.clicka)

    def clicka(self):
        self.label.setText("jemo ederrrrrrrrrrrrrrrrrrrrr")
        self.label.adjustSize()


def clicka():
    print("clicked")


def window():
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())


window()
