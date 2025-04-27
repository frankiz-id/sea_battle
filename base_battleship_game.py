from abc import ABC, abstractmethod
import pygame
from enums import Color
from draw_field import DrawField, FieldSize
from ships_on_grid import ShipsOnGrid
from ships import Ship


class BaseBattleshipGame(ABC):
    """Базовый абстрактный класс для игр 'Морской бой'."""

    def __init__(
        self,
        field_size: FieldSize,
        ship_config: list[int],
        ship_placement: int,
    ) -> None:
        self._field_size = field_size
        self._ship_config = ship_config
        self._field = DrawField(field_size)
        self._ship_placement = ship_placement
        self._game_over = False
        self._winner: str | None = None

    @abstractmethod
    def start_game(self) -> None:
        """Начало игры (расстановка кораблей)."""
        pass

    @abstractmethod
    def start_manual_placement(self) -> None:
        """Начинает процесс ручной расстановки кораблей."""
        pass

    @abstractmethod
    def handle_setup_event(self, event: pygame.event.Event) -> None:
        """
        Обрабатывает события во время фазы расстановки.

        Args:
            event: Событие pygame для обработки
        """
        pass

    @abstractmethod
    def draw_setup_screen(self) -> None:
        """Отрисовывает экран во время фазы расстановки."""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def mark_destroyed_ship(self, ship: Ship, shots_set: set[tuple[int, int]]) -> None:
        """
        Помечает область вокруг уничтоженного корабля.

        Args:
            ship: Уничтоженный корабль
            shots_set: Множество, из которого нужно удалить корабль
        """
        pass

    @abstractmethod
    def run(self) -> None:
        """Основной игровой цикл."""
        pass

    def show_game_result(self) -> None:
        """Отображение результата игры."""
        font = pygame.font.SysFont("Arial", 40)
        result_text = font.render(
            f"Игрок {self._winner} победил!", True, Color.BLACK.value
        )
        text_rect = result_text.get_rect(
            center=(
                self._field.get_screen().get_width() // 2,
                self._field.get_screen().get_height() // 2,
            )
        )

        self._field.get_screen().fill(Color.WHITE.value)
        self._field.get_screen().blit(result_text, text_rect)
        pygame.display.update()
