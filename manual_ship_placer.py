import copy
from Ship import *
from draw_Field import *


class manual_ship_placer:
    def __init__(self, field_size, ship_config, field_offset, screen_width):
        self.field_size = field_size
        self.ship_config = ship_config
        self.field_offset = field_offset
        self.screen_width = screen_width

        self.current_ship_type = None
        self.current_ship_cells = []
        self.available_cells = set((i, j) for i in range(1, field_size[0] + 1) for j in range(1, field_size[1] + 1))
        # Инициализируем счетчики кораблей
        self.ship_counts = self.count_ships_by_type()
        self.placed_ships = []
        self.completed = False

    def count_ships_by_type(self):
        counts = {}
        for size in self.ship_config:
            counts[size] = counts.get(size, 0) + 1
        return counts

    def handle_event(self, event, screen):
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_4:
                size = event.key - pygame.K_0
                if size in self.ship_counts and self.ship_counts[size] > 0:
                    self.current_ship_type = size
                    self.current_ship_cells = []

        elif event.type == pygame.MOUSEBUTTONDOWN and self.current_ship_type:
            x, y = event.pos
            if (self.field_offset[0] <= x <= self.field_offset[0] + self.field_size[1] * BLOCK_SIZE and
                    self.field_offset[1] <= y <= self.field_offset[1] + self.field_size[0] * BLOCK_SIZE):

                col = ((x - self.field_offset[0]) // BLOCK_SIZE) + 1
                row = ((y - self.field_offset[1]) // BLOCK_SIZE) + 1
                cell = (row, col)

                if self.can_place_cell(cell):
                    self.add_ship_cell(cell)
                    if len(self.current_ship_cells) == self.current_ship_type:
                        self.finalize_ship()

        self.draw(screen)

    def can_place_cell(self, cell):
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

    def get_ship_direction(self):
        if len(self.current_ship_cells) < 2:
            return None
        first, second = self.current_ship_cells[0], self.current_ship_cells[1]
        return 'horizontal' if first[0] == second[0] else 'vertical'

    def get_cell_direction(self, cell):
        last = self.current_ship_cells[-1]
        if cell[0] == last[0]:
            return 'horizontal'
        elif cell[1] == last[1]:
            return 'vertical'
        return None

    def is_at_end(self, cell, direction):
        if direction == 'horizontal':
            min_col = min(c[1] for c in self.current_ship_cells)
            max_col = max(c[1] for c in self.current_ship_cells)
            return (cell[0] == self.current_ship_cells[0][0] and
                    (cell[1] == min_col - 1 or cell[1] == max_col + 1))
        else:
            min_row = min(c[0] for c in self.current_ship_cells)
            max_row = max(c[0] for c in self.current_ship_cells)
            return (cell[1] == self.current_ship_cells[0][1] and
                    (cell[0] == min_row - 1 or cell[0] == max_row + 1))

    def add_ship_cell(self, cell):
        self.current_ship_cells.append(cell)

    def finalize_ship(self):
        if not self.current_ship_cells or not self.current_ship_type:
            return
        # Определяем ориентацию корабля
        if len(self.current_ship_cells) > 1:
            first, second = self.current_ship_cells[:2]
            orientation = "horizontal" if first[0] == second[0] else "vertical"
        else:
            orientation = "horizontal"

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

    def draw_ship_info(self, screen):
        """Отрисовка информации о кораблях между полями"""
        x_pos = LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 2 * BLOCK_SIZE
        y_pos = UPPER_MARGIN

        font = pygame.font.SysFont('Arial', 20)
        # Отображаем только те типы кораблей, которые еще нужно разместить
        for size in sorted([s for s in self.ship_counts if self.ship_counts[s] > 0], reverse=True):
            text = f"{size}-палубный: {self.ship_counts[size]} осталось"
            text_surface = font.render(text, True, BLACK)
            screen.blit(text_surface, (x_pos, y_pos))
            y_pos += 25

    def draw(self, screen):
        # Отрисовка фона
        pygame.draw.rect(screen, WHITE,
                         (self.field_offset[0], self.field_offset[1],
                          self.field_size[1] * BLOCK_SIZE, self.field_size[0] * BLOCK_SIZE))

        # Отрисовка сетки
        for i in range(self.field_size[0] + 1):
            pygame.draw.line(screen, BLACK,
                             (self.field_offset[0], self.field_offset[1] + i * BLOCK_SIZE),
                             (self.field_offset[0] + self.field_size[1] * BLOCK_SIZE,
                              self.field_offset[1] + i * BLOCK_SIZE), 1)

        for i in range(self.field_size[1] + 1):
            pygame.draw.line(screen, BLACK,
                             (self.field_offset[0] + i * BLOCK_SIZE, self.field_offset[1]),
                             (self.field_offset[0] + i * BLOCK_SIZE,
                              self.field_offset[1] + self.field_size[0] * BLOCK_SIZE), 1)

        # Отрисовка размещенных кораблей
        for ship in self.placed_ships:
            for cell in ship.cells:
                x = self.field_offset[0] + (cell[1] - 1) * BLOCK_SIZE
                y = self.field_offset[1] + (cell[0] - 1) * BLOCK_SIZE
                pygame.draw.rect(screen, BLACK, (x, y, BLOCK_SIZE, BLOCK_SIZE), 3)

        # Отрисовка текущего корабля
        for cell in self.current_ship_cells:
            x = self.field_offset[0] + (cell[1] - 1) * BLOCK_SIZE
            y = self.field_offset[1] + (cell[0] - 1) * BLOCK_SIZE
            pygame.draw.rect(screen, BLACK, (x, y, BLOCK_SIZE, BLOCK_SIZE), 3)