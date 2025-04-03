import copy
import random
from Ship import *


class ships_on_grid:
    def __init__(self, field_size, ship_config):
        self.set_available_cells = set((i, j) for i in range(1, field_size[0] + 1)
                                       for j in range(1, field_size[1] + 1))
        self.list_of_game_ships = list()
        self.list_alive_ships = list()
        self.field_size = field_size
        self.ship_config = ship_config
        self.ship_groups = self.group_ships_by_size()

    # формирует словарь : {размер : количество}
    def group_ships_by_size(self):
        groups = {}
        for size in self.ship_config:
            groups[size] = groups.get(size, 0) + 1
        return groups

    def find_ship_by_cell(self, cell):
        for ship in self.list_of_game_ships:
            if cell in ship.cells:
                return ship
        return None

    def generate_first_cells_for_new_ships(self):
        string_coord, column_coord = random.choice(list(self.set_available_cells))
        # 1 - горизонтальное размещение
        horizontal_or_vertical = random.choice((0, 1))
        direction = 1
        return string_coord, column_coord, horizontal_or_vertical, direction

    def create_new_ship(self, dimension_ship):
        while True:
            string_coord, column_coord, horizontal_or_vertical, direction = self.generate_first_cells_for_new_ships()
            new_ship = list()

            if horizontal_or_vertical:  # горизонтальное размещение
                for _ in range(dimension_ship):
                    new_ship.append((string_coord, column_coord))
                    if column_coord < self.field_size[1]:
                        column_coord += direction
                    else:
                        column_coord = new_ship[0][1] - 1
                        direction *= -1
            else:  # вертикальное размещение
                for _ in range(dimension_ship):
                    new_ship.append((string_coord, column_coord))
                    if string_coord < self.field_size[0]:
                        string_coord += direction
                    else:
                        string_coord = new_ship[0][0] - 1
                        direction *= -1

            if self.is_correct_place(new_ship):
                self.reserve_ship_area(new_ship)
                return Ship(new_ship, "horizontal" if horizontal_or_vertical else "vertical")

    def reserve_ship_area(self, ship_cells):
        for cell in ship_cells:
            for x_offset in range(-1, 2):
                for y_offset in range(-1, 2):
                    x = cell[0] + x_offset
                    y = cell[1] + y_offset
                    self.set_available_cells.discard((x, y))

    def is_correct_place(self, ship):
        for cell in ship:
            if cell not in self.set_available_cells:
                return False
        return True

    def create_lots_of_game_ships(self):
        # Сортируем размеры по убыванию для большей надежности, хотя корректность конфигурации кораблей и так гарантируется
        for size in sorted(self.ship_groups.keys(), reverse=True):
            count = self.ship_groups[size]
            for _ in range(count):
                ship = self.create_new_ship(size)
                self.list_of_game_ships.append(ship)

    def create_list_alive_ships(self):
        self.list_alive_ships = [
            Ship(copy.deepcopy(ship.cells), ship.orientation) for ship in self.list_of_game_ships
        ]