import copy

from computerAI_advanced import computerAI_advanced
from computerAI import computerAI
from ships_on_grid import ships_on_grid
from draw_Field import *
from Ship import *


class game_with_computer:
    def __init__(self, ai_type, field_size, ship_config, ship_placement):
        self.field_size = field_size
        self.ship_config = ship_config
        self.field = draw_Field(field_size)
        self.ship_placement = ship_placement

        # Инициализация игроков
        self.player = ships_on_grid(field_size, ship_config)
        self.computer = ships_on_grid(field_size, ship_config)

        # Инициализация ИИ
        self.ai = computerAI() if ai_type == "weak_ai" else computerAI_advanced()
        self.ai.set_field_size(field_size)

        # Наборы доступных выстрелов
        self.available_to_fire_set_computer = set(
            (i, j) for i in range(1, field_size[0] + 1)
            for j in range(1, field_size[1] + 1)
        )

        self.game_over = False
        self.computer_turn = False
        self.winner = None

        #для ручной расстановки
        self.manual_placement_mode = False  # Флаг режима ручной расстановки
        self.current_ship_type = None  # Текущий тип корабля (1-4)
        self.current_ship_cells = []  # Клетки текущего корабля
        self.available_cells_to_manual_placement = set((i, j) for i in range(1, field_size[0] + 1) for j in range(1, field_size[1] + 1))
        self.ship_counts = self.count_ships_by_type()  # Счетчик оставшихся кораблей
        self.manual_ships = []  # Список размещенных кораблей (экземпляры Ship)

    def count_ships_by_type(self):
        counts = {}
        for size in self.ship_config:
            counts[size] = counts.get(size, 0) + 1
        return counts

    def draw_manual_placement_ui(self):
        self.field.screen.fill(WHITE)
        self.field.draw_field_grid()
        self.field.sign_grids()

        # Отрисовка кораблей компьютера (для отладки)
        if hasattr(self.computer, 'list_of_game_ships'):
            self.field.draw_ships(self.computer.list_of_game_ships, LEFT_RIGHT_MARGIN)

        # Переносим отрисовку списка кораблей между полями
        x_pos = LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 2 * BLOCK_SIZE
        y_pos = UPPER_MARGIN

        for size, count in sorted(self.ship_counts.items(), reverse=True):
            if count > 0:
                text = f"{size}-палубный: {count} осталось"
                text_surface = FONT.render(text, True, BLACK)
                self.field.screen.blit(text_surface, (x_pos, y_pos))
                y_pos += 30
        # Отрисовка уже размещенных кораблей
        offset = LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE
        for ship in self.manual_ships:
            for cell in ship.cells:
                x = offset + (cell[1] - 1) * BLOCK_SIZE
                y = UPPER_MARGIN + (cell[0] - 1) * BLOCK_SIZE
                pygame.draw.rect(self.field.screen, BLACK, (x, y, BLOCK_SIZE, BLOCK_SIZE), 3)
        # Отрисовка текущего корабля
        for cell in self.current_ship_cells:
            x = offset + (cell[1] - 1) * BLOCK_SIZE
            y = UPPER_MARGIN + (cell[0] - 1) * BLOCK_SIZE
            pygame.draw.rect(self.field.screen, BLACK, (x, y, BLOCK_SIZE, BLOCK_SIZE), 3)
        pygame.display.update()

    def _can_place_cell(self, cell):
        # Проверка, что клетка доступна
        if cell not in self.available_cells_to_manual_placement:
            return False
        # Для первой клетки проверка не нужна
        if not self.current_ship_cells:
            return True
        # Проверка, что клетка не совпадает с уже выбранными
        if cell in self.current_ship_cells:
            return False
        # Для второй клетки проверяем соседство
        if len(self.current_ship_cells) == 1:
            prev = self.current_ship_cells[0]
            return (abs(cell[0] - prev[0]) + abs(cell[1] - prev[1])) == 1
        # Для последующих клеток проверяем направление и линейность
        first, second = self.current_ship_cells[:2]
        if first[0] == second[0]:  # Горизонтальный
            return (cell[0] == first[0] and
                    abs(cell[1] - self.current_ship_cells[-1][1]) == 1 and
                    all(c[0] == first[0] for c in self.current_ship_cells))
        else:  # Вертикальный
            return (cell[1] == first[1] and
                    abs(cell[0] - self.current_ship_cells[-1][0]) == 1 and
                    all(c[1] == first[1] for c in self.current_ship_cells))

    def _add_ship_cell(self, cell):
        self.current_ship_cells.append(cell)


    def _finalize_ship(self):
        # Определение ориентации
        if len(self.current_ship_cells) > 1:
            first, second = self.current_ship_cells[:2]
            orientation = "horizontal" if first[0] == second[0] else "vertical"
        else:
            orientation = "horizontal"

        # Создание корабля
        new_ship = Ship(copy.deepcopy(self.current_ship_cells), orientation)
        self.manual_ships.append(new_ship)

        # Резервирование области
        for cell in self.current_ship_cells:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    self.available_cells_to_manual_placement.discard((cell[0] + i, cell[1] + j))

        # Обновление счетчиков
        self.ship_counts[self.current_ship_type] -= 1
        self.current_ship_type = None
        self.current_ship_cells = []

        # Проверка завершения расстановки
        if all(count == 0 for count in self.ship_counts.values()):
            self.player.create_lots_of_game_ships_manual(self.manual_ships)
            self.player.create_list_alive_ships()
            self.manual_placement_mode = False
            self._start_normal_game()

        self.draw_manual_placement_ui()

    def handle_manual_placement(self, event):
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_4:
                size = event.key - pygame.K_0
                if size in self.ship_counts and self.ship_counts[size] > 0:
                    self.current_ship_type = size
                    self.current_ship_cells = []
                    self.draw_manual_placement_ui()
        elif event.type == pygame.MOUSEBUTTONDOWN and self.current_ship_type:
            x, y = event.pos
            offset = LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE
            if (offset <= x <= offset + self.field_size[1] * BLOCK_SIZE and
                    UPPER_MARGIN <= y <= UPPER_MARGIN + self.field_size[0] * BLOCK_SIZE):

                col = ((x - offset) // BLOCK_SIZE) + 1
                row = ((y - UPPER_MARGIN) // BLOCK_SIZE) + 1
                cell = (row, col)

                if self._can_place_cell(cell):
                    self._add_ship_cell(cell)
                    if len(self.current_ship_cells) == self.current_ship_type:
                        self._finalize_ship()
                    self.draw_manual_placement_ui()

    def start_game(self):
        self.field.draw_field_grid()
        self.field.sign_grids()

        self.computer.create_lots_of_game_ships()
        self.computer.create_list_alive_ships()
        if self.ship_placement == 1:  # Автоматическая расстановка
            self.player.create_lots_of_game_ships()
            self.player.create_list_alive_ships()
            self._start_normal_game()
        else:  # Ручная расстановка
            self.manual_placement_mode = True
            self.draw_manual_placement_ui()


    def _start_normal_game(self):
        player_offset = LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE
        self.field.draw_ships(self.player.list_of_game_ships, player_offset)
        self.field.draw_ships(self.computer.list_of_game_ships, LEFT_RIGHT_MARGIN)
        pygame.display.update()

    def handle_player_turn(self, event):
        x, y = event.pos
        field_right = LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE
        field_bottom = UPPER_MARGIN + self.field_size[0] * BLOCK_SIZE

        if LEFT_RIGHT_MARGIN <= x <= field_right and UPPER_MARGIN <= y <= field_bottom:
            col = ((x - LEFT_RIGHT_MARGIN) // BLOCK_SIZE) + 1
            row = ((y - UPPER_MARGIN) // BLOCK_SIZE) + 1
            fired_block = (row, col)

            if fired_block in self.available_to_fire_set_computer:
                self.available_to_fire_set_computer.discard(fired_block)
                self.process_shot(fired_block, self.computer, LEFT_RIGHT_MARGIN)

    def handle_computer_turn(self):
        fired_block, success = self.ai.make_shot(self.player.list_alive_ships)
        self.process_shot(fired_block, self.player,
                          LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE)
        if not success:
            self.computer_turn = False

    def process_shot(self, fired_block, target, offset):
        success = any(fired_block in ship.cells for ship in target.list_alive_ships)
        self.field.draw_after_shot(fired_block, offset)

        if success:
            self.handle_successful_shot(fired_block, target, offset)
            if not target.list_alive_ships:
                self.game_over = True
                self.winner = "Player" if target == self.computer else "Computer"
        else:
            self.computer_turn = target == self.computer

    def handle_successful_shot(self, fired_block, target, offset):
        for ship in target.list_alive_ships:
            if fired_block in ship.cells:
                ship.cells.remove(fired_block)
                if not ship.cells:  # Корабль уничтожен
                    destroyed_ship = target.find_ship_by_cell(fired_block)
                    self.field.draw_destroyed_area(destroyed_ship, offset)
                    if target == self.computer:
                        self.mark_destroyed_ship_area(destroyed_ship)
                    else:
                        self.ai.delete_area_destroyed_ship(destroyed_ship)
                    target.list_alive_ships.remove(ship)

    def mark_destroyed_ship_area(self, ship):
        for cell in ship.cells:
            row, col = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 1 <= row + i <= self.field_size[0] and 1 <= col + j <= self.field_size[1]:
                        self.available_to_fire_set_computer.discard((row + i, col + j))

    def run(self):
        self.start_game()
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                elif self.manual_placement_mode:
                    self.handle_manual_placement(event)
                elif not self.computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_player_turn(event)

            if not self.manual_placement_mode and self.computer_turn:
                self.handle_computer_turn()

            pygame.display.update()

        self.end_game()
        pygame.quit()

    def end_game(self):
        print(f"Game over! Winner: {self.winner}")
        # Можно добавить отображение результата на экране