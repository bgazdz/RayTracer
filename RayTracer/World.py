import math
from Camera import *
from Constants import *
from GeometricObjects import *
from Light import *
from Material import *
from Octree import *
from Sampler import *
from ShadeRec import *
from Tracer import *
from Utilities import *
from ViewPort import *


class World:
    def __init__(self):
        """
        Attributes:
            objects: list of all objects
            lights: list of all lights
            camera: camera
            rays: num of rays shot
        """
        self.objects = []
        self.lights = []
        self.camera = None
        self.rays = 0
        
    #Add light to list
    def addLight(self, light):
        self.lights.append(light)

    #Add object to list (and put in Octree)
    def addObject(self, object):
        #Add to tree
        self.objects.append(object)
        self.tree.insertChild(self.tree.root, self.tree.root.s, self.tree.root, object)

    #obj file reader
    def OBJLoad(filename):
        vertices = []
        faces = []
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if(values[0] == "v"):
                v = Point(float(values[1]), float(values[2]), float(values[3]))
                vertices.append(v)
            if(values[0] == "f"):   
                w = values[1].split('/')
                u = values[2].split('/')
                v = values[3].split('/')
                f = np.array([int(w[0]), int(u[0]), int(v[0])]) 
                faces.append(f)
        return vertices, faces

    #Build the beginning of the World
    def build(self, width, height, samples):
        """
        Attributes:
            width: width of viewport
            height: height of viewport
            samples: num of samples for viewport
            tree: Octree of world Geometry
            view_port: world viewport
            background: background color
            tracer: Tracer for Primary rays
            ambient: Ambient Light of world
        """
        s = samples
        sets = 83
        self.tree = Octree(width)
        self.view_port = ViewPort(width, height, RAYDEPTH, samples, sets)
        self.background = Color(0, 0, 0)

        self.tracer = AreaLighting(self)
        self.ambient = AmbientLight(0.4, Color(1.0, 1.0, 1.0))

    #Checks if ray hits Objects
    def hitObjects(self, ray):
        sr = ShadeRec(self)
        tmin = BIGTIME
        
        #Acceleration
        children = []
        children.append(self.tree.root)
        while(len(children) != 0):
            node = children[0]
            if node != None:
                #Not a leaf
                if node.leaf == False:
                    if node.intersectRay(ray) and node.t < tmin:
                        #Add children
                        for c in node.children:
                            children.append(c)
                        #Check objects (if any)
                        if node.o.count != 0:
                            for object in node.o:
                                #Check hit
                                if object.intersectRay(ray, sr) and object.t < tmin:
                                    sr.hit = True
                                    sr.normal = object.normal
                                    sr.local_hit = object.local_hit
                                    sr.t = object.t
                                    sr.mat = object.material
                                    sr.hit_point = ray.o + object.t * ray.d
                                    tmin = object.t
                #Leaf Node, so no children to add
                elif node.leaf:
                    if node.intersectRay(ray) and node.t < tmin:
                        #Check objects (if any)
                        if node.o.count != 0:
                            for object in node.o:
                                if object.intersectRay(ray, sr) and object.t < tmin:
                                    sr.hit = True
                                    sr.normal = object.normal
                                    sr.local_hit = object.local_hit
                                    sr.t = object.t
                                    sr.mat = object.material
                                    sr.hit_point = ray.o + object.t * ray.d
                                    tmin = object.t
            #Done checking current node, so remove it
            children.remove(node)

        """
        #No Acceleration
        for object in self.objects:
            self.addRay()
            if object.intersectRay(ray, sr) and object.t < tmin:
                sr.hit = True
                sr.normal = object.normal
                sr.local_hit = object.local_hit
                sr.t = object.t
                sr.mat = object.material
                sr.hit_point = ray.o + object.t * ray.d
                tmin = object.t
        """
        return sr

    #Calls camera's renderScene function
    def renderScene(self):
        self.camera.renderScene(self)

    #Add another ray to the count
    def addRay(self):
        self.rays += 1
