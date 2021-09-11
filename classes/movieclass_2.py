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
import functions.blob_contour as blobf


class MovieUpdate:
    """"
    This class is responsible for handling the collection of frames and properly edit them according to the GUI.
    The movieclass stores the parameters and then the update class performs all the image manipulation
    """
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
        self.blackim = np.zeros((100,100))

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

    def update(self, morph_vars, segment_state, timer_list,templates,heq):
        """"
        This is the place where 'all the action is' regarding the image manipulation.
        """

        # due to the C implementation of numpy, np.ndarray has the tendancy to be shared in memory
        # all kinds of funky things happen when you omit this step.
        base_image = np.copy(self.currentframe)
        base_image2 = np.copy(self.currentframe)

        im_with_keypoints = base_image

        para = self.parameters  # shorthand notation
        output = [list, list]  # predefine
        gls_t, pre_t, edge_t, morph_t, seg_t, lf_t, cqpx_t, tm_t, sort_t, draw_t, spl1_t, spl2_t = timer_list
        # transfer and unpack class instances (of QWidgets.QLineEdit) for usage of added methods for timing


        # by calling .start and .stop of the appropriate lineEdit, the performance of the piece of code can
        # be measured. Nanosecond possibility.
        gls_t.start(ns=False)
        self.gls_image, histogram = process.calc_gls(base_image, para['GLS'])
        #self.gls_image = 255-self.gls_image  # invert image
        if heq is True:
            self.gls_image = cv2.equalizeHist(self.gls_image)
            l, b = self.gls_image.shape
            img2 = np.reshape(self.gls_image, l * b)
            histogram = np.log10(np.bincount(img2, minlength=255) + 1)
            print("didgls")

        gls_t.stop(mode='avg', ns=False, cutoff=5)

        pre_t.start()

        """"
        Due to the messed up way of doing the initial cropping, i cannot do the equalitiy check in the
        filter parameters..  2 be fixed... 
        """

        # if self.prevpar == [para['b_filter'], para['g_filter']]:
        #     pass
        # else:
        self.b_filter = filterf.b_filter(parameters=para['b_filter'], shape=np.shape(self.currentframe))
        self.g_filter = filterf.g_filter(parameters=para['g_filter'], shape=np.shape(self.currentframe))
        self.prevpar = [para['b_filter'], para['g_filter']]

        # 'fourier' is raw complex128.
        # para['b_filter'] is only needed for the checkbox
        filtered_image1, fourier, = filterf.apply_filter(parameters=para['b_filter'], filterz=self.b_filter,
                                                         image=np.copy(self.gls_image))
        filtered_image2, fourier, = filterf.apply_filter(parameters=para['g_filter'], filterz=self.g_filter,
                                                         image=filtered_image1)
        pre_t.stop(mode='avg', cutoff=5)

        # call 2 edge function, to determine wheter canny or sobel is used...
        edge_t.start()
        edge_found, self.edge_status = edge.edge_call(filtered_image2, para['canny'], para['sobel'])
        no_edgefinding = not (para['canny'][0] or para['sobel'])
        edge_t.stop(mode='avg', cutoff=5)

        morph_t.start()
        morph_vars1 = [morph_vars[0][0], morph_vars[1], morph_vars[2]]
        morph_img = edge.do_morph(edge_found, morph_vars1, no_edgefinding)
        morph_t.stop(mode='avg', cutoff=5)

        seg_t.start()
        mask, masked = edge.flood(morph_img, base_image, segment_state)
        seg_t.stop(mode='avg', cutoff=5)

        # Now we do everything again........
        gls_image2, histogram2 = process.calc_gls(masked, para['GLS2'])

        # if self.prevpar2 == [para['b_filter2'], para['g_filter2']]:
        #     pass
        # else:
        self.b_filter2 = filterf.b_filter(parameters=para['b_filter2'], shape=np.shape(self.currentframe))
        self.g_filter2 = filterf.g_filter(parameters=para['g_filter2'], shape=np.shape(self.currentframe))
        self.prevpar2 = [para['b_filter2'], para['g_filter2']]

        # 'fourier' is raw complex128.
        # para['b_filter'] is only needed for the checkbox
        filtered_image12, fourier2, = filterf.apply_filter(parameters=para['b_filter2'], filterz=self.b_filter2,
                                                         image=gls_image2)
        filtered_image22, fourier2, = filterf.apply_filter(parameters=para['g_filter2'], filterz=self.g_filter2,
                                                         image=filtered_image12)

        # call 2 edge function, to determine wheter canny or sobel is used...
        edge_found2, self.edge_status2 = edge.edge_call(filtered_image22, para['canny2'], para['sobel2'])
        no_edgefinding2 = not (para['canny2'][0] or para['sobel2'])

        morph_vars2 = [morph_vars[0][1], morph_vars[1], morph_vars[2]]
        morph_img2 = edge.do_morph(edge_found2, morph_vars2, no_edgefinding2)

        # # circle finding
        # circle_im2 = tpm.circlefind(para['circlefinder'], morph_img2)
        # print(para['blob'])
        if para['template'][0] == True:

            tm_t.start()
            tlist = tpm.templatematch(morph_img2, para['template'], templates)
            tm_t.stop(mode='avg', cutoff=5)


        elif para['blob'][0] == True:
            tlist,keypoints = blobf.blobf(morph_img2, para['blob'])
            im_with_keypoints = cv2.drawKeypoints(masked, keypoints, np.array([]), (255),
                                                  cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            # do blob detection

        # if para['blob'][0] | para['template'][0] == True:
        if (para['template'][0] | para['blob'][0]) == True:
            sort_t.start()
            real_coords = tpm.sort_out(tlist)
            sort_t.stop(mode='avg', cutoff=5)

            draw_t.start()
            pre_spline_im = tpm.drawsq(base_image, real_coords, cirq=True)
            draw_t.stop(mode='avg', cutoff=5)

            spl1_t.start()
            spline_coords = spl.get_spline(real_coords, pre_spline_im, para['template'])
            spl1_t.stop(mode='avg', cutoff=5)

            spl2_t.start()
            mask2 = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, self.kernel)
            spline_im, distances = spl.draw_spline(pre_spline_im, spline_coords, mask2, para['template'])
            spl2_t.stop(mode='avg', cutoff=5)

            # angle determination
            bbox_im = lf.draw_bb(para['linefinder'], base_image2, spline_coords)
            lf_t.start()
            cutout, angles = lf.takelines(para['linefinder'], spline_coords, mask)
            lf_t.stop(mode='avg', cutoff=5)

        else:
            # set to standard if not done.
            bbox_im,cutout,spline_im = [self.blackim, self.blackim, self.blackim]
            angles, distances = [None,None]


        cqpx_t.start()
        #              0                    1              2            3               4
        output[0] = [cqpx(base_image), cqpx(self.gls_image), histogram, cqpx(self.b_filter), cqpx(filtered_image2),
                     #              5                    6                      7                8
                     cqpx(filterf.prep_fft(fourier)), cqpx(self.g_filter), cqpx(edge_found), cqpx(morph_img),
                     #   9           10
                     cqpx(mask), cqpx(masked)]


        #               0               1           2                         3
        output[1] = [cqpx(gls_image2), histogram, cqpx(self.b_filter2), cqpx(filtered_image22),
                     #          4                          5                 6                  7
                     cqpx(filterf.prep_fft(fourier2)), cqpx(self.g_filter2), cqpx(edge_found2), cqpx(morph_img2),
                     #       8               9          10           11       12               13
                     cqpx(base_image), cqpx(bbox_im), cqpx(cutout), angles, distances, cqpx(spline_im),
                     #      14
                     cqpx(im_with_keypoints)]
                    # 8 used to be circleim2.. what?

        cqpx_t.stop(mode='avg', cutoff=5)
        return output
