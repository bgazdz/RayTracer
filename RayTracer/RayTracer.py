from PIL import Image
from Camera import *
from Constants import *
from GeometricObjects import *
from Instance import *
from Light import *
from Material import *
from Sampler import *
from ShadeRec import *
from Tracer import *
from Utilities import *
from ViewPort import *
from World import *
import time

NUMRAYS = 0

world = World()

world.build(128, 128, 1)

#Set up Camera
eye = Point(0, 0, -25)
lookat = Vector(0, 0, 1)
ra = 0
up = Vector(0, 1, 0)
cam = PerspectiveCamera(eye, lookat, ra, up)
world.camera = cam

#Colors
red = Color(1.0, 0, 0)
green = Color(0, 1.0, 0)
blue = Color(0, 0, 1.0)
white = Color(1.0, 1.0, 1.0)
grey = Color(0.5, 0.5, 0.5)
Sred = RegularSurface(red)
Sgrey = RegularSurface(grey)
Sgreen = RegularSurface(green)
Sblue = RegularSurface(blue)
Swhite = RegularSurface(white)

r_sample = Regular(25, 83)
#Materials
mat = Matte(1.0, 1.0, Sred)
phong = Phong(1.0, 0.7, 0.3, Sred, 80.0)
greymat = Matte(0.5, 0.5, Sgrey)
bluemat = Matte(0.5, 0.5, Sblue)
reflective = Reflective(0.25, 0.25, 0.75, Sgreen, 500, 1.0, Swhite)
transparent = Transparent(0.0, 0.1, 0.1, Swhite, 200, 0.1, Swhite, 1.0, 1.5)
glossy = GlossyReflective(1, 1, 1, Sred, 50000, 1.0, Sred, r_sample)

#Objects

plane = Plane(Point(0, -15, 0), Vector(0, 1, -0.1), greymat)
world.addObject(plane)
plane2 = Plane(Point(0, 0, 20), Vector(0, 0, 1), bluemat)
world.addObject(plane2)

#Reflective Spheres
s3 =Sphere(Point(-22, 0, -3), 10.0, glossy)
world.addObject(s3)

#Instance
sphere = Sphere(Point( 0, 0, -5), 5.0, mat)
s_i = Instance(sphere)
s_i.translate(25, 10, 0)
s_i.scale(1, 2, 1)
world.addObject(s_i)

#Transparent Sphere
c = Point(0, 0, -5)
r = 10.0
s = Sphere(c, r, transparent)
world.addObject(s)

#Texture Sphere
image = Image.open("earthmap1k.jpg")
texels = image.load()
sphere_map = SphericalMapping(8.0)
sampler = Regular(25, 83)
texture = ImageTexture(texels, sphere_map, image.size[0], image.size[1])
t_mat = Matte(0.75, 0.75, texture, sampler)
t_s = Sphere(Point(0, 0, -5), 8.0, t_mat)
world.addObject(t_s)

#area Light
intensity = 10.0
emissive = Emissive(intensity, white)
p0 = Point(-5, 20, -12)
a = Vector(10.0, 0, 0)
b = Vector(0, 10.0, 0)
sampler = Regular(25, 83)
rectangle = Rectangle(p0, a, b, emissive, sampler)
world.addObject(rectangle)
area_light = AreaLight(rectangle)
world.addLight(area_light)

"""
#Bunny
vertices, faces = world.OBJLoad("bunny.obj")
for f in faces:
    t = Triangle(vertices[f[0]-1], vertices[f[1]-1], vertices[f[2]-1], phong)
    world.addObject(t)

"""
start_time = time.time()
world.renderScene()
print("Time elapsed: {0}".format(time.time() - start_time))
print("with {0} rays shot".format(world.rays))
