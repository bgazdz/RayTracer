from Utilities import *

# #419begin #type=3 #src= Ray Trace Ground Up
class ShadeRec():
    def __init__(self, world):
        """
        Attributes:
            w: World
            hit: bool on if hit an object
            mat: material of object hit
            hit_point: point where object is hit
            local_hit: point on object that was hit
            normal: normal of object at local_hit
            ray: ray that is shot
            t: time of hit
            depth: Number of times reflected
            color: color at hit_point
        """
        self.w = world
        self.hit = False
        self.mat = None
        self.hit_point = Point(0.0, 0.0, 0.0)
        self.local_hit = Point(0.0, 0.0, 0.0)
        self.normal = Vector(0.0, 0.0, 0.0)
        self.ray = Ray(Point(0.0, 0.0, 0.0), Vector(0.0, 0.0, 0.0))
        self.t = 0.0
        self.depth = 0
        self.color = Color(0.0, 0.0, 0.0)

# #419end