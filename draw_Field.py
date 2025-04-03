import pygame

pygame.init()
pygame.display.set_caption("Морской бой")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Константы
BLOCK_SIZE = 30
LEFT_RIGHT_MARGIN = 50
UPPER_MARGIN = 40
FONT_SIZE = int(BLOCK_SIZE / 1.5)
FONT = pygame.font.SysFont('notosans', FONT_SIZE)


class draw_Field:
    def __init__(self, field_size=(10, 10)):
        self.field_size = field_size
        # Динамический расчет размера окна
        self.screen_width = LEFT_RIGHT_MARGIN * 2 + field_size[1] * BLOCK_SIZE * 2 + 10 * BLOCK_SIZE
        self.screen_height = UPPER_MARGIN + field_size[0] * BLOCK_SIZE + 100
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen.fill(WHITE)

    def get_screen_size(self):
        return self.screen_width, self.screen_height

    def draw_field_grid(self):
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P'][:self.field_size[1]]

        # Отрисовка сетки для обоих полей
        for field in range(2):
            offset_x = LEFT_RIGHT_MARGIN + (self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE) * field

            # Горизонтальные и вертикальные линии
            for i in range(self.field_size[0] + 1):
                pygame.draw.line(self.screen, BLACK,
                                 (offset_x, UPPER_MARGIN + i * BLOCK_SIZE),
                                 (offset_x + self.field_size[1] * BLOCK_SIZE, UPPER_MARGIN + i * BLOCK_SIZE), 1)

            for i in range(self.field_size[1] + 1):
                pygame.draw.line(self.screen, BLACK,
                                 (offset_x + i * BLOCK_SIZE, UPPER_MARGIN),
                                 (offset_x + i * BLOCK_SIZE, UPPER_MARGIN + self.field_size[0] * BLOCK_SIZE), 1)

            # Разметка координат
            for i in range(self.field_size[0]):
                num_ver = FONT.render(str(i + 1), True, BLACK)
                self.screen.blit(num_ver, (offset_x - BLOCK_SIZE // 2 - num_ver.get_width() // 2,
                                           UPPER_MARGIN + i * BLOCK_SIZE + (
                                                       BLOCK_SIZE // 2 - num_ver.get_height() // 2)))

            for i in range(self.field_size[1]):
                letter = FONT.render(letters[i], True, BLACK)
                self.screen.blit(letter, (offset_x + i * BLOCK_SIZE + (BLOCK_SIZE // 2 - letter.get_width() // 2),
                                          UPPER_MARGIN + self.field_size[0] * BLOCK_SIZE + 10))

    def sign_grids(self):
        player1 = FONT.render("Player 1", True, BLACK)
        player2 = FONT.render("Player 2", True, BLACK)

        # Подписи для обоих полей
        self.screen.blit(player1, (LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE // 2 - player1.get_width() // 2,
                                   UPPER_MARGIN - BLOCK_SIZE // 2 - FONT_SIZE))

        offset = LEFT_RIGHT_MARGIN + self.field_size[1] * BLOCK_SIZE + 10 * BLOCK_SIZE
        self.screen.blit(player2, (offset + self.field_size[1] * BLOCK_SIZE // 2 - player2.get_width() // 2,
                                   UPPER_MARGIN - BLOCK_SIZE // 2 - FONT_SIZE))

    def draw_ships(self, ships, offset_x):
        for ship in ships:
            for cell in ship.cells:
                row, col = cell
                rect_x = offset_x + (col - 1) * BLOCK_SIZE
                rect_y = UPPER_MARGIN + (row - 1) * BLOCK_SIZE
                pygame.draw.rect(self.screen, BLACK, (rect_x, rect_y, BLOCK_SIZE, BLOCK_SIZE), 3)

    def draw_after_shot(self, fired_block, offset_x):
        row, col = fired_block
        x = offset_x + (col - 1) * BLOCK_SIZE
        y = UPPER_MARGIN + (row - 1) * BLOCK_SIZE

        # Рисуем крестик
        pygame.draw.line(self.screen, BLACK, (x, y), (x + BLOCK_SIZE, y + BLOCK_SIZE), 2)
        pygame.draw.line(self.screen, BLACK, (x + BLOCK_SIZE, y), (x, y + BLOCK_SIZE), 2)

    def draw_destroyed_area(self, ship, offset_x):
        for cell in ship.cells:
            row, col = cell
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 1 <= row + i <= self.field_size[0] and 1 <= col + j <= self.field_size[1]:
                        x = offset_x + (col + j - 1) * BLOCK_SIZE
                        y = UPPER_MARGIN + (row + i - 1) * BLOCK_SIZE
                        pygame.draw.line(self.screen, BLACK, (x, y), (x + BLOCK_SIZE, y + BLOCK_SIZE), 1)
                        pygame.draw.line(self.screen, BLACK, (x + BLOCK_SIZE, y), (x, y + BLOCK_SIZE), 1)