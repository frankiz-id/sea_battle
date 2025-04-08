from game_with_computer import *
from game_with_friend import *
from main_menu import *


def main():
    menu = main_menu()
    game_mode, ship_placement, field_size, ship_config = menu.run()
    if game_mode == "weak_ai":
        cur_game = game_with_computer("weak_ai", field_size, ship_config, ship_placement)
    elif game_mode == "strong_ai":
        cur_game = game_with_computer("strong_ai", field_size, ship_config, ship_placement)
    elif game_mode == "friend":
        cur_game = game_with_friend(field_size, ship_config, ship_placement)
    cur_game.run()

main()