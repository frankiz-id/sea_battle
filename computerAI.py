import random

class computerAI:
    def __init__(self):
        self.available_shots = set()
        self.last_hit = None
        self.direction = None
        self.target_stack = []
        self.hits = []
        self.field_size = (10, 10)

    def set_field_size(self, size):
        self.field_size = size
        self.available_shots = set((i, j) for i in range(1, size[0] + 1) for j in range(1, size[1] + 1))

    def check_shot_for_success(self, cell_for_shot, target_ships):
        for ship in target_ships:
            if cell_for_shot in ship.cells:
                return True
        return False

    def make_shot(self, player_ships):
        if self.last_hit:
            if not self.target_stack:
                self.generate_target_stack()
            target = self.target_stack.pop()
        else:
            target = self.make_target()

        self.available_shots.discard(target)

        success = self.check_shot_for_success(target, player_ships)
        if success:
            self.last_hit = target
            self.hits.append(target)
            if len(self.hits) >= 2:
                self.determine_direction()
            if self.is_ship_destroyed(player_ships):
                self.reset_search()
            else:
                self.generate_target_stack()
        elif not success and not self.target_stack:
            self.reset_search()

        return target, success

    def make_target(self):
        return random.choice(list(self.available_shots))

    def determine_direction(self):
        x1, y1 = self.hits[-2]
        x2, y2 = self.hits[-1]

        if x1 == x2:
            self.direction = "vertical"
        elif y1 == y2:
            self.direction = "horizontal"
        self.filter_target_stack()

    def filter_target_stack(self):
        if self.direction == "horizontal":
            self.target_stack = [cell for cell in self.target_stack if cell[1] == self.last_hit[1]]
        elif self.direction == "vertical":
            self.target_stack = [cell for cell in self.target_stack if cell[0] == self.last_hit[0]]

    def generate_target_stack(self):
        x, y = self.last_hit
        if self.direction is None:
            directions = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        elif self.direction == "horizontal":
            directions = [(x + 1, y), (x - 1, y)]
        elif self.direction == "vertical":
            directions = [(x, y + 1), (x, y - 1)]

        for cell in directions:
            if cell in self.available_shots and cell not in self.target_stack:
                self.target_stack.append(cell)

    def is_ship_destroyed(self, player_ships):
        for ship in player_ships:
            if all(cell in self.hits for cell in ship.cells):
                ship.destroyed = True
                return True
        return False

    def reset_search(self):
        self.last_hit = None
        self.direction = None
        self.hits = []
        self.target_stack = []

    def delete_area_destroyed_ship(self, destroyed_ship):
        for cell in destroyed_ship.cells:
            y, x = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    self.available_shots.discard((y + i, x + j))