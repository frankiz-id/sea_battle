import copy
from typing import Dict, List, Optional, Set, Tuple

import pygame

from draw_field import BLOCK_SIZE, LEFT_RIGHT_MARGIN, UPPER_MARGIN
from enums import ShipOrientation, Color
from ships_ import Ship


class manual_ship_placer:
    """Класс для ручной расстановки кораблей на поле."""

    def __init__(
        self,
        field_size: Tuple[int, int],
        ship_config: List[int],
        field_offset: Tuple[int, int],
        screen_width: int,
    ) -> None:
        """
        Инициализация объекта ручной расстановки кораблей.

        Args:
            field_size: Размер поля в клетках (ширина, высота)
            ship_config: Конфигурация кораблей
            field_offset: Смещение поля от краев экрана (x, y)
            screen_width: Ширина экрана
        """
        self.field_size = field_size
        self.ship_config = ship_config
        self.field_offset = field_offset
        self.screen_width = screen_width

        self.current_ship_type: Optional[int] = None
        self.current_ship_cells: List[Tuple[int, int]] = []
        self.available_cells: Set[Tuple[int, int]] = set(
            (i, j)
            for i in range(1, field_size[0] + 1)
            for j in range(1, field_size[1] + 1)
        )
        # Инициализируем счетчики кораблей
        self.ship_counts: Dict[int, int] = self.count_ships_by_type()
        self.placed_ships: List[Ship] = []
        self.completed = False

    def count_ships_by_type(self) -> Dict[int, int]:
        """
        Подсчитывает количество кораблей каждого типа.

        Returns:
            Словарь с количеством кораблей по размерам
        """
        counts: dict[int, int] = {}
        for size in self.ship_config:
            counts[size] = counts.get(size, 0) + 1
        return counts

    def handle_event(self, event: pygame.event.Event, screen: pygame.Surface) -> None:
        """
        Обрабатывает события во время расстановки кораблей.

        Args:
            event: Событие pygame для обработки
            screen: Поверхность pygame для отрисовки
        """
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_4:
                size = event.key - pygame.K_0
                if size in self.ship_counts and self.ship_counts[size] > 0:
                    self.current_ship_type = size
                    self.current_ship_cells = []

        elif event.type == pygame.MOUSEBUTTONDOWN and self.current_ship_type:
            x, y = event.pos
            if (
                self.field_offset[0]
                <= x
                <= self.field_offset[0] + self.field_size[1] * BLOCK_SIZE
                and self.field_offset[1]
                <= y
                <= self.field_offset[1] + self.field_size[0] * BLOCK_SIZE
            ):

                col = ((x - self.field_offset[0]) // BLOCK_SIZE) + 1
                row = ((y - self.field_offset[1]) // BLOCK_SIZE) + 1
                cell = (row, col)

                if self.can_place_cell(cell):
                    self.add_ship_cell(cell)
                    if len(self.current_ship_cells) == self.current_ship_type:
                        self.finalize_ship()

        self.draw(screen)

    def can_place_cell(self, cell: Tuple[int, int]) -> bool:
        """
        Проверяет, можно ли разместить клетку корабля.

        Args:
            cell: Координаты клетки (строка, столбец)

        Returns:
            True, если клетку можно разместить, иначе False
        """
        if cell not in self.available_cells or cell in self.current_ship_cells:
            return False

        if not self.current_ship_cells:
            return True

        if len(self.current_ship_cells) == 1:
            prev = self.current_ship_cells[0]
            return (abs(cell[0] - prev[0]) + abs(cell[1] - prev[1])) == 1

        first_dir = self.get_ship_direction()
        new_dir = self.get_cell_direction(cell)
        return new_dir == first_dir and self.is_at_end(cell, first_dir)

    def get_ship_direction(self) -> ShipOrientation:
        """
        Определяет направление корабля.

        Returns:
            ShipOrientation.HORIZONTAL - горизонтальное, ShipOrientation.VERTICAL - вертикальное
        """
        if len(self.current_ship_cells) < 2:
            return ShipOrientation.HORIZONTAL
        first, second = self.current_ship_cells[0], self.current_ship_cells[1]
        return ShipOrientation.HORIZONTAL if first[0] == second[0] else ShipOrientation.VERTICAL

    def get_cell_direction(self, cell: Tuple[int, int]) -> ShipOrientation:
        """
        Определяет направление новой клетки относительно последней в корабле.

        Args:
            cell: Координаты клетки (строка, столбец)

        Returns:
            'horizontal' - горизонтальное, 'vertical' - вертикальное, None - не определено
        """
        last = self.current_ship_cells[-1]
        if cell[0] == last[0]:
            return ShipOrientation.HORIZONTAL
        elif cell[1] == last[1]:
            return ShipOrientation.VERTICAL

    def is_at_end(self, cell: Tuple[int, int], direction: ShipOrientation) -> bool:
        """
        Проверяет, находится ли клетка на конце корабля.

        Args:
            cell: Координаты клетки (строка, столбец)
            direction: Направление корабля ('horizontal' или 'vertical')

        Returns:
            True, если клетка на конце, иначе False
        """
        if direction == ShipOrientation.HORIZONTAL:
            min_col = min(c[1] for c in self.current_ship_cells)
            max_col = max(c[1] for c in self.current_ship_cells)
            return cell[0] == self.current_ship_cells[0][0] and (
                cell[1] == min_col - 1 or cell[1] == max_col + 1
            )
        else:
            min_row = min(c[0] for c in self.current_ship_cells)
            max_row = max(c[0] for c in self.current_ship_cells)
            return cell[1] == self.current_ship_cells[0][1] and (
                cell[0] == min_row - 1 or cell[0] == max_row + 1
            )

    def add_ship_cell(self, cell: Tuple[int, int]) -> None:
        """
        Добавляет клетку к текущему кораблю.

        Args:
            cell: Координаты клетки (строка, столбец)
        """
        self.current_ship_cells.append(cell)

    def finalize_ship(self) -> None:
        """Завершает создание корабля и резервирует область вокруг него."""
        if not self.current_ship_cells or not self.current_ship_type:
            return
        # Определяем ориентацию корабля
        if len(self.current_ship_cells) > 1:
            first, second = self.current_ship_cells[:2]
            orientation = ShipOrientation.HORIZONTAL if first[0] == second[0] else ShipOrientation.VERTICAL
        else:
            orientation = ShipOrientation.HORIZONTAL

        # Создаем новый корабль
        new_ship = Ship(copy.deepcopy(self.current_ship_cells), orientation)
        self.placed_ships.append(new_ship)

        # Резервируем область вокруг корабля
        for cell in self.current_ship_cells:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    self.available_cells.discard((cell[0] + i, cell[1] + j))

        # Уменьшаем счетчик кораблей этого типа
        if self.current_ship_type in self.ship_counts:
            self.ship_counts[self.current_ship_type] -= 1

            # Если кораблей этого типа больше не осталось, сбрасываем выбор типа
            if self.ship_counts[self.current_ship_type] <= 0:
                self.current_ship_type = None

        # Сбрасываем текущие клетки корабля
        self.current_ship_cells = []

        # Проверяем, все ли корабли размещены
        if all(count <= 0 for count in self.ship_counts.values()):
            self.completed = True

    def draw_ship_info(self, screen: pygame.Surface) -> None:
        """Отрисовка информации о кораблях между полями."""
        x_pos = LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 2 * BLOCK_SIZE
        y_pos = UPPER_MARGIN

        font = pygame.font.SysFont("Arial", 20)
        # Отображаем только те типы кораблей, которые еще нужно разместить
        for size in sorted(
            [s for s in self.ship_counts if self.ship_counts[s] > 0], reverse=True
        ):
            text = f"{size}-палубный: {self.ship_counts[size]} осталось"
            text_surface = font.render(text, True, Color.BLACK.value)
            screen.blit(text_surface, (x_pos, y_pos))
            y_pos += 25

    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка процесса расстановки кораблей."""
        # Отрисовка фона
        pygame.draw.rect(
            screen,
            Color.WHITE.value,
            (
                self.field_offset[0],
                self.field_offset[1],
                self.field_size[1] * BLOCK_SIZE,
                self.field_size[0] * BLOCK_SIZE,
            ),
        )

        # Отрисовка сетки
        for i in range(self.field_size[0] + 1):
            pygame.draw.line(
                screen,
                Color.BLACK.value,
                (self.field_offset[0], self.field_offset[1] + i * BLOCK_SIZE),
                (
                    self.field_offset[0] + self.field_size[1] * BLOCK_SIZE,
                    self.field_offset[1] + i * BLOCK_SIZE,
                ),
                1,
            )

        for i in range(self.field_size[1] + 1):
            pygame.draw.line(
                screen,
                Color.BLACK.value,
                (self.field_offset[0] + i * BLOCK_SIZE, self.field_offset[1]),
                (
                    self.field_offset[0] + i * BLOCK_SIZE,
                    self.field_offset[1] + self.field_size[0] * BLOCK_SIZE,
                ),
                1,
            )

        # Отрисовка размещенных кораблей
        for ship in self.placed_ships:
            for cell in ship.cells:
                x = self.field_offset[0] + (cell[1] - 1) * BLOCK_SIZE
                y = self.field_offset[1] + (cell[0] - 1) * BLOCK_SIZE
                pygame.draw.rect(screen, Color.BLACK.value, (x, y, BLOCK_SIZE, BLOCK_SIZE), 3)

        # Отрисовка текущего корабля
        for cell in self.current_ship_cells:
            x = self.field_offset[0] + (cell[1] - 1) * BLOCK_SIZE
            y = self.field_offset[1] + (cell[0] - 1) * BLOCK_SIZE
            pygame.draw.rect(screen, Color.BLACK.value, (x, y, BLOCK_SIZE, BLOCK_SIZE), 3)
