from Utilities import *
from Sampler import *
from ShadeRec import *
from GeometricObjects import *
from Constants import *
# #419begin #type=3 #src=Ray Tracing from the Ground Up 

class Light:
    def getDirection(self, sr):
        pass

    def L(self, sr):
        pass

class AmbientLight(Light):
    def __init__(self, ls, color):
        """
        Attributes:
            ls: light intensity
            color: color of light
        """
        self.ls = ls
        self.color = color

    #No direction for ambient
    def getDirection(self, sr):
        return Vector(0, 0, 0)

    #Return ambient light color
    def L(self, sr):
        return self.ls * self.color

class PointLight(Light):
    def __init__(self, p, ls, color):
        """
        Simple point light class
        p : point of point light 
        ls : specular intensity (range from 0 to 1)
        color: color of light
        """
        self.p = p
        self.ls = ls
        self.color = color

    #Get Vector to hit_point
    def getDirection(self, sr):
        self.distance = (sr.hit_point - self.p).length()
        return sr.hit_point - self.p

    #Return Light color
    def L(self, sr):
        return self.ls * self.color / (self.distance * self.distance)

    #Check if object is in shadow
    def inShadow(self, ray, sr):
        for object in sr.w.objects:
            sr.w.addRay()
            ts = (self.p - ray.o).length()
            if object.shadowHit(ray):
                if(object.st < ts):
                    return True

        return False

class DirectionLight(Light):
    def __init__(self, d, ls, color):
        """
        Simple direction light class
        d : direction of light
        ls : specular intensity (range from 0 to 1)
        color: Color of light
        """
        self.d = d
        self.ls = ls
        self.color = color

    #Return Direction
    def getDirection(self, sr):
        return self.d

    #Return light color
    def L(self, sr):
        return self.ls * self.color

    #Check if object is in shadow
    def inShadow(self, ray, sr):
        for object in sr.w.objects:
            sr.w.addRay()
            if object.shadowHit(ray):
                return True
        return False

class AreaLight(Light):
    """
    Attributes:
        o: object
        p: point on sample
        n: normal at p
        wi: Direction Vector
    """
    def __init__(self, o):
        self.o = o

    #Get direction of the light
    def getDirection(self, sr):
        self.p = self.o.sample()
        self.n = self.o.getNormal(self.p)
        self.wi = self.p - sr.hit_point
        self.wi = self.wi.normalize()
        return -1.0 * self.wi

    #Check if in a shadow
    def inShadow(self, ray, sr):
        ts = (self.p - ray.o) * ray.d
        for object in sr.w.objects:
            sr.w.addRay()
            if object.shadowHit(ray) and object.st < ts:
                return True

        return False

    #Returns color depending on whether or not we are on the lit side
    def L(self, sr):
        n = (-1.0*self.n * self.wi)

        if(n > 0):
            return self.o.material.getLe()
        else: 
            return Color(0, 0, 0)

    #Get G
    def G(self, sr):
        nd = (-1.0*self.n * self.wi)
        d = self.p - sr.hit_point
        ddot = d*d
        return nd/ddot

    #Get pdf
    def pdf(self, sr):
        return self.o.pdf
# #419end