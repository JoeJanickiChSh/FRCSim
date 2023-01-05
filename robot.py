from vector3d.vector import Vector

from box import Box
from loader import get_color, get_vec
from units import inches_to_meters, degrees_to_radians


class Robot:
    def __init__(self, dct):
        self.position = inches_to_meters(get_vec(dct["position"]))
        self.velocity = Vector(0, 0, 0)
        self.rot_vel = 0
        self.rotation = degrees_to_radians(get_vec(dct["rotation"]))
        self.size = inches_to_meters(get_vec(dct["size"]))
        self.color = get_color(dct["color"])
        self.acceleration = inches_to_meters(dct["speed"])
        self.rot_speed = degrees_to_radians(dct["rotationSpeed"])
        self.shoot_angle = degrees_to_radians(dct["shootAngle"])
        self.shoot_speed = inches_to_meters(dct["shootSpeed"])
        self.friction = dct["friction"]

    def get_box(self):
        return Box(self.position, self.size, self.rotation, self.color)
