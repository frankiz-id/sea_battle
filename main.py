from game_with_computer import game_with_computer
from game_with_friend import game_with_friend
from main_menu import main_menu
from enums import AIType, GameMode
from typing import Union


def main() -> None:
    """
    Основная функция игры.
    Запускает главное меню и инициализирует выбранный режим игры.
    """
    menu = main_menu()
    game_mode, ship_placement, field_size, ship_config = menu.run()

    cur_game: Union[game_with_computer, game_with_friend]

    if game_mode == GameMode.WEAK_AI:
        cur_game = game_with_computer(
            AIType.WEAK, field_size, ship_config, ship_placement
        )
    elif game_mode == GameMode.STRONG_AI:
        cur_game = game_with_computer(
            AIType.STRONG, field_size, ship_config, ship_placement
        )
    elif game_mode == GameMode.FRIEND:
        cur_game = game_with_friend(field_size, ship_config, ship_placement)
    cur_game.run()


if __name__ == "__main__":
    main()
