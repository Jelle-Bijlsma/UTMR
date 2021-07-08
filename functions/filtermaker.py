import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt


fft = np.empty([370, 370])
cutoff = 100

x_dim, y_dim = np.shape(fft)
x_max = x_dim / 2
y_max = y_dim / 2
x = np.arange(-x_max, x_max, 1)
y = np.arange(-y_max, y_max, 1)

X,Y = np.meshgrid(x,y)

xterm = 1/(np.sqrt(1+(X/cutoff)**2))
yterm = 1/(np.sqrt(1+(Y/cutoff)**2))

Z = (xterm+yterm)/2
Z = np.fft.ifftshift(Z)
fig, ax = plt.subplots()
im = ax.imshow(Z,interpolation='nearest')

a = np.multiply(np.fft.fftshift(Z),Z)

plt.show()

# x = y = np.arange(0, 10, 0.1)
# n = 1
# cutoff = 10
#
# X,Y = np.meshgrid(x,y)
# xterm = 1/(np.sqrt(1+X**2))
# yterm = 1/(np.sqrt(1+Y**2))
# Z = xterm + yterm
# # for element in x:
# #     dataX.append(element)
# #     func = 1/(np.sqrt(1+(element/cutoff)**(2*n)))
# #     dataY.append(func)
#
# # dataX = np.fft.ifftshift(dataX)
# #Z = np.fft.ifftshift(Z)
# #ax.plot(dataX,dataY)
#
# # ax.set(xlabel='time (s)', ylabel='voltage (mV)',
# #        title='About as simple as it gets, folks')
# # ax.grid()
#
