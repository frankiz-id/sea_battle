from abc import ABC, abstractmethod


class IBattleshipGame(ABC):
    @abstractmethod
    def run(self) -> None:
        """Основной игровой цикл"""
        pass

    @abstractmethod
    def show_game_result(self) -> None:
        """Показывает результат игры"""
        pass
