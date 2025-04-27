import pygame
from base_battleship_game import BaseBattleshipGame
from draw_field import BLOCK_SIZE, LEFT_RIGHT_MARGIN, UPPER_MARGIN, FieldSize
from manual_ship_placer import ManualShipPlacer
from ships import Ship
from ships_on_grid import ShipsOnGrid
from enums import TypePlayer, Color


class GameWithFriend(BaseBattleshipGame):
    """Класс для управления игрой против друга."""

    def __init__(
        self, field_size: FieldSize, ship_config: list[int], ship_placement: int
    ) -> None:
        """
        Инициализация игры против друга.

        Args:
            field_size: Размер игрового поля
            ship_config: Конфигурация кораблей
            ship_placement: Способ расстановки кораблей (0 - ручной, 1 - автоматический)
        """
        super().__init__(field_size, ship_config, ship_placement)

        self.player1 = ShipsOnGrid(field_size, ship_config)
        self.player2 = ShipsOnGrid(field_size, ship_config)

        self._ship_placer: ManualShipPlacer | None = None
        self._setup_phase = True
        self._current_setup_player = 1
        self._current_player = 1

        # Множества выстрелов и попаданий
        self._player1_shots: set[tuple[int, int]] = (
            set()
        )  # выстрелы 1-го игрока (по полю 2-го)
        self._player2_shots: set[tuple[int, int]] = (
            set()
        )  # выстрелы 2-го игрока (по полю 1-го)
        self._player1_hits: set[tuple[int, int]] = set()  # попадания 1-го игрока
        self._player2_hits: set[tuple[int, int]] = set()  # попадания 2-го игрока

    def start_game(self) -> None:
        """Начинает игру с расстановкой кораблей."""
        if self._ship_placement == 1:  # Автоматическая расстановка
            self.player1.create_lots_of_game_ships()
            self.player1.create_list_alive_ships()
            self.player2.create_lots_of_game_ships()
            self.player2.create_list_alive_ships()
            self._setup_phase = False
            self._current_player = 1
        else:  # Ручная расстановка
            self.start_manual_placement()

    def start_manual_placement(self) -> None:
        """Начинает процесс ручной расстановки кораблей."""
        if self._current_setup_player == 1:
            offset = (LEFT_RIGHT_MARGIN, UPPER_MARGIN)  # Левое поле
        else:
            offset = (
                LEFT_RIGHT_MARGIN
                + self._field_size.width * BLOCK_SIZE
                + 10 * BLOCK_SIZE,
                UPPER_MARGIN,
            )  # Правое поле

        self._ship_placer = ManualShipPlacer(
            self._field_size,
            self._ship_config,
            offset,
            self._field.get_screen().get_width(),
        )
        self.draw_setup_screen()

    def handle_setup_event(self, event: pygame.event.Event) -> None:
        """
        Обрабатывает события во время фазы расстановки.

        Args:
            event: Событие pygame для обработки
        """
        if event.type == pygame.QUIT:
            self._game_over = True
            return

        if self._ship_placer is None:
            return

        if event.type == pygame.KEYDOWN and self._setup_phase:
            # Обработка выбора типа корабля (1-4)
            if pygame.K_1 <= event.key <= pygame.K_4:
                size = event.key - pygame.K_0
                if (
                    size in self._ship_placer.ship_counts
                    and self._ship_placer.ship_counts[size] > 0
                ):
                    self._ship_placer.current_ship_type = size
                    self._ship_placer.current_ship_cells = []

        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and self._setup_phase
            and self._ship_placer.current_ship_type
        ):
            # Обработка клика по полю для размещения корабля
            x, y = event.pos
            offset_x, offset_y = self._ship_placer.field_offset

            if (
                offset_x <= x <= offset_x + self._field_size.width * BLOCK_SIZE
                and offset_y <= y <= offset_y + self._field_size.height * BLOCK_SIZE
            ):
                col = ((x - offset_x) // BLOCK_SIZE) + 1
                row = ((y - offset_y) // BLOCK_SIZE) + 1
                cell = (row, col)

                if self._ship_placer.can_place_cell(cell):
                    self._ship_placer.add_ship_cell(cell)
                    if (
                        len(self._ship_placer.current_ship_cells)
                        == self._ship_placer.current_ship_type
                    ):
                        self._ship_placer.finalize_ship()

                        # Если размещение завершено, переключаем игрока
                        if self._ship_placer.completed:
                            self.switch_setup_player()

        self.draw_setup_screen()

    def draw_setup_screen(self) -> None:
        """Отрисовывает экран во время фазы расстановки."""
        self._field.get_screen().fill(Color.WHITE.value)
        self._field.draw_field_grid()
        self._field.sign_grids(TypePlayer.PLAYER, 1)

        # Отрисовка процесса расстановки
        if self._ship_placer:
            self._ship_placer.draw(self._field.get_screen())
            self._ship_placer.draw_ship_info(self._field.get_screen())

        # Подпись текущего игрока
        font = pygame.font.SysFont("Arial", 30)
        text = f"Игрок {self._current_setup_player} размещает корабли"
        text_surface = font.render(text, True, Color.BLACK.value)
        self._field.get_screen().blit(
            text_surface,
            (
                self._field.get_screen().get_width() // 2
                - text_surface.get_width() // 2,
                10,
            ),
        )

        pygame.display.update()

    def process_shot(
        self, fired_block: tuple[int, int], target: ShipsOnGrid, offset: int
    ) -> None:
        """
        Обработка выстрела.

        Args:
            fired_block: Координаты выстрела (строка, столбец)
            target: Цель выстрела (игрок)
            offset: Смещение по оси X для отрисовки
        """
        if self._current_player == 1:
            shots_set = self._player1_shots
            hits_set = self._player1_hits
        else:
            shots_set = self._player2_shots
            hits_set = self._player2_hits

        shots_set.add(fired_block)
        success = any(fired_block in ship.cells for ship in target.list_alive_ships)
        self._field.draw_after_shot(fired_block, offset, success)

        if success:
            hits_set.add(fired_block)
            for ship in target.list_alive_ships:
                if fired_block in ship.cells:
                    ship.cells.remove(fired_block)
                    if not ship.cells:  # Корабль уничтожен
                        destroyed_ship = target.find_ship_by_cell(fired_block)
                        if destroyed_ship is not None:
                            self._field.draw_destroyed_area(destroyed_ship, offset)
                            self.mark_destroyed_ship(destroyed_ship, shots_set)
                            target.list_alive_ships.remove(ship)

                            if not target.list_alive_ships:
                                self._game_over = True
                                self._winner = "1" if target == self.player2 else "2"
                    break

    def mark_destroyed_ship(self, ship: Ship, shots_set: set[tuple[int, int]]) -> None:
        """
        Помечаем область вокруг уничтоженного корабля.

        Args:
            ship: Уничтоженный корабль
            shots_set: Множество выстрелов для обновления
        """
        for cell in ship.cells:
            row, col = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (
                        1 <= row + i <= self._field_size.height
                        and 1 <= col + j <= self._field_size.width
                    ):
                        mark_cell = (row + i, col + j)
                        shots_set.add(mark_cell)

    def run(self) -> None:
        """Основной игровой цикл."""
        self.start_game()
        while not self._game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._game_over = True
                elif self._setup_phase:
                    self.handle_setup_event(event)
                else:
                    self.handle_turn(event)

            if not self._setup_phase:
                self.draw_game_state()

            pygame.display.update()

        self.show_game_result()
        pygame.time.wait(3000)
        pygame.quit()

    def switch_setup_player(self) -> None:
        """Переключение между игроками при ручной расстановке."""
        if self._ship_placer is not None:
            if self._current_setup_player == 1:
                # Сохраняем корабли для игрока 1
                self.player1.create_lots_of_game_ships_manual(
                    self._ship_placer.placed_ships
                )
                self.player1.create_list_alive_ships()
                # Переключаем на игрока 2
                self._current_setup_player = 2
                self.start_manual_placement()
            else:
                # Сохраняем корабли для игрока 2
                self.player2.create_lots_of_game_ships_manual(
                    self._ship_placer.placed_ships
                )
                self.player2.create_list_alive_ships()
                # Завершаем фазу расстановки
                self._setup_phase = False
                self._current_player = 1

    def draw_game_state(self) -> None:
        """Отрисовка текущего состояния игры."""
        self._field.get_screen().fill(Color.WHITE.value)
        self._field.draw_field_grid()
        self._field.sign_grids(TypePlayer.PLAYER)

        if self._current_player == 1:
            # Для игрока 1 левое поле - поле игрока 2 (корабли не видны)
            self.draw_enemy_field(
                LEFT_RIGHT_MARGIN, self._player1_shots, self._player1_hits
            )
            # Правое поле - свое поле (корабли видны)
            self.draw_own_field(
                LEFT_RIGHT_MARGIN
                + self._field_size.width * BLOCK_SIZE
                + 10 * BLOCK_SIZE,
                self.player1,
                self._player2_shots,
                self._player2_hits,
            )
        else:
            # Для игрока 2 левое поле - поле игрока 1 (корабли не видны)
            self.draw_enemy_field(
                LEFT_RIGHT_MARGIN, self._player2_shots, self._player2_hits
            )
            # Правое поле - свое поле (корабли видны)
            self.draw_own_field(
                LEFT_RIGHT_MARGIN
                + self._field_size.width * BLOCK_SIZE
                + 10 * BLOCK_SIZE,
                self.player2,
                self._player1_shots,
                self._player1_hits,
            )

        # Отображение текущего игрока
        turn_font = pygame.font.SysFont("Arial", 30)
        turn_text = turn_font.render(
            f"Ход игрока {self._current_player}", True, Color.BLACK.value
        )
        self._field.get_screen().blit(
            turn_text,
            (
                self._field.get_screen().get_width() // 2 - turn_text.get_width() // 2,
                10,
            ),
        )

    def draw_own_field(
        self,
        offset_x: int,
        player: ShipsOnGrid,
        enemy_shots: set[tuple[int, int]],
        enemy_hits: set[tuple[int, int]],
    ) -> None:
        """
        Отрисовка своего поля с кораблями.

        Args:
            offset_x: Смещение по оси X для отрисовки
            player: Объект игрока, чье поле отрисовывается
            enemy_shots: Множество выстрелов противника
            enemy_hits: Множество попаданий противника
        """
        # Отрисовка кораблей
        self._field.draw_ships(player.list_of_game_ships, offset_x)

        # Отрисовка выстрелов противника
        for shot in enemy_shots:
            self.draw_shot_marker(shot, offset_x, shot in enemy_hits)

    def draw_enemy_field(
        self,
        offset_x: int,
        my_shots: set[tuple[int, int]],
        my_hits: set[tuple[int, int]],
    ) -> None:
        """
        Отрисовка поля противника (без кораблей).

        Args:
            offset_x: Смещение по оси X для отрисовки
            my_shots: Множество моих выстрелов
            my_hits: Множество моих попаданий
        """
        # Отрисовка только своих выстрелов
        for shot in my_shots:
            self.draw_shot_marker(shot, offset_x, shot in my_hits)

    def draw_shot_marker(
        self, cell: tuple[int, int], offset_x: int, is_hit: bool
    ) -> None:
        """
        Отрисовка маркера выстрела.

        Args:
            cell: Координаты клетки (строка, столбец)
            offset_x: Смещение по оси X для отрисовки
            is_hit: Флаг попадания
        """
        row, col = cell
        x = offset_x + (col - 1) * BLOCK_SIZE
        y = UPPER_MARGIN + (row - 1) * BLOCK_SIZE

        if is_hit:
            # Красный кружок для попадания
            pygame.draw.circle(
                self._field.get_screen(),
                Color.RED.value,
                (x + BLOCK_SIZE // 2, y + BLOCK_SIZE // 2),
                BLOCK_SIZE // 3,
            )
        else:
            # Крестик для промаха
            pygame.draw.line(
                self._field.get_screen(),
                Color.BLACK.value,
                (x, y),
                (x + BLOCK_SIZE, y + BLOCK_SIZE),
                2,
            )
            pygame.draw.line(
                self._field.get_screen(),
                Color.BLACK.value,
                (x + BLOCK_SIZE, y),
                (x, y + BLOCK_SIZE),
                2,
            )

    def handle_turn(self, event: pygame.event.Event) -> None:
        """
        Обработка хода игрока с задержкой перед переключением.

        Args:
            event: Событие pygame для обработки
        """
        if event.type == pygame.MOUSEBUTTONDOWN and not self._game_over:
            x, y = event.pos
            field_left = LEFT_RIGHT_MARGIN
            field_right = field_left + self._field_size.width * BLOCK_SIZE

            if (
                field_left <= x <= field_right
                and UPPER_MARGIN
                <= y
                <= UPPER_MARGIN + self._field_size.height * BLOCK_SIZE
            ):
                col = (x - field_left) // BLOCK_SIZE + 1
                row = (y - UPPER_MARGIN) // BLOCK_SIZE + 1
                fired_block = (row, col)

                if self._current_player == 1 and fired_block not in self._player1_shots:
                    self.process_shot(fired_block, self.player2, LEFT_RIGHT_MARGIN)
                    self.draw_game_state()
                    pygame.display.update()

                    if fired_block not in self._player1_hits:
                        pygame.time.wait(450)
                        self._current_player = 2

                elif (
                    self._current_player == 2 and fired_block not in self._player2_shots
                ):
                    self.process_shot(
                        fired_block,
                        self.player1,
                        LEFT_RIGHT_MARGIN
                        + self._field_size.width * BLOCK_SIZE
                        + 10 * BLOCK_SIZE,
                    )
                    self.draw_game_state()
                    pygame.display.update()

                    if fired_block not in self._player2_hits:
                        pygame.time.wait(450)
                        self._current_player = 1

                self.draw_game_state()
                pygame.display.update()
