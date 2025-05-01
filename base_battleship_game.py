from abc import ABC, abstractmethod
import pygame
from enums import Color
from draw_field import DrawField, FieldSize
from ships_on_grid import ShipsOnGrid
from ships import Ship
from battleship_interface import IBattleshipGame


class BaseBattleshipGame(IBattleshipGame, ABC):
    """Base abstract class for Battleship games."""

    def __init__(
        self,
        _field_size: FieldSize,
        _ship_config: list[int],
        _ship_placement: int,
    ) -> None:
        self._field_size = _field_size
        self._ship_config = _ship_config
        self._field = DrawField(_field_size)
        self._ship_placement = _ship_placement
        self._game_over = False
        self._winner: str | None = None

    @abstractmethod
    def _start_game(self) -> None:
        """Start the game (ship placement)."""
        pass

    @abstractmethod
    def _start_manual_placement(self) -> None:
        """Start manual ship placement process."""
        pass

    @abstractmethod
    def _handle_setup_event(self, event: pygame.event.Event) -> None:
        """Handle events during setup phase."""
        pass

    @abstractmethod
    def _draw_setup_screen(self) -> None:
        """Draw setup screen."""
        pass

    @abstractmethod
    def _process_shot(
        self, fired_block: tuple[int, int], target: ShipsOnGrid, offset: int
    ) -> None:
        """Process shot result."""
        pass

    @abstractmethod
    def _mark_destroyed_ship(self, ship: Ship, shots_set: set[tuple[int, int]]) -> None:
        """Mark area around destroyed ship."""
        pass

    def show_game_result(self) -> None:
        """Display game result."""
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
