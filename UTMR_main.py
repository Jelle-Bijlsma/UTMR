import os
import sys

from PyQt5.QtCore import QTimer, QThreadPool
from PyQt5.QtGui import QPixmap, QColor
from PyQt5 import QtWidgets
import pyqtgraph as pg

import classes.class_extra
import classes.class_frameclass
import classes.class_movieclass
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
        # initialize timer video player. timer is started in the self.play_button
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.coords = None
        # morph
        self.morphstatus = False
        self.floodparam = False
        self.radio_circle = False
        self.radio_image = True
        self.circleparam = False
        # this is a double, should be passed through function but frameclass has an independent
        # variable too
        self.valid_ops = ["dilate", "erosion", "m_grad", "blackhat", "whitehat"]

        self.threadpool = QThreadPool()
        # print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

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

        # slider list for circle finding IN THE REAL DEAL
        circle_finder_sliderlist_2 = [self.slider_dp_2, self.slider_mindist_2, self.slider_param1_2,
                                      self.slider_param2_2, self.slider_minradius_2, self.slider_maxradius_2]
        circle_finder_line_editlist_2 = [self.lineEdit_dp_2, self.lineEdit_minDist_2, self.lineEdit_param1_2,
                                         self.lineEdit_param2_2, self.lineEdit_minradius_2, self.lineEdit_maxradius_2]
        self.My_circlefinder_slider_2 = classes.class_extra.SliderClass(
            circle_finder_sliderlist_2, circle_finder_line_editlist_2, self.circle_change)

        # slider list for sobel
        sobel_sliderlist = [self.slider_Skernel, self.slider_Sdst, self.slider_Sscale]
        sobel_line_editlist = [self.lineEdit_Skernel, self.lineEdit_Sdst, self.lineEdit_Sscale]
        self.My_sobel_slider = classes.class_extra.SliderClass(
            sobel_sliderlist, sobel_line_editlist, self.edge_change, [self.checkBox_sobel])

        # slider list for canny
        canny_sliderlist = [self.slider_Cthresh1, self.slider_Cthresh2]
        canny_line_editlist = [self.lineEdit_Cthresh1, self.lineEdit_Cthresh2]
        self.My_canny_slider = classes.class_extra.SliderClass(canny_sliderlist, canny_line_editlist,
                                                               self.edge_change, [self.checkBox_Canny])

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

        # app.focusChanged.connect(self.on_focuschanged)

        # square move
        self.SqMv = TwoDclass.TwoDimMover([500, 500])
        self.centralwidget.setFocus()

        # morphology:
        self.dilation.clicked.connect(lambda: self.morphstring_add("dilate"))
        self.erosion.clicked.connect(lambda: self.morphstring_add("erosion"))
        self.m_grad.clicked.connect(lambda: self.morphstring_add("m_grad"))
        self.blackhat.clicked.connect(lambda: self.morphstring_add("blackhat"))
        self.white_hat.clicked.connect(lambda: self.morphstring_add("whitehat"))

        self.checkBox_morph.pressed.connect(self.startmorph)
        self.mr_image.mousePressEvent = self.get_pixel
        self.checkBox_segment.pressed.connect(self.floodit)

        # circle finding
        self.radioButton_image.setChecked(True)
        self.radioButton_circle.toggled.connect(self.changestat)
        self.radioButton_image.toggled.connect(self.changestat)
        self.checkBox_circle.pressed.connect(self.find_circle)

    # $$$$$$$$  functions relating to video editor
    def find_circle(self):
        # this is just copy paste drama and can be simplified.
        if self.checkBox_circle.isChecked() is True:
            self.circleparam = False
        else:
            self.circleparam = True

        self.update_all_things()

    def changestat(self):
        if self.radioButton_circle.isChecked() is False:
            self.radio_circle = False
            self.radio_image = True
        else:
            self.radio_circle = True
            self.radio_image = False

        # print(f"circle = {self.radio_circle}, image = {self.radio_image}")

    def floodit(self):
        # meaning it is not checked
        if self.checkBox_segment.isChecked() is True:
            self.floodparam = False
        else:
            self.floodparam = True

        self.update_all_things()

    def morphstring_add(self, stringz):
        """"
        function called when new text is added to the 'textEdit_morph' box in the morphology tab.
        TextColor is set to black, data is pulled from the 'spinBox' regarding kernel size
        and the comboBox for kernel shape.

        cv2.getStructuringElement uses a '0,1,2' notation for sq. rect. ellipse, thus the index of the
        dropdown menu corresponds to these.
        """
        self.textEdit_morph.setTextColor(QColor(0, 0, 0, 255))
        stringz += f" kernel: {self.spinBox.value()} shape: {self.comboBox.currentIndex()}"
        self.textEdit_morph.append(stringz)

    def startmorph(self):
        error = self.checkmorph()
        if error == 1:
            # if there is an error in the checker, uncheck the checkbox
            self.checkBox_morph.setChecked(True)
            self.morphstatus = False
            self.update_all_things()
            return

        # dont think this applies now..
        if self.checkBox_morph.isChecked() is not False:
            # if the code is called when the checkbox is unchecked, return
            self.morphstatus = False
            self.update_all_things()
            return

        self.morphstatus = True
        self.update_all_things()

    def checkmorph(self):
        """"
        Checking function to see if the operation is spelled correctly, and if not, color the corresponding
        operation red. The addition of kernel + size was done later, and thus no error checking exists for that
        yet..
        """
        errorcode = 0
        cursor_pos = 0
        clrR = QColor(255, 0, 0, 255)
        clrB = QColor(0, 0, 0, 255)
        cursor = self.textEdit_morph.textCursor()

        for element in self.textEdit_morph.toPlainText().split('\n'):
            # split the full textEdit_morph up into newlines
            starter = element.split(' ')
            # split the newlines up into words
            if starter[0] in self.valid_ops:
                # we color it black, in case it previously has been colored red.
                # could color all black on each iteration and recolor all the reds. too bad!
                cursor.setPosition(cursor_pos)
                cursor.movePosition(20, 1, 1)
                self.textEdit_morph.setTextCursor(cursor)
                self.textEdit_morph.setTextColor(clrB)
                cursor_pos += len(element) + 1
                # print(cursor_pos)
                cursor.setPosition(0)
                # calls to setTextCursor are made to move the cursor to the actual position on screen
                self.textEdit_morph.setTextCursor(cursor)
            else:
                # maybe move next 7 lines into morp, and call it for this 1 and the previous 1?
                cursor.setPosition(cursor_pos)
                cursor.movePosition(20, 1, 1)
                self.textEdit_morph.setTextCursor(cursor)
                self.textEdit_morph.setTextColor(clrR)
                cursor_pos += len(element) + 1
                cursor.setPosition(0)
                self.textEdit_morph.setTextCursor(cursor)
                print("something is wrong!!")
                errorcode = 1
        return errorcode

    def get_pixel(self, event):
        x = event.pos().x()
        y = event.pos().y()
        h, w = self.CurMov.get_og_frame().shape
        xtot = self.mr_image.width()
        ytot = self.mr_image.height()
        x = int((x / xtot) * w)
        y = int((y / ytot) * h)
        print(f"rescaled x = {x}, rescaled y = {y}")
        coords = f"x:{x}, y:{y}"
        self.coords = (x, y)
        self.lineEdit_coords.setText(coords)

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

        # create temp list of all images in np.array() format
        # im = im[58:428, 143:513]
        imlist = functions.auxiliary.loadin(filelist, path, size=[58, 428, 143, 513])
        # the loadin function does the RESIZE.
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

        # GLS
        qpix, histogram, fft, b_filter, g_filter = self.CurMov.return_frame()
        # self.mr_image.setPixmap(qpix)  # set the main image to the current Frame
        # self.filter_image_g.setPixmap(g_filter)  # i think this can go down
        # histogram time
        newbar = pg.BarGraphItem(x=self.histogramx, height=histogram, width=5, brush='g')
        self.histogram.clear()
        self.bargraph = newbar
        self.histogram.addItem(self.bargraph)
        # FFT
        self.fourier_image.setPixmap(fft)
        # FILTERS
        self.filter_image_g.setPixmap(g_filter)
        self.filter_image1.setPixmap(b_filter)
        # EDGES
        self.edge_change(killer=True)
        main, side = self.CurMov.edge_call()
        self.label_qim_tester.setPixmap(side)
        self.mr_image.setPixmap(main)

        # MORPH

        if self.morphstatus is True:
            temp = self.CurMov.morphstart(self.textEdit_morph.toPlainText())
            print("return")
            self.mr_image.setPixmap(temp)

        if self.floodparam is True:
            if self.coords is None:
                print("pls click image :DD")
                return
            mask, masked_im = self.CurMov.call_flood(self.coords)
            self.mr_image.setPixmap(masked_im)
            self.label_mask_im.setPixmap(mask)
            # round 2, fight!
            self.CurMov.gls2()                      # GLS
            temp1 = self.CurMov.gfilter2()                  # Gfilter
            temp2 = self.CurMov.edge_call2()         # Canny
            self.mr_image_2.setPixmap(temp2)

        if self.circleparam is True:
            temp = self.CurMov.circlefind()
            self.mr_image_2.setPixmap(temp)
            self.mr_image.setPixmap(cqpx(self.CurMov.get_og_frame()))

    def framechange(self):
        # called when you (or the machine) change the progress bar in the video player
        slider_value = self.progress_bar.value()
        self.CurMov.currentframe = slider_value
        # updating the slider automatically (due to the movie playing, also triggers this command). This means
        # calling an update on the progress bar position by means of "progress.bar.setValue" will lead you back
        # an make for double calculations.

    def circle_change(self):
        self.CurMov.parameters['hough'] = self.My_circlefinder_slider_2.getvalue
        self.update_all_things()

    def edge_change(self, jemo = 0, eder = 0, killer=False):
        # WHAT DOES the clicked.connect and Valuechange return in SETFUN in CLASS EXTRA?
        # so this is a completely different strat here.
        # why did i do it like this...........
        if self.radio_image is True:
            self.CurMov.parameters['sobel'] = self.My_sobel_slider.getvalue
            self.CurMov.parameters['canny'] = self.My_canny_slider.getvalue
        if self.radio_circle is True:
            self.CurMov.parameters['sobel2'] = self.My_sobel_slider.getvalue
            self.CurMov.parameters['canny2'] = self.My_canny_slider.getvalue

        print(killer)
        if killer is False:
            self.update_all_things()

    def b_filterchange(self):
        self.CurMov.parameters['b_filter'] = self.My_b_filter_slider.getvalue
        self.CurMov.getnewbfilter()
        self.update_all_things()

    def g_filterchange(self):
        if self.radio_image is True:
            self.CurMov.parameters['g_filter'] = self.My_g_filter_slider.getvalue
        if self.radio_circle is True:
            self.CurMov.parameters['g_filter2'] = self.My_g_filter_slider.getvalue
        self.CurMov.getnewgfilter()
        self.update_all_things()

    def sliderchange(self):
        # [self.slider_brightness, self.slider_boost, self.slider_Lbound, self.slider_Rbound]
        if self.radio_image is True:
            self.CurMov.parameters['gls'] = self.My_gls_slider.getvalue
        if self.radio_circle is True:
            self.CurMov.parameters['gls2'] = self.My_gls_slider.getvalue
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

    # $$$$$$ functions related to circle finder
    def circle_newim(self):
        self.circim = functions.circle_tracking.circle_finder.new()
        self.label_imcircle.setPixmap(cqpx(self.circim))
        self.circle_find()

    def circle_find(self):
        if self.circim is None:
            self.circle_newim()
        parameters = self.My_circlefinder_slider.getvalue
        img = functions.circle_tracking.circle_finder.update(self.circim, parameters)
        self.label_imcircle.setPixmap(cqpx(img))


if __name__ == "__main__":
    # chad no argument vs virgin sys.argv
    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()
    ui = BuildUp()
    MainWindow.show()

    sys.exit(app.exec_())
