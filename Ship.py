class Ship:
    def __init__(self, cells, orientation):
        self.cells = cells
        self.orientation = orientation
        self.destroyed = False