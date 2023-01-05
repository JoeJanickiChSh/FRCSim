from vector3d.vector import Vector


def get_vec(dct):
    return Vector(dct["x"], dct["y"], dct["z"])


def get_color(dct):
    return Vector(dct["r"], dct["g"], dct["b"])
