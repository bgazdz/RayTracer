from Utilities import *
from ShadeRec import *
from Sampler import *

# #419begin #type=3 #src= Ray Trace Ground Up
class Material():
    def shade(self, sr):
        pass

class Matte(Material):
    def __init__(self, ka, kd, cd, sampler = None):
        """
        Attributes:
            ambient: Lambertian of ambient
            diffuse: Lambertian of diffuse
            cd: Surface
        """
        self.ambient = Lambertian(ka, cd, sampler)
        self.diffuse = Lambertian(kd, cd, sampler)
        self.cd = cd

    #Non-area light shade function
    def shade(self, sr):
        #Add ambient light
        L = self.ambient.rho(sr) * sr.w.ambient.L(sr)
        #For each light, add up color
        for light in sr.w.lights:
            wi = -1.0 * light.getDirection(sr)
            wi = wi.normalize()
            ndotwi = sr.normal * wi
            if ndotwi > 0.0:
                shadow = False

                #Check if there's another object in the way
                shadowRay = Ray(sr.hit_point, wi)
                shadow = light.inShadow(shadowRay, sr)
                #No object in the way, so add the color
                if not shadow:
                    L += self.diffuse.f(sr) * light.L(sr) * ndotwi

        return L

    #Area light shade func
    def areaLightShade(self, sr):
        #Add ambient light
        L = self.ambient.rho(sr) * sr.w.ambient.L(sr)
        #For each light, add up color
        for light in sr.w.lights:
            wi = -1.0 * light.getDirection(sr)
            wi = wi.normalize()
            ndotwi = sr.normal * wi
            if ndotwi > 0.0:
                shadow = False
                #Check if object is in the way
                shadowRay = Ray(sr.hit_point, wi)
                shadow = light.inShadow(shadowRay, sr)
                #No object in the way, so add color
                if not shadow:
                    L += self.diffuse.f(sr) * light.L(sr) * ndotwi * light.G(sr) / light.pdf(sr)

        return L

class Phong(Material):
    def __init__(self, ka, kd, ks, cd, exp):
        """
        Attributes:
            ambient: Lambertian of ambient
            diffuse: Lambertian of diffuse
            specular: GlossySpecular
            cd: Surface
        """
        self.ambient = Lambertian(ka, cd)
        self.diffuse = Lambertian(ka, cd)
        self.specular = GlossySpecular(ks, cd, exp, None)
        self.cd = cd

    #Non area light shade, similar to Matte (but add specular)
    def shade(self, sr):
        wo  = -1.0 * sr.ray.d
        wo = wo.normalize()
        L = self.ambient.rho(sr) * sr.w.ambient.L(sr)
        for light in sr.w.lights:
            wi = -1.0 * light.getDirection(sr)
            wi = wi.normalize()
            ndotwi = sr.normal * wi
            if ndotwi > 0:
                shadow = False
                shadowRay = Ray(sr.hit_point, wi)
                shadow = light.inShadow(shadowRay, sr)
                if not shadow:
                    L += (self.diffuse.f(sr) + self.specular.f(sr, wo, wi)) * light.L(sr) * ndotwi

        return L

    #Area light shade, similar to Matte (but add specular)
    def areaLightShade(self, sr):
        wo  = -1.0 * sr.ray.d
        wo = wo.normalize()
        L = self.ambient.rho(sr) * sr.w.ambient.L(sr)
        for light in sr.w.lights:
            wi = -1.0 * light.getDirection(sr)
            wi = wi.normalize()
            ndotwi = sr.normal * wi
            if ndotwi > 0:
                shadow = False
                shadowRay = Ray(sr.hit_point, wi)
                shadow = light.inShadow(shadowRay, sr)
                if not shadow:
                    L += (self.diffuse.f(sr) + self.specular.f(sr, wo, wi)) * light.L(sr) * ndotwi * light.G(sr) / light.pdf(sr)

        return L

class Reflective(Phong):
    def __init__(self, ka, kd, ks, cd, exp, kr, cr):
        #Subclass of Phong Material
        #reflective is the PerfectSpecular reflection
        Phong.__init__(self, ka, kd, ks, cd, exp)
        self.reflective = PerfectSpecular(kr, cr)

    #Non area light shade, similar to Phong (but add reflective)
    def shade(self, sr):
        L = Phong.shade(self, sr)

        wo = -1.0 * sr.ray.d
        fr = self.reflective.sample_f(sr, wo)
        wi = self.reflective.wi
        reflectedRay = Ray(sr.hit_point, wi)
        ndotwi = sr.normal * wi
        L += fr * sr.w.tracer.trace(reflectedRay, sr.depth+1) * (ndotwi)

        return L
    #Area light shade, similar to Phong (but add reflective)
    def areaLightShade(self, sr):
        L = Phong.areaLightShade(self, sr)

        wo = -1.0 * sr.ray.d
        fr = self.reflective.sample_f(sr, wo)
        wi = self.reflective.wi
        reflectedRay = Ray(sr.hit_point, wi)
        ndotwi = sr.normal * wi
        L += fr * sr.w.tracer.trace(reflectedRay, sr.depth+1) * (ndotwi)

        return L

class GlossyReflective(Phong):
    def __init__(self, ka, kd, ks, cd, exp, kr, cr, sampler):
        #Subclass of phong
        #Attributes to add:
        #   glossy: Glossy Reflection
        Phong.__init__(self, ka, kd, ks, cd, exp)
        self.glossy = GlossySpecular(kr, cr, exp, sampler)
        self.glossy.setSamples(exp)

    #Area light shade, similar to Phong (but add reflective)
    def areaLightShade(self, sr):
        L = Phong.areaLightShade(self, sr)
        wo = -1.0 * sr.ray.d
        fr = self.glossy.sample_f(sr, wo)
        r_ray = Ray(sr.hit_point, self.glossy.wi)
        L += fr * sr.w.tracer.trace(r_ray, sr.depth + 1) * (sr.normal * self.glossy.wi) / self.glossy.pdf
        return L



class Transparent(Reflective):
    def __init__(self, ka, kd, ks, cd, exp, kr, cr, kt, ior):
        #Subclass of Reflective
        #transparent: Transparent BTDF
        L = Phong.__init__(self, ka, kd, ks, cd, exp)
        self.reflective = PerfectSpecular(kr, cr)
        self.transparent = PerfectTransmitter(kt, ior)

    #Non area light shade, similar to Reflective (but add Transparence)
    def shade(self, sr):
        L = Phong.shade(self, sr)
        wo = -1.0 * sr.ray.d
        fr = reflective.sample_f(sr, wo)
        wi = self.reflective.wi
        r_ray = Ray(sr.hit_point, wi)
        if(self.transparent.tir(sr)):
            L += sr.w.tracer.trace(r_ray, sr.depth + 1)
        else:
            ft = self.transparent.sample_f(sr, wo)
            wt = self.transparent.wt
            t_ray = Ray(sr.hit_point, wt)
            L += fr * sr.w.tracer.trace(r_ray, sr.depth + 1) * math.fabs(sr.normal * wi)
            L += ft * sr.w.tracer.trace(t_ray, sr.depth + 1) * math.fabs(sr.normal * wt)
        return L

    #Area light shade, similar to Reflective (but add Transparence)
    def areaLightShade(self, sr):
        L = Phong.shade(self, sr)
        wo = -1.0 * sr.ray.d
        fr = self.reflective.sample_f(sr, wo)
        wi = self.reflective.wi
        r_ray = Ray(sr.hit_point, wi)
        if(self.transparent.tir(sr)):
            L += sr.w.tracer.trace(r_ray, sr.depth + 1)
        else:
            ft = self.transparent.sample_f(sr, wo)
            wt = self.transparent.wt
            t_ray = Ray(sr.hit_point, wt)
            L += fr * sr.w.tracer.trace(r_ray, sr.depth + 1) * math.fabs(sr.normal * wi)
            L += ft * sr.w.tracer.trace(t_ray, sr.depth + 1) * math.fabs(sr.normal * wt)
        return L


class Emissive(Material):
    def __init__(self, ls, ce):
        """
        Attributes:
            ls: Light intensity
            ce: Emissive Color
        """
        self.ls = ls
        self.ce = ce

    #No shade func since emissive is only used for Area Lights

    #Area Light Shade func
    def areaLightShade(self, sr):
        wo = -1.0 * sr.ray.d
        wo = wo.normalize()
        #If on emissive side
        if sr.normal * wo > 0.0:
            return self.ls * self.ce
        else:
            return Color(0, 0, 0)

    #Return Color * Intensity
    def getLe(self):
        return self.ls * self.ce

    #Return color
    def getColor(self, sr):
        return self.ce


class Surface:
    def getColor(self, sr):
        pass

class RegularSurface(Surface):
    def __init__(self, color):
        #Constant surface, aka non-textured surface
        #Color: color of surface
        self.color = color

    #Return surface's color
    def getColor(self, sr):
        return self.color

class ImageTexture(Surface):
    def __init__(self, texels, mapping, image_width, image_height):
        """
        Attrubutes:
            t: list of texel values
            m: Type of mapping
            hres: width
            vres: height
        """
        self.t = texels
        self.m = mapping
        self.hres = image_width
        self.vres = image_height

    #Return Color at sr.local_hit of the texture
    def getColor(self, sr):
        column, row = self.m.getCoordinates(sr.local_hit, self.hres, self.vres)
        r, g, b = self.t[column, row]
        return Color(r/255.0, g/255.0, b/255.0)

class TextureMapping:
    def getCoordinates(self, local_hit, hres, vres):
        pass

class SphericalMapping(TextureMapping):
    def __init__(self, r):
        """
        Attributes:
            c: column for texel
            r: row for texel
            radius: radius of sphere we are mapping to
        """
        self.c = 0
        self.r = 0
        self.radius = r

    #get c and r for texel
    def getCoordinates(self, local_hit, hres, vres):
        theta = math.acos(local_hit.y/self.radius)
        phi = math.atan2(local_hit.x/self.radius, local_hit.z/self.radius)
        pi = math.pi

        if phi < 0.0:
            phi += 2*pi

        u = phi * (1.0/(2*pi))
        v = 1.0 - theta * (1.0 / pi)
        c = int((hres - 1) * u)
        r = int((vres - 1) * v)

        return c, r


class BRDF:
    def f(self):
        pass

class Lambertian(BRDF):
    def __init__(self, kd, surface, sampler = None):
        """
        Attributes:
            kd: intensity
            surface: Object surface
            sampler: Sampler (if any)
        """
        self.kd = kd
        self.surface = surface
        if sampler != None:
            self.sampler = sampler
            self.sampler.mapHemisphere(1)

    #Return kd * color
    def rho(self, sr):
        return self.kd * self.surface.getColor(sr)

    #Return kd * color / PI
    def f(self, sr):
        return (self.kd * self.surface.getColor(sr))/math.pi

    #Sample sampler, return values for coloring
    def sample_f(self, sr):
        w = sr.normal
        v = Vector(0.0034, 1, 0.0071).cross(w)
        v.normalize()
        u = v.cross(w)

        sp = self.sampler.sampleHemisphere()
        wi = sp.x * u + sp.y * v + sp.z * w
        wi.normalize()
        pdf = sr.normal * wi / math.pi

        return pdf, wi, (self.kd * self.surface.getColor(sr) / math.pi)


class GlossySpecular(BRDF):
    def __init__(self, ks, surface, exp, sampler):
        """
        Attributes:
            ks: intensity
            surface: Object surface
            exp: Exponent e
            sampler: Sampler (if any)
        """
        self.ks = ks
        self.surface = surface
        self.exp = exp
        if(sampler != None):
            self.sampler = Regular(25, 83)

    #Set up samples
    def setSamples(self, exp):
        self.sampler.mapHemisphere(exp)

    #Return L (coloring)
    def f(self, sr, wo, wi):
        ndotwi = sr.normal * wi
        r = -1.0 * wi + 2 * sr.normal * ndotwi
        rdotwo = r * wo
        L = Color(0, 0, 0)

        if rdotwo > 0.0:
            L = self.ks * self.surface.getColor(sr) * pow(rdotwo, self.exp)

        return L

    #Sample sampler, return coloring value
    def sample_f(self, sr, wo):
        ndotwo = sr.normal * wo
        r = -1.0 * wo + 2 * sr.normal * ndotwo
        w = r
        u = Vector(0.00424, 1, 0.00764).cross(w)
        u.normalize()
        v = u.cross(w)
        sp = self.sampler.sampleHemisphere()
        #Store wi
        self.wi = sp.x * u + sp.y * v + sp.z * w
        if sr.normal * self.wi < 0.0:
            self.wi = -1.0 * sp.x * u - sp.y * v - sp.z * w

        phong_lobe = pow(r * self.wi, self.exp)
        #Store pdf
        self.pdf = phong_lobe * (sr.normal * self.wi)
        return (self.ks * self.surface.getColor(sr) * phong_lobe)

class PerfectSpecular(BRDF):
    def __init__(self, kr, surface):
        """
        Attributes:
            kr: intensity
            surface: Object Surface
        """
        self.kr = kr
        self.surface = surface

    #F func (return Black)
    def f(self):
        return Color(0, 0, 0)

    #Return coloring values
    def sample_f(self, sr, wo):
        ndotwo = sr.normal * wo
        #Store wi
        self.wi = -1.0 * wo + 2 * sr.normal * ndotwo
        pdf = math.fabs(sr.normal * self.wi)
        return (self.kr * self.surface.getColor(sr) / pdf)

class PerfectTransmitter(BRDF):
    def __init__(self, kt, ior):
        """
        Attributes:
            kt: intensity
            ior: refraction
        """
        self.kt = kt
        self.ior = ior

    #Ignore
    def f(self):
        pass

    #Return White modified by refraction values
    def sample_f(self, sr, wo):
        cos_thetai = sr.normal * wo
        n = sr.normal
        eta = self.ior
        if cos_thetai < 0.0:
            cos_thetai = -cos_thetai
            n = -1.0 * n
            eta = 1.0 / eta

        temp = 1.0 - (1.0 - cos_thetai*cos_thetai) / (eta*eta)
        cos_theta2 = math.sqrt(temp)
        #Save wt
        self.wt = -1.0 * wo / eta - (cos_theta2 - cos_thetai / eta) * n
        return (self.kt / (eta * eta) * Color(1, 1, 1) / math.fabs(sr.normal * self.wt))

    #Ignore
    def rho(self):
        pass

    #Total internal reflection
    def tir(self, sr):
        wo = -1.0 * sr.ray.d
        cos_thetai = sr.normal * wo
        eta = self.ior
        if cos_thetai < 0.0:
            eta = 1.0/eta
        #Return true or false
        return (1.0 - (1.0 - cos_thetai * cos_thetai) / (eta * eta) < 0) 

# #419end