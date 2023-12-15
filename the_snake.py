"""
Данная программа выполнена по ТЗ, а также добавлено:
Изменена палитра цветов, размеры экрана,
добавлен новый класс _class WrongApple,
который добавляет на игровое поле Неправильное/гнилое яблоко,
если подобрать которое, длина змейки уменьшится на 1.
Также в игру добавлена проверка на состояние Победа/Поражение.
Если длина змейки будет равна 0, отрисуется экран "Поражение",
если длина змейки будет равна 50, отрисуется экран "Победа".
"""

import pygame
from random import choice

pygame.init()

# Константы для размеров
SCREEN_WIDTH, SCREEN_HEIGHT = 1240, 800
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета фона - черный
BOARD_BACKGROUND_COLOR = (0, 234, 242)

# Скорость движения змейки
SPEED = 13

# Настройка игрового окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
screen.fill(BOARD_BACKGROUND_COLOR)

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
    """
    На основе этого класса создаётся яблоко в игре.
    Если змейка поднимает яблоко, её длина увеличивается на 1.
    """

    def __init__(self):
        GameObject.__init__(self)
        self.body_color = (255, 0, 0)
        self.position = None
        Apple.randomize_position(self)

    def randomize_position(self):
        """Устанавливает случайную позицию для яблока в игре."""
        self.position = (
            choice([_ for _ in range(0, 1240) if _ % 40 == 0]),
            choice([_ for _ in range(0, 800) if _ % 40 == 0])
        )

    def draw(self, surface):
        """Метод отрисовывает яблоко в игре."""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, (244, 255, 0), rect, 3)


class WrongApple(GameObject):
    """
    На основе этого класса создаётся гнилое яблоко,
    при съедании которого змейка уменьшает свою длину на 1.
    """

    def __init__(self):
        GameObject.__init__(self)
        self.body_color = (0, 0, 0)
        self.position = None
        WrongApple.randomize_position(self)

    def randomize_position(self):
        """Устанавливает случайную позицию для гнилого яблока в игре."""
        self.position = (
            choice([_ for _ in range(0, 1240) if _ % 40 == 0]),
            choice([_ for _ in range(0, 800) if _ % 40 == 0])
        )

    def draw(self, surface):
        """Метод отрисовывает яблоко в игре."""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, (244, 255, 0), rect, 3)


class Snake(GameObject):
    """На основе этого класса создаётся змейка в игре."""

    def __init__(self):
        GameObject.__init__(self)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = (0, 219, 0)
        self.last = None

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self, apple, *wr_apples):
        """Метод отвечает за обновление положения змейки в игре."""
        self.head = Snake.get_head_position(self.positions)
        self.last = self.positions[-1]

        if self.head[0] >= SCREEN_WIDTH:
            self.head = (-20, self.head[1])
        elif self.head[1] >= SCREEN_HEIGHT:
            self.head = (self.head[0], 0)
        elif self.head[0] < 0:
            self.head = (1240, self.head[1])
        elif self.head[1] < 0:
            self.head = (self.head[0], 800)

        Snake.check_and_set_direction(self)
        Snake.check_collision(self, apple, wr_apples)

        while len(self.positions) > self.length:
            self.positions.pop(-1)

    def draw(self, surface):
        """Метод отрисовывает змейку и затирает последний сегмент."""
        for position in self.positions:
            rect = (
                pygame.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, (93, 216, 228), rect, 1)

        head = self.positions[0]
        head_rect = pygame.Rect((head[0], head[1]), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, (0, 0, 0), head_rect, 4)
        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def check_win_lose(self):
        """Метод проверки победы или поражения в игре."""
        if self.length == 50:
            Snake.draw_win_screen(self)
            pygame.display.update()
            pygame.time.wait(3000)
            pygame.quit()
        elif self.length < 1:
            Snake.draw_loose_screen(self)
            pygame.display.update()
            pygame.time.wait(3000)
            pygame.quit()

    def draw_win_screen(self):
        """Метод отрисовывает экран победы в игре."""
        win_src = pygame.image.load('win.png')
        screen.blit(win_src, (0, 0))

    def draw_loose_screen(self):
        """Метод отрисовывает экран поражения в игре."""
        loose_src = pygame.image.load('loose.png')
        screen.blit(loose_src, (0, 0))

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

    @staticmethod
    def check_and_set_direction(value):
        """
        Функция задаёт напрвление движения
        змейки исходя из нажатой клавиши.
        """
        if value.direction is UP:
            value.positions.insert(
                0, (value.head[0], value.head[1] - GRID_SIZE)
            )
        elif value.direction is RIGHT:
            value.positions.insert(
                0, (value.head[0] + GRID_SIZE, value.head[1])
            )
        elif value.direction is DOWN:
            value.positions.insert(
                0, (value.head[0], value.head[1] + GRID_SIZE)
            )
        elif value.direction is LEFT:
            value.positions.insert(
                0, (value.head[0] - GRID_SIZE, value.head[1])
            )

    @staticmethod
    def check_collision(snake, apple, wr_apples):
        """
        Функци проверяет было ли столкновение(коллизия) головы змейки с её
        телом, с яблоком или с гнилым яблоком.
        """
        for wr_apple in wr_apples:
            for match in snake.positions[2:]:
                if snake.positions[0] == match and snake.positions[0] == match:
                    Snake.reset(snake)
            if snake.positions[0] == apple.position:
                snake.length += 1
                apple.randomize_position()
            elif snake.positions[0] == wr_apple.position:
                snake.length -= 1
                screen.fill(BOARD_BACKGROUND_COLOR)
                wr_apple.randomize_position()


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
    wr_apple_1 = WrongApple()
    wr_apple_2 = WrongApple()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move(apple, wr_apple_1, wr_apple_2)
        snake.check_win_lose()
        apple.draw(screen)
        wr_apple_1.draw(screen)
        wr_apple_2.draw(screen)
        snake.draw(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()
