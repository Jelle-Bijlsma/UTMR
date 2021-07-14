import classes.class_frameclass


class MovieClass:
    def __init__(self):
        self.currentframe = 0
        self.maxframes = int
        self.framelist = []
        self.parameters = {'GLS': [0, 0, 0, 0]}
        # the parameters can be explained as follows
        # gls: brightness[0] boost[1]  lbound[2]  rbound[3]

        # self.b_filter_p = [False, 1, 0]   # on [0] cutoff [1] order [2]

    def create_frameclass(self, imlist):
        self.framelist.clear()  # in case of re-initialization empty the previous list.
        for element in imlist:
            self.framelist.append(classes.class_frameclass.FrameClass(element))
        self.maxframes = len(imlist) - 1

    def next_frame(self):
        if self.currentframe == self.maxframes:
            self.currentframe = 0
        else:
            self.currentframe += 1
        print("current frame is: " + str(self.currentframe))

    def return_frame(self):
        cframe = self.framelist[self.currentframe]  # cframe for [c]urrent frame
        cframe.return_info(self.parameters['GLS'])
        return cframe.qpix['main'], cframe.histogram, cframe.qpix['fft']

    # def getnewbfilter(self):
    #     # self.b_filter = functions.auxiliary.butter_filter(self.b_filter, self.b_filter_p[1], self.b_filter_p[2])
    #     pass
