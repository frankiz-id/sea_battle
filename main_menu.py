from draw_Field import FONT, WHITE, BLACK, draw_Field
import pygame

#field_size_in_blocks = (10, 10)
field = draw_Field()

class main_menu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(field.get_screen_size())
        self.screen.fill(WHITE)
        self.font = FONT
        self.game_mode = None
        self.field_size_in_blocks = (10, 10) # Размеры игрового поля: строки столбцы
        self.ship_config = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]  # Базовая конфигурация кораблей
        self.temp_ship_counts = [0, 0, 0, 0]  # Для временного хранения количества кораблей (4,3,2,1 палубные)
        self.plus_buttons = []  # Для хранения прямоугольников кнопок "+"
        self.minus_buttons = []  # Для хранения прямоугольников кнопок "-"
        self.error_message = None
        self.error_time = 0
        self.number_free_cells = self.field_size_in_blocks[0] * self.field_size_in_blocks[1]
        self.ship_cell_requirements = {4: 18, 3: 13, 2: 9, 1: 5} #значения для каждого типа придуманы не мной и вроде работают

    def draw_text(self, text, x, y):
        text_surface = self.font.render(text, False, BLACK)
        self.screen.blit(text_surface, (x, y))

    def run(self):
        running = True
        while running:
            self.screen.fill(WHITE)
            self.draw_text('1. Play vs Weak AI', 100, 100)
            self.draw_text('2. Play vs Strong AI', 100, 150)
            self.draw_text('3. Play vs Friend', 100, 200)
            self.draw_text('4. Settings', 100, 250)
            self.draw_text('5. Exit', 100, 300)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.game_mode = 'weak_ai'
                        running = False
                    elif event.key == pygame.K_2:
                        self.game_mode = 'strong_ai'
                        running = False
                    elif event.key == pygame.K_3:
                        self.game_mode = 'friend'
                        running = False
                    elif event.key == pygame.K_4:
                        self.settings(0)
                    elif event.key == pygame.K_5:
                        running = False

        return self.game_mode, self.field_size_in_blocks, self.ship_config

    def settings(self, option):
        settings_running = True
        selected_option = option
        count_options = 3

        def draw_menu():
            options = [
                "Field Size (5-16): " + str(self.field_size_in_blocks[0]),
                "Ship Configuration",
                "Back to Main Menu"
            ]

            # Отрисовываем меню настроек
            for i, option in enumerate(options):
                color = BLACK if i == selected_option else (128, 128, 128)
                text_surface = self.font.render(option, False, color)
                self.screen.blit(text_surface, (100, 100 + i * 50))
            pygame.display.update()

        while settings_running:
            self.screen.fill(WHITE)
            draw_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    settings_running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % count_options
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % count_options
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:
                            self.change_field_size()
                            draw_menu()
                        elif selected_option == 1:
                            self.configure_ships()
                            draw_menu()
                        elif selected_option == 2:
                            settings_running = False
                    elif event.key == pygame.K_ESCAPE:
                        settings_running = False

    def change_field_size(self):
        new_size = self.get_user_input("Enter field size (6-16): ")
        if new_size:
            new_size = int(new_size)
            if 6 <= new_size <= 16:
                self.field_size_in_blocks = (new_size, new_size)
                self.number_free_cells = new_size * new_size
                self.ship_config = [1]
                self.temp_ship_counts = [0, 0, 0, 1]

    def configure_ships(self):
        # Инициализируем временные счетчики на основе текущей конфигурации
        self.temp_ship_counts = [0, 0, 0, 0]  # [4-палубные, 3-палубные, 2-палубные, 1-палубные]
        for ship in self.ship_config:
            if ship == 4: self.temp_ship_counts[0] += 1
            elif ship == 3: self.temp_ship_counts[1] += 1
            elif ship == 2: self.temp_ship_counts[2] += 1
            elif ship == 1: self.temp_ship_counts[3] += 1

        # Рассчитываем количество занятых клеток
        occupied_cells = 0
        for size, count in zip([4, 3, 2, 1], self.temp_ship_counts):
            occupied_cells += count * self.ship_cell_requirements[size]
        self.number_free_cells = self.field_size_in_blocks[0] * self.field_size_in_blocks[1] - occupied_cells

        self.plus_buttons = []  # Очищаем список кнопок
        self.minus_buttons = []  # Очищаем список кнопок
        configuring = True

        while configuring:
            self.screen.fill(WHITE)

            # Рисуем заголовок
            title = self.font.render("Configure Ships", True, BLACK)
            self.screen.blit(title, (100, 50))

            # Отображение свободных клеток
            free_cells_text = self.font.render(f"Свободных клеток: {self.number_free_cells}", True, BLACK)
            self.screen.blit(free_cells_text, (400, 50))

            if hasattr(self, 'error_message') and pygame.time.get_ticks() - self.error_time < 5000:
                error_text = self.font.render(self.error_message, True, (255, 0, 0))
                self.screen.blit(error_text, (100, 80))

            # Рисуем список кораблей и кнопки
            ship_types = ["4-deck ship", "3-deck ship", "2-deck ship", "1-deck ship"]
            start_y = 100

            for i, (ship_type, count) in enumerate(zip(ship_types, self.temp_ship_counts)):
                # Рисуем тип корабля
                ship_text = self.font.render(ship_type, True, BLACK)
                self.screen.blit(ship_text, (100, start_y + i * 50))

                # Рисуем текущее количество
                count_text = self.font.render(str(count), True, BLACK)
                self.screen.blit(count_text, (250, start_y + i * 50))

                # Рисуем кнопку "-"
                minus_rect = pygame.Rect(300, start_y + i * 50, 30, 30)
                pygame.draw.rect(self.screen, BLACK, minus_rect, 2)
                minus_text = self.font.render("-", True, BLACK)
                self.screen.blit(minus_text, (310, start_y + i * 50))

                # Рисуем кнопку "+"
                plus_rect = pygame.Rect(350, start_y + i * 50, 30, 30)
                pygame.draw.rect(self.screen, BLACK, plus_rect, 2)
                plus_text = self.font.render("+", True, BLACK)
                self.screen.blit(plus_text, (360, start_y + i * 50))

                # Сохраняем прямоугольники кнопок
                if len(self.minus_buttons) <= i:
                    self.minus_buttons.append(minus_rect)
                    self.plus_buttons.append(plus_rect)
                else:
                    self.minus_buttons[i] = minus_rect
                    self.plus_buttons[i] = plus_rect

            # Рисуем кнопку подтверждения
            confirm_rect = pygame.Rect(100, 350, 200, 40)
            pygame.draw.rect(self.screen, BLACK, confirm_rect, 2)
            confirm_text = self.font.render("Confirm", True, BLACK)
            self.screen.blit(confirm_text, (180, 360))

            # Рисуем кнопку сброса
            reset_rect = pygame.Rect(100, 400, 200, 40)
            pygame.draw.rect(self.screen, BLACK, reset_rect, 2)
            reset_text = self.font.render("Reset to Default", True, BLACK)
            self.screen.blit(reset_text, (140, 410))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    configuring = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    # # Обработка кнопок +
                    # for i, button_rect in enumerate(self.plus_buttons):
                    #     if button_rect.collidepoint(pos):
                    #         if self.is_can_place(4 - i):
                    #             self.temp_ship_counts[i] += 1
                    #         else:
                    #             self.error_message = "Еще один такой корабль не поместится на поле"
                    #             self.error_time = pygame.time.get_ticks()

                    # Обработка кнопок +
                    for i, button_rect in enumerate(self.plus_buttons):
                        if button_rect.collidepoint(pos):
                            ship_size = 4 - i  # 4, 3, 2 или 1
                            if self.is_can_place(ship_size):
                                self.temp_ship_counts[i] += 1

                    # Обработка кнопок -
                    for i, button_rect in enumerate(self.minus_buttons):
                        if button_rect.collidepoint(pos) and self.temp_ship_counts[i] > 0:
                            ship_size = 4 - i
                            self.temp_ship_counts[i] -= 1
                            # Возвращаем клетки при удалении корабля
                            self.number_free_cells += self.ship_cell_requirements[ship_size]

                    # Проверяем нажатие на кнопку подтверждения
                    if confirm_rect.collidepoint(pos):
                        # Формируем новую конфигурацию кораблей
                        new_config = []
                        for i, count in enumerate(self.temp_ship_counts):
                            ship_size = 4 - i  # 4, 3, 2, 1
                            new_config.extend([ship_size] * count)
                        self.ship_config = new_config
                        configuring = False

                    # Проверяем нажатие на кнопку сброса
                    if reset_rect.collidepoint(pos):
                        self.temp_ship_counts = [0, 0, 0, 1]
                        self.number_free_cells = self.field_size_in_blocks[0] * self.field_size_in_blocks[1] - \
                                                 self.ship_cell_requirements[1]

    def is_can_place(self, ship_size):
        """
        Проверяет, можно ли добавить еще один корабль указанного размера
        ship_size: размер корабля (4, 3, 2 или 1)
        Возвращает True/False
        """
        if self.number_free_cells <= 0:
            self.error_message = "Еще один такой корабль не поместится на поле"
            self.error_time = pygame.time.get_ticks()
            return False
        required_cells = self.ship_cell_requirements.get(ship_size, 0)
        if required_cells <= self.number_free_cells:
            self.number_free_cells -= required_cells
            return True
        else:
            self.error_message = "Еще один такой корабль не поместится на поле"
            self.error_time = pygame.time.get_ticks()
            return False

    def get_user_input(self, prompt):
        input_box = pygame.Rect(100, 200, 140, 32)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False
        text = ''
        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            done = True
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            self.screen.fill(WHITE)
            txt_surface = self.font.render(prompt + text, True, color)
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            self.screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(self.screen, color, input_box, 2)
            pygame.display.update()

        return text