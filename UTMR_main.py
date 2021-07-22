import os
import sys

import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets

import classes.class_extra
import classes.class_frameclass
import classes.class_movieclass
import functions.auxiliary
import functions.circle_tracking.circle_finder
from QT_Gui import gui_full
from functions.image_processing.image_process import change_qpix as cqpx


# the whole thing is just existing within this class.
class BuildUp(gui_full.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(MainWindow)
        # initialize timer video player. timer is started in the self.play_button
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.next_frame)

        self.threadpool = QtCore.QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        # start initializing variables
        self.CurMov = classes.class_movieclass.MovieClass()
        self.histogramx = list(range(0, 255))  # the x-range of the histogram
        self.bargraph = pg.BarGraphItem()  # the histogram widget inside plotwidget (which is called self.histogram)
        self.check_filter1.setChecked(1)

        # slider list for the GLS
        gls_sliderlist = [self.slider_brightness, self.slider_boost, self.slider_Lbound, self.slider_Rbound]
        gls_line_editlist = [self.lineEdit_Brightness, self.lineEdit_Boost,
                             self.lineEdit_Lbound, self.lineEdit_Rbound]
        self.My_gls_slider = classes.class_extra.SliderClass(gls_sliderlist, gls_line_editlist, self.sliderchange)

        # slider list for the b_filter
        b_filter_sliderlist = [self.slider_f_cutoff, self.slider_f_order]
        b_filter_line_editlist = [self.lineEdit_f_cutoff, self.lineEdit_f_order]
        self.My_b_filter_slider = classes.class_extra.SliderClass(b_filter_sliderlist, b_filter_line_editlist,
                                                                  self.b_filterchange, [self.check_filter1])

        # slider list for the G_filter
        g_filter_sliderlist = [self.slider_g_size, self.slider_g_sigX, self.slider_g_sigY]
        g_filter_line_editlist = [self.lineEdit_g_size, self.lineEdit_g_sigx, self.lineEdit_g_sigY]
        self.My_g_filter_slider = classes.class_extra.SliderClass(g_filter_sliderlist, g_filter_line_editlist,
                                                                  self.g_filterchange, [self.check_filter_g])

        # slider list for circle finding
        circle_finder_sliderlist = [self.slider_dp, self.slider_mindist, self.slider_param1, self.slider_param2,
                                    self.slider_minradius, self.slider_maxradius]
        circle_finder_line_editlist = [self.lineEdit_dp, self.lineEdit_minDist, self.lineEdit_param1,
                                       self.lineEdit_param2, self.lineEdit_minradius, self.lineEdit_maxradius]
        self.My_circlefinder_slider = classes.class_extra.SliderClass(circle_finder_sliderlist,
                                                                      circle_finder_line_editlist, self.circle_find)

        # slider list for sobel
        sobel_sliderlist = [self.slider_Skernel, self.slider_Sdst, self.slider_Sscale]
        sobel_line_editlist = [self.lineEdit_Skernel, self.lineEdit_Sdst, self.lineEdit_Sscale]
        self.My_sobel_slider = classes.class_extra.SliderClass(
            sobel_sliderlist, sobel_line_editlist, self.sobel_change, [self.checkBox_sobel])

        # load pictures in
        self.mr_image.setPixmap(QtGui.QPixmap("./QT_Gui/images/baseimage.png"))
        self.label_logo_uni.setPixmap((QtGui.QPixmap("./QT_Gui/images/UTlogo.png")))

        # self.stackedWidget.setCurrentIndex(0)  # initialize to homepage
        self.stackedWidget.setCurrentIndex(1)  # initialize to video-edit-page

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

        # dicom page
        self.pb_convert.clicked.connect(self.convert)
        self.pb_browse_dcm.clicked.connect(self.filebrowse_dcm)
        self.pb_reset_terminal.clicked.connect(self.txtbox_cmd.clear)

        # menu buttons
        self.actionMain.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.actionImage_processing.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.actionDicom_Edit.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.actionCircle_Tracking.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(3))

        # circle finder
        self.pb_newim.clicked.connect(self.circle_newim)

        # test (also very important)
        self.filebrowse_png(True)  # load in all images and go through update cycle
        self.sliderchange()  # load the slider brightness settings in, go through update cycle

    def sobel_change(self):
        params = self.My_sobel_slider.getvalue()
        main, side = self.CurMov.qimtest(params)
        self.label_qim_tester.setPixmap(side)
        self.mr_image.setPixmap(main)

    # $$$$$$$$  functions relating to video editor
    def b_filterchange(self):
        self.CurMov.parameters['b_filter'] = self.My_b_filter_slider.getvalue()
        self.CurMov.getnewbfilter()
        self.update_all_things()

    def g_filterchange(self):
        self.CurMov.parameters['g_filter'] = self.My_g_filter_slider.getvalue()
        self.CurMov.getnewgfilter()
        self.update_all_things()

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
        if functions.auxiliary.checkifpng(filelist) == 0:
            functions.auxiliary.popupmsg("NO PNG IN FOLDER", "warning")
            self.pb_play.setEnabled(False)
            self.pb_play.setToolTip("Try selecting a folder with .png")
            return
        self.pb_play.setEnabled(True)
        self.pb_play.setToolTip("")

        # create temp list of all images in np.array() format
        imlist = functions.auxiliary.loadin(filelist, path)
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

        qpix, histogram, fft, b_filter, g_filter = self.CurMov.return_frame()
        # self.mr_image.setPixmap(qpix)  # set the main image to the current Frame
        self.filter_image_g.setPixmap(g_filter)
        # histogram time
        newbar = pg.BarGraphItem(x=self.histogramx, height=histogram, width=5, brush='g')
        self.histogram.clear()
        self.bargraph = newbar
        self.histogram.addItem(self.bargraph)
        self.fourier_image.setPixmap(fft)
        self.filter_image1.setPixmap(b_filter)
        self.sobel_change()

    def framechange(self):
        # called when you (or the machine) change the progress bar in the video player
        slider_value = self.progress_bar.value()
        self.CurMov.currentframe = slider_value
        # updating the slider automatically (due to the movie playing, also triggers this command). This means
        # calling an update on the progress bar position by means of "progress.bar.setValue" will lead you back
        # an make for double calculations.

    def sliderchange(self):
        # [self.slider_brightness, self.slider_boost, self.slider_Lbound, self.slider_Rbound]
        self.CurMov.parameters['gls'] = self.My_gls_slider.getvalue()
        self.update_all_things()

    def play_button(self):
        # you could skip this check, on the expense that repeatedly pressing play lags the player a bit
        if self.timer.isActive():
            return
        self.timer.start(50)


    # pause_button is through a lambda function.

    def reset_button(self):
        self.CurMov.currentframe = 0
        self.My_gls_slider.valueset(0)
        self.My_b_filter_slider.valueset(0)
        self.My_g_filter_slider.valueset(0)
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

    # $$$$$$ functions related to circle finder
    def circle_newim(self):
        self.circim = functions.circle_tracking.circle_finder.new()
        self.label_imcircle.setPixmap(cqpx(self.circim))
        self.circle_find()

    def circle_find(self):
        if self.circim is None:
            self.circle_newim()
        parameters = self.My_circlefinder_slider.getvalue()
        img = functions.circle_tracking.circle_finder.update(self.circim, parameters)
        self.label_imcircle.setPixmap(cqpx(img))


if __name__ == "__main__":
    # chad no argument vs virgin sys.argv
    app = QtWidgets.QApplication([])
    MainWindow = QtWidgets.QMainWindow()
    ui = BuildUp()
    MainWindow.show()
    sys.exit(app.exec_())
