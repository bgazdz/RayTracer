import numpy as np
from numpy import linalg as LA
from PIL import Image
from ViewPort import ViewPort
from Material import *
from Tracer import *
#from Octree import *
from Utilities import *
from Constants import *
from World import *

class PerspectiveCamera:

     # #419begin #type=3 #src=Ray Tracing from the Ground Up 
    def __init__(self, eye, lookat, ra, up):
        #Initializes the camera
        self.eye = eye
        self.lookat = lookat
        self.ra = ra
        self.up = up
        w = eye - lookat
        self.w = w.normalize()
        u = up.cross(w)
        self.u = u.normalize()
        self.v = self.w.cross(self.u)

    def rayDirection(self, p, d):
        """ Determine the direction of the ray given a point and distance to viewport
            Returns: a tuple that containes the normalized direction of the ray
        """  
        dir = self.u*p[0] + self.v*p[1] - self.w*d;
        return dir.normalize()
    #  #419end


    def renderScene(self, w):
        #create a viewport and image
        v = w.view_port
        im = Image.new("RGB",(v.w,v.h))
        pix = im.load()
        depth = 0
               
        #perform perspective ray-tracing
        ray = Ray(self.eye, self.lookat)
        d = 1
        #Square root of number of rays per pixel
        n = 4

        #Run through each pixel
        for col in range(v.w):
            for row in range(v.h):
                color = Color(0, 0, 0)

                #Run through each ray per pixel
                for p in range(n):
                    for q in range(n):
                        ray.o = Point(v.s*(col - 0.5*v.w +(q+0.5)/n) + self.eye.x,
                                       v.s*(row - 0.5*v.h + (p+0.5)/n)+ self.eye.y, self.eye.z)
                        color += w.tracer.trace(ray, depth)
                            
                #Divide by number of rays per pixel        
                color /= n*n
                pix[col, v.h-1-row] = (int(color.r*255), int(color.g*255), int(color.b*255))
        #Print to my desktop, change Bob to your user name to print to desktop           
        im.save("C:/Users/Bob/Desktop/image.bmp")
