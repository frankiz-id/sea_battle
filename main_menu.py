import pygame

from draw_field import FONT, DrawField, FieldSize
from enums import Color, GameMode

# Константы для улучшения читаемости
MENU_OPTIONS = {
    "WEAK_AI": "1. Play vs Weak AI",
    "STRONG_AI": "2. Play vs Strong AI",
    "FRIEND": "3. Play vs Friend",
    "SETTINGS": "4. Settings",
    "HELP": "5. Help",
    "EXIT": "6. Exit",
}

SETTINGS_OPTIONS = [
    "Field Size (5-16): ",
    "Ship Configuration",
    "manual/automatic placement: ",
    "Back to Main Menu",
]

help_lines = [
    "1. Главное меню:"
    "Главное меню предоставляет 6 опций, которые можно выбрать на цифры 1-6:",
    "Play vs Weak AI - игра против слабого ИИ (клавиша 1)",
    "Play vs Strong AI - игра против сильного ИИ (клавиша 2)",
    "Play vs Friend - игра против друга на одном устройстве (клавиша 3)",
    "Settings - настройки игры (клавиша 4)",
    "Help - справка по игре (клавиша 5)",
    "Exit - выход из игры (клавиша 6)",
    "",
    "2. Settings:",
    "При выборе 'Settings' (клавиша 4) открывается подменю с настройками:",
    "Field Size (5-16) - размер игрового поля",
    "Ship Configuration - конфигурация кораблей",
    "manual/automatic placement - выбор способа расстановки кораблей",
    "Back to Main Menu - возврат в главное меню",
    "Управление в меню настроек:",
    "Клавиши ↑ и ↓ - перемещение между пунктами меню",
    "Enter - выбор текущего пункта",
    "ESC - возврат в главное меню",
    "",
    "3. Особенности игры при выборе manual(ручной) расстановки кораблей в настройках:",
    "1-4 - выбор размера корабля, который хотите установить",
    "ЛКМ - выбор клетки для размещения корабля. Выбирайте клетки до тех пор, ",
    "пока не разместите весь корабль",
    "Если во время размещения вы поймете, что корабль не помещается ",
    "на выбранное место или вы передумали с расстановкой, ",
    "повторно нажмите 1-4 для выбора размера и начните установку заново",
]

SHIP_TYPES = ["4-deck ship", "3-deck ship", "2-deck ship", "1-deck ship"]
SHIP_SIZES = [4, 3, 2, 1]
MIN_FIELD_SIZE = 6
MAX_FIELD_SIZE = 16
PLACEMENT_OPTIONS = ["Manual", "Auto"]


class MainMenu:
    """Класс для реализации главного меню игры."""

    def __init__(self) -> None:
        """Инициализация главного меню."""
        pygame.init()
        # Указываем стандартный размер поля 10x10 для меню
        default_field_size = FieldSize(10, 10)
        self._screen = pygame.display.set_mode(
            DrawField(default_field_size).get_screen_size()
        )
        self._screen.fill(Color.WHITE.value)
        self._font = FONT
        self._game_mode: str | None = None
        self._field_size_in_blocks: FieldSize = default_field_size
        self.ship_config: list[int] = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self._temp_ship_counts: list[int] = [0, 0, 0, 0]
        self._plus_buttons: list[pygame.Rect] = []
        self._minus_buttons: list[pygame.Rect] = []
        self._error_message: str = ""
        self._error_time: int = 0
        self._number_free_cells: int = (
            self._field_size_in_blocks.height * self._field_size_in_blocks.width
        )
        self._ship_cell_requirements: dict[int, int] = {4: 14, 3: 12, 2: 9, 1: 5}
        self.ship_placement: int = 1  # 0 - ручная, 1 - автоматическая

        self._show_help: bool = False  # Флаг отображения справки
        self._content_height: int = len(help_lines) * 30 + 200
        self._help_scroll_y: int = 0

    def draw_text(self, text: str, x: int, y: int, color: Color = Color.BLACK) -> None:
        """
        Отрисовывает текст на экране.

        Args:
            text: Текст для отрисовки
            x: Координата по X
            y: Координата по Y
            color: Цвет текста
        """
        text_surface = self._font.render(text, False, color.value)
        self._screen.blit(text_surface, (x, y))

    def run(self) -> tuple[str | None, int, FieldSize, list[int]]:
        """
        Основной цикл главного меню.

        Returns:
            Кортеж (режим игры, способ расстановки, размер поля, конфигурация кораблей)
        """
        running = True
        while running:
            if self._show_help:
                self.draw_help_screen()
                running = self.handle_help_events()  # Используем специальный обработчик
            else:
                self.draw_main_menu()
                running = self.handle_main_menu_events()

            pygame.display.update()

        return (
            self._game_mode,
            self.ship_placement,
            self._field_size_in_blocks,
            self.ship_config,
        )

    def draw_help_screen(self) -> None:
        """Отрисовывает экран справки."""
        self._screen.fill(Color.LIGHT_GRAY.value)

        # Инициализация параметров прокрутки
        if not hasattr(self, "help_scroll_y"):
            self._help_scroll_y = 0
        self._content_height = 1500  # Общая высота контента

        # Создаем поверхность для контента
        content_surface = pygame.Surface(
            (self._screen.get_width(), self._content_height)
        )
        content_surface.fill(Color.LIGHT_GRAY.value)

        # Отрисовка текста на content_surface
        y_pos = 20
        for line in help_lines:
            text = self._font.render(line, True, Color.BLACK.value)
            content_surface.blit(text, (50, y_pos))
            y_pos += 30

        # Отображаем видимую часть с учетом прокрутки
        self._screen.blit(content_surface, (0, -self._help_scroll_y))

        # Кнопка "Назад" (рисуем отдельно, чтобы была фиксированной)
        back_button = pygame.Rect(
            self._screen.get_width() // 2 - 100, self._screen.get_height() - 80, 200, 50
        )
        pygame.draw.rect(self._screen, Color.PALE_GRAY.value, back_button)
        back_text = self._font.render("Назад", True, Color.BLACK.value)
        self._screen.blit(
            back_text,
            (
                back_button.x + back_button.width // 2 - back_text.get_width() // 2,
                back_button.y + back_button.height // 2 - back_text.get_height() // 2,
            ),
        )

    def handle_help_events(self) -> bool:
        """
        Обрабатывает события на экране справки.

        Returns:
            True, если нужно продолжить работу меню, False для выхода
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Проверяем кнопку "Назад" (фиксированная позиция)
                back_button = pygame.Rect(
                    self._screen.get_width() // 2 - 100,
                    self._screen.get_height() - 80,
                    200,
                    50,
                )
                if back_button.collidepoint(mouse_pos):
                    self._show_help = False
                    return True

            # Обработка прокрутки колесиком мыши
            if event.type == pygame.MOUSEWHEEL:
                visible_height = self._screen.get_height()
                max_scroll = self._content_height - visible_height
                self._help_scroll_y = max(
                    0, min(self._help_scroll_y - event.y * 30, max_scroll)
                )

        return True

    def draw_main_menu(self) -> None:
        """Отрисовывает главное меню."""
        self._screen.fill(Color.WHITE.value)
        y_position = 100
        for option in MENU_OPTIONS.values():
            self.draw_text(option, 100, y_position)
            y_position += 50

    def handle_main_menu_events(self) -> bool:
        """
        Обрабатывает события главного меню.

        Returns:
            True, если нужно продолжить работу меню, False для выхода
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self._show_help:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    back_button = pygame.Rect(
                        self._screen.get_width() // 2 - 100,
                        self._screen.get_height() - 80,
                        200,
                        50,
                    )
                    if back_button.collidepoint(mouse_pos):
                        self._show_help = False
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self._game_mode = GameMode.WEAK_AI
                        return False
                    elif event.key == pygame.K_2:
                        self._game_mode = GameMode.STRONG_AI
                        return False
                    elif event.key == pygame.K_3:
                        self._game_mode = GameMode.FRIEND
                        return False
                    elif event.key == pygame.K_4:
                        self.show_settings(0)
                    elif event.key == pygame.K_5:
                        self._show_help = True
                    elif event.key == pygame.K_6:
                        return False
        return True

    def show_settings(self, selected_option: int) -> None:
        """
        Следит за тем, отображать меню настроек или нет.

        Args:
            selected_option: Индекс выбранной опции
        """
        settings_running = True
        current_option = selected_option
        while settings_running:
            self.draw_settings_menu(current_option)
            settings_running, current_option = self.handle_settings_events(
                current_option
            )

    def draw_settings_menu(self, selected_option: int) -> None:
        """
        Отрисовывает меню настроек.

        Args:
            selected_option: Индекс выбранной опции
        """
        self._screen.fill(Color.WHITE.value)
        for i, option in enumerate(SETTINGS_OPTIONS):
            text = option
            if i == 0:
                text += str(self._field_size_in_blocks.height)
            elif i == 2:
                if self.ship_placement == 1:
                    text += PLACEMENT_OPTIONS[self.ship_placement]
                elif self.ship_placement == 0:
                    text += PLACEMENT_OPTIONS[self.ship_placement]
            color = Color.BLACK if i == selected_option else Color.MEDIUM_GRAY
            self.draw_text(text, 100, 100 + i * 50, color)
        pygame.display.update()

    def handle_settings_events(self, selected_option: int) -> tuple[bool, int]:
        """
        Обрабатывает события меню настроек.

        Args:
            selected_option: Индекс выбранной опции

        Returns:
            Кортеж (продолжить работу или нет, новая выбранная опция)
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, selected_option
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(SETTINGS_OPTIONS)
                    return True, selected_option
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(SETTINGS_OPTIONS)
                    return True, selected_option
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        if self.change_field_size():
                            self.configure_ships()
                    elif selected_option == 1:
                        self.configure_ships()
                    elif selected_option == 2:
                        self.ship_placement = (self.ship_placement + 1) % len(
                            PLACEMENT_OPTIONS
                        )
                    elif selected_option == 3:
                        return False, selected_option
                elif event.key == pygame.K_ESCAPE:
                    return False, selected_option
        return True, selected_option

    def change_field_size(self) -> bool:
        """
        Изменяет размер игрового поля.

        Returns:
            True, если размер был изменен, False в случае ошибки
        """
        new_size = self.get_user_input("Enter field size (6-16): ")
        if new_size:
            new_size_field = int(new_size)
            if MIN_FIELD_SIZE <= new_size_field <= MAX_FIELD_SIZE:
                self._field_size_in_blocks = FieldSize(new_size_field, new_size_field)
                self._number_free_cells = new_size_field * new_size_field
                self.ship_config = [1]
                self._temp_ship_counts = [0, 0, 0, 1]
                return True
        return False

    def configure_ships(self) -> None:
        """Настраивает конфигурацию кораблей."""
        self.init_temp_ship_counts()
        self.calculate_occupied_cells()
        self._plus_buttons = []
        self._minus_buttons = []

        configuring = True
        while configuring:
            self.draw_ship_configuration()
            configuring = self.handle_ship_configuration_events()

    def init_temp_ship_counts(self) -> None:
        """Инициализирует временные счетчики кораблей."""
        self._temp_ship_counts = [0, 0, 0, 0]
        for ship in self.ship_config:
            if ship == 4:
                self._temp_ship_counts[0] += 1
            elif ship == 3:
                self._temp_ship_counts[1] += 1
            elif ship == 2:
                self._temp_ship_counts[2] += 1
            elif ship == 1:
                self._temp_ship_counts[3] += 1

    def calculate_occupied_cells(self) -> None:
        """Вычисляет количество занятых клеток на поле."""
        occupied_cells = 0
        for size, count in zip(SHIP_SIZES, self._temp_ship_counts):
            occupied_cells += count * self._ship_cell_requirements[size]
        self._number_free_cells = (
            self._field_size_in_blocks.height * self._field_size_in_blocks.width
            - occupied_cells
        )

    def draw_ship_configuration(self) -> None:
        """Отрисовывает экран конфигурации кораблей."""
        self._screen.fill(Color.WHITE.value)
        self.draw_configuration_header()
        self.draw_ship_controls()
        self.draw_action_buttons()
        pygame.display.update()

    def draw_configuration_header(self) -> None:
        """Отрисовывает заголовок экрана конфигурации кораблей."""
        self.draw_text("Configure Ships", 100, 50)
        self.draw_text(f"Свободных клеток: {self._number_free_cells}", 400, 50)

        if (
            hasattr(self, "error_message")
            and pygame.time.get_ticks() - self._error_time < 5000
        ):
            self.draw_text(self._error_message, 100, 80, Color.RED)

    def draw_ship_controls(self) -> None:
        """Отрисовывает элементы управления конфигурацией кораблей."""
        start_y = 100
        for i, (ship_type, count) in enumerate(zip(SHIP_TYPES, self._temp_ship_counts)):
            self.draw_ship_type(ship_type, 100, start_y + i * 50)
            self.draw_ship_count(count, 250, start_y + i * 50)
            self.draw_control_buttons(i, 300, 350, start_y + i * 50)

    def draw_ship_type(self, ship_type: str, x: int, y: int) -> None:
        """
        Отрисовывает тип корабля.

        Args:
            ship_type: Тип корабля
            x: Координата X
            y: Координата Y
        """
        self.draw_text(ship_type, x, y)

    def draw_ship_count(self, count: int, x: int, y: int) -> None:
        """
        Отрисовывает количество кораблей.

        Args:
            count: Количество кораблей
            x: Координата X
            y: Координата Y
        """
        self.draw_text(str(count), x, y)

    def draw_control_buttons(
        self, index: int, minus_x: int, plus_x: int, y: int
    ) -> None:
        """
        Отрисовывает кнопки управления количеством кораблей.

        Args:
            index: Индекс типа корабля
            minus_x: Координата X кнопки "-"
            plus_x: Координата X кнопки "+"
            y: Координата Y
        """
        minus_rect = pygame.Rect(minus_x, y, 30, 30)
        pygame.draw.rect(self._screen, Color.BLACK.value, minus_rect, 2)
        self.draw_text("-", minus_x + 10, y)

        plus_rect = pygame.Rect(plus_x, y, 30, 30)
        pygame.draw.rect(self._screen, Color.BLACK.value, plus_rect, 2)
        self.draw_text("+", plus_x + 10, y)

        if len(self._minus_buttons) <= index:
            self._minus_buttons.append(minus_rect)
            self._plus_buttons.append(plus_rect)
        else:
            self._minus_buttons[index] = minus_rect
            self._plus_buttons[index] = plus_rect

    def draw_action_buttons(self) -> None:
        """Отрисовывает кнопки действий для меню настройки конфигурации кораблей (подтвердить, сбросить)."""
        confirm_rect = pygame.Rect(100, 350, 200, 40)
        pygame.draw.rect(self._screen, Color.BLACK.value, confirm_rect, 2)
        self.draw_text("Confirm", 180, 360)

        reset_rect = pygame.Rect(100, 400, 200, 40)
        pygame.draw.rect(self._screen, Color.BLACK.value, reset_rect, 2)
        self.draw_text("Reset to Default", 140, 410)

    def handle_ship_configuration_events(self) -> bool:
        """
        Обрабатывает события экрана конфигурации кораблей.

        Returns:
            True, если нужно продолжить конфигурацию, False для выхода
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                self.handle_plus_minus_buttons(pos)
                if self.handle_confirm_button(pos):
                    return False
                self.handle_reset_button(pos)
        return True

    def handle_plus_minus_buttons(self, pos: tuple[int, int]) -> None:
        """
        Обрабатывает нажатия на кнопки "+" и "-".

        Args:
            pos: Позиция клика (x, y)
        """
        for i, (plus_rect, minus_rect) in enumerate(
            zip(self._plus_buttons, self._minus_buttons)
        ):
            ship_size = SHIP_SIZES[i]
            if plus_rect.collidepoint(pos) and self.can_place_ship(ship_size):
                self._temp_ship_counts[i] += 1
            elif minus_rect.collidepoint(pos) and self._temp_ship_counts[i] > 0:
                self._temp_ship_counts[i] -= 1
                self._number_free_cells += self._ship_cell_requirements[ship_size]

    def handle_confirm_button(self, pos: tuple[int, int]) -> bool:
        """
        Обрабатывает нажатие кнопки подтверждения для меню изменения конфигурации.

        Args:
            pos: Позиция клика (x, y)

        Returns:
            True, если нажатие обработано, иначе False
        """
        confirm_rect = pygame.Rect(100, 350, 200, 40)
        if confirm_rect.collidepoint(pos):
            new_config = []
            for i, count in enumerate(self._temp_ship_counts):
                ship_size = SHIP_SIZES[i]
                new_config.extend([ship_size] * count)
            self.ship_config = new_config
            return True
        return False

    def handle_reset_button(self, pos: tuple[int, int]) -> None:
        """
        Обрабатывает нажатие кнопки сброса для меню изменения конфигурации.

        Args:
            pos: Позиция клика (x, y)
        """
        reset_rect = pygame.Rect(100, 400, 200, 40)
        if reset_rect.collidepoint(pos):
            self._temp_ship_counts = [0, 0, 0, 1]
            self._number_free_cells = (
                self._field_size_in_blocks.height * self._field_size_in_blocks.width
                - self._ship_cell_requirements[1]
            )

    def can_place_ship(self, ship_size: int) -> bool:
        """
        Проверяет, можно ли разместить корабль заданного размера.

        Args:
            ship_size: Размер корабля

        Returns:
            True, если корабль можно разместить, иначе False
        """
        if self._number_free_cells <= 0:
            self.show_error_message("Еще один такой корабль не поместится на поле")
            return False

        required_cells = self._ship_cell_requirements.get(ship_size, 0)
        if required_cells <= self._number_free_cells:
            self._number_free_cells -= required_cells
            return True
        else:
            self.show_error_message("Еще один такой корабль не поместится на поле")
            return False

    def show_error_message(self, message: str) -> None:
        """
        Отображает сообщение об ошибке.

        Args:
            message: Текст сообщения
        """
        self._error_message = message
        self._error_time = pygame.time.get_ticks()

    def get_user_input(self, prompt: str) -> str | None:
        """
        Получает пользовательский ввод через текстовое поле.

        Args:
            prompt: Подсказка для ввода

        Returns:
            Введенный текст или None, если ввод отменен
        """
        input_box = pygame.Rect(100, 200, 140, 32)
        color_inactive = Color.PALE_GRAY.value
        color_active = Color.BLACK.value
        color = color_inactive
        active = False
        text = ""
        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    active = input_box.collidepoint(event.pos)
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN and active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif pygame.K_0 <= event.key <= pygame.K_9:
                        text += event.unicode

            self._screen.fill(Color.WHITE.value)
            txt_surface = self._font.render(prompt + text, True, color)
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            self._screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(self._screen, color, input_box, 2)
            pygame.display.update()

        return text
