import numpy as np 
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
import math, random

class Surface(object):
    def __init__(self, function, resolution=(90, 90), origin=(100, 100), maxsize=(200, 200)):
        ''' The points are ordered as row column not width height! '''
        self.function = function
        self.buffer = np.zeros(resolution)
        self.maxsize = maxsize
        self.origin = origin

        self.ry = resolution[0] / maxsize[0]
        self.rx = resolution[1] / maxsize[1]

        self.t = 0

        self.compute()
    
    def compute(self):
        row, column = self.buffer.shape

        for j in range(row):
            for i in range(column):
                x = (i / self.rx) - self.origin[1]
                y = ((row - 1 - j) / self.ry) - self.origin[0]

                self.buffer[j, i] = self.function(x, y, self.t)
    
    def animate(self, pause=50, duration=20, save=False):
        ax = plt.subplot(111)
        img = ax.imshow(self.buffer, vmin=0, vmax=1)

        def update(_):
            self.compute()
            img.set_data(self.buffer)
            self.t += pause / 1000

        anim = FuncAnimation(plt.gcf(), update, interval=pause)

        if not save:
            plt.show()

        if save:
            anim.save('data/collision.gif', writer='imagemagick')

class GaussianFunction(object):
    def __init__(self, gaussianlist=[(0, 0, 5, 30), (0, 0, 5, 30)], depchance=0.003):
        self.gaussianlist = gaussianlist
        self.count = len(gaussianlist)
        self.depchance = depchance
    
    def __call__(self, x, y, t):
        z = 0
        v = 10
        v1 = 23
        v2 = 29
        vt = 12
        for i, gaussian in enumerate(self.gaussianlist):
            x0, y0, sx, sy = gaussian

            sx = 10 + 5 * math.sin(vt * t)
            sy = 30 + 5 * math.cos(vt * t)

            if i == 0:
                x0 = 30 * math.sin(v1 * t / v)
            elif i == 1:
                x0 = 30 * math.sin(v2 * t / v)

            z += math.exp(-(((x - x0) / (2 * sx))**2 + ((y - y0) / (2 * sy))**2 ))
        
        return z / 2 # if z / 2 > .5 else 0        

prob = Surface(GaussianFunction())
prob.animate(save=True)