import numpy as np
import classes.class_frameclass
import functions.image_process
from functions.image_process import change_qpix as cqpx


class MovieClass:
    def __init__(self):
        self.currentframe = 0
        self.maxframes = int
        self.framelist = []
        self.parameters = {'gls': [0, 0, 0, 0], 'b_filter': [False, 1, 0], 'shape': (0, 0),
                           'g_filter': [False, 0, 0]}
        # the parameters can be explained as follows
        # gls:          brightness[0] boost[1]  lbound[2]  rbound[3]
        # b_filter:     on/off [0] cutoff [1] order [2]
        # shape:        size of the frames (x,y)
        self.filters = {'b_filter': np.array([]), 'g_filter': np.array([])}
        self.qpix = {'b_filter': cqpx(np.array([])), 'g_filter': cqpx(np.array([]))}

    def create_frameclass(self, imlist):
        self.framelist.clear()  # in case of re-initialization empty the previous list.
        for element in imlist:
            self.framelist.append(classes.class_frameclass.FrameClass(element))
        self.maxframes = len(imlist) - 1
        self.parameters['shape'] = self.framelist[self.maxframes].parameters['shape']
        # (370, 370) for current call
        self.getnewbfilter()

    def next_frame(self):
        if self.currentframe == self.maxframes:
            self.currentframe = 0
        else:
            self.currentframe += 1
        print("current frame is: " + str(self.currentframe))

    def return_frame(self):
        print("return called")
        print(self.parameters['gls'])
        cframe = self.framelist[self.currentframe]  # cframe for [c]urrent frame
        cframe.return_info(self.parameters['gls'], self.parameters['b_filter'][0], self.filters['b_filter'],
                           self.parameters['g_filter'][0], self.filters['g_filter'])
        return cframe.qpix['main'], cframe.histogram, cframe.qpix['fft'], self.qpix['b_filter'], self.qpix['g_filter']

    def getnewbfilter(self):
        # the filter is 'good looking' meaning it is centered aesthetically.
        self.filters['b_filter'] = functions.image_process.butter_filter(
            self.parameters['shape'], self.parameters['b_filter'][1], self.parameters['b_filter'][2])
        self.qpix['b_filter'] = cqpx(self.filters['b_filter'])

    def getnewgfilter(self):
        self.filters['g_filter'] = functions.image_process.gaus_filter(
            self.parameters['shape'], self.parameters['g_filter'][1], self.parameters['g_filter'][2],
            self.parameters['g_filter'][3])
        self.qpix['g_filter'] = cqpx(self.filters['g_filter'])
