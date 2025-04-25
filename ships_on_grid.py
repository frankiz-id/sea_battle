import copy
import random

from ships import Ship
from enums import ShipOrientation
from draw_field import FieldSize


class ShipsOnGrid:
    """Класс для управления кораблями на игровом поле."""

    def __init__(self, field_size: FieldSize, ship_config: list[int]) -> None:
        """
        Инициализация объекта управления кораблями.

        Args:
            field_size: Размер поля в клетках (ширина, высота)
            ship_config: Конфигурация кораблей
        """
        self.set_available_cells: set[tuple[int, int]] = set(
            (i, j)
            for i in range(1, field_size.height + 1)
            for j in range(1, field_size.width + 1)
        )
        self.list_of_game_ships: list[Ship] = list()
        self.list_alive_ships: list[Ship] = list()
        self.field_size: FieldSize = field_size
        self.ship_config: list[int] = ship_config
        self.ship_groups: dict[int, int] = self.group_ships_by_size()

    def group_ships_by_size(self) -> dict[int, int]:
        """
        Группирует корабли по размерам.

        Returns:
            Словарь с количеством кораблей по размерам
        """
        groups: dict[int, int] = {}
        for size in self.ship_config:
            groups[size] = groups.get(size, 0) + 1
        return groups

    def find_ship_by_cell(self, cell: tuple[int, int]) -> Ship | None:
        """
        Находит корабль по координатам клетки.

        Args:
            cell: Координаты клетки (строка, столбец)

        Returns:
            Объект корабля или None, если не найден
        """
        for ship in self.list_of_game_ships:
            if cell in ship.cells:
                return ship
        return None

    def generate_first_cells_for_new_ships(self) -> tuple[int, int, int, int]:
        """
        Генерирует начальные координаты и направление для нового корабля.

        Returns:
            Кортеж (строка, столбец, ориентация, направление)
        """
        string_coord, column_coord = random.choice(list(self.set_available_cells))
        horizontal_or_vertical = random.choice((0, 1))
        direction = 1
        return string_coord, column_coord, horizontal_or_vertical, direction

    def create_new_ship(self, dimension_ship: int) -> Ship:
        """
        Создает новый корабль заданного размера.

        Args:
            dimension_ship: Размер корабля (количество клеток)

        Returns:
            Новый объект корабля
        """
        while True:
            string_coord, column_coord, horizontal_or_vertical, direction = (
                self.generate_first_cells_for_new_ships()
            )
            new_ship: list[tuple[int, int]] = []

            if horizontal_or_vertical:  # горизонтальное размещение
                for _ in range(dimension_ship):
                    new_ship.append((string_coord, column_coord))
                    if column_coord < self.field_size.width:
                        column_coord += direction
                    else:
                        column_coord = new_ship[0][1] - 1
                        direction *= -1
            else:  # вертикальное размещение
                for _ in range(dimension_ship):
                    new_ship.append((string_coord, column_coord))
                    if string_coord < self.field_size.height:
                        string_coord += direction
                    else:
                        string_coord = new_ship[0][0] - 1
                        direction *= -1

            if self.is_correct_place(new_ship):
                self.reserve_ship_area(new_ship)
                return Ship(
                    new_ship,
                    (
                        ShipOrientation.HORIZONTAL
                        if horizontal_or_vertical
                        else ShipOrientation.VERTICAL
                    ),
                )

    def reserve_ship_area(self, ship_cells: list[tuple[int, int]]) -> None:
        """
        Резервирует область вокруг корабля.

        Args:
            ship_cells: Список координат клеток корабля
        """
        for cell in ship_cells:
            for x_offset in range(-1, 2):
                for y_offset in range(-1, 2):
                    x = cell[0] + x_offset
                    y = cell[1] + y_offset
                    self.set_available_cells.discard((x, y))

    def is_correct_place(self, ship: list[tuple[int, int]]) -> bool:
        """
        Проверяет, можно ли разместить корабль в данной позиции.

        Args:
            ship: Список координат клеток корабля

        Returns:
            True, если размещение возможно, иначе False
        """
        for cell in ship:
            if cell not in self.set_available_cells:
                return False
        return True

    def create_lots_of_game_ships_manual(
        self, manually_placed_ships: list[Ship]
    ) -> None:
        """
        Создает корабли из ручной расстановки.

        Args:
            manually_placed_ships: Список кораблей, размещенных вручную
        """
        self.list_of_game_ships.clear()
        self.set_available_cells = set(
            (i, j)
            for i in range(1, self.field_size.height + 1)
            for j in range(1, self.field_size.width + 1)
        )

        for ship in manually_placed_ships:
            self.list_of_game_ships.append(copy.deepcopy(ship))
            self.reserve_ship_area(ship.cells)

    def create_lots_of_game_ships(self) -> None:
        """Создает все корабли для игры (автоматическая расстановка)."""
        for size in sorted(self.ship_groups.keys(), reverse=True):
            count = self.ship_groups[size]
            for _ in range(count):
                ship = self.create_new_ship(size)
                self.list_of_game_ships.append(ship)

    def create_list_alive_ships(self) -> None:
        """Создает список живых кораблей для игры."""
        self.list_alive_ships = [
            Ship(copy.deepcopy(ship.cells), ship.orientation)
            for ship in self.list_of_game_ships
        ]
