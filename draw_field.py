from typing import List, Tuple

import pygame

from ships_ import Ship
from enums import Color, type_player

pygame.init()
pygame.display.set_caption("Морской бой")

# Константы
BLOCK_SIZE = 30
LEFT_RIGHT_MARGIN = 50
UPPER_MARGIN = 40
FONT_SIZE = int(BLOCK_SIZE / 1.6)
FONT = pygame.font.SysFont("Verdana", FONT_SIZE)


class draw_Field:
    """Класс для отрисовки игрового поля и его элементов."""

    def __init__(self, field_size: Tuple[int, int] = (10, 10)) -> None:
        """
        Инициализация объекта отрисовки поля.

        Args:
            field_size: Размер поля в клетках (ширина, высота)
        """
        self.field_size = field_size
        # Динамический расчет размера окна
        self.screen_width = (
            LEFT_RIGHT_MARGIN * 2 + field_size[1] * BLOCK_SIZE * 2 + 10 * BLOCK_SIZE
        )
        self.screen_height = UPPER_MARGIN + field_size[0] * BLOCK_SIZE + 150
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen.fill(Color.WHITE.value)

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Возвращает размеры экрана.

        Returns:
            Кортеж (ширина, высота) экрана
        """
        return self.screen_width, self.screen_height

    def draw_field_grid(self) -> None:
        """Отрисовывает сетку игрового поля с координатами."""
        letters = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
        ][: self.field_size[1]]

        # Отрисовка сетки для обоих полей
        for field in range(2):
            offset_x = (
                LEFT_RIGHT_MARGIN
                + (self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE) * field
            )

            # Горизонтальные и вертикальные линии
            for i in range(self.field_size[0] + 1):
                pygame.draw.line(
                    self.screen,
                    Color.BLACK.value,
                    (offset_x, UPPER_MARGIN + i * BLOCK_SIZE),
                    (
                        offset_x + self.field_size[1] * BLOCK_SIZE,
                        UPPER_MARGIN + i * BLOCK_SIZE,
                    ),
                    1,
                )

            for i in range(self.field_size[1] + 1):
                pygame.draw.line(
                    self.screen,
                    Color.BLACK.value,
                    (offset_x + i * BLOCK_SIZE, UPPER_MARGIN),
                    (
                        offset_x + i * BLOCK_SIZE,
                        UPPER_MARGIN + self.field_size[0] * BLOCK_SIZE,
                    ),
                    1,
                )

            # Разметка координат
            for i in range(self.field_size[0]):
                num_ver = FONT.render(str(i + 1), True, Color.BLACK.value)
                self.screen.blit(
                    num_ver,
                    (
                        offset_x - BLOCK_SIZE // 2 - num_ver.get_width() // 2,
                        UPPER_MARGIN
                        + i * BLOCK_SIZE
                        + (BLOCK_SIZE // 2 - num_ver.get_height() // 2),
                    ),
                )

            for i in range(self.field_size[1]):
                letter = FONT.render(letters[i], True, Color.BLACK.value)
                self.screen.blit(
                    letter,
                    (
                        offset_x
                        + i * BLOCK_SIZE
                        + (BLOCK_SIZE // 2 - letter.get_width() // 2),
                        UPPER_MARGIN + self.field_size[0] * BLOCK_SIZE + 10,
                    ),
                )

    def sign_grids(
        self, mode: type_player = type_player.COMPUTER, draw_captions_when_playing_with_friend: int = 0
    ) -> None:
        """
        Подписывает игровые поля (имена игроков или компьютера).

        Args:
            mode: Режим игры ('Computer' или 'Player')
            draw_captions_when_playing_with_friend: Флаг отображения подписей при игре с другом
        """
        if mode == type_player.COMPUTER:
            player1 = FONT.render("Computer", True, Color.BLACK.value)
            player2 = FONT.render("Player", True, Color.BLACK.value)
        elif draw_captions_when_playing_with_friend:
            player1 = FONT.render("Player 1", True, Color.BLACK.value)
            player2 = FONT.render("Player 2", True, Color.BLACK.value)
        else:
            player1 = FONT.render("", True, Color.BLACK.value)
            player2 = FONT.render("", True, Color.BLACK.value)

        # Подписи для обоих полей
        self.screen.blit(
            player1,
            (
                LEFT_RIGHT_MARGIN
                + self.field_size[1] * BLOCK_SIZE // 2
                - player1.get_width() // 2,
                UPPER_MARGIN - BLOCK_SIZE // 2 - FONT_SIZE,
            ),
        )

        offset = LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE
        self.screen.blit(
            player2,
            (
                offset
                + self.field_size[1] * BLOCK_SIZE // 2
                - player2.get_width() // 2,
                UPPER_MARGIN - BLOCK_SIZE // 2 - FONT_SIZE,
            ),
        )

    def draw_ships(self, ships: List["Ship"], offset_x: int) -> None:
        """
        Отрисовывает корабли на поле.

        Args:
            ships: Список кораблей для отрисовки
            offset_x: Смещение по оси X для отрисовки
        """
        for ship in ships:
            for cell in ship.cells:
                row, col = cell
                rect_x = offset_x + (col - 1) * BLOCK_SIZE
                rect_y = UPPER_MARGIN + (row - 1) * BLOCK_SIZE
                pygame.draw.rect(
                    self.screen, Color.BLACK.value, (rect_x, rect_y, BLOCK_SIZE, BLOCK_SIZE), 3
                )

    def draw_after_shot(
        self, fired_block: Tuple[int, int], offset_x: int, success: bool
    ) -> None:
        """
        Отрисовывает результат выстрела.

        Args:
            fired_block: Координаты выстрела (строка, столбец)
            offset_x: Смещение по оси X для отрисовки
            success: Флаг успешного попадания
        """
        row, col = fired_block
        x = offset_x + (col - 1) * BLOCK_SIZE
        y = UPPER_MARGIN + (row - 1) * BLOCK_SIZE

        # Рисуем крестик
        pygame.draw.line(
            self.screen, Color.BLACK.value, (x, y), (x + BLOCK_SIZE, y + BLOCK_SIZE), 2
        )
        pygame.draw.line(
            self.screen, Color.BLACK.value, (x + BLOCK_SIZE, y), (x, y + BLOCK_SIZE), 2
        )
        if success:
            pygame.draw.rect(self.screen, Color.BLACK.value, (x, y, BLOCK_SIZE, BLOCK_SIZE), 3)

    def draw_destroyed_area(self, ship: "Ship", offset_x: int) -> None:
        """
        Отрисовывает область вокруг уничтоженного корабля.

        Args:
            ship: Уничтоженный корабль
            offset_x: Смещение по оси X для отрисовки
        """
        for cell in ship.cells:
            row, col = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (
                        1 <= row + i <= self.field_size[0]
                        and 1 <= col + j <= self.field_size[1]
                    ):
                        x = offset_x + (col + j - 1) * BLOCK_SIZE
                        y = UPPER_MARGIN + (row + i - 1) * BLOCK_SIZE
                        pygame.draw.line(
                            self.screen,
                            Color.BLACK.value,
                            (x, y),
                            (x + BLOCK_SIZE, y + BLOCK_SIZE),
                            1,
                        )
                        pygame.draw.line(
                            self.screen,
                            Color.BLACK.value,
                            (x + BLOCK_SIZE, y),
                            (x, y + BLOCK_SIZE),
                            1,
                        )
