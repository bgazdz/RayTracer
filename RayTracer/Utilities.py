import math
import Constants

class Ray():
    def __init__(self, origin, direction):
        """
        Attributes:
            o: Origin Point
            d: Direction Vector
        """
        self.o = origin
        self.d = direction

class Point():
    def __init__(self, x, y, z):
        """
        Attributes:
            x: x value of point
            y: y value of point
            z: z value of point
            w: w value (for Matrix Mult)
        """
        self.x = x
        self.y = y
        self.z = z
        self.w = 1

    #Add with another point, vector, or scalar
    def __add__(self, other):
        if isinstance(other, Vector) or isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            return Point(self.x + other, self.y + other, self.z + other)
    #Subtract with another point, vector, or scalar
    def __sub__(self, other):
        if isinstance(other, Point) or isinstance(other, Vector):
            return Vector(self.x-other.x, self.y-other.y, self.z-other.z)
        else:
            return Point(self.x - other, self.y - other, self.z - other)

    #Mult by scalar
    def __mul__(self, other):
        return Point(self.x*other, self.y*other, self.z*other)
    #Mult by scalar
    def __rmul__(self, other):
        return Point(self.x*other, self.y*other, self.z*other)
    #Div by scalar
    def __truediv__(self, other):
        return Point(self.x / other, self.y / other, self.z / other)

    #returns distance between two points
    def distance(self, other):
        return math.sqrt((self.x - other.x)*(self.x - other.x)
                         + (self.y - other.y)*(self.y - other.y)
                         + (self.z - other.z)*(self.z - other.z))

    #Matrix Multiplication
    def Mmult(self, matrix):
        return Point(matrix.m[0]*self.x + matrix.m[1]*self.y + matrix.m[2]*self.z + matrix.m[3],
                     matrix.m[4]*self.x + matrix.m[5]*self.y + matrix.m[6]*self.z + matrix.m[7],
                     matrix.m[8]*self.x + matrix.m[9]*self.y + matrix.m[10]*self.z + matrix.m[11])

class Vector():
    def __init__(self, x, y, z):
        """
        Attributes:
            x: x value of vector
            y: y value of vector
            z: z value of vector
            w: w value (for Matrix Mult)
        """
        self.x = x
        self.y = y
        self.z = z
        self.w = 0

    #Add with another vector or scalar
    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            return Vector(self.x + other, self.y + other, self.z + other)

    #Subtract from another vector
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
    
    #Mult with another vector(cross) or scalar
    def __mul__(self, other):
        if isinstance(other, Vector):
            return (self.x * other.x + self.y * other.y + self.z * other.z)
        else:
            return Vector(self.x * other, self.y*other, self.z*other)
    #Mult with another vector(cross) or scalar
    def __rmul__(self, other):
        if isinstance(other, Vector):
            return (self.x * other.x + self.y * other.y + self.z * other.z)
        else:
            return Vector(self.x * other, self.y*other, self.z*other)

    #Divide by scalar
    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other, self.z / other)

    #Return cross of two vectors
    def cross(self, other):
        return Vector(self.y * other.z - self.z * other.y, self.z * other.x - self.x * other.z, self.x * other.y - self.y * other.x)

    #Return length of vector
    def length(self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

    #normalize vector
    def normalize(self):
        l = math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
        self.x = self.x/l
        self.y = self.y/l
        self.z = self.z/l
        return self

    #Matrix multiplication
    def Mmult(self, matrix):
        return Vector(matrix.m[0]*self.x + matrix.m[1]*self.y + matrix.m[2]*self.z,
                     matrix.m[4]*self.x + matrix.m[5]*self.y + matrix.m[6]*self.z,
                     matrix.m[8]*self.x + matrix.m[9]*self.y + matrix.m[10]*self.z)

class Matrix():
    #m: list of 16 floats that make up 4x4 matrix
    def __init__(self, x1, y1, z1, w1, x2, y2, z2, w2, x3, y3, z3, w3, x4, y4, z4, w4):
        self.m = [x1, y1, z1, w1, x2, y2, z2, w2, x3, y3, z3, w3, x4, y4, z4, w4]

    #Create a translation matrix by (x,y,z)
    def Translate(x, y, z):
        return Matrix(1, 0, 0, x, 
                      0, 1, 0, y, 
                      0, 0, 1, z,
                      0, 0, 0, 1)

    #Create a scale matrix by (x, y, z)
    def Scale(x, y, z):
        return Matrix(
            x, 0, 0, 0,
            0, y, 0, 0,
            0, 0, z, 0,
            0, 0, 0, 1)

    #Create a Rotate matrix around x by theta
    def RotateX(theta):
        return Matrix(
            1, 0, 0, 0,
            0, math.cos(theta), -1*math.sin(theta), 0,
            0, math.sin(theta), math.cos(theta), 0,
            0, 0, 0, 1)

    #Create a Rotate matrix around Y by theta
    def RotateY(theta):
        return Matrix(
            math.cos(theta), 0, -1*math.sin(theta), 0,
            0, 1, 0, 0,
            math.sin(theta), 0, math.cos(theta), 0,
            0, 0, 0, 1)

    #Create a Rotate matrix around Z by theta
    def RotateZ(theta):
        return Matrix(
            math.cos(theta), -1*math.sin(theta), 0, 0,
            math.sin(theta), math.cos(theta), 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1)

     
    #Matrix multiplication
    def __mul__(self, other):
        product = Matrix(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        for y in range(4):
            for x in range(4):
                sum = 0.0
                for j in range(4):
                    sum += self.m[x+j*4] * other.m[j+y*4]

                product.m[x+y*4] = sum
        return product

    #Scalar division by other
    def divide(self, other):
        for y in range(4):
            for x in range(4):
                self.m[x+y*4] = self.m[x+y*4]/other

    #Return Identity matrix
    def identity():
        return Matrix(
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1)


class Color():
    def __init__(self, r, g, b):
        """
        Attributes:
            r: R value of RGB
            g: G value of RGB
            b: B value of RGB
        """
        self.r = r
        self.g = g
        self.b = b

    #Add two colors
    def __add__(self, other):
        return Color(self.r + other.r, self.g + other.g, self.b + other.b)

    #Subtract two colors
    def __sub__(self, other):
        return Color(self.r - other.r, self.g - other.g, self.b - other.b)

    #Mult two colors, or by scalar
    def __mul__(self, other):
        if isinstance(other, Color):
            return Color(self.r * other.r, self.g * other.g, self.b * other.b)
        else:
            return Color(self.r*other, self.g*other, self.b*other)

    #Mult two colors, or by scalar
    def __rmul__(self, other):
        if isinstance(other, Color):
            return Color(self.r * other.r, self.g * other.g, self.b * other.b)
        else:
            return Color(self.r*other, self.g*other, self.b*other)

    #divide by scalar
    def __truediv__(self, other):
        return Color(self.r/other, self.g/other, self.b/other)


#NOT USED
# #419begin #type=3 #src= Ray Trace Ground Up
class Bbox():
    def __init__(self):
        self.l = Point(-1.0, -1.0, -1.0)
        self.u = Point(1.0, 1.0, 1.0)

    def __init__(self, p0, p1):
        self.l = p0
        self.u = p1

    def getPoints(self):
        return [
            Point(self.l.x, self.l.y, self.l.z),
            Point(self.l.x, self.l.y, self.u.z),
            Point(self.l.x, self.u.y, self.l.z),
            Point(self.l.x, self.u.y, self.u.z),
            Point(self.u.x, self.l.y, self.l.z),
            Point(self.u.x, self.l.y, self.u.z),
            Point(self.u.x, self.u.y, self.l.z),
            Point(self.u.x, self.u.y, self.u.z)
        ]
        

    def hit(self, ray):
        t1 = (self.l.x - ray.o.x)/ray.d.x
        t2 = (self.u.x - ray.o.x)/ray.d.x
        t3 = (self.l.y - ray.o.y)/ray.d.y
        t4 = (self.u.y - ray.o.y)/ray.d.y
        t5 = (self.l.z - ray.o.z)/ray.d.z
        t6 = (self.u.z - ray.o.z)/ray.d.z
        tmin = max(max(min(t1, t2), min(t3, t4)), min(t5, t6))
        tmax = min(min(max(t1, t2), max(t3, t4)), max(t5, t6))
        return (tmin < tmax and tmax > kEpsilon)
    
    def inside(self, p):
        return ((p.x > self.l.x and p.x < self.u.x) and (p.y > self.l.y and p.y < self.u.y) and (p.z > self.l.z and p.z < self.u.z))

# #419end