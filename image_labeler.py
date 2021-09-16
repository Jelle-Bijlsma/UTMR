from PyQt5 import QtWidgets
import QT_Gui.image_labeler
import sys

class MainWindowz(QtWidgets.QMainWindow, QT_Gui.image_labeler.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindowz, self).__init__(parent)
        self.setupUi(MainWindow)
        self.label.setText("Hi")




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    sshFile = "./QT_Gui/Dtor.qss"
    # its not dtor. It is from https://github.com/GTRONICK/QSS/blob/master/Aqua.qss
    with open(sshFile, 'r') as fh:
        app.setStyleSheet(fh.read())
    MainWindow = QtWidgets.QMainWindow()
    ui = MainWindowz()
    MainWindow.show()
    sys.exit(app.exec_())