from vector3d.vector import Vector


class Camera:
    def __init__(
        self, position: Vector = Vector(0, 0, 0), rotation: Vector = Vector(0, 0, 0), zoom: float = 1.0
    ):
        self.position = position
        self.rotation = rotation
        self.zoom = zoom
