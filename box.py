class Box:
    def __init__(self, position, size, rotation, color, show_dir=False):
        self.position = position
        self.size = size
        self.rotation = rotation
        self.color = color
        self.show_dir = show_dir

    def collision(self, other):
        x_collision = (
            abs(self.positioin.x - other.position.x)
            > (self.size.x + other.size.x) * 0.5
        )
        y_collision = (
            abs(self.positioin.y - other.position.y)
            > (self.size.y + other.size.y) * 0.5
        )
        z_collision = (
            abs(self.positioin.z - other.position.z)
            > (self.size.z + other.size.z) * 0.5
        )
        return x_collision and y_collision and z_collision
