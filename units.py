from math import pi


def inches_to_meters(x):
    return x * 0.0254


def meters_to_inches(x):
    return x * (1 / 0.0254)


def degrees_to_radians(x):
    return x * (pi / 180.0)


def radians_to_degrees(x):
    return x * (180.0 / pi)
