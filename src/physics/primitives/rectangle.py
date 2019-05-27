from .polygon import Polygon


class Rectangle(Polygon):
    def __init__(self, x, y, w, h):
        Polygon.__init__(self, (x, y), (x, y + h), (x + w, y + h), (x + w, y))
