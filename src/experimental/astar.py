import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np 
import math
import random

def make_array(shape=(50, 50), func=lambda x, y: x + y):
    xhalf = shape[1] / 2
    yhalf = shape[0] / 2
    xres = 100 / xhalf
    yres = 100 / yhalf

    Z = np.zeros(shape)

    for i in range(Z.shape[1]):
        for j in range(Z.shape[0]):
            x = (i - xhalf) * xres
            y = (j - yhalf) * yres

            Z[j, i] = func(x, y)
    return Z

def make_plot(Z):
    xhalf = Z.shape[1] / 2
    yhalf = Z.shape[0] / 2
    xres = 100 / xhalf
    yres = 100 / yhalf

    fig, ax = plt.subplots(figsize=(13,8), subplot_kw={'projection': '3d'})

    X = np.arange(-xhalf * xres, xhalf * xres, xres)
    Y = np.arange(-yhalf * yres, yhalf * yres, yres)

    X, Y = np.meshgrid(X, Y)
    surf1 = ax.plot_surface(X, Y, Z, cmap=plt.cm.RdYlBu_r, antialiased=False)

    ax.set_zlim(0, 1)
    fig.colorbar(surf1)

    plt.show()

def func(x, y, allf=[(0, 60, 30, 30), (0, -60, 30, 30)], depression=0.003):
    total = 0

    for fun in allf:
        total += math.exp(-(((x - fun[0])**2) / (2 * fun[2]**2) + ((y - fun[1])**2) / (2 * fun[3]**2)))

    return (total / len(allf)) + (random.random() / 20) - (0.4 if random.randint(1, int(1 / depression)) == 1 else 0)

def get_neighbors(i, j, Z):
    row, col = Z.shape
    bef = [(i + 1, j - 1), (i, j - 1), (i - 1, j - 1), (i + 1, j + 1), (i, j + 1), (i - 1, j + 1), (i + 1, j), (i - 1, j)]
    aft = []

    for x, y in bef:
        if 0 <= x < row and 0 <= y < col: 
            aft.append((x, y))
    
    return [Z[x, y] for x, y in aft]

def fill_singlecell_depressions(Z):
    row, col = Z.shape
    
    for j in range(row):
        for i in range(col):
            minneighbor = min(get_neighbors(i, j, Z))
            Z[i, j] = max(minneighbor, Z[i, j])

def flow_directions(Z):
    row, col = Z.shape
    FD = np.zeros(Z.shape)
    
    for j in range(row):
        for i in range(col):
            pass
            

Z = make_array(func=func)

fill_singlecell_depressions(Z)

make_plot(Z)