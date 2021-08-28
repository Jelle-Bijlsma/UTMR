import pickle
import sys
import os
import time
import warnings

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, QThreadPool
from PyQt5.QtGui import QPixmap, QColor

import classes.class_extra
import classes.movieclass_2 as mvc2
import functions.auxiliary
from QT_Gui import gui_full
from classes.class_extra import SliderClass as SliderClass


def set_to_ms(self: QtWidgets.QLineEdit,seconds,cutoff = 8, mode = 'normal',ns=False):
    if self.za is None:
        self.za = np.zeros(self.fps)
    if ns is False:
        ms = seconds * 100
    else:
        # this is really awkward but okay..
        ms = seconds

    if mode == 'normal':
        ms_string = self.strstr(ms,cutoff)

    #elif mode == 'avg':
    else:
        if self.tc == self.fps or self.tc == 0:
            self.tc = 0
            self.t_max = self.strstr(np.max(self.za),cutoff)
            self.t_min = self.strstr(np.min(self.za),cutoff)
        self.za[self.tc] = ms
        self.mean = np.mean(self.za)
        ms_string = self.strstr(self.mean,cutoff)
        self.tc += 1

    self.setText(ms_string)

def strip_str(self, num,cutoff):
    return str(num)[0:cutoff]

def start(self: QtWidgets.QLineEdit, ns = False):
    if ns is False:
        self.start_t = time.perf_counter()
    else:
        self.start_t = time.perf_counter_ns()

def stop(self: QtWidgets.QLineEdit,cutoff = 8, mode = 'normal',ns = False):
    if ns is False:
        elapsed = time.perf_counter() - self.start_t
    else:
        elapsed = time.perf_counter_ns() - self.start_t

    self.setTime(elapsed, cutoff, mode, ns=ns)



QtWidgets.QLineEdit.setTime = set_to_ms
QtWidgets.QLineEdit.start = start
QtWidgets.QLineEdit.stop = stop
QtWidgets.QLineEdit.strstr = strip_str

QtWidgets.QLineEdit.tc = 0  # times called (tc)
QtWidgets.QLineEdit.start_t = 0
QtWidgets.QLineEdit.za = None
QtWidgets.QLineEdit.fps = 15

# the whole thing is just existing within this class.
class BuildUp(QtWidgets.QMainWindow, gui_full.Ui_MainWindow):
    def __init__(self, parent=None):
        super(BuildUp, self).__init__(parent)
        self.setupUi(MainWindow)
        # start initializing variables
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.timer_value = self.spinbox_fps.value()
        self.threadpool = QThreadPool()
        self.CurMov = mvc2.MovieUpdate()  # name of the class
        self.imlist = []
        self.histogramx = list(range(0, 255))  # the x-range of the histogram
        self.bargraph = pg.BarGraphItem()  # the histogram widget inside plotwidget (which is called self.histogram)
        self.morphstatus = False
        self.floodparam = False
        self.radio_circle = False
        self.radio_image = True
        self.circleparam = False
        self.coords = None
        self.past_10 = np.zeros(10)
        self.update_call = 0
        self.req_time = 0
        self.FPS = self.spinBox_FPS.value()

        self.frametime = time.perf_counter()

        self.valid_ops = ["dilate", "erosion", "m_grad", "blackhat", "whitehat"]
        radiotuple = (self.radioButton_image, self.radioButton_circle)

        #                       image = 0       circle = 1
        self.morph_state = [[False, "image"], [False, "dilate kernel: 7 shape: 0"]]

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
            slides=sl_gfilter, line_edits=le_gfilter, function=self.pre_value_changed, keyword='g_filter',
            radiotuple=radiotuple, checklist=[self.check_filter_g])

        # slider list for sobel
        sl_sobel = [self.slider_Skernel, self.slider_Sdst, self.slider_Sscale]
        le_sobel = [self.lineEdit_Skernel, self.lineEdit_Sdst, self.lineEdit_Sscale]
        self.My_sobel_slider = SliderClass(
            slides=sl_sobel, line_edits=le_sobel, function=self.pre_value_changed, keyword='sobel',
            radiotuple=radiotuple, checklist=[self.checkBox_sobel])

        # slider list for canny
        sl_canny = [self.slider_Cthresh1, self.slider_Cthresh2]
        le_canny = [self.lineEdit_Cthresh1, self.lineEdit_Cthresh2]
        self.My_canny_slider = SliderClass(
            slides=sl_canny, line_edits=le_canny, function=self.pre_value_changed, keyword='canny',
            radiotuple=radiotuple, checklist=[self.checkBox_Canny])

        # slider list for circle finding
        sl_cf = [self.slider_dp_2, self.slider_mindist_2, self.slider_param1_2,
                 self.slider_param2_2, self.slider_minradius_2, self.slider_maxradius_2]
        le_cf = [self.lineEdit_dp_2, self.lineEdit_minDist_2, self.lineEdit_param1_2,
                 self.lineEdit_param2_2, self.lineEdit_minradius_2, self.lineEdit_maxradius_2]
        self.SC_circlefinder = SliderClass(
            slides=sl_cf, line_edits=le_cf, function=self.pre_value_changed, keyword='circlefinder',
            radiotuple=None, checklist=[self.checkBox_circle])

        sl_tm = [self.slider_template, self.slider_tm_safe, self.slider_tm_medium, self.slider_tm_danger]
        le_tm = [self.lineEdit_template, self.lineEdit_tm_safe, self.lineEdit_tm_medium, self.lineEdit_tm_danger]
        self.SC_template = SliderClass(slides=sl_tm, line_edits=le_tm, function=self.pre_value_changed,
                                       keyword='template', radiotuple=None, checklist=[self.checkBox_template])

        sl_lf = [self.slider_lf_ar, self.slider_lf_dr, self.slider_lf_thr, self.slider_lf_minl, self.slider_lf_maxl,
                 self.slider_bb_minr, self.slider_bb_maxr]
        le_lf = [self.lineEdit_lf_ar, self.lineEdit_lf_dr, self.lineEdit_lf_thr, self.lineEdit_lf_minl,
                 self.lineEdit_lf_maxl, self.lineEdit_bb_minr, self.lineEdit_bb_maxr]
        self.SC_lf = SliderClass(slides=sl_lf, line_edits=le_lf, function=self.pre_value_changed,
                                 keyword='linefinder', radiotuple=None, checklist=[self.checkBox_lf])

        # this makes sure there are keys for the circle finding as well
        self.radioButton_circle.setChecked(True)
        for clazz in SliderClass.all_sliders:
            clazz.getvalue()
            print(f"{clazz.keyword} has the following params {clazz._params_image}")
            clazz._coolfun()
        self.radioButton_image.setChecked(True)

        # putting this ahead of the button switching causes problems due to morph switch actually
        # updating some values calling an indirect 'update_all'
        self.radioButton_image.toggled.connect(self.morph_switch)
        # .radioButton_circle.toggled.connect(self.morph_switch)

        # load pictures in
        # self.mr_image.setPixmap(QPixmap("./QT_Gui/images/baseimage.png"))
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
        self.spinBox_FPS.valueChanged.connect(self.play_button)
        self.pb_pause.clicked.connect(lambda: self.timer.stop())
        self.pb_save_params.clicked.connect(self.para_saver)
        self.pb_load_params.clicked.connect(self.para_loader)

        # dicom page
        self.pb_convert.clicked.connect(self.convert)
        self.pb_browse_dcm.clicked.connect(self.filebrowse_dcm)
        self.pb_reset_terminal.clicked.connect(self.txtbox_cmd.clear)

        # menu buttons
        self.actionMain.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.actionImage_processing.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.actionDicom_Edit.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.actionCircle_Tracking.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(3))

        # morphology:
        self.dilation.clicked.connect(lambda: self.morphstring_add("dilate"))
        self.erosion.clicked.connect(lambda: self.morphstring_add("erosion"))
        self.m_grad.clicked.connect(lambda: self.morphstring_add("m_grad"))
        self.blackhat.clicked.connect(lambda: self.morphstring_add("blackhat"))
        self.white_hat.clicked.connect(lambda: self.morphstring_add("whitehat"))

        self.checkBox_morph.stateChanged.connect(self.startmorph)
        self.mr_image.mousePressEvent = self.get_pixel
        self.mr_image_2.mousePressEvent = self.get_pixel
        self.checkBox_segment.stateChanged.connect(self.update_all_things)

        # timers

        # running functions at start:
        self.filebrowse_png(True)  # load in all images and go through update cycle
        self.para_loader("./data/parameters/params_tm.txt")

    # $$$$$$$$  functions relating to video editor
    def para_saver(self):
        para_list = []
        path = self.lineEdit_params.text()
        print(path)
        radio_is_circle = self.radioButton_circle.isChecked()

        if radio_is_circle:
            self.radioButton_image.setChecked(True)

        file = open(path, 'wb')
        for clazz in SliderClass.all_sliders:
            para1 = clazz._params_image
            para_list.append(para1)
            if clazz.radio_image is not None:
                para2 = clazz._params_circle
                para_list.append(para2)
        para_list.append(self.morph_state)
        para_list.append(self.coords)
        para_list.append(self.checkBox_segment.isChecked())
        para_list.append(radio_is_circle)
        # self.morph_state = [[False, "image"], [False, "dilate kernel: 7 shape: 0"]]

        pickle.dump(para_list, file)
        file.close()

        if radio_is_circle:
            self.radioButton_circle.setChecked(True)

    def para_loader(self, path=True):
        if path is True:
            path = self.lineEdit_params.text()
        print(path)

        file = open(path, 'rb')
        loaded_p_list = pickle.load(file)
        file.close()
        counter = 0

        radio_is_image = self.radioButton_circle.isChecked()

        if radio_is_image:
            self.radioButton_image.setChecked(True)

        for clazz in SliderClass.all_sliders:

            # ## if you added a new sliderclass and want to load your old parameters, you can use this little hack
            # classname = 'linefinder'
            # #print(loaded_p_list[counter])
            # #print(f"the latest keyword = {clazz.keyword}")
            # if clazz.keyword == [classname]:
            #     warnings.warn("parameters are messed up! save new ones")
            #     break

            try:
                clazz.settr(loaded_p_list[counter])
                counter += 1
                if clazz.radio_image is not None:
                    clazz._params_circle = loaded_p_list[counter]
                    counter += 1
            except IndexError:
                # again a small hack for when you add an extra element to the class and this is not yet implemented
                # in your parameter saves.
                warnings.warn("parameters are messed up! save new ones")
                counter += 1
        print(f"should be morph: {loaded_p_list[counter]}")
        # in the save, manually set the morph_state as the final thing to load in
        self.morph_state = loaded_p_list[counter]
        self.checkBox_morph.setChecked(self.morph_state[0][0])
        self.textEdit_morph.setText(self.morph_state[0][1])

        self.coords = loaded_p_list[counter + 1]
        self.checkBox_segment.setChecked(loaded_p_list[counter + 2])
        self.lineEdit_coords.setText(str(self.coords))
        radio_is_circle = loaded_p_list[counter + 3]

        if radio_is_circle:
            self.radioButton_circle.setChecked(True)
            self.radioButton_circle.click()

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
        cropsize = [58, 428, 243, 413]  # im = im[58:428, 143:513]
        self.imlist = functions.auxiliary.loadin(filelist, path, size=cropsize)
        self.CurMov.get_imlist(imlist=self.imlist)
        self.progress_bar.setMaximum(self.CurMov.maxframes)
        self.update_all_things()
        # print(SliderClass.all_sliders)

    def next_frame(self):
        # called when the timer says it is time for the next frame
        # i.e. increments '.frame_number'
        current_time = time.perf_counter()
        self.lineEdit_frameT.setTime(current_time-self.frametime)
        self.frametime = current_time

        self.CurMov.get_frame()  # MovieClass method to go to the next frame index
        if self.progress_bar.value() != self.CurMov.frame_number:
            self.progress_bar.setValue(self.CurMov.frame_number)  # edit the progress bar

        # don't call update_all here. it is already done by the moving progress bar.

    def pre_value_changed(self, key, fun):
        self.CurMov.value_changed(key, fun)
        # in the initialisation step do not update all
        if self.CurMov.currentframe is None:
            return
        self.update_all_things()

    def progress_bar_fun(self):
        # called when you (or the machine) change the progress bar in the video player
        self.CurMov.frame_number = self.progress_bar.value()
        # whenever current frame is changed, the used_parameters must be destroyed
        self.CurMov.currentframe = self.CurMov.imlist[self.CurMov.frame_number]
        self.CurMov.used_parameters = {}

        # print("progress_bar")
        self.update_all_things()

    def update_all_things(self):
        # called whenever the main screen should be updated
        self.lineEdit_uaT.start()

        check_input = [self.checkBox_sobel, self.checkBox_Canny]
        if self.morph_state[0][1] == "image":
            # only done on initializer run
            self.morph_state[0][0] = self.checkBox_morph.isChecked()
            self.morph_state[0][1] = self.textEdit_morph.toPlainText()
        morph_vars = [self.morph_state, self.valid_ops, self.checkBox_morph]
        segment_state = [self.checkBox_segment, self.coords]
        circ_state = []
        self.lineEdit_sumT.start()

        timer_list = [self.lineEdit_glsT,self.lineEdit_preT,self.lineEdit_edgeT,self.lineEdit_morphT,
                      self.lineEdit_segT,self.lineEdit_lfT, self.lineEdit_cqpx, self.lineEdit_tmT,
                      self.lineEdit_sortT]

        output = self.CurMov.update(check_input, morph_vars, segment_state, circ_state,timer_list)
        self.lineEdit_sumT.stop()
        # to implement:!
        # Depending on the RADIOBUTTON: show different images..

        self.lineEdit_dispT.start()

        if self.radioButton_image.isChecked():
            self.histogram.clear()
            self.histogram.addItem(pg.BarGraphItem(x=self.histogramx, height=output[0][2], width=5, brush='g'))
            self.filter_image1.setPixmap(output[0][3])
            self.label_qim_tester.setPixmap(output[0][4])
            self.fourier_image.setPixmap(output[0][5])
            self.filter_image_g.setPixmap(output[0][6])
            self.label_mask_im.setPixmap(output[0][9])
            self.mr_image.setPixmap(output[0][10])
        else:
            self.histogram.clear()
            self.histogram.addItem(pg.BarGraphItem(x=self.histogramx, height=output[1][1], width=5, brush='g'))
            self.filter_image1.setPixmap(output[1][2])
            self.label_qim_tester.setPixmap(output[1][10])
            self.fourier_image.setPixmap(output[1][4])
            self.filter_image_g.setPixmap(output[1][5])
            self.label_mask_im.setPixmap(output[0][9])
            if self.checkBox_template.isChecked():
                self.mr_image.setPixmap(output[1][9])
            else:
                self.mr_image.setPixmap(output[1][8])

        if output[1][11] != []:
            self.lineEdit_tip_a.setText(str(round(output[1][11][0])))
            self.lineEdit_wall_a.setText(str(round(output[1][11][1])))
        if output[1][12] != []:
            self.lineEdit_tip_wall.setText(str(output[1][12][0]))
            self.lineEdit_closest.setText(str(min(output[1][12])))
        self.mr_image_2.setPixmap(output[0][0])
        self.lineEdit_dispT.stop(mode='avg')

        # now you want to do update2, on the improved and cutout frame..

        self.lineEdit_uaT.stop(mode='avg')
        self.lineEdit_uaT_min.setText(self.lineEdit_uaT.t_min)
        self.lineEdit_uaT_max.setText(self.lineEdit_uaT.t_max)

        self.lineEdit_difT.setText(str(self.req_time*100-self.lineEdit_uaT.mean)[0:8])


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
        """"
        Checking function to see if the operation is spelled correctly, and if not, color the corresponding
        operation red. The addition of kernel + size was done later, and thus no error checking exists for that
        yet..
        """
        cursor_pos = 0
        clrR = QColor(255, 0, 0, 255)
        clrB = QColor(0, 0, 0, 255)
        cursor = self.textEdit_morph.textCursor()

        if self.radioButton_image.isChecked():
            self.morph_state[0][0] = self.checkBox_morph.isChecked()
        else:
            self.morph_state[1][0] = self.checkBox_morph.isChecked()

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
                self.checkBox_morph.setChecked(False)

        if self.radioButton_circle.isChecked():
            self.morph_state[1][1] = self.textEdit_morph.toPlainText()
        else:
            self.morph_state[0][1] = self.textEdit_morph.toPlainText()

        self.update_all_things()

    def morph_switch(self):
        # use self.morph_state to transfer
        # state checkboxes being checked
        # and text in textbox
        if self.radioButton_image.isChecked() is True:
            # recording values
            self.morph_state[1][0] = self.checkBox_morph.isChecked()
            self.morph_state[1][1] = self.textEdit_morph.toPlainText()
            # setting them
            self.checkBox_morph.setChecked(self.morph_state[0][0])
            self.textEdit_morph.setText(self.morph_state[0][1])

        if self.radioButton_circle.isChecked() is True:
            # recording values
            self.morph_state[0][0] = self.checkBox_morph.isChecked()
            self.morph_state[0][1] = self.textEdit_morph.toPlainText()
            # setting them
            self.checkBox_morph.setChecked(self.morph_state[1][0])
            self.textEdit_morph.setText(self.morph_state[1][1])

    def get_pixel(self, event):
        x = event.pos().x()
        y = event.pos().y()
        h, w = self.CurMov.currentframe.shape
        xtot = self.mr_image.width()
        ytot = self.mr_image.height()
        x = int((x / xtot) * w)
        y = int((y / ytot) * h)
        print(f"rescaled x = {x}, rescaled y = {y}")
        coords = f"x:{x}, y:{y}"
        self.coords = (x, y)
        self.lineEdit_coords.setText(coords)

    def play_button(self):
        self.FPS = self.spinBox_FPS.value()
        self.req_time = 1/self.FPS
        current_timer = int((self.req_time) * 1000)
        self.lineEdit_tfpsT.setTime(self.req_time)
        if self.timer_value != current_timer:
            self.timer.stop()
            self.timer.start(current_timer)
            self.timer_value = current_timer
        if self.timer.isActive():
            return
        self.timer.start(current_timer)

        # set update rate on mean/avg in line_edits for timers.
        QtWidgets.QLineEdit.za = np.zeros(self.FPS)  # zero array (za)
        QtWidgets.QLineEdit.fps = self.FPS

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
        except FileNotFoundError:
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
