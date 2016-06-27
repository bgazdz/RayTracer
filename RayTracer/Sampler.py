import numpy as np
import math
import random
from numpy import linalg as LA
from Utilities import *
from ShadeRec import *

# #419begin #type=3 #src=Ray Tracing from the Ground Up 
class Sampler:
    """
    Regular Sampler
    s: number of samples
    sets: number of sets
    count: count of samples checked
    samples: list of all samples
    jump: for when new pixel is reached
    """
    def __init__(self, s, sets):
        self.s = s
        self.sets = sets
        self.count = 0
        self.samples = []
        self.hsamples = []
        self.jump = 0
        self.generateSamples()

    #Return sample point on Square
    def sampleSquare(self):
        if self.count % self.s == 0:
            self.jump = (random.randint(1, self.sets) % self.sets) * self.s
        idx = self.jump + self.count % self.s
        sample = self.samples[idx]
        self.count += 1
        return sample

    #Set up hsamples based on hemisphere
    def mapHemisphere(self, exp):
        for sample in self.samples:
            cos_phi = math.cos(2*math.pi*sample.x)
            sin_phi = math.sin(2*math.pi*sample.x)
            cos_theta = pow((1.0 - sample.y), 1.0 / (exp+1))
            sin_theta = math.sqrt(1.0 - cos_theta * cos_theta)
            pu = sin_theta * cos_phi
            pv = sin_theta * sin_phi
            pw = cos_theta
            self.hsamples.append(Point(pu, pv, pw))

    #Return sample point on Hemisphere
    def sampleHemisphere(self):
        if(self.count % self.s == 0):
            self.jump = (random.randint(0, self.s) % self.sets) * self.s
        idx = self.jump + self.count % self.s
        sample = self.hsamples[idx]
        self.count += 1
        return sample

class Regular(Sampler):        
    #Generate the Regular samples and add them to the list samples
    def generateSamples(self):
        n = int(math.sqrt(self.s))
        for i in range(self.sets):
            for j in range (n):
                for k in range(n):
                    self.samples.append(Point((k+.5)/n, (j+.5)/n, 0))
# #419end