from computerAI_advanced import computerAI_advanced
from computerAI import computerAI
from ships_on_grid import ships_on_grid
from draw_Field import *


class game_with_computer:
    def __init__(self, ai_type, field_size, ship_config):
        self.field_size = field_size
        self.ship_config = ship_config
        self.field = draw_Field(field_size)

        # Инициализация игроков
        self.player = ships_on_grid(field_size, ship_config)
        self.computer = ships_on_grid(field_size, ship_config)

        # Инициализация ИИ
        self.ai = computerAI() if ai_type == "weak" else computerAI_advanced()
        self.ai.set_field_size(field_size)

        # Наборы доступных выстрелов
        self.available_to_fire_set_computer = set(
            (i, j) for i in range(1, field_size[0] + 1)
            for j in range(1, field_size[1] + 1)
        )

        self.game_over = False
        self.computer_turn = False
        self.winner = None

    def start_game(self):
        self.field.draw_field_grid()
        self.field.sign_grids()

        # Создание кораблей
        self.player.create_lots_of_game_ships()
        self.player.create_list_alive_ships()
        self.computer.create_lots_of_game_ships()
        self.computer.create_list_alive_ships()

        # Отрисовка кораблей
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
        #self.ai.available_shots.discard(fired_block)
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
                elif not self.computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_player_turn(event)

            if self.computer_turn:
                self.handle_computer_turn()

            pygame.display.update()

        self.end_game()
        pygame.quit()

    def end_game(self):
        print(f"Game over! Winner: {self.winner}")
        # Можно добавить отображение результата на экране