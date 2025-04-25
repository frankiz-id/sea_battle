from enums import ShipOrientation


class Ship:
    """Класс для представления корабля в игре."""

    def __init__(
        self, cells: list[tuple[int, int]], orientation: ShipOrientation
    ) -> None:
        """
        Инициализация корабля.

        Args:
            cells: Список координат клеток корабля (строка, столбец)
            orientation: Ориентация корабля ('horizontal' или 'vertical')
        """
        self.cells: list[tuple[int, int]] = cells
        self.orientation: ShipOrientation = orientation
        self.destroyed: bool = False
