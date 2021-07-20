import numpy as np
from numpy import transpose as tp
from scipy.interpolate import interp1d
from scipy import interpolate

import matplotlib.pyplot as plt


def grabfirst(alist: list, integer: int):
    return [item[integer] for item in alist]


X = np.zeros((10, 1))
Y = np.zeros((10, 1))

for element in range(0, 10):
    X[element] = np.random.randint(0, 50)
    Y[element] = np.random.randint(0, 50)

mylist = []

for x, y in zip(X, Y):
    mylist.append((x, y))

print(tp(X))
print(tp(Y))

ASD = np.concatenate([X, Y], axis=1)
print(ASD)
mysort = sorted(ASD, key=lambda p: p[0])
x = grabfirst(mysort, 0)
y = grabfirst(mysort, 1)

f = interp1d(x, y)
f2 = interp1d(x, y, kind='cubic')
tck = interpolate.splrep(x, y, s=10)
xnew = np.linspace(np.min(x), np.max(x), num=60, endpoint=True)
spl = interpolate.InterpolatedUnivariateSpline(x,y,k=2)
spl.set_smoothing_factor(0.5)
xnew2 = np.linspace(0, 50, num=60, endpoint=True)
# ynew = interpolate.splev(xnew, tck, der=0)

# plt.plot(x, y, 'o', xnew, f(xnew), '-', xnew, f2(xnew), '--', xnew, ynew, 'x')
plt.plot(x, y, 'o', xnew, f(xnew), '-', xnew, f2(xnew), '--', xnew2, spl(xnew2), 'x')

print(np.round(xnew2))
print(spl(xnew2))

plt.legend(['data', 'linear', 'cubic', 'cubic_spline'], loc='best')
plt.show()
