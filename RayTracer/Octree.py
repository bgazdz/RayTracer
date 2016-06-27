from GeometricObjects import *
from ShadeRec import *
from Material import *
import Constants
#Maximum number of objects a leaf can hold before it adds children

class Octnode:

    def __init__(self, p, s, obj, h):
        """
        Node of the OcTree

        Attributes:
            p: tuple representing the center of the box
            s: size of the box
            o: list of objects in the box
            children: list of children of box
            h: depth of node in the tree
            l: tuple representing the lower back corner of box
            u: tuple representing the upper front corner of the box
        """
        self.p = p
        self.s = s
        self.children = [None, None, None, None, None, None, None, None]
        self.leaf = True
        self.h = h+1
        self.o = obj
        off = self.s/2
        self.l = Point(self.p.x-off, self.p.y-off, self.p.z-off)
        self.u = Point(self.p.x+off, self.p.y+off, self.p.z+off)

    def intersectRay(self, ray):
        """ Determine if a ray intersects the box
            Returns: the parameter t for the closest intersection point to
                     the ray origin.
                     Returns a value of None for no intersection
        """  
        tmin = -BIGTIME
        tmax = BIGTIME
        if ray.d.x != 0:
            t1 = (self.l.x - ray.o.x)/(ray.d.x)
            t2 = (self.u.x - ray.o.x)/(ray.d.x)
            tmin = max(min(t1, t2), tmin)
            tmax = min(max(t1, t2), tmax)
        if ray.d.y != 0:
            t3 = (self.l.y - ray.o.y)/(ray.d.y)
            t4 = (self.u.y - ray.o.y)/(ray.d.y)
            tmin = max(min(t3, t4), tmin)
            tmax = min(max(t3, t4), tmax)
        if ray.d.z != 0:
            t5 = (self.l.z - ray.o.z)/(ray.d.z)
            t6 = (self.u.z - ray.o.z)/(ray.d.z)
            tmin = max(min(t5, t6), tmin)
            tmax = min(max(t5, t6), tmax)
        if tmax < kEpsilon:
            return False
        if tmin > tmax:
            return False
        self.t = tmin
        return True


class Octree:

    def __init__(self, ws):
        """
        OcTree

        Attributes:
            root: root node of the tree
            ws: size of the root of the tree
        """
        self.root = self.addNode(Point(0, 0, 0), ws, [], -1)
        self.ws = ws
        
    def addNode(self, p, s, o, h):
        """ Creates the actual node and returns it """
        return Octnode(p, s, o, h)

    def insertChild(self, root, s, parent, obj):
        """
        Inserts obj to the correct leaf node
        Takes in:
            The current node to look at (root)
            The size of the parent (s)
            The parent node (parent)
            The object to add (obj)
        Extends the tree if need be
        Returns the node that holds the object
        """
        #Doesn't exist, so make it
        if root == None:
            p = parent.p
            off = s/2
            branch = self.findDirection(parent, obj)

            if branch == 0:
                nC = Point(p.x-off, p.y-off, p.z-off)
            elif branch == 1:
                nC = Point(p.x-off, p.y-off, p.z+off)
            elif branch == 2:
                nC = Point(p.x-off, p.y+off, p.z-off)
            elif branch == 3:
                nC = Point(p.x-off, p.y+off, p.z+off)
            elif branch == 4:
                nC = Point(p.x+off, p.y-off, p.z-off)
            elif branch == 5:
                nC = Point(p.x+off, p.y-off, p.z+off)
            elif branch == 6:
                nC = Point(p.x+off, p.y+off, p.z-off)
            elif branch == 7:
                nC = Point(p.x+off, p.y+off, p.z+off)
            return self.addNode(nC, s, [obj], parent.h)

        #Not a leaf node, so search the correct child
        elif root.leaf == False:
            branch = self.findDirection(root, obj)
            s = root.s/2
            if branch < 8:
                root.children[branch] = self.insertChild(root.children[branch], s, root, obj)
            else:
                root.o.append(obj)
                if root.h < MAX_DEPTH:
                    if len(root.o) >= MAX_OBJ:
                        objects = root.o
                        root.leaf = False
                        s = root.s/2
                        for ob in objects:
                            root.o.remove(ob)
                            branch = self.findDirection(root, ob)
                            if branch < 8:
                                root.children[branch] = self.insertChild(root.children[branch], s, root, ob)
                            else:
                                root.o.append(ob)
       
        #Add to leaf, if need to make new nodes, then make them and move the objects into their correct nodes
        elif root.leaf:
            root.o.append(obj)
            if root.h < MAX_DEPTH:
                if len(root.o) >= MAX_OBJ:
                    objects = root.o
                    root.leaf = False
                    s = root.s/2
                    for ob in objects:
                        root.o.remove(ob)
                        branch = self.findDirection(root, ob)
                        if branch < 8:
                            root.children[branch] = self.insertChild(root.children[branch], s, root, ob)
                        else:
                            root.o.append(ob)

        return root

    def findDirection(self, root, ob):
        """ 
        Finds which child of root that holds obj inside of it
        Returns: the value of the correct child in the list that holds the point
                 Returns 8 if the object is too big for the child and should stay in the current root
        """
        p2 = root.p
        p1 = ob.position
        child = 7
        if(p1.x < p2.x):
            child -= 4
        if(p1.y < p2.y):
            child -= 2
        if(p1.z < p2.z):
            child -= 1

        #Check if out of range of child's box
        #Find child's center
        branch = child
        off = root.s/2
        if branch == 0:
            p3 = Point(p2.x-off, p2.y-off, p2.z-off)
        elif branch == 1:
            p3 = Point(p2.x-off, p2.y-off, p2.z+off)
        elif branch == 2:
            p3 = Point(p2.x-off, p2.y+off, p2.z-off)
        elif branch == 3:
            p3 = Point(p2.x-off, p2.y+off, p2.z+off)
        elif branch == 4:
            p3 = Point(p2.x+off, p2.y-off, p2.z-off)
        elif branch == 5:
            p3 = Point(p2.x+off, p2.y-off, p2.z+off)
        elif branch == 6:
            p3 = Point(p2.x+off, p2.y+off, p2.z-off)
        elif branch == 7:
            p3 = Point(p2.x+off, p2.y+off, p2.z+off)

        if ob.type == "Sphere":
            #Compare to the 8 edges to find which is closest
            p4 = Point(p3.x-off, p3.y-off, p3.z-off)
            dx = p4.x - p1.x
            dy = p4.y - p1.y
            dz = p4.z - p1.z
            if abs(dx) < ob.r or abs(dy) < ob.r or abs(dz) < ob.r:
                child = 8
            p4 = Point(p3.x+off, p3.y+off, p3.z+off)
            dx = p4.x - p1.x
            dy = p4.y - p1.y
            dz = p4.z - p1.z
            if abs(dx) < ob.r or abs(dy) < ob.r or abs(dz) < ob.r:
                child = 8
        elif ob.type == "Triangle":
            #Check if any of the edge points are outside of the box
            #Check lower
            p4 = Point(p3.x-off, p3.y-off, p3.z-off)
            if ob.p0.x < p4.x or ob.p1.x < p4.x or ob.p2.x < p4.x:
                child = 8
            elif ob.p0.y < p4.y or ob.p1.y < p4.y or ob.p2.y < p4.y:
                child = 8
            elif ob.p0.z < p4.z or ob.p1.z < p4.z or ob.p2.z < p4.z:
                child = 8
            #Check upper
            p4 = Point(p3.x+off, p3.y+off, p3.z+off)
            if ob.p0.x > p4.x or ob.p1.x > p4.x or ob.p2.x > p4.x:
                child = 8
            elif ob.p0.y > p4.y or ob.p1.y > p4.y or ob.p2.y > p4.y:
                child = 8
            elif ob.p0.z > p4.z or ob.p1.z > p4.z or ob.p2.z > p4.z:
                child = 8
        elif ob.type == "Plane":
            #Keep on root always
            child = 8
        return child

        