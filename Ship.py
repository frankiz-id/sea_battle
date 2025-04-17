from typing import List, Tuple


class Ship:
    """Класс для представления корабля в игре."""

    def __init__(self, cells: List[Tuple[int, int]], orientation: str) -> None:
        """
        Инициализация корабля.

        Args:
            cells: Список координат клеток корабля (строка, столбец)
            orientation: Ориентация корабля ('horizontal' или 'vertical')
        """
        self.cells: List[Tuple[int, int]] = cells
        self.orientation: str = orientation
        self.destroyed: bool = False
