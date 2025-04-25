import random

from ships import Ship
from enums import ShipOrientation
from draw_field import FieldSize


class ComputerAI:
    """Класс для реализации ИИ компьютера (базовая версия)."""

    def __init__(self) -> None:
        """Инициализация базового ИИ компьютера."""
        self._available_shots: set[tuple[int, int]] = set()
        self._last_hit: tuple[int, int] | None = None
        self._direction: str | None = None
        self._target_stack: list[tuple[int, int]] = []
        self._hits: list[tuple[int, int]] = []
        self._field_size: FieldSize = FieldSize(10, 10)

    def set_field_size(self, size: FieldSize) -> None:
        """
        Устанавливает размер игрового поля.

        Args:
            size: Размер поля (ширина, высота)
        """
        self._field_size = size
        self._available_shots = set(
            (i, j) for i in range(1, size.height + 1) for j in range(1, size.width + 1)
        )

    def check_shot_for_success(
        self, cell_for_shot: tuple[int, int], target_ships: list[Ship]
    ) -> bool:
        """
        Проверяет, является ли выстрел успешным.

        Args:
            cell_for_shot: Координаты выстрела (строка, столбец)
            target_ships: Список кораблей цели

        Returns:
            True, если выстрел попал в корабль, иначе False
        """
        for ship in target_ships:
            if cell_for_shot in ship.cells:
                return True
        return False

    def make_shot(self, player_ships: list[Ship]) -> tuple[tuple[int, int], bool]:
        """
        Совершает выстрел по полю игрока.

        Args:
            player_ships: Список кораблей игрока

        Returns:
            Кортеж (координаты выстрела, успех попадания)
        """
        if self._last_hit:
            if not self._target_stack:
                self.generate_target_stack()
            target = self._target_stack.pop()
        else:
            target = self.make_target()

        self._available_shots.discard(target)
        success = self.check_shot_for_success(target, player_ships)

        if success:
            self._last_hit = target
            self._hits.append(target)
            if len(self._hits) >= 2:
                self.determine_direction()
            if self.is_ship_destroyed(player_ships):
                self.reset_search()
            else:
                self.generate_target_stack()
        elif not self._target_stack:
            self.reset_search()

        return target, success

    def make_target(self) -> tuple[int, int]:
        """
        Выбирает цель для выстрела.

        Returns:
            Координаты цели (строка, столбец)
        """
        return random.choice(list(self._available_shots))

    def determine_direction(self) -> None:
        """Определяет направление корабля после второго попадания."""
        x1, y1 = self._hits[-2]
        x2, y2 = self._hits[-1]

        if x1 == x2:
            self._direction = ShipOrientation.VERTICAL
        elif y1 == y2:
            self._direction = ShipOrientation.HORIZONTAL
        self.filter_target_stack()

    def filter_target_stack(self) -> None:
        """Фильтрует возможные цели в зависимости от направления корабля."""
        if not self._last_hit:
            return
        if self._direction == ShipOrientation.HORIZONTAL:
            self._target_stack = [
                cell for cell in self._target_stack if cell[1] == self._last_hit[1]
            ]
        elif self._direction == ShipOrientation.VERTICAL:
            self._target_stack = [
                cell for cell in self._target_stack if cell[0] == self._last_hit[0]
            ]

    def generate_target_stack(self) -> None:
        """Генерирует возможные цели вокруг последнего попадания."""
        if not self._last_hit:
            return
        x, y = self._last_hit
        directions = list()
        if self._direction is None:
            directions = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        elif self._direction == ShipOrientation.HORIZONTAL:
            directions = [(x + 1, y), (x - 1, y)]
        elif self._direction == ShipOrientation.VERTICAL:
            directions = [(x, y + 1), (x, y - 1)]

        for cell in directions:
            if cell in self._available_shots and cell not in self._target_stack:
                self._target_stack.append(cell)

    def is_ship_destroyed(self, player_ships: list[Ship]) -> bool:
        """
        Проверяет, уничтожен ли корабль.

        Args:
            player_ships: Список кораблей игрока

        Returns:
            True, если корабль уничтожен, иначе False
        """
        for ship in player_ships:
            if all(cell in self._hits for cell in ship.cells):
                ship.destroyed = True
                return True
        return False

    def reset_search(self) -> None:
        """Сбрасывает параметры поиска корабля."""
        self._last_hit = None
        self._direction = None
        self._hits = []
        self._target_stack = []

    def delete_area_destroyed_ship(self, destroyed_ship: Ship) -> None:
        """
        Удаляет область вокруг уничтоженного корабля из доступных выстрелов.

        Args:
            destroyed_ship: Уничтоженный корабль
        """
        for cell in destroyed_ship.cells:
            y, x = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    self._available_shots.discard((y + i, x + j))
