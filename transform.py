from math import sin, cos
from vector3d.vector import Vector


def scale_vector(a, b):
    return Vector(a.x * b.x, a.y * b.y, a.z * b.z)


def rotate_vector(vec, vec2):
    xRot = vec2.x
    yRot = vec2.y
    zRot = vec2.z

    cosa = cos(zRot)
    sina = sin(zRot)

    cosb = cos(yRot)
    sinb = sin(yRot)

    cosc = cos(xRot)
    sinc = sin(xRot)

    Axx = cosa * cosb
    Axy = cosa * sinb * sinc - sina * cosc
    Axz = cosa * sinb * cosc + sina * sinc

    Ayx = sina * cosb
    Ayy = sina * sinb * sinc + cosa * cosc
    Ayz = sina * sinb * cosc - cosa * sinc

    Azx = -sinb
    Azy = cosb * sinc
    Azz = cosb * cosc

    px = vec.x
    py = vec.y
    pz = vec.z

    pointx = Axx * px + Axy * py + Axz * pz
    pointy = Ayx * px + Ayy * py + Ayz * pz
    pointz = Azx * px + Azy * py + Azz * pz
    return Vector(pointx, pointy, pointz)
