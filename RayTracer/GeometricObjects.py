import math
import numpy as np
from Utilities import *
from Material import *
from ShadeRec import *
from Constants import *


# #419begin #type=3 #src= Ray Trace Ground Up

class GeometricObject():
    def getNormal(self, ray):
        return Vector(0.0, 0.0, 0.0)

    def setBbox(self):
        pass

    def getBbox(self):
        return Bbox()

    def sample(self):
        return Point(0.0, 0.0, 0.0)

    def pdf(self):
        return 0.0

    def shadowHit(self, ray):
        return Color(0, 0, 0)

class Sphere(GeometricObject):
    def __init__(self, center, radius, material):
        """
        Attributes:
            r: radius
            c: center
            material : material
            position: position for Octree
            shadows: sets shadows (not used)
            type: type for Octree
        """
        self.r = radius
        self.c = center
        self.material = material
        self.position = center
        self.shadows = True
        self.type = "Sphere"

    def intersectRay(self,ray, sr):
        """ Determine if a ray intersects the sphere
            Returns: the parameter t for the closest intersection point to
                     the ray origin.
                     Returns a value of None for no intersection
        """  
        temp= ray.o - self.c
        a = ray.d * ray.d
        b = temp * ray.d * 2.0
        cq = temp * temp - self.r * self.r
        disc = b * b -4.0 * a *cq
        if (disc < 0.0):
            return False
        else:
            e = np.sqrt(disc)
            denom = 2.0 * a
            t = (-b - e) / denom
            if (t>kEpsilon):
                self.t = t
                self.normal = (temp + t*ray.d) / self.r
                self.local_hit = ray.o + ray.d * t
                return True

            t = (-1.0*b+e)/denom
            if (t>kEpsilon):
                self.t = t
                self.normal = (temp + t*ray.d) / self.r
                self.local_hit = ray.o + ray.d * t
                return True
        return False  

    #Same as intersectRay, except no sr
    def shadowHit(self, ray):
        temp= ray.o - self.c
        a = ray.d * ray.d
        b = 2.0 * temp * ray.d
        cq = temp * temp - self.r * self.r
        disc = b * b -4.0 * a *cq
        if (disc < 0.0):
            return False
        else:
            e = np.sqrt(disc)
            denom = 2.0 * a
            t = (-b - e) / denom
            if (t>kEpsilon):
                self.st = t
                return True

            t = (-1.0*b+e)/denom
            if (t>kEpsilon):
                self.st = t
                return True
        return False  

    #return bbox of Sphere
    def getBbox(self):
        return Bbox(Point(self.c.x - self.r, self.c.y - self.r, self.c.z - self.r), Point(self.c.x + self.r, self.c.y + self.r, self.c.z + self.r))


    
    def getNormal(self, pt):
        """ Returns unit normal of sphere at the point pt """
        n=pt-self.c
        return m.normalize()

class Plane(GeometricObject):
    def __init__(self, point, normal, material):
        """
        Attributes:
            p: point on plane
            n: normal
            position: position for Octree
            material: material
            shadows: not used
            type: type for Octree
        """
        self.p = point
        self.n = normal
        self.position = point
        self.material = material
        self.shadows = True
        self.type = "Plane"

    def intersectRay(self,ray, sr):
        """ Determine if a ray intersects the plane
            Returns: the parameter t for the closest intersection point to
                     the ray origin.
                     Returns a value of None for no intersection
        """  
        test = ray.d * self.n
        if test == 0:
            return False
        t = ((self.p - ray.o) * self.n)/(ray.d * self.n)
        if (t>kEpsilon):
            self.t = t
            self.normal = self.n
            self.local_hit = ray.o + t * ray.d
            return True
        return False

    #Same as intersectRay, but without sr
    def shadowHit(self, ray):
        test = ray.d * self.n
        if test == 0:
            return False
        t = ((self.p - ray.o) * self.n)/(ray.d * self.n)
        if (t>kEpsilon):
                self.st = t
                return True
        return False
    
    def getNormal(self,pt):
        """ Returns unit normal of sphere at the point pt """
        return self.n



class Rectangle(GeometricObject):
    """Simple geometric Retctange 
    Attributes:
        kEpsilon: floating value used for allowable error in equality tests
        p: point in the rectangle
        h: height vector
        w: width vector
        n: Normal of the face
        a: The area of the rectangle (XY)
        sample: the sampler of the Rectangle
        pdf: inverse area of Rectangle (distribution factor)
        material: tuple representing an RGB color with values in [0,255]
        position: point for Octree
        type: object type for Octree
    """
    def __init__(self, p, w, h, mat, sampler):
        """Initializes plane attributes"""
        self.p = p
        self.h = h
        self.w = w
        self.n = w.cross(h).normalize()
        self.a = w.length() * h.length()
        self.material=mat
        self.position = p
        self.s = sampler
        self.pdf = 1/self.a
        self.type = "Plane"
        self.shadows = False
     
          
    def intersectRay(self,ray, sr):
        """ Determine if a ray intersects the Rectangle
            Returns: the parameter t for the closest intersection point to
                     the ray origin.
                     Returns a value of None for no intersection
        """  
        test = ray.d * self.n
        if test == 0:
            return False
        t = ((self.position - ray.o) * self.n)/(ray.d * self.n)
        if (t<kEpsilon):
                return False
        p = ray.o + t*ray.d
        v = p - self.p
        h = v*self.h
        if(h < 0 or h > self.h.length()*self.h.length()):
            return False
        w = v*self.w
        if w < 0 or w > (self.w.length()*self.w.length()):
            return False
        self.t = t
        self.normal = self.n
        self.local_hit = p
        return True

    #Same as intersectRay, but no sr
    def shadowHit(self, ray):
        return False
        test = ray.d * self.n
        if test == 0:
            return False
        t = ((self.position - ray.o) * self.n)/(ray.d * self.n)
        if (t<kEpsilon):
                return False
        p = ray.o + t*ray.d
        v = p - self.p
        h = v*self.h
        if(h < 0 or h > self.h.length()*self.h.length()):
            return False
        w = v*self.w
        if w < 0 or w > (self.w.length()*self.w.length()):
            return False
        self.st = t
        return True

    #Return sample point
    def sample(self):
        s = self.s.sampleSquare();
        return (self.p + s.x * self.w + s.y * self.h)
 

    
    def getNormal(self,pt):
        """ Returns unit normal of sphere at the point pt """
        return self.n


class Triangle(GeometricObject):
    """Simple Triangke

    Attributes:
        kEpsilon: floating value used for allowable error in equality tests
        p0: tuple representing Point 0 of the triangle
        p1: tuple representing Point 1 of the triangle
        p2: tuple representing Point 2 of the triangle
        n: tuple representing normal of the triangle
        material: tuple representing RGB color with values in [0, 255]
        position: position for Octree
        type: type of object for Octree
    """

    kEpsilon = 0.0000001

    def __init__(self, p0, p1, p2, mat):
        #initialize the triangle
        self.p0=p0;
        self.p1=p1;
        self.p2=p2;
        self.n = self.getNormal(p0)
        self.material=mat
        self.position = p0+p1+p2/3
        self.shadows = True
        self.type = "Triangle"


    def intersectRay(self, ray, sr):
        """ Determine if a ray intersects the triangle
            Returns: the parameter t for the closest intersection point to
                     the ray origin.
                     Returns a value of None for no intersection
        """  
        a = self.p0.x - self.p1.x
        b = self.p0.x - self.p2.x
        c = ray.d.x
        d = self.p0.x - ray.o.x

        e = self.p0.y - self.p1.y
        f = self.p0.y - self.p2.y
        g = ray.d.y
        h = self.p0.y - ray.o.y

        i = self.p0.z - self.p1.z
        j = self.p0.z - self.p2.z
        k = ray.d.z
        l = self.p0.z - ray.o.z

        m = f*k - g*j
        n = h*k - g*l
        p = f*l - h*j
        q = g*i - e*k
        s = e*j - f*i

        if (a*m+b*q+c*s) == 0:
            return False
        inv_denom = 1.0/(a*m+b*q+c*s)

        e1 = d*m - b*n - c*p

        beta = e1*inv_denom

        if(beta < 0.0):
            return False

        r = e*l - h*i
        e2 = a*n + d*q + c*r
        gamma = e2*inv_denom

        if(gamma < 0.0):
            return False

        if((beta+gamma) > 1.0):
            return False

        e3 = a*p - b*r + d*s
        t = e3*inv_denom

        if(t<self.kEpsilon):
            return False

        self.t = t
        self.normal = self.n
        self.local_hit = ray.o + t*ray.d
        return True

    #Same as intersectRay, without the sr, shadowing only
    def shadowHit(self, ray):
        a = self.p0.x - self.p1.x
        b = self.p0.x - self.p2.x
        c = ray.d.x
        d = self.p0.x - ray.o.x

        e = self.p0.y - self.p1.y
        f = self.p0.y - self.p2.y
        g = ray.d.y
        h = self.p0.y - ray.o.y

        i = self.p0.z - self.p1.z
        j = self.p0.z - self.p2.z
        k = ray.d.z
        l = self.p0.z - ray.o.z

        m = f*k - g*j
        n = h*k - g*l
        p = f*l - h*j
        q = g*i - e*k
        s = e*j - f*i

        if (a*m+b*q+c*s) == 0:
            return False
        inv_denom = 1.0/(a*m+b*q+c*s)

        e1 = d*m - b*n - c*p

        beta = e1*inv_denom

        if(beta < 0.0):
            return False

        r = e*l - h*i
        e2 = a*n + d*q + c*r
        gamma = e2*inv_denom

        if(gamma < 0.0):
            return False

        if((beta+gamma) > 1.0):
            return False

        e3 = a*p - b*r + d*s
        t = e3*inv_denom

        if(t<self.kEpsilon):
            return False

        self.st = t
        return True

    #Not used
    def getBbox(self):
        return Bbox(Point(min(min(p0.x, p1.x), p2.x) - kEpsilon, min(min(p0.y, p1.y), p2.y) - kEpsilon, min(min(p0.z, p1.z), p2.z) - kEpsilon), Point(max(max(p0.x, p1.x), p2.x) + kEpsilon, max(max(p0.y, p1.y), p2.y) + kEpsilon, max(max(p0.z, p1.z), p2.z) + kEpsilon))

    def getNormal(self, p):
        #Sets the normal of the triangle to face camera
        n = Vector.cross(self.p0-self.p1, self.p2-self.p0)
        if( n.z < 0):
            n.x = -n.x
            n.y = -n.y
            n.z = -n.z
        return Vector.normalize(n)
# #419end