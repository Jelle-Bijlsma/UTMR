from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

def window():
    app = QApplication(sys.argv) #initializer
    win = QMainWindow()
    win.setGeometry(400,400,300,300) #x,y , width,height
    win.setWindowTitle("Een window")
    linedit = QtWidgets.QLineEdit(win)
    linedit.setFixedWidth(140)
    linedit.move(80, 80)
    linedit.editingFinished.connect(lambda: print("jemo"))
    win.show()
    sys.exit(app.exec_()) #waits until you press 'x' to do a clean shutdown
    window()


window()

