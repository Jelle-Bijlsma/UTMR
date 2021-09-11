import numpy as np
from PyQt5 import QtWidgets
import time

"""
This file hosts the changes I made to existing classes. Currently only QLineEdit has fallen victim to this
practice. The class now has timekeeping abilities. Can do averaging based on FPS, and has ns. timing capability
for FAST functions. 
"""


def set_to_ms(self: QtWidgets.QLineEdit, seconds, cutoff=8, mode='normal', ns=False):
    # za = Zero Array. This array will host all the different times, so an average can be made.
    if self.za is None:
        self.za = np.zeros(self.fps)
    if ns is False:
        ms = seconds * 1000
    else:
        # this is really awkward but okay..
        # somewhere else we use perf_counter_ns, so the counter outputs already in nanoseconds compared to
        # the perf_counter, which outputs seconds.
        ms = seconds

    if mode == 'normal':
        ms_string = self.strstr(ms, cutoff)

    # elif mode == 'avg':
    else:
        if self.tc == self.fps or self.tc == 0:
            self.tc = 0
            # FYI: strstr refers to strip_str function and it just puts the number (example):
            # 0.2423542345235325423 into a shorter version and a string.
            self.t_max = self.strstr(np.max(self.za), cutoff)
            self.t_min = self.strstr(np.min(self.za), cutoff)
        try:
            self.za[self.tc] = ms
        except IndexError:
            # catch error if we switch FPS, since the averaging is based on FPS.
            self.tc = 0
            self.za = np.zeros(self.fps)
            self.za[self.tc] = ms
        self.mean = np.mean(self.za)
        ms_string = self.strstr(self.mean, cutoff)
        self.tc += 1

    self.setText(ms_string)


def strip_str(self, num, cutoff):
    # although self is not used in this context I prefer to have it as a separate method of the class
    return str(num)[0:cutoff]


def start(self: QtWidgets.QLineEdit, ns=False):
    if ns is False:
        self.start_t = time.perf_counter()
    else:
        self.start_t = time.perf_counter_ns()


def stop(self: QtWidgets.QLineEdit, cutoff=8, mode='normal', ns=False):
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
