from draw_Field import *
from ships_on_grid import ships_on_grid
import pygame


class game_with_friend:
    def __init__(self, field_size, ship_config):
        self.field_size = field_size
        self.ship_config = ship_config
        self.field = draw_Field(field_size)

        # Инициализация игроков
        self.player1 = ships_on_grid(field_size, ship_config)
        self.player2 = ships_on_grid(field_size, ship_config)

        # Текущий игрок (1 или 2)
        self.current_player = 1
        self.game_over = False
        self.winner = None

        # Множества выстрелов и попаданий
        self.player1_shots = set()  # выстрелы 1-го игрока (по полю 2-го)
        self.player2_shots = set()  # выстрелы 2-го игрока (по полю 1-го)
        self.player1_hits = set()  # попадания 1-го игрока
        self.player2_hits = set()  # попадания 2-го игрока

    def start_game(self):
        """Инициализация игры и расстановка кораблей"""
        self.player1.create_lots_of_game_ships()
        self.player1.create_list_alive_ships()
        self.player2.create_lots_of_game_ships()
        self.player2.create_list_alive_ships()
        self.draw_game_state()
        pygame.display.update()

    def draw_game_state(self):
        """Отрисовка текущего состояния игры"""
        self.field.screen.fill(WHITE)
        self.field.draw_field_grid()
        self.field.sign_grids()

        # Подписи полей
        font = pygame.font.SysFont('Arial', 20)
        enemy_text = font.render("Поле противника", True, BLACK)
        your_text = font.render("Ваше поле", True, BLACK)

        if self.current_player == 1:
            # Для игрока 1 левое поле - поле игрока 2 (корабли не видны)
            self.draw_enemy_field(LEFT_RIGHT_MARGIN, self.player1_shots, self.player1_hits)
            self.field.screen.blit(enemy_text, (LEFT_RIGHT_MARGIN + 50, UPPER_MARGIN - 30))

            # Правое поле - свое поле (корабли видны)
            self.draw_own_field(LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE,
                                self.player1, self.player2_shots, self.player2_hits)
            self.field.screen.blit(your_text,
                                   (LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE + 50,
                                    UPPER_MARGIN - 30))
        else:
            # Для игрока 2 левое поле - поле игрока 1 (корабли не видны)
            self.draw_enemy_field(LEFT_RIGHT_MARGIN, self.player2_shots, self.player2_hits)
            self.field.screen.blit(enemy_text, (LEFT_RIGHT_MARGIN + 50, UPPER_MARGIN - 30))

            # Правое поле - свое поле (корабли видны)
            self.draw_own_field(LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE,
                                self.player2, self.player1_shots, self.player1_hits)
            self.field.screen.blit(your_text,
                                   (LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE + 50,
                                    UPPER_MARGIN - 30))

        # Отображение текущего игрока
        turn_font = pygame.font.SysFont('Arial', 30)
        turn_text = turn_font.render(f"Ход игрока {self.current_player}", True, BLACK)
        self.field.screen.blit(turn_text, (self.field.screen.get_width() // 2 - turn_text.get_width() // 2, 10))

    def draw_own_field(self, offset_x, player, enemy_shots, enemy_hits):
        """Отрисовка своего поля с кораблями"""
        # Отрисовка кораблей
        self.field.draw_ships(player.list_of_game_ships, offset_x)

        # Отрисовка выстрелов противника
        for shot in enemy_shots:
            self.draw_shot_marker(shot, offset_x, shot in enemy_hits)

    def draw_enemy_field(self, offset_x, my_shots, my_hits):
        """Отрисовка поля противника (без кораблей)"""
        # Отрисовка только своих выстрелов
        for shot in my_shots:
            self.draw_shot_marker(shot, offset_x, shot in my_hits)

    def draw_shot_marker(self, cell, offset_x, is_hit):
        """Отрисовка маркера выстрела"""
        row, col = cell
        x = offset_x + (col - 1) * BLOCK_SIZE
        y = UPPER_MARGIN + (row - 1) * BLOCK_SIZE

        if is_hit:
            # Красный кружок для попадания
            pygame.draw.circle(self.field.screen, (255, 0, 0),
                               (x + BLOCK_SIZE // 2, y + BLOCK_SIZE // 2),
                               BLOCK_SIZE // 3)
        else:
            # Крестик для промаха
            pygame.draw.line(self.field.screen, BLACK, (x, y), (x + BLOCK_SIZE, y + BLOCK_SIZE), 2)
            pygame.draw.line(self.field.screen, BLACK, (x + BLOCK_SIZE, y), (x, y + BLOCK_SIZE), 2)

    def handle_turn(self, event):
        """Обработка хода игрока с задержкой перед переключением"""
        if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
            x, y = event.pos
            field_left = LEFT_RIGHT_MARGIN
            field_right = field_left + self.field_size[1] * BLOCK_SIZE

            if field_left <= x <= field_right and UPPER_MARGIN <= y <= UPPER_MARGIN + self.field_size[0] * BLOCK_SIZE:
                col = (x - field_left) // BLOCK_SIZE + 1
                row = (y - UPPER_MARGIN) // BLOCK_SIZE + 1
                fired_block = (row, col)

                if self.current_player == 1 and fired_block not in self.player1_shots:
                    self.process_shot(fired_block, self.player2,
                                      self.player1_shots, self.player1_hits)
                    self.draw_game_state()
                    pygame.display.update()

                    # Добавляем задержку только если был промах (чтобы ход переключился)
                    if fired_block not in self.player1_hits:
                        pygame.time.wait(450)  # Задержка 450 мс
                        self.current_player = 2

                elif self.current_player == 2 and fired_block not in self.player2_shots:
                    self.process_shot(fired_block, self.player1,
                                      self.player2_shots, self.player2_hits)
                    self.draw_game_state()
                    pygame.display.update()

                    if fired_block not in self.player2_hits:
                        pygame.time.wait(450)  # Задержка 450 мс
                        self.current_player = 1

                # Перерисовываем состояние после возможного переключения игрока
                self.draw_game_state()
                pygame.display.update()

    def process_shot(self, fired_block, target, shots_set, hits_set):
        """Обработка выстрела (без автоматического переключения игрока)"""
        shots_set.add(fired_block)

        for ship in target.list_alive_ships:
            if fired_block in ship.cells:
                hits_set.add(fired_block)
                ship.cells.remove(fired_block)

                if not ship.cells:  # Корабль уничтожен
                    destroyed_ship = target.find_ship_by_cell(fired_block)
                    self.mark_destroyed_ship(destroyed_ship, shots_set)
                    target.list_alive_ships.remove(ship)

                    if not target.list_alive_ships:
                        self.game_over = True
                        self.winner = 1 if target == self.player2 else 2
                break

    def mark_destroyed_ship(self, ship, shots_set):
        """Помечаем область вокруг уничтоженного корабля"""
        for cell in ship.cells:
            row, col = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 1 <= row + i <= self.field_size[0] and 1 <= col + j <= self.field_size[1]:
                        mark_cell = (row + i, col + j)
                        shots_set.add(mark_cell)  # Добавляем в выстрелы (будет отрисован крестик)

    def run(self):
        """Основной игровой цикл"""
        self.start_game()

        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                else:
                    self.handle_turn(event)

            pygame.display.update()

        self.show_game_result()
        pygame.time.wait(3000)  # Задержка перед закрытием
        pygame.quit()

    def show_game_result(self):
        """Отображение результата игры"""
        font = pygame.font.SysFont('Arial', 40)
        result_text = font.render(f"Игрок {self.winner} победил!", True, BLACK)
        text_rect = result_text.get_rect(center=(self.field.screen.get_width() // 2,
                                                 self.field.screen.get_height() // 2))

        self.field.screen.fill(WHITE)
        self.field.screen.blit(result_text, text_rect)
        pygame.display.update()