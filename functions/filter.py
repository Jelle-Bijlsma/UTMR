import numpy as np
from functions.process import float_uint8 as float_uint8


def apply_filter(parameters, image, filterz):
    truth = parameters[0]
    image_fft = np.fft.fft2(image)
    if not truth:
        return image, image_fft

    # filters come in the undeformed state, thus to properly multiply them, they have to be shifted
    fft_filtered_image = np.multiply(image_fft, np.fft.fftshift(filterz))
    filtered_image = np.fft.ifft2(fft_filtered_image)
    # fft_filtered and filtered return as complex 128

    return float_uint8(filtered_image), fft_filtered_image


def para_zero(value, name, replacement=1):
    if value == 0:
        print(f"{name} cannot be zero, set to: {replacement}")
        return replacement
    return value


def b_filter(parameters, shape):
    truth, cutoff, order = parameters
    y_dim = para_zero(shape[0], "y in b_filter")
    x_dim = para_zero(shape[1], "x in b_filter")

    x_max = x_dim / 2
    y_max = y_dim / 2
    x = np.arange(-x_max, x_max, 1)
    y = np.arange(-y_max, y_max, 1)

    big_x, big_y = np.meshgrid(x, y)

    xterm = 1 / (np.sqrt(1 + (big_x / cutoff) ** (2 * order)))
    yterm = 1 / (np.sqrt(1 + (big_y / cutoff) ** (2 * order)))
    big_z = (xterm + yterm) / 2
    return big_z


def g_filter(parameters, shape):
    truth, a, sigx, sigy = parameters
    sigx = para_zero(sigx, "g_filter sigmax")
    sigy = para_zero(sigy, "g_filter sigmay")
    y_dim, x_dim = shape
    x_max = x_dim / 2
    y_max = y_dim / 2
    x = np.arange(-x_max, x_max, 1)
    y = np.arange(-y_max, y_max, 1)

    big_x, big_y = np.meshgrid(x, y)

    xterm = (big_x ** 2) / (2 * sigx ** 2)
    yterm = (big_y ** 2) / (2 * sigy ** 2)
    big_z = (a / 100) * np.exp(-(xterm + yterm))
    return big_z

def prep_fft(fft_frame):
    fft_shift = np.fft.fftshift(fft_frame)
    fft_gl = np.log(np.abs(fft_shift) + 5)
    return fft_gl