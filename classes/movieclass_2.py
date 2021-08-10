import numpy as np

import functions.image_processing.base_fun as ipgun
# specific call since it is used often (and maybe a bit legacy)
from functions.image_processing.base_fun import change_qpix as cqpx


def check_equal(fun, first_result, used_params, keyword, **kwargs):
    """"
    function checks if anything changed..
    If it didnt it returns the cached value. This speeds up the calculation later on
    """

    # to note, kwargs is a dictionary.

    if keyword in used_params:
        if kwargs['parameters'] == used_params[keyword]:
            # print("save a calc")
            # when the parameters in the 'used' bin are the same as the fed parameters, return cached
            return first_result, used_params

    # if not the same, do the calculation with all the keyword arguments
    a = fun(**kwargs)
    # and save the parameters in the 'used_params' variable
    used_params[keyword] = kwargs['parameters']
    return a, used_params


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

    def update(self):
        para = self.parameters
        base_image = np.copy(self.currentframe)
        self.gls_image, self.used_parameters = check_equal(ipgun.calc_gls, self.gls_image, self.used_parameters,
                                                           'GLS', image=base_image, parameters=para['GLS'])
        # print(f"these are the used parameters{self.used_parameters}")

        # for function with checkboxes, if unchecked, execute function but return the input image.

        return cqpx(self.gls_image)
