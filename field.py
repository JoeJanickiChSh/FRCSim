from box import Box
from loader import get_color, get_vec
from units import degrees_to_radians, inches_to_meters


class Field:
    def __init__(self, dct):
        self.boxes = []
        for box_name in dct:
            box = dct[box_name]
            self.boxes.append(
                Box(
                    inches_to_meters(get_vec(box["position"])),
                    inches_to_meters(get_vec(box["size"])),
                    degrees_to_radians(get_vec(box["rotation"])),
                    get_color(box["color"]),
                    "showDir" in box,
                )
            )
