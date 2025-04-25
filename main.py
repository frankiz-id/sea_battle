from game_with_computer import GameWithComputer
from game_with_friend import GameWithFriend
from main_menu import MainMenu
from enums import AIType, GameMode


def main() -> None:
    """
    Основная функция игры.
    Запускает главное меню и инициализирует выбранный режим игры.
    """
    menu = MainMenu()
    game_mode, ship_placement, field_size, ship_config = menu.run()

    cur_game: GameWithComputer | GameWithFriend

    if game_mode == GameMode.WEAK_AI:
        cur_game = GameWithComputer(
            AIType.WEAK, field_size, ship_config, ship_placement
        )
    elif game_mode == GameMode.STRONG_AI:
        cur_game = GameWithComputer(
            AIType.STRONG, field_size, ship_config, ship_placement
        )
    elif game_mode == GameMode.FRIEND:
        cur_game = GameWithFriend(field_size, ship_config, ship_placement)
    cur_game.run()


if __name__ == "__main__":
    main()
