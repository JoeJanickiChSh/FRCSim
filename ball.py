from vector3d.vector import Vector
from box import Box


class Ball:
    def __init__(self, position, velocity, diameter, color):
        self.position = position
        self.velocity = velocity
        self.radius = diameter / 2
        self.color = color
        self.rotation = 0

    def get_box(self):
        return Box(
            self.position,
            Vector(1, 1, 1) * (self.radius * 2),
            Vector(1, 1, 1) * self.rotation,
            self.color,
        )
