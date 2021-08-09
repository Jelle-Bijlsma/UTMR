import numpy as np


class MovieUpdate:

    def __init__(self):
        # we just initialize variables
        self.imlist = []
        self.frame = np.array([])
        self.imloaded = False
        self.maxframes = 0
        self.frame_number = 0
        self.parameters = {}
        self.currentframe = None

    def get_imlist(self, imlist):
        """
        This funciton is called whenever the 'self_imlist' is updated. Imlist is a concept which is used to artificially
        created the concept of an image stream together with "get_frame"
        It is not put in __init__ due to the 'imlist' being available only after the creation of the MovieUpdate class.
        """
        self.maxframes = len(imlist) - 1
        self.imlist = imlist
        self.currentframe = self.imlist[self.frame_number]

    def get_frame(self):
        """"
        Getframe will produce a new frame in the 'self.currentframe'
        """
        if self.imloaded is False:
            raise Exception("call 'get_imlist' first")
        # introduce a frame
        if self.frame_number == self.maxframes:
            self.frame_number = 0
        else:
            self.frame_number += 1
        self.currentframe = self.imlist[self.frame_number]

    def value_changed(self, key, fun):
        """"
        function is called through the update sliderclass
        """
        self.parameters[key] = fun()
        print(self.parameters)


    def update(self):
        # this is where we do all the cool stuff
        pass


