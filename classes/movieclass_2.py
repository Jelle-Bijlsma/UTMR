# specific call since it is used often (and maybe a bit legacy)
import cv2
import numpy as np
from functions.process import change_qpix as cqpx
import functions.process as process
import functions.edge as edge
import functions.filter as filterf
import functions.line_find as lf
import functions.spline as spl
import functions.template as tpm


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
        self.kernel = cv2.getStructuringElement(shape=0, ksize=(2, 2))

        # results
        self.gls_image = []
        self.histogram = []
        self.b_filter = []
        self.g_filter = []
        self.b_filter2 = []
        self.g_filter2 = []
        self.fourier = []
        self.filtered_image1 = []

        self.prevpar = None
        self.prevpar2 = None
        self.edge_status = None

        t1 = cv2.imread("./data/templates/scale1.png", 0)
        t2 = cv2.imread("./data/templates/scale2.png", 0)
        self.template_list = [t1, t2]

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
        progress_bar_fun in MAIN can also edit the 'currentframe'
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
        # the value of the dict key is the evaluation of the given function
        self.parameters[key] = fun()

    def update(self, morph_vars, segment_state, timer_list):
        """"
        This is the place where 'all the action is' regarding the

        """

        # due to the C implementation of numpy, np.ndarray has the tendancy to be shared in memory
        # all kinds of funky things happen when you omit this step.
        base_image = np.copy(self.currentframe)

        para = self.parameters  # shorthand notation
        output = [list, list]  # predefine
        glsT, preT, edgeT, morphT, segT, lfT, cqpxT, tmT, sortT, drawT, spl1T, spl2T = timer_list
        # transfer and unpack class instances (of QWidgets.QLineEdit) for usage of added methods for timing

        # by calling .start and .stop of the appropriate lineEdit, the performance of the piece of code can
        # be measured. Nanosecond possibility.
        glsT.start(ns=False)
        gls_image, histogram = process.calc_gls(base_image, para['GLS'])
        glsT.stop(mode='avg', ns=False, cutoff=5)

        preT.start()
        if self.prevpar == [para['b_filter'], para['g_filter']]:
            pass
        else:
            self.b_filter = filterf.b_filter(parameters=para['b_filter'], shape=np.shape(self.currentframe))
            self.g_filter = filterf.g_filter(parameters=para['g_filter'], shape=np.shape(self.currentframe))
            self.prevpar = [para['b_filter'], para['g_filter']]

        # 'fourier' is raw complex128.
        # para['b_filter'] is only needed for the checkbox
        filtered_image1, fourier, = filterf.apply_filter(parameters=para['b_filter'], filterz=self.b_filter,
                                                         image=gls_image)
        filtered_image2, fourier, = filterf.apply_filter(parameters=para['g_filter'], filterz=self.g_filter,
                                                         image=filtered_image1)
        preT.stop(mode='avg', cutoff=5)

        # call 2 edge function, to determine wheter canny or sobel is used...
        edgeT.start()
        edge_found, self.edge_status = edge.edge_call(filtered_image2, para['canny'], para['sobel'])
        # what am i doing on the next line?!
        no_edgefinding = not (para['canny'][0] or para['sobel'])
        # no_edgefinding = False
        edgeT.stop(mode='avg', cutoff=5)

        morphT.start()
        morph_vars1 = [morph_vars[0][0], morph_vars[1], morph_vars[2]]
        morph_img = edge.do_morph(edge_found, morph_vars1, no_edgefinding)
        morphT.stop(mode='avg', cutoff=5)

        segT.start()
        mask, masked = edge.flood(morph_img, base_image, segment_state)
        segT.stop(mode='avg', cutoff=5)

        cqpxT.start()
        #              0                    1              2            3               4
        output[0] = [cqpx(base_image), cqpx(gls_image), histogram, cqpx(self.b_filter), cqpx(filtered_image2),
                     #              5                    6              7                8
                     cqpx(filterf.prep_fft(fourier)), cqpx(self.g_filter), cqpx(edge_found), cqpx(morph_img),
                     #   9           10
                     cqpx(mask), cqpx(masked)]
        cqpxT.stop(mode='avg', cutoff=5)

        # Now we do everythang again........
        gls_image, histogram = process.calc_gls(masked, para['GLS2'])

        if self.prevpar2 == [para['b_filter2'], para['g_filter2']]:
            pass
        else:
            self.b_filter2 = filterf.b_filter(parameters=para['b_filter2'], shape=np.shape(self.currentframe))
            self.g_filter2 = filterf.g_filter(parameters=para['g_filter2'], shape=np.shape(self.currentframe))
            self.prevpar2 = [para['b_filter2'], para['g_filter2']]

        # 'fourier' is raw complex128.
        # para['b_filter'] is only needed for the checkbox
        filtered_image1, fourier, = filterf.apply_filter(parameters=para['b_filter2'], filterz=self.b_filter2,
                                                         image=gls_image)
        filtered_image2, fourier, = filterf.apply_filter(parameters=para['g_filter2'], filterz=self.g_filter2,
                                                         image=filtered_image1)

        # call 2 edge function, to determine wheter canny or sobel is used...
        edge_found, self.edge_status = edge.edge_call(filtered_image2, para['canny2'], para['sobel2'])
        no_edgefinding = not (para['canny2'][0] or para['sobel2'])

        morph_vars2 = [morph_vars[0][1], morph_vars[1], morph_vars[2]]
        morph_img = edge.do_morph(edge_found, morph_vars2, no_edgefinding)

        # circle finding
        circle_im = tpm.circlefind(para['circlefinder'], morph_img)

        tmT.start()
        template, tlist = tpm.templatematch(morph_img, para['template'], self.template_list)
        tmT.stop(mode='avg', cutoff=5)

        sortT.start()
        real_coords = tpm.sort_out(tlist)
        sortT.stop(mode='avg', cutoff=5)

        # print(real_coords)
        drawT.start()
        pre_spline_im = tpm.drawsq(base_image, real_coords, cirq=True)
        drawT.stop(mode='avg', cutoff=5)

        spl1T.start()
        spline_coords = spl.get_spline(real_coords, pre_spline_im, para['template'])
        spl1T.stop(mode='avg', cutoff=5)

        spl2T.start()
        mask2 = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, self.kernel)
        spline_im, distances = spl.draw_spline(pre_spline_im, spline_coords, mask2, para['template'])
        spl2T.stop(mode='avg', cutoff=5)

        template = lf.draw_bb(para['linefinder'], template, spline_coords)
        lfT.start()
        cutout, angles = lf.takelines(para['linefinder'], spline_coords, mask)
        lfT.stop(mode='avg', cutoff=5)

        """"
        Still need to fix: coordinates are the lower left vertex of the matched template. To draw square I add 15
        Which is the approximate square of the template. Get it right soon. 
        """

        #               0               1           2                         3
        output[1] = [cqpx(gls_image), histogram, cqpx(self.b_filter), cqpx(filtered_image2),
                     #          4                          5                 6                  7
                     cqpx(filterf.prep_fft(fourier)), cqpx(self.g_filter), cqpx(edge_found), cqpx(morph_img),
                     #       8               9          10           11       12               13
                     cqpx(circle_im), cqpx(template), cqpx(cutout), angles, distances, cqpx(spline_im)]

        return output
