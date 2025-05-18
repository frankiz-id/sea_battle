import pytest
import sys
from unittest.mock import MagicMock, patch
import random


sys.modules['pygame'] = MagicMock()

from draw_field import FieldSize
from ships import Ship
from enums import ShipOrientation
from computer_ai import ComputerAI
from computer_ai_advanced import computerAIAdvanced
from ships_on_grid import ShipsOnGrid


@pytest.fixture
def field_size():
    return FieldSize(10, 10)


@pytest.fixture
def ship_config():
    return [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]


@pytest.fixture
def horizontal_ship():
    return Ship([(1, 1), (1, 2), (1, 3)], ShipOrientation.HORIZONTAL)


@pytest.fixture
def vertical_ship():
    return Ship([(1, 1), (2, 1), (3, 1)], ShipOrientation.VERTICAL)


@pytest.fixture
def basic_ai(field_size):
    ai = ComputerAI()
    ai.set_field_size(field_size)
    return ai


@pytest.fixture
def advanced_ai(field_size):
    ai = computerAIAdvanced()
    ai.set_field_size(field_size)
    return ai


@pytest.fixture
def ships_on_grid(field_size, ship_config):
    ships = ShipsOnGrid(field_size, ship_config)
    # патчим, чтобы random.choice всегда выбирал первый элемент
    with patch.object(random, 'choice', side_effect=lambda x: x[0]):
        ships.create_lots_of_game_ships()
    ships.create_list_alive_ships()
    return ships


class TestComputerAI:
    def test_initialization(self, basic_ai, field_size):
        """Проверяет, что ИИ корректно инициализируется с заданным размером"""
        assert basic_ai._field_size == field_size
        assert len(basic_ai._available_shots) == 100  # 10x10 grid

    def test_check_shot_for_success(self, basic_ai, horizontal_ship):
        """Проверяет, правильно ли определяется попадание в корабль"""
        assert basic_ai.check_shot_for_success((1, 1), [horizontal_ship]) is True
        assert basic_ai.check_shot_for_success((2, 2), [horizontal_ship]) is False

    def test_make_target(self, basic_ai):
        """Убеждается, что ИИ выбирает допустимые координаты для выстрела"""
        target = basic_ai.make_target()
        assert isinstance(target, tuple)
        assert len(target) == 2
        assert 1 <= target[0] <= 10
        assert 1 <= target[1] <= 10

    def test_make_shot(self, basic_ai, horizontal_ship):
        """Проверяет, что после выстрела клетка исключается из доступных"""
        with patch.object(random, 'choice', return_value=(1, 1)):
            target, success = basic_ai.make_shot([horizontal_ship])
            assert target == (1, 1)
            assert success is True
            assert (1, 1) not in basic_ai._available_shots

    def test_reset_search(self, basic_ai):
        """Проверяет сброс состояния ИИ после уничтожения корабля"""
        basic_ai._last_hit = (1, 1)
        basic_ai._direction = ShipOrientation.HORIZONTAL
        basic_ai._hits = [(1, 1)]
        basic_ai._target_stack = [(1, 2)]

        basic_ai.reset_search()

        assert basic_ai._last_hit is None
        assert basic_ai._direction is None
        assert basic_ai._hits == []
        assert basic_ai._target_stack == []

    def test_generate_target_stack(self, basic_ai):
        """Проверяет генерацию возможных целей вокруг попадания"""
        basic_ai._last_hit = (3, 3)
        basic_ai._direction = None
        basic_ai.generate_target_stack()

        expected_targets = [(4, 3), (2, 3), (3, 4), (3, 2)]
        assert len(basic_ai._target_stack) == 4
        for target in basic_ai._target_stack:
            assert target in expected_targets

    def test_determine_direction(self, basic_ai):
        """Проверяет определение направления корабля после попадания"""
        basic_ai._hits = [(3, 3), (3, 4)]
        basic_ai._target_stack = [(3, 5), (3, 2), (4, 3), (2, 3)]
        basic_ai._last_hit = (3, 4)

        basic_ai.determine_direction()

        assert basic_ai._direction == ShipOrientation.VERTICAL

        # тест с вертикальным напрвлением
        basic_ai._hits = [(3, 3), (4, 3)]
        basic_ai._target_stack = [(5, 3), (2, 3), (3, 4), (3, 2)]
        basic_ai._last_hit = (4, 3)

        basic_ai.determine_direction()

        assert basic_ai._direction == ShipOrientation.HORIZONTAL

    def test_filter_target_stack(self, basic_ai):
        """Убеждается, что ИИ корректно фильтрует цели после определения направления"""
        basic_ai._last_hit = (3, 3)
        basic_ai._direction = ShipOrientation.HORIZONTAL
        basic_ai._target_stack = [(3, 4), (3, 2), (4, 3), (2, 3)]

        basic_ai.filter_target_stack()

        assert all(target[1] == 3 for target in basic_ai._target_stack)
        assert len(basic_ai._target_stack) == 2

        basic_ai._direction = ShipOrientation.VERTICAL
        basic_ai._target_stack = [(3, 4), (3, 2), (4, 3), (2, 3)]

        basic_ai.filter_target_stack()

        assert all(target[0] == 3 for target in basic_ai._target_stack)
        assert len(basic_ai._target_stack) == 2

    def test_is_ship_destroyed(self, basic_ai, horizontal_ship):
        """Проверяет, что уничтожение корабля отмечается правильно"""
        basic_ai._hits = [(1, 1), (1, 2), (1, 3)]

        assert basic_ai.is_ship_destroyed([horizontal_ship]) is True
        assert horizontal_ship.destroyed is True

        basic_ai._hits = [(1, 1), (1, 2)]
        horizontal_ship.destroyed = False

        assert basic_ai.is_ship_destroyed([horizontal_ship]) is False
        assert horizontal_ship.destroyed is False

    def test_delete_area_destroyed_ship(self, basic_ai, horizontal_ship):
        """Проверяет, что зона вокруг уничтоженного корабля помечается как недоступная"""
        initial_shots = len(basic_ai._available_shots)

        basic_ai.delete_area_destroyed_ship(horizontal_ship)

        assert len(basic_ai._available_shots) < initial_shots

        for cell in horizontal_ship.cells:
            y, x = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    assert (y + i, x + j) not in basic_ai._available_shots


class TestComputerAIAdvanced:
    def test_initialization(self, advanced_ai, field_size):
        """Проверяет, что ИИ корректно инициализируется с заданным размером"""
        assert advanced_ai._field_size == field_size
        assert len(advanced_ai._available_shots) == 100  # 10x10 grid
        assert len(advanced_ai.set_available_cells_to_shots_while_four_ships) > 0
        assert len(advanced_ai.set_available_cells_to_shots_while_three_and_two_ships) > 0

    def test_generate_strategic_sets(self, advanced_ai):
        """Проверяет, что ИИ генерирует правильные стратегические клетки"""
        advanced_ai.set_available_cells_to_shots_while_four_ships.clear()
        advanced_ai.set_available_cells_to_shots_while_three_and_two_ships.clear()

        advanced_ai.generate_strategic_sets()

        assert len(advanced_ai.set_available_cells_to_shots_while_four_ships) > 0
        assert len(advanced_ai.set_available_cells_to_shots_while_three_and_two_ships) > 0

    def test_make_target_uses_strategic_sets(self, advanced_ai):
        """Проверяет, что ИИ сначала стреляет по стратегическим клеткам"""
        initial_four_ships = len(advanced_ai.set_available_cells_to_shots_while_four_ships)

        for _ in range(5):
            advanced_ai.make_target()

        assert len(advanced_ai.set_available_cells_to_shots_while_four_ships) < initial_four_ships

    def test_fallback_to_basic_targeting(self, advanced_ai):
        """Проверяет, что ИИ переключается на случайные выстрелы, если стратегические клетки закончились"""
        advanced_ai.set_available_cells_to_shots_while_four_ships.clear()
        advanced_ai.set_available_cells_to_shots_while_three_and_two_ships.clear()

        target = advanced_ai.make_target()

        assert target is not None
        assert isinstance(target, tuple)
        assert len(target) == 2

    def test_delete_area_destroyed_ship(self, advanced_ai, horizontal_ship):
        """Проверяет, что зона вокруг уничтоженного корабля удаляется из стратегических наборов"""
        initial_four_ships = len(advanced_ai.set_available_cells_to_shots_while_four_ships)
        initial_three_two_ships = len(advanced_ai.set_available_cells_to_shots_while_three_and_two_ships)

        advanced_ai.delete_area_destroyed_ship(horizontal_ship)

        assert len(advanced_ai.set_available_cells_to_shots_while_four_ships) < initial_four_ships
        assert len(advanced_ai.set_available_cells_to_shots_while_three_and_two_ships) < initial_three_two_ships


class TestShipsOnGrid:
    def test_initialization(self, ships_on_grid, field_size, ship_config):
        """Проверяет, что поле и конфигурация кораблей задаются правильно"""
        assert ships_on_grid.field_size == field_size
        assert ships_on_grid.ship_config == ship_config
        assert len(ships_on_grid.set_available_cells) > 0

    def test_group_ships_by_size(self, ships_on_grid):
        """Проверяет, что корабли группируются по размерам"""
        expected_groups = {1: 4, 2: 3, 3: 2, 4: 1}
        assert ships_on_grid.ship_groups == expected_groups

    def test_create_lots_of_game_ships(self, ships_on_grid):
        """Проверяет автоматическую расстановку кораблей"""
        assert len(ships_on_grid.list_of_game_ships) == 10

    def test_create_list_alive_ships(self, ships_on_grid):
        """Проверяет создание списка "живых" кораблей"""
        assert len(ships_on_grid.list_alive_ships) == 10

        for i, ship in enumerate(ships_on_grid.list_of_game_ships):
            assert ship is not ships_on_grid.list_alive_ships[i]
            assert ship.cells == ships_on_grid.list_alive_ships[i].cells

    def test_find_ship_by_cell(self, ships_on_grid):
        """ Проверяет поиск корабля по координатам"""
        first_ship = ships_on_grid.list_of_game_ships[0]
        first_cell = first_ship.cells[0]

        found_ship = ships_on_grid.find_ship_by_cell(first_cell)
        assert found_ship is first_ship

        non_existent_cell = (9, 9)
        not_found_ship = ships_on_grid.find_ship_by_cell(non_existent_cell)
        assert not_found_ship is None

    def test_reserve_ship_area(self, ships_on_grid):
        """Убеждается, что зона вокруг корабля резервируется"""
        initial_cells = len(ships_on_grid.set_available_cells)

        ship_cells = [(5, 5), (5, 6), (5, 7)]
        ships_on_grid.reserve_ship_area(ship_cells)

        assert len(ships_on_grid.set_available_cells) < initial_cells

        for i in range(4, 7):
            for j in range(4, 9):
                assert (i, j) not in ships_on_grid.set_available_cells

    def test_is_correct_place(self, ships_on_grid):
        """Проверяет, можно ли разместить корабль в заданной позиции"""
        empty_area_ship = [(8, 8), (8, 9)]
        assert ships_on_grid.is_correct_place(empty_area_ship) is True

        ships_on_grid.reserve_ship_area([(7, 7)])
        reserved_area_ship = [(7, 7), (7, 8)]
        assert ships_on_grid.is_correct_place(reserved_area_ship) is False


class TestGameIntegration:
    def test_ai_shooting_sequence(self, basic_ai, horizontal_ship):
        """Проверяет последовательность выстрелов ИИ (поиск, определение направления, уничтожение корабля)"""
        with patch.object(random, 'choice', return_value=(1, 1)):
            target, success = basic_ai.make_shot([horizontal_ship])
            assert target == (1, 1)
            assert success is True

            assert len(basic_ai._target_stack) > 0

            with patch.object(basic_ai, 'make_target', return_value=(1, 2)):
                target, success = basic_ai.make_shot([horizontal_ship])
                assert target == (1, 2)
                assert success is True

                assert basic_ai._direction == ShipOrientation.HORIZONTAL

                with patch.object(basic_ai, 'make_target', return_value=(1, 3)):
                    target, success = basic_ai.make_shot([horizontal_ship])
                    assert target == (1, 3)
                    assert success is True

                    assert horizontal_ship.destroyed is True
                    assert basic_ai._last_hit is None
                    assert basic_ai._direction is None

    def test_ship_destruction_game_state(self, ships_on_grid):
        """Проверяет, что уничтожение корабля обновляет состояние игры"""
        initial_ships = len(ships_on_grid.list_alive_ships)

        first_ship = ships_on_grid.list_alive_ships[0]
        first_ship.cells = []

        ships_on_grid.list_alive_ships = [ship for ship in ships_on_grid.list_alive_ships if ship.cells]

        assert len(ships_on_grid.list_alive_ships) == initial_ships - 1

    def test_advanced_ai_targeting_strategy(self, advanced_ai, field_size):
        """Проверяет, что продвинутый ИИ корректно использует стратегические клетки"""
        ship = Ship([(1, 4), (1, 5), (1, 6), (1, 7)], ShipOrientation.HORIZONTAL)

        assert (1, 4) in advanced_ai.set_available_cells_to_shots_while_four_ships

        with patch.object(advanced_ai, 'make_target', return_value=(1, 4)):
            target, success = advanced_ai.make_shot([ship])
            assert target == (1, 4)
            assert success is True

            assert len(advanced_ai._target_stack) > 0

            with patch.object(advanced_ai, 'make_target', return_value=(1, 5)):
                advanced_ai.make_shot([ship])

                assert advanced_ai._direction == ShipOrientation.HORIZONTAL

                with patch.object(advanced_ai, 'make_target', return_value=(1, 6)):
                    advanced_ai.make_shot([ship])
                    with patch.object(advanced_ai, 'make_target', return_value=(1, 7)):
                        advanced_ai.make_shot([ship])

                        assert ship.destroyed is True

                        for i in range(0, 3):
                            for j in range(3, 9):
                                cell = (i + 1, j + 1)
                                assert cell not in advanced_ai.set_available_cells_to_shots_while_four_ships
                                assert cell not in advanced_ai.set_available_cells_to_shots_while_three_and_two_ships
