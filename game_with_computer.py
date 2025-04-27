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
        field_size: FieldSize,
        ship_config: list[int],
        ship_placement: int,
    ) -> None:
        """
        Инициализация игры против компьютера.

        Args:
            ai_type: Тип ИИ ('weak_ai' или 'strong_ai')
            field_size: Размер игрового поля
            ship_config: Конфигурация кораблей
            ship_placement: Способ расстановки кораблей (0 - ручной, 1 - автоматический)
        """
        super().__init__(field_size, ship_config, ship_placement)

        # Инициализация игроков
        self._player = ShipsOnGrid(field_size, ship_config)
        self._computer = ShipsOnGrid(field_size, ship_config)

        # Инициализация ИИ
        self._ai = ComputerAI() if ai_type == AIType.WEAK else computerAIAdvanced()
        self._ai.set_field_size(field_size)

        # Наборы доступных выстрелов
        self._available_to_fire_set_computer = set(
            (i, j)
            for i in range(1, field_size.height + 1)
            for j in range(1, field_size.width + 1)
        )

        self._computer_turn = False
        self._ship_placer: ManualShipPlacer | None = None

    def start_game(self) -> None:
        """Отрисовка полей и расстановка кораблей."""
        self._field.draw_field_grid()
        self._field.sign_grids()

        # Компьютер всегда расставляет корабли автоматически
        self._computer.create_lots_of_game_ships()
        self._computer.create_list_alive_ships()

        if self._ship_placement:  # Автоматическая расстановка
            self._player.create_lots_of_game_ships()
            self._player.create_list_alive_ships()
            self.start_normal_game()
        else:  # Ручная расстановка
            self.start_manual_placement()

    def start_manual_placement(self) -> None:
        """Начинает процесс ручной расстановки кораблей."""
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

        self._ship_placer.handle_event(event, self._field.get_screen())
        self.draw_setup_screen()

        if self._ship_placer.completed:
            # Сохраняем расставленные корабли
            self._player.create_lots_of_game_ships_manual(
                self._ship_placer.placed_ships
            )
            self._player.create_list_alive_ships()
            self._ship_placement = 1
            self.start_normal_game()

    def draw_setup_screen(self) -> None:
        """Отрисовывает экран во время фазы расстановки."""
        self._field.get_screen().fill(Color.WHITE.value)
        self._field.draw_field_grid()
        self._field.sign_grids()

        # Отрисовка процесса расстановки
        if self._ship_placer:
            self._ship_placer.draw(self._field.get_screen())
            self._ship_placer.draw_ship_info(self._field.get_screen())
        pygame.display.update()

    def process_shot(
        self, fired_block: tuple[int, int], target: ShipsOnGrid, offset: int
    ) -> None:
        """
        Обрабатывает результат выстрела.

        Args:
            fired_block: Координаты выстрела (строка, столбец)
            target: Цель выстрела (игрок или компьютер)
            offset: Смещение по оси X для отрисовки
        """
        success = any(fired_block in ship.cells for ship in target.list_alive_ships)
        self._field.draw_after_shot(fired_block, offset, success)

        if success:
            for ship in target.list_alive_ships:
                if fired_block in ship.cells:
                    ship.cells.remove(fired_block)
                    if not ship.cells:  # Корабль уничтожен
                        destroyed_ship = target.find_ship_by_cell(fired_block)
                        if destroyed_ship is not None:
                            self._field.draw_destroyed_area(destroyed_ship, offset)
                            if target == self._computer:
                                self.mark_destroyed_ship(
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

    def mark_destroyed_ship(self, ship: Ship, shots_set: set[tuple[int, int]]) -> None:
        """
        Помечает область вокруг уничтоженного корабля.

        Args:
            ship: Уничтоженный корабль
            shots_set: Множество, из которого нужно удалить корабль
        """
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
        """Основной игровой цикл."""
        self.start_game()

        while not self._game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._game_over = True
                elif not self._ship_placement:
                    self.handle_setup_event(event)
                elif not self._computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_player_turn(event)

            if self._ship_placement and self._computer_turn:
                self.handle_computer_turn()

            pygame.display.update()

        self.show_game_result()
        pygame.time.wait(3000)
        pygame.quit()

    def handle_player_turn(self, event: pygame.event.Event) -> None:
        """Обрабатывает ход игрока."""
        x, y = event.pos
        field_right = LEFT_RIGHT_MARGIN + self._field_size.width * BLOCK_SIZE
        field_bottom = UPPER_MARGIN + self._field_size.height * BLOCK_SIZE

        if LEFT_RIGHT_MARGIN <= x <= field_right and UPPER_MARGIN <= y <= field_bottom:
            col = ((x - LEFT_RIGHT_MARGIN) // BLOCK_SIZE) + 1
            row = ((y - UPPER_MARGIN) // BLOCK_SIZE) + 1
            fired_block = (row, col)

            if fired_block in self._available_to_fire_set_computer:
                self._available_to_fire_set_computer.discard(fired_block)
                self.process_shot(fired_block, self._computer, LEFT_RIGHT_MARGIN)

    def handle_computer_turn(self) -> None:
        """Обрабатывает ход компьютера."""
        fired_block, success = self._ai.make_shot(self._player.list_alive_ships)
        self.process_shot(
            fired_block,
            self._player,
            LEFT_RIGHT_MARGIN + self._field_size.width * BLOCK_SIZE + 10 * BLOCK_SIZE,
        )
        if not success:
            self._computer_turn = False

    def start_normal_game(self) -> None:
        """Начинает основную фазу игры после расстановки кораблей."""
        player_offset = (
            LEFT_RIGHT_MARGIN + self._field_size.width * BLOCK_SIZE + 10 * BLOCK_SIZE
        )
        self._field.draw_ships(self._player.list_of_game_ships, player_offset)
        pygame.display.update()
