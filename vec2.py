from __future__ import annotations
from typing import List
import numpy as np
import math


class Vector2(object):
    def __init__(self, X, Y):
        self.x: int = X
        self.y: int = Y

    def magnitude(self) -> float:
        return math.sqrt(pow(self.x, 2) + pow(self.y, 2))

    def to_tuple(self) -> tuple:
        return (self.x, self.y)

    def to_list(self) -> List:
        return [self.x, self.y]

    def normalized(self) -> Vector2:
        mag: float = self.magnitude()
        return Vector2(self.x / mag, self.y / mag)

    def rotate_around(self, target, deg):
        x, y = self.x, self.y
        ox, oy = target.x, target.y
        radians: float = np.deg2rad(deg)
        qx = ox + math.cos(radians) * (x - ox) + math.sin(radians) * (y - oy)
        qy = oy + -math.sin(radians) * (x - ox) + math.cos(radians) * (y - oy)
        return Vector2(qx, qy)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2((self.x - other.x), (self.y - other.y))

    def __add__(self, other: Vector2):
        return Vector2((self.x + other.x), (self.y + other.y))

    def __str__(self):
        string: string = "Vector2(%i, %i)" % (self.x, self.y)
        return string;
