import random
from typing import List, Set, Tuple, Optional

from ships_ import Ship
from enums import ShipOrientation


class computerAI:
    """Класс для реализации ИИ компьютера (базовая версия)."""

    def __init__(self) -> None:
        """Инициализация базового ИИ компьютера."""
        self.available_shots: Set[Tuple[int, int]] = set()
        self.last_hit: Optional[Tuple[int, int]] = None
        self.direction: Optional[str] = None
        self.target_stack: List[Tuple[int, int]] = []
        self.hits: List[Tuple[int, int]] = []
        self.field_size: Tuple[int, int] = (10, 10)

    def set_field_size(self, size: Tuple[int, int]) -> None:
        """
        Устанавливает размер игрового поля.

        Args:
            size: Размер поля (ширина, высота)
        """
        self.field_size = size
        self.available_shots = set(
            (i, j) for i in range(1, size[0] + 1) for j in range(1, size[1] + 1)
        )

    def check_shot_for_success(
        self, cell_for_shot: Tuple[int, int], target_ships: List["Ship"]
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

    def make_shot(self, player_ships: List["Ship"]) -> Tuple[Tuple[int, int], bool]:
        """
        Совершает выстрел по полю игрока.

        Args:
            player_ships: Список кораблей игрока

        Returns:
            Кортеж (координаты выстрела, успех попадания)
        """
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

    def make_target(self) -> Tuple[int, int]:
        """
        Выбирает цель для выстрела.

        Returns:
            Координаты цели (строка, столбец)
        """
        return random.choice(list(self.available_shots))

    def determine_direction(self) -> None:
        """Определяет направление корабля после второго попадания."""
        x1, y1 = self.hits[-2]
        x2, y2 = self.hits[-1]

        if x1 == x2:
            self.direction = ShipOrientation.VERTICAL
        elif y1 == y2:
            self.direction = ShipOrientation.HORIZONTAL
        self.filter_target_stack()

    def filter_target_stack(self) -> None:
        """Фильтрует возможные цели в зависимости от направления корабля."""
        if self.last_hit:
            if self.direction == ShipOrientation.HORIZONTAL:
                self.target_stack = [
                    cell for cell in self.target_stack if cell[1] == self.last_hit[1]
                ]
            elif self.direction == ShipOrientation.VERTICAL:
                self.target_stack = [
                    cell for cell in self.target_stack if cell[0] == self.last_hit[0]
                ]

    def generate_target_stack(self) -> None:
        """Генерирует возможные цели вокруг последнего попадания."""
        if self.last_hit:
            x, y = self.last_hit
            directions = list()
            if self.direction is None:
                directions = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            elif self.direction == ShipOrientation.HORIZONTAL:
                directions = [(x + 1, y), (x - 1, y)]
            elif self.direction == ShipOrientation.VERTICAL:
                directions = [(x, y + 1), (x, y - 1)]

            for cell in directions:
                if cell in self.available_shots and cell not in self.target_stack:
                    self.target_stack.append(cell)

    def is_ship_destroyed(self, player_ships: List["Ship"]) -> bool:
        """
        Проверяет, уничтожен ли корабль.

        Args:
            player_ships: Список кораблей игрока

        Returns:
            True, если корабль уничтожен, иначе False
        """
        for ship in player_ships:
            if all(cell in self.hits for cell in ship.cells):
                ship.destroyed = True
                return True
        return False

    def reset_search(self) -> None:
        """Сбрасывает параметры поиска корабля."""
        self.last_hit = None
        self.direction = None
        self.hits = []
        self.target_stack = []

    def delete_area_destroyed_ship(self, destroyed_ship: "Ship") -> None:
        """
        Удаляет область вокруг уничтоженного корабля из доступных выстрелов.

        Args:
            destroyed_ship: Уничтоженный корабль
        """
        for cell in destroyed_ship.cells:
            y, x = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    self.available_shots.discard((y + i, x + j))
