import pygame
from base_battleship_game import BaseBattleshipGame
from computer_ai import ComputerAI
from computer_ai_advanced import computerAIAdvanced
from draw_field import BLOCK_SIZE, LEFT_RIGHT_MARGIN, UPPER_MARGIN, FieldSize
from manual_ship_placer import ManualShipPlacer
from ships import Ship
from ships_on_grid import ShipsOnGrid
from enums import AIType, Color, TypePlayer


class GameWithComputer(BaseBattleshipGame):
    """Класс для управления логикой игры против компьютера."""

    def __init__(
        self,
        ai_type: AIType,
        _field_size: FieldSize,
        _ship_config: list[int],
        _ship_placement: int,
    ) -> None:
        super().__init__(_field_size, _ship_config, _ship_placement)
        self._player = ShipsOnGrid(_field_size, _ship_config)
        self._computer = ShipsOnGrid(_field_size, _ship_config)
        self._ai = ComputerAI() if ai_type == AIType.WEAK else computerAIAdvanced()
        self._ai.set_field_size(_field_size)
        self._available_to_fire_set_computer = set(
            (i, j)
            for i in range(1, _field_size.height + 1)
            for j in range(1, _field_size.width + 1)
        )
        self._computer_turn = False
        self._ship_placer: ManualShipPlacer | None = None

    def _start_game(self) -> None:
        self._field.draw_field_grid()
        self._field.sign_grids()
        self._computer.create_lots_of_game_ships()
        self._computer.create_list_alive_ships()

        if self._ship_placement:
            self._player.create_lots_of_game_ships()
            self._player.create_list_alive_ships()
            self._start_normal_game()
        else:
            self._start_manual_placement()

    def _start_manual_placement(self) -> None:
        offset = (
            LEFT_RIGHT_MARGIN + self._field_size.width * BLOCK_SIZE + 10 * BLOCK_SIZE,
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

        self._ship_placer.handle_event(event, self._field.get_screen())
        self._draw_setup_screen()

        if self._ship_placer.completed:
            self._player.create_lots_of_game_ships_manual(
                self._ship_placer.placed_ships
            )
            self._player.create_list_alive_ships()
            self._ship_placement = 1
            self._start_normal_game()

    def _draw_setup_screen(self) -> None:
        self._field.get_screen().fill(Color.WHITE.value)
        self._field.draw_field_grid()
        self._field.sign_grids()

        if self._ship_placer:
            self._ship_placer.draw(self._field.get_screen())
            self._ship_placer.draw_ship_info(self._field.get_screen())
        pygame.display.update()

    def _process_shot(
        self, fired_block: tuple[int, int], target: ShipsOnGrid, offset: int
    ) -> None:
        success = any(fired_block in ship.cells for ship in target.list_alive_ships)
        self._field.draw_after_shot(fired_block, offset, success)

        if success:
            for ship in target.list_alive_ships:
                if fired_block in ship.cells:
                    ship.cells.remove(fired_block)
                    if not ship.cells:
                        destroyed_ship = target.find_ship_by_cell(fired_block)
                        if destroyed_ship is not None:
                            self._field.draw_destroyed_area(destroyed_ship, offset)
                            if target == self._computer:
                                self._mark_destroyed_ship(
                                    destroyed_ship, self._available_to_fire_set_computer
                                )
                            else:
                                self._ai.delete_area_destroyed_ship(destroyed_ship)
                            target.list_alive_ships.remove(ship)
            if not target.list_alive_ships:
                self._game_over = True
                self._winner = (
                    TypePlayer.PLAYER.value
                    if target == self._computer
                    else TypePlayer.COMPUTER.value
                )
        else:
            self._computer_turn = target == self._computer

    def _mark_destroyed_ship(self, ship: Ship, shots_set: set[tuple[int, int]]) -> None:
        for cell in ship.cells:
            row, col = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (
                        1 <= row + i <= self._field_size.height
                        and 1 <= col + j <= self._field_size.width
                    ):
                        shots_set.discard((row + i, col + j))

    def run(self) -> None:
        self._start_game()
        while not self._game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._game_over = True
                elif not self._ship_placement:
                    self._handle_setup_event(event)
                elif not self._computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_player_turn(event)

            if self._ship_placement and self._computer_turn:
                self._handle_computer_turn()
            pygame.display.update()

        self.show_game_result()
        pygame.time.wait(3000)
        pygame.quit()

    def _start_normal_game(self) -> None:
        player_offset = (
            LEFT_RIGHT_MARGIN + self._field_size.width * BLOCK_SIZE + 10 * BLOCK_SIZE
        )
        self._field.draw_ships(self._player.list_of_game_ships, player_offset)
        pygame.display.update()

    def _handle_player_turn(self, event: pygame.event.Event) -> None:
        x, y = event.pos
        field_right = LEFT_RIGHT_MARGIN + self._field_size.width * BLOCK_SIZE
        field_bottom = UPPER_MARGIN + self._field_size.height * BLOCK_SIZE

        if LEFT_RIGHT_MARGIN <= x <= field_right and UPPER_MARGIN <= y <= field_bottom:
            col = ((x - LEFT_RIGHT_MARGIN) // BLOCK_SIZE) + 1
            row = ((y - UPPER_MARGIN) // BLOCK_SIZE) + 1
            fired_block = (row, col)

            if fired_block in self._available_to_fire_set_computer:
                self._available_to_fire_set_computer.discard(fired_block)
                self._process_shot(fired_block, self._computer, LEFT_RIGHT_MARGIN)

    def _handle_computer_turn(self) -> None:
        fired_block, success = self._ai.make_shot(self._player.list_alive_ships)
        self._process_shot(
            fired_block,
            self._player,
            LEFT_RIGHT_MARGIN + self._field_size.width * BLOCK_SIZE + 10 * BLOCK_SIZE,
        )
        if not success:
            self._computer_turn = False
