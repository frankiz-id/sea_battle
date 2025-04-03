import random
from computerAI import computerAI


class computerAI_advanced(computerAI):
    def __init__(self):
        super().__init__()
        self.set_available_cells_to_shots_while_four_ships = set()
        self.set_available_cells_to_shots_while_three_and_two_ships = set()

    def set_field_size(self, size):
        """Переопределяем метод для установки размера поля с генерацией стратегических наборов"""
        super().set_field_size(size)
        self.generate_strategic_sets()

    def generate_strategic_sets(self):
        """Генерирует стратегические наборы клеток для стрельбы"""
        self.set_available_cells_to_shots_while_four_ships = self.generate_set_available_cells_to_shots(4)
        self.set_available_cells_to_shots_while_three_and_two_ships = self.generate_set_available_cells_to_shots(2)

    def generate_set_available_cells_to_shots(self, init_j):
        """Генерирует множество клеток для стратегической стрельбы"""
        initial_i = 1
        initial_j = init_j
        set_cells = set()

        for _ in range(self.field_size[0]):
            i = initial_i
            j = initial_j
            while j <= self.field_size[1]:
                set_cells.add((i, j))
                j += 4
            initial_i += 1
            initial_j = (initial_j - 1) if 2 <= initial_j <= 4 else 4
        return set_cells

    def make_target(self):
        """Выбирает цель согласно стратегии"""
        if self.set_available_cells_to_shots_while_four_ships:
            target = random.choice(list(self.set_available_cells_to_shots_while_four_ships))
            self.set_available_cells_to_shots_while_four_ships.discard(target)
        elif self.set_available_cells_to_shots_while_three_and_two_ships:
            target = random.choice(list(self.set_available_cells_to_shots_while_three_and_two_ships))
            self.set_available_cells_to_shots_while_three_and_two_ships.discard(target)
        else:
            target = super().make_target()
        return target

    def delete_area_destroyed_ship(self, destroyed_ship):
        """Удаляет область вокруг уничтоженного корабля из доступных выстрелов"""
        super().delete_area_destroyed_ship(destroyed_ship)

        for cell in destroyed_ship.cells:
            y, x = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 1 <= y + i <= self.field_size[0] and 1 <= x + j <= self.field_size[1]:
                        self.set_available_cells_to_shots_while_four_ships.discard((y + i, x + j))
                        self.set_available_cells_to_shots_while_three_and_two_ships.discard((y + i, x + j))