from random import choice

import pygame

# Инициализация PyGame
pygame.init()

# Константы для размеров
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета фона - черный
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Скорость движения змейки
SPEED = 10

# Настройка игрового окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля
pygame.display.set_caption('Змейка')

# Настройка времени
clock = pygame.time.Clock()


class GameObject:
    """Родительский класс для Snake и Apple."""

    def __init__(self):
        self.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.body_color = None

    def draw(self):
        """
        Метод, который предназначен для переопределения
        в дочерних классах. Этот метод должен определять, как объект
        будет отрисовываться на экране.
        """
        pass


class Apple(GameObject):
    """На основе этого класса создаётся яблоко в игре."""

    def __init__(self):
        GameObject.__init__(self)
        self.body_color = (255, 0, 0)
        self.position = None
        Apple.randomize_position(self)

    def randomize_position(self):
        """Устанавливает случайную позицию для яблока в игре."""
        self.position = (
            choice([_ for _ in range(0, 640) if _ % 20 == 0]),
            choice([_ for _ in range(0, 480) if _ % 20 == 0])
        )

    def draw(self, surface):
        """Метод отрисовывает яблоко в игре."""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, (93, 216, 228), rect, 1)


class Snake(GameObject):
    """На основе этого класса создаётся змейка в игре."""

    def __init__(self):
        GameObject.__init__(self)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = (0, 255, 0)
        self.last = None

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Метод отвечает за обновление положения змейки в игре."""
        self.head = Snake.get_head_position(self.positions)
        self.last = self.positions[-1]

        if self.head[0] >= SCREEN_WIDTH:
            self.head = (-20, self.head[1])
        elif self.head[1] >= SCREEN_HEIGHT:
            self.head = (self.head[0], 0)
        elif self.head[0] < 0:
            self.head = (640, self.head[1])
        elif self.head[1] < 0:
            self.head = (self.head[0], 480)

        if self.direction is UP:
            self.positions.insert(0, (self.head[0], self.head[1] - GRID_SIZE))
        elif self.direction is RIGHT:
            self.positions.insert(0, (self.head[0] + GRID_SIZE, self.head[1]))
        elif self.direction is DOWN:
            self.positions.insert(0, (self.head[0], self.head[1] + GRID_SIZE))
        elif self.direction is LEFT:
            self.positions.insert(0, (self.head[0] - GRID_SIZE, self.head[1]))
        while len(self.positions) > self.length:
            self.positions.pop(-1)
        for match in self.positions[2:]:
            if self.positions[0] == match and self.positions[0] == match:
                Snake.reset(self)

    def draw(self, surface):
        """Функция отрисовывает змейку и затирает последний сегмент."""
        for position in self.positions[:-1]:
            rect = (
                pygame.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, (93, 216, 228), rect, 1)

        head = self.positions[0]
        head_rect = pygame.Rect((head[0], head[1]), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, (93, 216, 228), head_rect, 1)

        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    @staticmethod
    def get_head_position(positions):
        """Возвращает текущее положение головы змейки."""
        return positions[0]

    def reset(self):
        """
        Функция начинает игру сначала,
        в случае столкновения змейки с собой.
        """
        directions = (UP, DOWN, LEFT, RIGHT)
        self.direction = choice(directions)
        self.length = 1
        self.positions = [self.position]
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Функия с основной логикой игры."""
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.positions[0] == apple.position:
            snake.length += 1
            apple.randomize_position()

        apple.draw(screen)
        snake.draw(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()
