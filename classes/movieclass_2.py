import copy

import numpy as np

import functions.image_processing.base_fun as ipgun
# specific call since it is used often (and maybe a bit legacy)
from functions.image_processing.base_fun import change_qpix as cqpx


def check_equal(fun, first_result: tuple, keyword, **kwargs):
    """"
    function checks if anything changed..
    If it didnt it returns the cached value. This speeds up the calculation later on
    """

    # to note, kwargs is a dictionary.
    # used params should always be passed last
    used_params = first_result[-1]

    if not isinstance(used_params, dict):
        raise ValueError(f"last passed variable type is {type(used_params)}, not dict!")

    if keyword in used_params:
        if kwargs['parameters'] == used_params[keyword]:
            # print("save a calc")
            # when the parameters in the 'used' bin are the same as the fed parameters, return cached
            return first_result

    # if not the same, do the calculation with all the keyword arguments
    a = fun(**kwargs)
    newdict = copy.copy(used_params)
    popmode = False
    for key in used_params:
        if keyword == key:
            popmode = True
        if popmode is True:
            newdict.pop(key)
    # and save the parameters in the 'used_params' variable
    newdict[keyword] = kwargs['parameters']
    return a + (newdict,)


class MovieUpdate:

    def __init__(self):
        # we just initialize variables
        self.imlist = []
        self.frame = np.array([])
        self._imloaded = False
        self.maxframes = 0
        self.frame_number = 2
        self.parameters = {}
        self.used_parameters = {}
        self.currentframe = None

        # results
        self.gls_image = []
        self.histogram = []
        self.b_filter = []
        self.g_filter = []
        self.fourier = []
        self.filtered_image1 = []

    def get_imlist(self, imlist):
        """
        This funciton is called whenever the 'self_imlist' is updated. Imlist is a concept which is used to artificially
        created the concept of an image stream together with "get_frame"
        It is not put in __init__ due to the 'imlist' being available only after the creation of the MovieUpdate class.
        """
        self.maxframes = len(imlist) - 1
        self.imlist = imlist
        self.currentframe = self.imlist[self.frame_number]
        self._imloaded = True

    def get_frame(self):
        """"
        Getframe will produce a new frame in the 'self.currentframe'
        """
        if self._imloaded is False:
            raise Exception("call 'get_imlist' first")
        # introduce a frame
        if self.frame_number == self.maxframes:
            self.frame_number = 1
        else:
            self.frame_number += 1
        self.currentframe = self.imlist[self.frame_number]
        # destroy the used_parameters dictionary.
        self.used_parameters = {}

    def value_changed(self, key, fun):
        """"
        function is called through the update sliderclass
        """
        key = "".join(key)
        self.parameters[key] = fun()
        # print(self.parameters)

    def update(self,boxes):
        para = self.parameters
        base_image = np.copy(self.currentframe)

        """"
        This part is left in since it refers to the 'check_equal' which is a function to check whether calcs
        are not done too often. Say you are changing a hough circlefinding parameter... Now, the code recalculates
        everything, starting from GLS. Bailed on the idea because I couldn't make it work here. Sort of worked during
        the 'movieclass/frameclass' era, however I bailed on the idea since the code should be able to complete fully
        in 1/15 seconds, so the time gain is mariginal w.r.t. the added complexity. Left it in as an exercise to the 
        reader. Maybe ditch equality checks and use a more direct assignment approach with saved state variables as
        in 'movieclass/frameclass'?
        
        # 'expected_outcome' should be: return values of 'fun' from 'check_equal' + 'used_parameters'
        # 'check_equal' goes like: 'fun' to check, 'expected_outcome', keyword (for dict), and keyword variables
        # that go into 'fun'.
        # do graylevel slicing and calculate the histogram. Only KWARGS go into the function itself
        expected_outcome = (self.gls_image, self.histogram, self.used_parameters)
        self.gls_image, self.histogram, self.used_parameters = check_equal(
            ipgun.calc_gls, expected_outcome, 'GLS', image=base_image, parameters=para['GLS'])
        """

        gls_image, histogram = ipgun.calc_gls(base_image, para['GLS'])
        b_filter = ipgun.b_filter(
            parameters=para['b_filter'], shape=np.shape(self.currentframe))
        g_filter = ipgun.g_filter(
            parameters=para['g_filter'], shape=np.shape(self.currentframe))
        # 'fourier' is raw complex128.
        # para['b_filter'] is only needed for the checkbox
        filtered_image1, fourier, = ipgun.apply_filter(parameters=para['b_filter'], filterz=b_filter,
                                                                 image=gls_image)
        filtered_image2, fourier, = ipgun.apply_filter(parameters=para['g_filter'], filterz=g_filter,
                                                       image=filtered_image1)
        # call 2 edge function, to determine wheter canny or sobel is used...
        edge_found = ipgun.edge_call(boxes,filtered_image2,para['canny'],para['sobel'])

        return cqpx(gls_image), histogram, cqpx(b_filter), cqpx(filtered_image2), cqpx(ipgun.prep_fft(fourier)), \
               cqpx(g_filter), cqpx(edge_found)