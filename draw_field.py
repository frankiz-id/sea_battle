import pygame

from ships import Ship
from enums import Color, TypePlayer
from collections import namedtuple

pygame.init()
pygame.display.set_caption("Морской бой")

# Константы
BLOCK_SIZE = 30
LEFT_RIGHT_MARGIN = 50
UPPER_MARGIN = 40
FONT_SIZE = int(BLOCK_SIZE / 1.6)
FONT = pygame.font.SysFont("Verdana", FONT_SIZE)

FieldSize = namedtuple("FieldSize", ["height", "width"])


class DrawField:
    """Класс для отрисовки игрового поля и его элементов."""

    LETTERS = [
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
    ]

    def __init__(self, field_size: FieldSize = FieldSize(10, 10)) -> None:
        """
        Инициализация объекта отрисовки поля.

        Args:
            field_size: Размер поля в клетках (ширина, высота)
        """
        self._field_size: FieldSize = field_size
        # Динамический расчет размера окна
        self._screen_width = (
            LEFT_RIGHT_MARGIN * 2
            + self._field_size.width * BLOCK_SIZE * 2
            + 10 * BLOCK_SIZE
        )
        self._screen_height = UPPER_MARGIN + self._field_size.height * BLOCK_SIZE + 150
        self._screen = pygame.display.set_mode(
            (self._screen_width, self._screen_height)
        )
        self._screen.fill(Color.WHITE.value)

    def get_screen(self) -> pygame.Surface:
        return self._screen

    def get_screen_size(self) -> tuple[int, int]:
        """
        Возвращает размеры экрана.

        Returns:
            Кортеж (ширина, высота) экрана
        """
        return self._screen_width, self._screen_height

    def draw_field_grid(self) -> None:
        """Отрисовывает сетку игрового поля с координатами."""
        letters = self.LETTERS[: self._field_size.width]

        # Отрисовка сетки для обоих полей
        for field in range(2):
            offset_x = (
                LEFT_RIGHT_MARGIN
                + (self._field_size.width * BLOCK_SIZE + 10 * BLOCK_SIZE) * field
            )

            # Горизонтальные и вертикальные линии
            for row in range(self._field_size.height + 1):
                pygame.draw.line(
                    self._screen,
                    Color.BLACK.value,
                    (offset_x, UPPER_MARGIN + row * BLOCK_SIZE),
                    (
                        offset_x + self._field_size.width * BLOCK_SIZE,
                        UPPER_MARGIN + row * BLOCK_SIZE,
                    ),
                    1,
                )

            for col in range(self._field_size.width + 1):
                pygame.draw.line(
                    self._screen,
                    Color.BLACK.value,
                    (offset_x + col * BLOCK_SIZE, UPPER_MARGIN),
                    (
                        offset_x + col * BLOCK_SIZE,
                        UPPER_MARGIN + self._field_size.height * BLOCK_SIZE,
                    ),
                    1,
                )

            # Разметка координат
            for number in range(self._field_size.height):
                num_ver = FONT.render(str(number + 1), True, Color.BLACK.value)
                self._screen.blit(
                    num_ver,
                    (
                        offset_x - BLOCK_SIZE // 2 - num_ver.get_width() // 2,
                        UPPER_MARGIN
                        + number * BLOCK_SIZE
                        + (BLOCK_SIZE // 2 - num_ver.get_height() // 2),
                    ),
                )

            for num_letter in range(self._field_size.width):
                letter = FONT.render(letters[num_letter], True, Color.BLACK.value)
                self._screen.blit(
                    letter,
                    (
                        offset_x
                        + num_letter * BLOCK_SIZE
                        + (BLOCK_SIZE // 2 - letter.get_width() // 2),
                        UPPER_MARGIN + self._field_size.height * BLOCK_SIZE + 10,
                    ),
                )

    def sign_grids(
        self,
        mode: TypePlayer = TypePlayer.COMPUTER,
        draw_captions_when_playing_with_friend: int = 0,
    ) -> None:
        """
        Подписывает игровые поля (имена игроков или компьютера).

        Args:
            mode: Режим игры ('Computer' или 'Player')
            draw_captions_when_playing_with_friend: Флаг отображения подписей при игре с другом
        """
        if mode == TypePlayer.COMPUTER:
            player1 = FONT.render("Computer", True, Color.BLACK.value)
            player2 = FONT.render("Player", True, Color.BLACK.value)
        elif draw_captions_when_playing_with_friend:
            player1 = FONT.render("Player 1", True, Color.BLACK.value)
            player2 = FONT.render("Player 2", True, Color.BLACK.value)
        else:
            player1 = FONT.render("", True, Color.BLACK.value)
            player2 = FONT.render("", True, Color.BLACK.value)

        # Подписи для обоих полей
        self._screen.blit(
            player1,
            (
                LEFT_RIGHT_MARGIN
                + self._field_size.width * BLOCK_SIZE // 2
                - player1.get_width() // 2,
                UPPER_MARGIN - BLOCK_SIZE // 2 - FONT_SIZE,
            ),
        )

        offset = (
            LEFT_RIGHT_MARGIN + self._field_size.width * BLOCK_SIZE + 10 * BLOCK_SIZE
        )
        self._screen.blit(
            player2,
            (
                offset
                + self._field_size.width * BLOCK_SIZE // 2
                - player2.get_width() // 2,
                UPPER_MARGIN - BLOCK_SIZE // 2 - FONT_SIZE,
            ),
        )

    def draw_ships(self, ships: list[Ship], offset_x: int) -> None:
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
                    self._screen,
                    Color.BLACK.value,
                    (rect_x, rect_y, BLOCK_SIZE, BLOCK_SIZE),
                    3,
                )

    def draw_after_shot(
        self, fired_block: tuple[int, int], offset_x: int, success: bool
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
            self._screen, Color.BLACK.value, (x, y), (x + BLOCK_SIZE, y + BLOCK_SIZE), 2
        )
        pygame.draw.line(
            self._screen, Color.BLACK.value, (x + BLOCK_SIZE, y), (x, y + BLOCK_SIZE), 2
        )
        if success:
            pygame.draw.rect(
                self._screen, Color.BLACK.value, (x, y, BLOCK_SIZE, BLOCK_SIZE), 3
            )

    def draw_destroyed_area(self, ship: Ship, offset_x: int) -> None:
        """
        Отрисовывает область 3x3 вокруг уничтоженного корабля.

        Args:
            ship: Уничтоженный корабль
            offset_x: Смещение по оси X для отрисовки
        """
        for cell in ship.cells:
            row, col = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (
                        1 <= row + i <= self._field_size.height
                        and 1 <= col + j <= self._field_size.width
                    ):
                        x = offset_x + (col + j - 1) * BLOCK_SIZE
                        y = UPPER_MARGIN + (row + i - 1) * BLOCK_SIZE
                        pygame.draw.line(
                            self._screen,
                            Color.BLACK.value,
                            (x, y),
                            (x + BLOCK_SIZE, y + BLOCK_SIZE),
                            1,
                        )
                        pygame.draw.line(
                            self._screen,
                            Color.BLACK.value,
                            (x + BLOCK_SIZE, y),
                            (x, y + BLOCK_SIZE),
                            1,
                        )
