from Utilities import *
from GeometricObjects import *

class Instance:
    def __init__(self, object):
        """
        Attributes:
            o: object of instance
            inv_matrix: inverse transforms
            forward: Ignore (does nothing right now)
            material: Material of object
            position: position of object (For octree placement)
            type: object type (For octree placement)
            r: radius of object (sphere, for octree placement)
        """
        self.o = object
        self.inv_matrix = Matrix.identity()
        self.forward = Matrix.identity()
        self.material = object.material
        self.position = self.o.position
        self.type = self.o.type
        self.r = self.o.r

    #Not used
    def getBbox(self):
        p = self.o.getBbox().getPoints()
        transformed_p = []
        for point in p:
            transformed_p.append(point.Mmult(self.forward))
        
        l = transformed_p[0]
        u = transformed_p[0]
        for point in transformed_p:
            if point.x < l.x:
                l.x = point.x
            if point.y < l.y:
                l.y = point.y
            if point.z < l.z:
                l.z = point.z
            if point.x > u.x:
                u.x = point.x
            if point.y > u.y:
                u.y = point.y
            if point.x > u.x:
                u.z = point.z
        return Bbox(l, u)

    #Translate instance
    def translate(self, x, y, z):
        self.forward = Matrix.Translate(x, y, z) * (self.forward)
        self.inv_matrix = self.inv_matrix * (Matrix.Translate(-x, -y, -z))

    #Scale instance
    def scale(self, x, y, z):
        self.forward = Matrix.Scale(x, y, z) * (self.forward)
        self.inv_matrix = self.inv_matrix * (Matrix.Scale(1.0/x, 1.0/y, 1.0/z))

    #Rotate around X
    def rotateX(self, theta):
        self.forward = Matrix.RotateX(theta) * (self.forward)
        self.inv_matrix = self.inv_matrix * (Matrix.RotateX(-theta))

    #Rotate around Y
    def rotateY(self, theta):
        self.forward = Matrix.RotateY(theta) * (self.forward)
        self.inv_matrix = self.inv_matrix * (Matrix.RotateY(-theta))

    #Rotate around Z
    def rotateZ(self, theta):
        self.forward = Matrix.RotateZ(theta) * (self.forward)
        self.inv_matrix = self.inv_matrix * (Matrix.RotateZ(-theta))

    #Check Ray intersection
    def intersectRay(self, ray, sr):
        #Transform ray
        ro = ray.o.Mmult(self.inv_matrix)
        rd = ray.d.Mmult(self.inv_matrix)

        #Check transformed ray on object
        t_ray = Ray(ro, rd)
        hit = self.o.intersectRay(t_ray, sr)
        if hit:
            #Copy object values needed for sr
            self.t = self.o.t
            self.normal = self.o.normal.Mmult(self.inv_matrix).normalize()
            self.local_hit = self.o.local_hit
            self.material = self.o.material
        return hit

    #Shadow hit intersection
    def shadowHit(self, ray):
        #Transform Ray
        ro = ray.o.Mmult(self.inv_matrix)
        rd = ray.d.Mmult(self.inv_matrix)
        t_ray = Ray(ro, rd)        
        #Check transformed ray to object
        hit = self.o.shadowHit(t_ray)
        if hit:
            #Copy over object values needed for sr
            self.st = self.o.st
        return hit