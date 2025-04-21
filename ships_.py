from typing import List, Tuple
from enums import ShipOrientation


class Ship:
    """Класс для представления корабля в игре."""

    def __init__(self, cells: List[Tuple[int, int]], orientation: ShipOrientation) -> None:
        """
        Инициализация корабля.

        Args:
            cells: Список координат клеток корабля (строка, столбец)
            orientation: Ориентация корабля ('horizontal' или 'vertical')
        """
        self.cells: List[Tuple[int, int]] = cells
        self.orientation: ShipOrientation = orientation
        self.destroyed: bool = False
