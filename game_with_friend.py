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
        self, _field_size: FieldSize, _ship_config: list[int], _ship_placement: int
    ) -> None:
        super().__init__(_field_size, _ship_config, _ship_placement)
        self.player1 = ShipsOnGrid(_field_size, _ship_config)
        self.player2 = ShipsOnGrid(_field_size, _ship_config)
        self._ship_placer: ManualShipPlacer | None = None
        self._setup_phase = True
        self._current_setup_player = 1
        self._current_player = 1
        self._player1_shots: set[tuple[int, int]] = set()
        self._player2_shots: set[tuple[int, int]] = set()
        self._player1_hits: set[tuple[int, int]] = set()
        self._player2_hits: set[tuple[int, int]] = set()

    def _start_game(self) -> None:
        if self._ship_placement == 1:
            self.player1.create_lots_of_game_ships()
            self.player1.create_list_alive_ships()
            self.player2.create_lots_of_game_ships()
            self.player2.create_list_alive_ships()
            self._setup_phase = False
            self._current_player = 1
        else:
            self._start_manual_placement()

    def _start_manual_placement(self) -> None:
        if self._current_setup_player == 1:
            offset = (LEFT_RIGHT_MARGIN, UPPER_MARGIN)
        else:
            offset = (
                LEFT_RIGHT_MARGIN
                + self._field_size.width * BLOCK_SIZE
                + 10 * BLOCK_SIZE,
                UPPER_MARGIN,
            )

        self._ship_placer = ManualShipPlacer(
            self._field_size,
            self._ship_config,
            offset,
            self._field.get_screen().get_width(),
        )
        self._draw_setup_screen()

    def _handle_setup_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self._game_over = True
            return

        if self._ship_placer is None:
            return

        if event.type == pygame.KEYDOWN and self._setup_phase:
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
                        if self._ship_placer.completed:
                            self._switch_setup_player()

        self._draw_setup_screen()

    def _draw_setup_screen(self) -> None:
        self._field.get_screen().fill(Color.WHITE.value)
        self._field.draw_field_grid()
        self._field.sign_grids(TypePlayer.PLAYER, 1)

        if self._ship_placer:
            self._ship_placer.draw(self._field.get_screen())
            self._ship_placer.draw_ship_info(self._field.get_screen())

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

    def _process_shot(
        self, fired_block: tuple[int, int], target: ShipsOnGrid, offset: int
    ) -> None:
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
                    if not ship.cells:
                        destroyed_ship = target.find_ship_by_cell(fired_block)
                        if destroyed_ship is not None:
                            self._field.draw_destroyed_area(destroyed_ship, offset)
                            self._mark_destroyed_ship(destroyed_ship, shots_set)
                            target.list_alive_ships.remove(ship)

                            if not target.list_alive_ships:
                                self._game_over = True
                                self._winner = "1" if target == self.player2 else "2"
                    break

    def _mark_destroyed_ship(self, ship: Ship, shots_set: set[tuple[int, int]]) -> None:
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
        self._start_game()
        while not self._game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._game_over = True
                elif self._setup_phase:
                    self._handle_setup_event(event)
                else:
                    self._handle_turn(event)

            if not self._setup_phase:
                self._draw_game_state()
            pygame.display.update()

        self.show_game_result()
        pygame.time.wait(3000)
        pygame.quit()

    def _switch_setup_player(self) -> None:
        if self._ship_placer is not None:
            if self._current_setup_player == 1:
                self.player1.create_lots_of_game_ships_manual(
                    self._ship_placer.placed_ships
                )
                self.player1.create_list_alive_ships()
                self._current_setup_player = 2
                self._start_manual_placement()
            else:
                self.player2.create_lots_of_game_ships_manual(
                    self._ship_placer.placed_ships
                )
                self.player2.create_list_alive_ships()
                self._setup_phase = False
                self._current_player = 1

    def _draw_game_state(self) -> None:
        self._field.get_screen().fill(Color.WHITE.value)
        self._field.draw_field_grid()
        self._field.sign_grids(TypePlayer.PLAYER)

        if self._current_player == 1:
            self._draw_enemy_field(
                LEFT_RIGHT_MARGIN, self._player1_shots, self._player1_hits
            )
            self._draw_own_field(
                LEFT_RIGHT_MARGIN
                + self._field_size.width * BLOCK_SIZE
                + 10 * BLOCK_SIZE,
                self.player1,
                self._player2_shots,
                self._player2_hits,
            )
        else:
            self._draw_enemy_field(
                LEFT_RIGHT_MARGIN, self._player2_shots, self._player2_hits
            )
            self._draw_own_field(
                LEFT_RIGHT_MARGIN
                + self._field_size.width * BLOCK_SIZE
                + 10 * BLOCK_SIZE,
                self.player2,
                self._player1_shots,
                self._player1_hits,
            )

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

    def _draw_own_field(
        self,
        offset_x: int,
        player: ShipsOnGrid,
        enemy_shots: set[tuple[int, int]],
        enemy_hits: set[tuple[int, int]],
    ) -> None:
        self._field.draw_ships(player.list_of_game_ships, offset_x)
        for shot in enemy_shots:
            self._draw_shot_marker(shot, offset_x, shot in enemy_hits)

    def _draw_enemy_field(
        self,
        offset_x: int,
        my_shots: set[tuple[int, int]],
        my_hits: set[tuple[int, int]],
    ) -> None:
        for shot in my_shots:
            self._draw_shot_marker(shot, offset_x, shot in my_hits)

    def _draw_shot_marker(
        self, cell: tuple[int, int], offset_x: int, is_hit: bool
    ) -> None:
        row, col = cell
        x = offset_x + (col - 1) * BLOCK_SIZE
        y = UPPER_MARGIN + (row - 1) * BLOCK_SIZE

        if is_hit:
            pygame.draw.circle(
                self._field.get_screen(),
                Color.RED.value,
                (x + BLOCK_SIZE // 2, y + BLOCK_SIZE // 2),
                BLOCK_SIZE // 3,
            )
        else:
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

    def _handle_turn(self, event: pygame.event.Event) -> None:
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
                    self._process_shot(fired_block, self.player2, LEFT_RIGHT_MARGIN)
                    self._draw_game_state()
                    pygame.display.update()

                    if fired_block not in self._player1_hits:
                        pygame.time.wait(450)
                        self._current_player = 2

                elif (
                    self._current_player == 2 and fired_block not in self._player2_shots
                ):
                    self._process_shot(
                        fired_block,
                        self.player1,
                        LEFT_RIGHT_MARGIN
                        + self._field_size.width * BLOCK_SIZE
                        + 10 * BLOCK_SIZE,
                    )
                    self._draw_game_state()
                    pygame.display.update()

                    if fired_block not in self._player2_hits:
                        pygame.time.wait(450)
                        self._current_player = 1

                self._draw_game_state()
                pygame.display.update()
