import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from QT_Gui import gui_full
import functions.auxillary
import functions.classes
import pyqtgraph as pg


# the whole thing is just existing within this class.
class BuildUp(gui_full.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # initialize timer video player. timer is started in the self.play_button
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.next_frame)

        self.threadpool = QtCore.QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        # start initializing variables
        self.CurMov = functions.classes.MovieClass()
        self.histogramx = list(range(0, 255))  # the x-range of the histogram
        self.bargraph = pg.BarGraphItem()  # the histogram widget inside plotwidget (which is called self.histogram)


    def setup_ui2(self):
        # this is setting up the GUI more. More convenient here than in QT designer.
        # For some reason doesnt work when put in __init__

        sliderlist = [self.slider_brightness, self.slider_boost, self.slider_Lbound, self.slider_Rbound]
        line_editlist = [self.lineEdit_Brightness, self.lineEdit_Boost, self.lineEdit_Lbound, self.lineEdit_Rbound]
        self.MySliders = functions.classes.SliderClass(sliderlist, line_editlist)

        # load pictures in
        self.mr_image.setPixmap(QtGui.QPixmap("./QT_Gui/images/baseimage.png"))
        self.mr_image.setScaledContents(True)
        self.label_logo_uni.setPixmap((QtGui.QPixmap("./QT_Gui/images/UTlogo.png")))
        self.label_logo_uni.setScaledContents(True)
        self.fourier_image.setScaledContents(True)

        self.stackedWidget.setCurrentIndex(0)  # initialize to homepage

        # home page
        self.button_2dicom.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.button_2editor.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

        # $ $ $ $ video editor
        # video player
        self.pb_load_movie.clicked.connect(self.filebrowse_png)
        self.progress_bar.setMinimum(0)
        self.progress_bar.valueChanged.connect(self.framechange)
        self.pb_reset.clicked.connect(self.reset_button)
        self.pb_play.clicked.connect(self.play_button)
        self.pb_pause.clicked.connect(lambda: self.timer.stop())
        # sliders
        self.slider_brightness.valueChanged.connect(self.sliderchange)
        self.slider_boost.valueChanged.connect(self.sliderchange)
        self.slider_Lbound.valueChanged.connect(self.sliderchange)
        self.slider_Rbound.valueChanged.connect(self.sliderchange)

        # dicom page
        self.pb_convert.clicked.connect(self.convert)
        self.pb_browse_dcm.clicked.connect(self.filebrowse_dcm)
        self.pb_reset_terminal.clicked.connect(self.txtbox_cmd.clear)

        # menu buttons
        self.actionMain.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.actionImage_processing.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.actionDicom_Edit.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(2))

        # test
        self.filebrowse_png(True)
        self.sliderchange()

    # $$$$$$$$  functions relating to video editor
    def filebrowse_png(self, test=False):
        a = QtWidgets.QFileDialog()
        a.setDirectory("./data/png/")
        if test is False:
            path = str(a.getExistingDirectory(MainWindow, 'select folder with pngs'))
        else:
            path = "./data/png/correct_video"
        # 'get existing directory' never uses the final '/' so you have to manually input it.
        self.lineEdit_importpath.setText(path)
        filelist = os.listdir(path)
        filelist.sort()
        if functions.auxillary.checkifpng(filelist) == 0:
            functions.auxillary.popupmsg("NO PNG IN FOLDER", "warning")
            self.pb_play.setEnabled(False)
            self.pb_play.setToolTip("Try selecting a folder with .png")
            return
        self.pb_play.setEnabled(True)
        self.pb_play.setToolTip("")

        # create temp list of all images in np.array() format
        imlist = functions.auxillary.loadin(filelist, path)
        self.CurMov.create_frameclass(imlist)
        self.progress_bar.setMaximum(self.CurMov.maxframes)
        self.update_all_things()

    def next_frame(self):
        # called when the timer says it is time for the next frame
        self.CurMov.next_frame()  # MovieClass method to go to the next frame index
        self.update_all_things()

    def update_all_things(self):
        # called whenever the main screen should be updated
        # if statement to reduce calculation costs
        if self.progress_bar.value() != self.CurMov.currentframe:
            self.progress_bar.setValue(self.CurMov.currentframe)  # edit the progress bar

        qpix, histogram, fft = self.CurMov.return_frame()
        if self.mr_image.pixmap() != qpix:
            self.mr_image.setPixmap(qpix)  # set the main image to the current Frame
        # histogram time
        newbar = pg.BarGraphItem(x=self.histogramx, height=histogram, width=5, brush='g')
        if self.bargraph != newbar:
            self.histogram.clear()
            self.bargraph = newbar
            self.histogram.addItem(self.bargraph)
        if self.fourier_image != fft:
            self.fourier_image.setPixmap(fft)

    def framechange(self):
        # called when you change the progress bar in the video player
        slv = self.progress_bar.value()
        self.CurMov.currentframe = slv
        self.update_all_things()

    def sliderchange(self):
        # [self.slider_brightness, self.slider_boost, self.slider_Lbound, self.slider_Rbound]
        paramlist = self.MySliders.getvalue()
        self.CurMov.gray_slice_p = paramlist
        self.update_all_things()

    def play_button(self):
        # you could skip this check, on the expense that repeatedly pressing play lags the player a bit
        if self.timer.isActive():
            return
        self.timer.start(100)

    # pause_button is through a lambda function.

    def reset_button(self):
        self.timer.stop()
        self.CurMov.currentframe = 0
        self.MySliders.valueset(0)
        self.update_all_things()

    # $$$$$$ functions related to dicom manager
    def filebrowse_dcm(self):
        # this could definitely be done different, too bad!
        #
        path = str(QtWidgets.QFileDialog.getExistingDirectory(MainWindow, 'select folder'))
        try:
            self.lineEdit_dicom.setText(path)
            filelist = os.listdir(path)
            filelist.sort()
            self.txtbox_dcmcont.clear()
            for element in filelist:
                self.txtbox_dcmcont.append(element)
        except:
            self.txtbox_cmd.append("folder selection aborted")

    def convert(self):
        self.txtbox_cmd.append("starting conversion")
        skip2video = 0
        # get variables
        fps = self.spinbox_fps.value()
        project_name = self.lineEdit_save.text()
        dcmpath = self.lineEdit_dicom.text()
        savename = project_name + ".avi"
        videosave = "./data/video"
        videopath = videosave + "/" + savename
        if not os.path.exists(videosave):
            os.mkdir(videosave)

        # check conditions
        if fps <= 0:
            msg = QtWidgets.QMessageBox()
            msg.setText("FPS Cant be zero!")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.exec_()
            self.txtbox_cmd.append("FPS cant be set, exiting")
            return
        self.txtbox_cmd.append("FPS =" + str(self.spinbox_fps.value()))

        if project_name == "" or dcmpath == "":
            msg = QtWidgets.QMessageBox()
            msg.setText("Project name & dcm folder cant be empty")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.exec_()
            self.txtbox_cmd.append("Empty project name or dcm folder, exiting")
            return
        else:
            projectpath = "./data/png/" + project_name
            if os.path.exists(projectpath):
                msg = QtWidgets.QMessageBox()
                msg.setText("possibility of overwrite, continue?")
                msg.setStandardButtons(
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
                msg.exec_()
                bresult = (msg.clickedButton().text())
                if bresult == "&No":
                    self.txtbox_cmd.append("overwrite detected, exiting")
                    return
                elif bresult == "&Cancel":
                    skip2video = 1
            else:
                # you know this can be done easier
                if os.path.exists("./data"):
                    os.mkdir(projectpath)
                else:
                    os.mkdir("./data")
                    os.mkdir(projectpath)

        # initialize worker thread
        dcm2pngworker = functions.classes.Worker1()
        filelist = os.listdir(dcmpath)
        filelist.sort()

        path = dcmpath + "/"
        if skip2video == 0:
            self.threadpool.start(lambda a=filelist, b=path, c=project_name: dcm2pngworker.dicom2png(a, b, c))
            dcm2pngworker.signals.progress.connect(lambda prgz: self.txtbox_cmd.append("Converting image " + str(prgz)))
            dcm2pngworker.signals.finished.connect(lambda: self.txtbox_cmd.append("image conversion done"))
            dcm2pngworker.signals.finished.connect(lambda: self.threadpool.start(
                lambda a="./data/png/" + project_name + "/", b=fps, c=videopath:
                dcm2pngworker.png2avi(a, b, c)))
        else:
            self.threadpool.start(lambda a="./data/png/" + project_name + "/", b=fps, c=videopath:
                                  dcm2pngworker.png2avi(a, b, c))

        dcm2pngworker.signals.videodone.connect(lambda: self.txtbox_cmd.append("video conversion done"))


if __name__ == "__main__":
    # chad no argument vs virgin sys.argv
    app = QtWidgets.QApplication([])
    MainWindow = QtWidgets.QMainWindow()
    # class creation
    ui = BuildUp()
    # create an instance of Ui_MainWindow
    # fill in the instance into the setup function ?
    ui.setupUi(MainWindow)  # if i move this function into the __init__ i think I can get rid of the second setup_ui
    ui.setup_ui2()
    MainWindow.show()
    sys.exit(app.exec_())
