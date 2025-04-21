from typing import List, Optional, Set, Tuple

import pygame

from computer_ai import computerAI
from computer_ai_advanced import computerAI_advanced
from draw_field import BLOCK_SIZE, LEFT_RIGHT_MARGIN, UPPER_MARGIN, draw_Field
from manual_ship_placer import manual_ship_placer
from ships_ import Ship
from ships_on_grid import ships_on_grid
from enums import AIType, Color, type_player


class game_with_computer:
    """Класс для управления логикой игры против компьютера."""

    def __init__(
        self,
        ai_type: AIType,
        field_size: Tuple[int, int],
        ship_config: List[int],
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
        self.field_size = field_size
        self.ship_config = ship_config
        self.field = draw_Field(field_size)
        self.ship_placement = ship_placement

        # Инициализация игроков
        self.player = ships_on_grid(field_size, ship_config)
        self.computer = ships_on_grid(field_size, ship_config)

        # Инициализация ИИ
        self.ai = computerAI() if ai_type == AIType.WEAK else computerAI_advanced()
        self.ai.set_field_size(field_size)

        # Наборы доступных выстрелов
        self.available_to_fire_set_computer: Set[Tuple[int, int]] = set(
            (i, j)
            for i in range(1, field_size[0] + 1)
            for j in range(1, field_size[1] + 1)
        )

        self.game_over = False
        self.computer_turn = False
        self.winner: Optional[str] = None
        self.ship_placer: Optional[manual_ship_placer] = None

    def start_game(self) -> None:
        """Отрисовка полей и расстановка кораблей."""
        self.field.draw_field_grid()
        self.field.sign_grids()

        # Компьютер всегда расставляет корабли автоматически
        self.computer.create_lots_of_game_ships()
        self.computer.create_list_alive_ships()

        if self.ship_placement:  # Автоматическая расстановка
            self.player.create_lots_of_game_ships()
            self.player.create_list_alive_ships()
            self.start_normal_game()
        else:  # Ручная расстановка
            self.start_manual_placement()

    def start_normal_game(self) -> None:
        """Начинает основную фазу игры после расстановки кораблей."""
        player_offset = (
            LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE
        )
        self.field.draw_ships(self.player.list_of_game_ships, player_offset)
        pygame.display.update()

    def start_manual_placement(self) -> None:
        """Начинает процесс ручной расстановки кораблей."""
        offset = (
            LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE,
            UPPER_MARGIN,
        )
        self.ship_placer = manual_ship_placer(
            self.field_size, self.ship_config, offset, self.field.screen.get_width()
        )
        self.draw_setup_screen()

    def handle_setup_event(self, event: pygame.event.Event) -> None:
        """
        Обрабатывает события во время фазы расстановки.

        Args:
            event: Событие pygame для обработки
        """
        if event.type == pygame.QUIT:
            self.game_over = True
            return

        if self.ship_placer is None:
            return

        self.ship_placer.handle_event(event, self.field.screen)
        self.draw_setup_screen()

        if self.ship_placer.completed:
            # Сохраняем расставленные корабли
            self.player.create_lots_of_game_ships_manual(self.ship_placer.placed_ships)
            self.player.create_list_alive_ships()
            self.ship_placement = 1
            self.start_normal_game()

    def draw_setup_screen(self) -> None:
        """Отрисовывает экран во время фазы расстановки."""
        self.field.screen.fill(Color.WHITE.value)
        self.field.draw_field_grid()
        self.field.sign_grids()

        # Отрисовка процесса расстановки
        if self.ship_placer:
            self.ship_placer.draw(self.field.screen)
            self.ship_placer.draw_ship_info(self.field.screen)
        pygame.display.update()

    def handle_player_turn(self, event: pygame.event.Event) -> None:
        """
        Обрабатывает ход игрока.

        Args:
            event: Событие pygame для обработки
        """
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

    def handle_computer_turn(self) -> None:
        """Обрабатывает ход компьютера."""
        fired_block, success = self.ai.make_shot(self.player.list_alive_ships)
        self.process_shot(
            fired_block,
            self.player,
            LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE,
        )
        if not success:
            self.computer_turn = False

    def process_shot(
        self, fired_block: Tuple[int, int], target: "ships_on_grid", offset: int
    ) -> None:
        """
        Обрабатывает результат выстрела.

        Args:
            fired_block: Координаты выстрела (строка, столбец)
            target: Цель выстрела (игрок или компьютер)
            offset: Смещение по оси X для отрисовки
        """
        success = any(fired_block in ship.cells for ship in target.list_alive_ships)
        self.field.draw_after_shot(fired_block, offset, success)

        if success:
            self.handle_successful_shot(fired_block, target, offset)
            if not target.list_alive_ships:
                self.game_over = True
                self.winner = type_player.PLAYER.value if target == self.computer else type_player.COMPUTER.value
        else:
            self.computer_turn = target == self.computer

    def handle_successful_shot(
        self, fired_block: Tuple[int, int], target: "ships_on_grid", offset: int
    ) -> None:
        """
        Обрабатывает успешное попадание.

        Args:
            fired_block: Координаты выстрела (строка, столбец)
            target: Цель выстрела (игрок или компьютер)
            offset: Смещение по оси X для отрисовки
        """
        for ship in target.list_alive_ships:
            if fired_block in ship.cells:
                ship.cells.remove(fired_block)
                if not ship.cells:  # Корабль уничтожен
                    destroyed_ship = target.find_ship_by_cell(fired_block)
                    if destroyed_ship is not None:
                        self.field.draw_destroyed_area(destroyed_ship, offset)
                        if target == self.computer:
                            self.mark_destroyed_ship_area(destroyed_ship)
                        else:
                            self.ai.delete_area_destroyed_ship(destroyed_ship)
                        target.list_alive_ships.remove(ship)

    def mark_destroyed_ship_area(self, ship: "Ship") -> None:
        """
        Помечает область вокруг уничтоженного корабля.

        Args:
            ship: Уничтоженный корабль
        """
        for cell in ship.cells:
            row, col = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (
                        1 <= row + i <= self.field_size[0]
                        and 1 <= col + j <= self.field_size[1]
                    ):
                        self.available_to_fire_set_computer.discard((row + i, col + j))

    def run(self) -> None:
        """Основной игровой цикл."""
        self.start_game()

        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                elif not self.ship_placement:
                    self.handle_setup_event(event)
                elif not self.computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_player_turn(event)

            if self.ship_placement and self.computer_turn:
                self.handle_computer_turn()

            pygame.display.update()

        self.end_game()
        pygame.quit()

    def end_game(self) -> None:
        """Отображает результат игры."""
        print(f"Game over! Winner: {self.winner}")
