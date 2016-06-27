import numpy as np
from Sampler import *
from Utilities import *

# #419begin #type=3 #src=Professor's Example MP
class ViewPort:
    """ Simple viewport class center on z-axis """
    def __init__(self,width,height, max_depth, num_samples, num_sets, gamma=1.0):
        #Initialize the viewport
        self.w=width
        self.h=height
        self.g = gamma
        self.inv_g=1/gamma
        self.maxDepth = max_depth
        self.sampler = Regular(1, num_sets)
        self.minCorner = Point(-50.0, -50.0, 0.0)
        self.maxCorner = Point(50.0, 50.0, 0.0)
        self.s=(self.maxCorner.x-self.minCorner.x)/self.w
        
        
    def getPixelCenter(self,r,c):
        """ Find the Center of a pixel r,c
            Returns: a tuple containing the value for the center of the pixel r,c in the viewport
        """  
        return Point(self.s*(c - self.w/2.0 +0.5), self.s*(r - self.h/2.0 +0.5), self.minCorner.z)
#  #419end 