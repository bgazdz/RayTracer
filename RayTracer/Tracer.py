from Utilities import *
from ShadeRec import *
from Constants import *

# #419begin #type=3 #src= Ray Trace Ground Up
class Tracer:
    def __init__(self, world):
        self.world = world

    def trace(self, ray, depth):
        pass

#Non-Area Light Tracer
class RayCast(Tracer):
    #Shoot ray, return color that should be drawn
    def trace(self, ray, depth):
        #Check if hit any objects
        sr = self.world.hitObjects(ray)
        if sr.hit:
            sr.depth = depth
            sr.ray = ray
            return sr.mat.shade(sr)
        else:
            return self.world.background

#Area Light Tracer
class AreaLighting(Tracer):
    #Shoot ray, return color that should be drawn
    def trace(self, ray, depth):
        #If the depth is larger than max reflection depth (in Constants)
        if (depth > RAYDEPTH):
            return Color(0.0, 0.0, 0.0)
        else:
            #Check if hit any objects
            sr = self.world.hitObjects(ray)
            if sr.hit:
                sr.depth = depth
                sr.ray = ray
                return sr.mat.areaLightShade(sr)
            else:
                return self.world.background

# #419end