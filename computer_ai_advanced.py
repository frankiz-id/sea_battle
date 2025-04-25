import random

from computer_ai import ComputerAI
from ships import Ship
from draw_field import FieldSize


class computerAIAdvanced(ComputerAI):
    """Класс для реализации продвинутого ИИ компьютера."""

    def __init__(self) -> None:
        """Инициализация продвинутого ИИ компьютера."""
        super().__init__()
        self.set_available_cells_to_shots_while_four_ships: set[tuple[int, int]] = set()
        self.set_available_cells_to_shots_while_three_and_two_ships: set[
            tuple[int, int]
        ] = set()

    def set_field_size(self, size: FieldSize) -> None:
        """
        Устанавливает размер игрового поля и генерирует стратегические наборы.

        Args:
            size: Размер поля (ширина, высота)
        """
        super().set_field_size(size)
        self.generate_strategic_sets()

    def generate_strategic_sets(self) -> None:
        """Генерирует стратегические наборы клеток для стрельбы."""
        self.set_available_cells_to_shots_while_four_ships = (
            self.generate_set_available_cells_to_shots(4)
        )
        self.set_available_cells_to_shots_while_three_and_two_ships = (
            self.generate_set_available_cells_to_shots(2)
        )

    def generate_set_available_cells_to_shots(
        self, init_j: int
    ) -> set[tuple[int, int]]:
        """
        Генерирует множество клеток для стратегической стрельбы.

        Args:
            init_j: Начальное смещение для генерации шаблона

        Returns:
            Множество координат клеток для стратегической стрельбы
        """
        initial_i = 1
        initial_j = init_j
        set_cells: set[tuple[int, int]] = set()

        for _ in range(self._field_size.height):
            i = initial_i
            j = initial_j
            while j <= self._field_size.width:
                set_cells.add((i, j))
                j += 4
            initial_i += 1
            initial_j = (initial_j - 1) if 2 <= initial_j <= 4 else 4
        return set_cells

    def make_target(self) -> tuple[int, int]:
        """
        Выбирает цель согласно стратегии.

        Returns:
            Координаты цели (строка, столбец)
        """
        if self.set_available_cells_to_shots_while_four_ships:
            target = random.choice(
                list(self.set_available_cells_to_shots_while_four_ships)
            )
            self.set_available_cells_to_shots_while_four_ships.discard(target)
        elif self.set_available_cells_to_shots_while_three_and_two_ships:
            target = random.choice(
                list(self.set_available_cells_to_shots_while_three_and_two_ships)
            )
            self.set_available_cells_to_shots_while_three_and_two_ships.discard(target)
        else:
            target = super().make_target()
        return target

    def delete_area_destroyed_ship(self, destroyed_ship: Ship) -> None:
        """
        Удаляет область вокруг уничтоженного корабля из доступных выстрелов.

        Args:
            destroyed_ship: Уничтоженный корабль
        """
        super().delete_area_destroyed_ship(destroyed_ship)

        for cell in destroyed_ship.cells:
            y, x = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (
                        1 <= y + i <= self._field_size.height
                        and 1 <= x + j <= self._field_size.width
                    ):
                        self.set_available_cells_to_shots_while_four_ships.discard(
                            (y + i, x + j)
                        )
                        self.set_available_cells_to_shots_while_three_and_two_ships.discard(
                            (y + i, x + j)
                        )
