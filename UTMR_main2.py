import os
import sys

import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, QThreadPool
from PyQt5.QtGui import QPixmap

import classes.class_extra
from classes.class_extra import SliderClass as SliderClass
import classes.class_frameclass
import classes.class_movieclass
import classes.movieclass_2 as mvc2
import functions.auxiliary
import functions.circle_tracking.circle_finder
from QT_Gui import gui_full
from functions.image_processing.image_process import change_qpix as cqpx
from functions.threed_projection import twod_movement as TwoDclass


# the whole thing is just existing within this class.
class BuildUp(QtWidgets.QMainWindow, gui_full.Ui_MainWindow):
    def __init__(self, parent=None):
        super(BuildUp, self).__init__(parent)
        self.setupUi(MainWindow)
        # start initializing variables
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.threadpool = QThreadPool()
        self.CurMov = mvc2.MovieUpdate()
        self.imlist = []
        radiotuple = (self.radioButton_image, self.radioButton_circle)

        # load pictures in
        self.mr_image.setPixmap(QPixmap("./QT_Gui/images/baseimage.png"))
        self.label_logo_uni.setPixmap((QPixmap("./QT_Gui/images/UTlogo.png")))
        self.lineEdit_save.isEnabled()

        # self.stackedWidget.setCurrentIndex(0)  # initialize to homepage
        self.stackedWidget.setCurrentIndex(1)  # initialize to video-edit-page

        # home page
        self.button_2dicom.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.button_2editor.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

        # $ $ $ $ video editor
        # video player
        self.pb_load_movie.clicked.connect(self.filebrowse_png)
        self.progress_bar.setMinimum(2)
        self.progress_bar.valueChanged.connect(self.progress_bar_fun)
        self.pb_reset.clicked.connect(self.reset_button)
        self.pb_play.clicked.connect(self.play_button)
        self.pb_pause.clicked.connect(lambda: self.timer.stop())

        # dicom page
        self.pb_convert.clicked.connect(self.convert)
        self.pb_browse_dcm.clicked.connect(self.filebrowse_dcm)
        self.pb_reset_terminal.clicked.connect(self.txtbox_cmd.clear)

        # menu buttons
        self.actionMain.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.actionImage_processing.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.actionDicom_Edit.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.actionCircle_Tracking.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(3))

        # slider list for the GLS
        sl_gls = [self.slider_brightness, self.slider_boost, self.slider_Lbound, self.slider_Rbound]
        le_gls = [self.lineEdit_Brightness, self.lineEdit_Boost, self.lineEdit_Lbound, self.lineEdit_Rbound]
        self.SC_GLS = SliderClass(
            slides=sl_gls, line_edits=le_gls, function=self.pre_value_changed, keyword='GLS',
            radiotuple=radiotuple, checklist=None)

        # slider list for the b_filter
        sl_bfilter = [self.slider_f_cutoff, self.slider_f_order]
        le_bfilter = [self.lineEdit_f_cutoff, self.lineEdit_f_order]
        self.SC_b_filter = SliderClass(
            slides=sl_bfilter, line_edits=le_bfilter, function=self.pre_value_changed, keyword='b_filter',
            radiotuple=radiotuple, checklist=[self.check_filter1])

        # slider list for the G_filter
        sl_gfilter = [self.slider_g_size, self.slider_g_sigX, self.slider_g_sigY]
        le_gfilter = [self.lineEdit_g_size, self.lineEdit_g_sigx, self.lineEdit_g_sigY]
        self.SC_g_filter = SliderClass(
            slides=sl_gfilter, line_edits=le_gfilter, function=self.CurMov.value_changed, keyword='g_filter',
            radiotuple=radiotuple, checklist=[self.check_filter_g])

        # slider list for sobel
        sl_sobel = [self.slider_Skernel, self.slider_Sdst, self.slider_Sscale]
        le_sobel = [self.lineEdit_Skernel, self.lineEdit_Sdst, self.lineEdit_Sscale]
        self.My_sobel_slider = SliderClass(
            slides=sl_sobel, line_edits=le_sobel, function=self.CurMov.value_changed, keyword='sobel',
            radiotuple = radiotuple, checklist=[self.checkBox_sobel])

        # slider list for canny
        sl_canny = [self.slider_Cthresh1, self.slider_Cthresh2]
        le_canny = [self.lineEdit_Cthresh1, self.lineEdit_Cthresh2]
        self.My_canny_slider = SliderClass(
            slides=sl_canny, line_edits=le_canny, function=self.CurMov.value_changed, keyword='canny',
            radiotuple=radiotuple, checklist=[self.checkBox_Canny])

        # slider list for circle finding
        sl_cf = [self.slider_dp_2, self.slider_mindist_2, self.slider_param1_2,
                 self.slider_param2_2, self.slider_minradius_2, self.slider_maxradius_2]
        le_cf = [self.lineEdit_dp_2, self.lineEdit_minDist_2, self.lineEdit_param1_2,
                 self.lineEdit_param2_2, self.lineEdit_minradius_2, self.lineEdit_maxradius_2]
        self.SC_circlefinder = SliderClass(
            slides=sl_cf, line_edits=le_cf, function=self.CurMov.value_changed, keyword='circlefinder',
            radiotuple=None, checklist=[self.checkBox_circle])

        # running functions at start:
        self.filebrowse_png(True)  # load in all images and go through update cycle

    # $$$$$$$$  functions relating to video editor
    def filebrowse_png(self, test=False):
        a = QtWidgets.QFileDialog()
        a.setDirectory("./data/png/")

        if test is False:
            path = str(a.getExistingDirectory(MainWindow, 'select folder with pngs'))
        else:
            path = "/home/jelle/PycharmProjects/UTMR/data/png/0313_stationary"
        # 'get existing directory' never uses the final '/' so you have to manually input it.
        self.lineEdit_importpath.setText(path)
        filelist = os.listdir(path)
        filelist.sort()
        if functions.auxiliary.checkifpng(filelist) == 0:
            functions.auxiliary.popupmsg("NO PNG IN FOLDER", "warning")
            self.pb_play.setEnabled(False)
            self.pb_play.setToolTip("Try selecting a folder with .png")
            return
        self.pb_play.setEnabled(True)
        self.pb_play.setToolTip("")
        cropsize = [58, 428, 143, 513]  # im = im[58:428, 143:513]
        self.imlist = functions.auxiliary.loadin(filelist, path, size=cropsize)
        self.CurMov.get_imlist(imlist=self.imlist)
        self.progress_bar.setMaximum(self.CurMov.maxframes)
        self.update_all_things(getvalue=True)
        #print(SliderClass.all_sliders)

    def next_frame(self):
        # called when the timer says it is time for the next frame
        # i.e. increments '.frame_number'
        self.CurMov.get_frame()  # MovieClass method to go to the next frame index
        if self.progress_bar.value() != self.CurMov.frame_number:
            self.progress_bar.setValue(self.CurMov.frame_number)  # edit the progress bar
        #print("next_frame")
        self.update_all_things()

    def pre_value_changed(self,key,fun):
        self.CurMov.value_changed(key,fun)
        if self.CurMov.currentframe is None:
            return
        self.update_all_things()

    def progress_bar_fun(self):
        # called when you (or the machine) change the progress bar in the video player
        self.CurMov.frame_number = self.progress_bar.value()
        self.CurMov.currentframe = self.CurMov.imlist[self.CurMov.frame_number]
        #print("progress_bar")
        self.update_all_things()


    def update_all_things(self, getvalue=False):
        # called whenever the main screen should be updated
        # display = cqpx(self.CurMov.currentframe)
        display = self.CurMov.update()
        self.mr_image.setPixmap(display)


        #print("update_all")
        #
        # imagelist = []
        # imagelist.append(self.CurMov.update())




    def play_button(self):
        if self.timer.isActive():
            return
        self.timer.start(50)

    # pause_button is through a lambda function.

    def reset_button(self):
        pass

    #
    #
    #
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
        dcm2pngworker = classes.class_extra.Worker1()
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
    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()
    ui = BuildUp()
    MainWindow.show()

    sys.exit(app.exec_())
