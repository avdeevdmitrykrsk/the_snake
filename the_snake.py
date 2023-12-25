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

from random import choice, randint

import pygame

pygame.init()

# Константы для размеров
SCREEN_WIDTH: int = 1240    # Размер окна по координате X
SCREEN_HEIGHT: int = 800    # Размер окна по координате Y
GRID_SIZE: int = 20    # Размер 1 клетки
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE
START_POS_WIDTH: int = SCREEN_WIDTH // 2    # Начальная позиция по X
START_POS_HEIGHT: int = SCREEN_HEIGHT // 2    # Начальная позиция по Y

# Направления движения
UP: tuple = (0, -1)
DOWN: tuple = (0, 1)
LEFT: tuple = (-1, 0)
RIGHT: tuple = (1, 0)
U_L_DIAG: tuple = (-1, -1)
U_R_DIAG: tuple = (1, -1)
D_L_DIAG: tuple = (-1, 1)
D_R_DIAG: tuple = (1, 1)

# Длины тела змейки
SNAKE_DEFAULT_LENGTH: int = 1    # Базовая
SNAKE_CHANGE_LENGTH: int = 1    # Изменение длины

NEW_SNAKE_POS: int = -20

# Цвета
BOARD_BACKGROUND_COLOR: tuple = (0, 234, 242)
APPLE_BODY_COLOR: tuple = (255, 0, 0)
APPLE_AROUND_COLOR: tuple = (244, 255, 0)
WRONG_APPLE_COLOR: tuple = (0, 0, 0)
WRONG_APPLE_AROUND_COLOR: tuple = (244, 255, 0)
SNAKE_BODY_COLOR: tuple = (0, 219, 0)
SNAKE_AROUND_COLOR: tuple = (0, 0, 0)

# pygame_rect толщина линиий объектов
APPLE_LINE_THICKNESS: int = 3
SNAKE_HEAD_LINE_THICKNESS: int = 4
SNAKE_BODY_LINE_THICKNESS: int = 1

# Скорость движения змейки
SPEED: int = 13

# Настройка игрового окна
START_BOARD_X: int = 0
START_BOARD_Y: int = 0
WINDOW_TITLE: str = 'Змейка'
DISPLAY_MODE: int = 0    # Режим отображения экрана
COLOR_DEPTH_BIT: int = 32    # Глубина цвета экрана
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), DISPLAY_MODE, COLOR_DEPTH_BIT
)
screen.fill(BOARD_BACKGROUND_COLOR)

# Заголовок окна игрового поля
pygame.display.set_caption(WINDOW_TITLE)

# Настройка времени
clock = pygame.time.Clock()


class GameObject:
    """Родительский класс для Snake и Apple."""

    def __init__(self):
        self.position = (START_POS_WIDTH, START_POS_HEIGHT)
        self.body_color = None

    def draw(self):
        """
        Метод для отрисовки объектов.
        Для переопределения в дочерних классах.
        """
        pass

    def draw_cells(self, surface, color: tuple) -> None:
        """Метод отрисовывает яблоки в игре."""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, color, rect, APPLE_LINE_THICKNESS)

    def randomize_position(self) -> None:
        """Устанавливает случайную позицию для яблок в игре."""
        self.position = (
            (
                round(randint(
                    START_BOARD_X, SCREEN_WIDTH - 20
                ) / GRID_SIZE) * GRID_SIZE,
                round(randint(
                    START_BOARD_Y, SCREEN_HEIGHT - 20
                ) / GRID_SIZE) * GRID_SIZE,
            )
        )

        if self.position in Snake.available_positions:
            screen.fill(BOARD_BACKGROUND_COLOR)
            self.randomize_position


class Apple(GameObject):
    """
    На основе этого класса создаётся яблоко в игре.
    Если змейка поднимает яблоко, её длина увеличивается на 1.
    """

    def __init__(self):
        super().__init__()
        self.body_color = APPLE_BODY_COLOR
        self.position = None
        self.randomize_position()

    def draw_cells(self):
        """Отрисовывает яблоко в игре."""
        super().draw_cells(screen, APPLE_AROUND_COLOR)


class WrongApple(GameObject):
    """
    На основе этого класса создаётся гнилое яблоко,
    при съедании которого змейка уменьшает свою длину на 1.
    """

    def __init__(self):
        super().__init__()
        self.body_color = WRONG_APPLE_COLOR
        self.position = None
        self.randomize_position()

    def draw_cells(self):
        """Отрисовывает гнилое яблоко в игре."""
        super().draw_cells(screen, WRONG_APPLE_AROUND_COLOR)


class Snake(GameObject):
    """На основе этого класса создаётся змейка в игре."""

    available_positions: list = []

    def __init__(self):
        super().__init__()
        self.length = None
        self.positions = None
        self.direction = None
        self.last = None
        self.next_direction = None
        self.last = None
        self.body_color = SNAKE_BODY_COLOR
        self.reset()

    def update_direction(self) -> None:
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self, apple, *wr_apples) -> None:
        """Метод отвечает за обновление положения змейки в игре."""
        self.head = self.get_head_position(self.positions)
        self.last = self.positions[-1]
        Snake.available_positions.append(self.positions)

        self.cross_board_check()
        self.check_and_set_direction()
        self.check_collision(self, apple, wr_apples)

        while len(self.positions) > self.length:
            self.positions.pop(-1)

        if self.length == 0:
            self.reset()

    def draw_cells(self, surface):
        """Метод отрисовывает змейку и затирает последний сегмент."""
        for position in self.positions:
            rect = (
                pygame.Rect(
                    (position[0], position[1]), (GRID_SIZE, GRID_SIZE)
                )
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(
                surface, BOARD_BACKGROUND_COLOR,
                rect, SNAKE_BODY_LINE_THICKNESS,
            )

        head = self.positions[0]
        head_rect = pygame.Rect((head[0], head[1]), (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(
            surface, SNAKE_AROUND_COLOR, head_rect, SNAKE_HEAD_LINE_THICKNESS
        )
        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    @staticmethod
    def get_head_position(positions) -> tuple:
        """Возвращает текущее положение головы змейки."""
        return positions[0]

    def reset(self) -> None:
        """
        Функция начинает игру сначала,
        в случае столкновения змейки с собой.
        """
        directions = (UP, DOWN, LEFT, RIGHT)
        self.length = SNAKE_DEFAULT_LENGTH
        self.positions = [self.position]
        self.direction = choice(directions)
        self.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)

    def cross_board_check(self):
        """
        Метод проверки выхода змейки за пределы экрана
        и установки позиции с обратной стороны экрана.
        """
        if self.head[0] >= SCREEN_WIDTH:
            self.head = (NEW_SNAKE_POS, self.head[1])
        elif self.head[1] >= SCREEN_HEIGHT:
            self.head = (self.head[0], START_BOARD_Y)
        elif self.head[0] < START_BOARD_X:
            self.head = (SCREEN_WIDTH, self.head[1])
        elif self.head[1] < START_BOARD_Y:
            self.head = (self.head[0], SCREEN_HEIGHT)

    def check_and_set_direction(self) -> None:
        """
        Функция задаёт напрвление движения
        змейки исходя из нажатой клавиши.
        """
        if self.direction is UP:
            self.positions.insert(
                0, (self.head[0], self.head[1] - GRID_SIZE)
            )
        elif self.direction is RIGHT:
            self.positions.insert(
                0, (self.head[0] + GRID_SIZE, self.head[1])
            )
        elif self.direction is DOWN:
            self.positions.insert(
                0, (self.head[0], self.head[1] + GRID_SIZE)
            )
        elif self.direction is LEFT:
            self.positions.insert(
                0, (self.head[0] - GRID_SIZE, self.head[1])
            )
        # elif self.direction is U_L_DIAG:
        #     self.positions.insert(
        #         0, (self.head[0] - GRID_SIZE, self.head[1] - GRID_SIZE)
        #     )
        # elif self.direction is U_R_DIAG:
        #     self.positions.insert(
        #         0, (self.head[0] + GRID_SIZE, self.head[1] - GRID_SIZE)
        #     )
        # elif self.direction is D_L_DIAG:
        #     self.positions.insert(
        #         0, (self.head[0] - GRID_SIZE, self.head[1] + GRID_SIZE)
        #     )
        # elif self.direction is D_R_DIAG:
        #     self.positions.insert(
        #         0, (self.head[0] + GRID_SIZE, self.head[1] + GRID_SIZE)
        #     )

    @staticmethod
    def check_collision(snake, apple, wr_apples) -> None:
        """
        Функци проверяет было ли столкновение(коллизия) головы змейки с её
        телом, с яблоком или с гнилым яблоком.
        """
        for wr_apple in wr_apples:
            for match in snake.positions[2:]:
                if snake.positions[0] == match and snake.positions[0] == match:
                    snake.reset()
            if snake.positions[0] == apple.position:
                snake.length += SNAKE_CHANGE_LENGTH
                apple.randomize_position()
            elif apple.position in snake.positions:
                apple.randomize_position()
            elif snake.positions[0] == wr_apple.position:
                snake.length -= SNAKE_CHANGE_LENGTH
                screen.fill(BOARD_BACKGROUND_COLOR)
                wr_apple.randomize_position()
            elif wr_apple.position in snake.positions:
                apple.randomize_position()


full_directions: dict = {

    'One_direction': {
        (pygame.K_UP, UP): DOWN,
        (pygame.K_DOWN, DOWN): UP,
        (pygame.K_LEFT, LEFT): RIGHT,
        (pygame.K_RIGHT, RIGHT): LEFT,
    },

    # 'Diag_direction': {
    #     ((pygame.K_UP, pygame.K_LEFT), U_L_DIAG): D_R_DIAG,
    #     ((pygame.K_UP, pygame.K_RIGHT), U_R_DIAG): D_L_DIAG,
    #     ((pygame.K_DOWN, pygame.K_LEFT), D_L_DIAG): U_R_DIAG,
    #     ((pygame.K_DOWN, pygame.K_RIGHT), D_R_DIAG): U_L_DIAG,
    # }
}

DIAG_LIST: list = []

game_pause = False


def handle_keys(game_object) -> None:
    """Функция обработки действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN and event.key != pygame.K_p:
            DIAG_LIST.append(event.key)
            # if len(DIAG_LIST) == 2:
            #     for direction, value\
            #             in full_directions['Diag_direction'].items():
            #         if DIAG_LIST[0] in direction[0]\
            #                 and DIAG_LIST[1] in direction[0]\
            #                 and game_object.direction != value:
            #             game_object.direction = direction[1]
            # else:
            for direction, value\
                    in full_directions['One_direction'].items():
                if event.key in direction\
                        and game_object.direction != value:
                    game_object.direction = direction[1]
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            global game_pause
            game_pause = not game_pause
            if game_pause:
                pygame.time.wait(300)
        elif event.type == pygame.KEYUP and event.key != pygame.K_p:
            DIAG_LIST.pop(0)


def main() -> None:
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
        apple.draw_cells()
        wr_apple_1.draw_cells()
        wr_apple_2.draw_cells()
        snake.draw_cells(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()
