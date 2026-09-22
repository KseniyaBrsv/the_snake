import sys
from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Карта нажатий в повороты:
# код клавиши -> (новое_направление, запрещённое_направление)
TURNS = {
    pg.K_UP: (UP, DOWN),
    pg.K_DOWN: (DOWN, UP),
    pg.K_LEFT: (LEFT, RIGHT),
    pg.K_RIGHT: (RIGHT, LEFT),
    pg.K_w: (UP, DOWN),
    pg.K_s: (DOWN, UP),
    pg.K_a: (LEFT, RIGHT),
    pg.K_d: (RIGHT, LEFT),
}

# Позиция по умолчанию (центр экрана):
DEFAULT_POSITION = (
    SCREEN_WIDTH // 2,
    SCREEN_HEIGHT // 2,
)

# Базовые константы цветов:
BLACK = (0, 0, 0)
CYAN = (93, 216, 228)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Семантические цвета игровых объектов/фона:
BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = CYAN
APPLE_COLOR = RED
SNAKE_COLOR = GREEN

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=DEFAULT_POSITION, body_color=None):
        """Инициализирует позицию и цвет игрового объекта."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает игровой объект на экране."""
        raise NotImplementedError(
            'Метод draw не переопределён в классе '
            f'{self.__class__.__name__}'
        )

    def draw_cell(
        self,
        position,
        fill_color=None,
        border_color=BORDER_COLOR,
        border_width=1,
    ):
        """Отрисовывает одну клетку сетки по указанной позиции."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        fill = self.body_color if fill_color is None else fill_color
        if fill is not None:
            pg.draw.rect(screen, fill, rect)
        if border_color is not None and border_width > 0:
            pg.draw.rect(screen, border_color, rect, border_width)


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, position=DEFAULT_POSITION, body_color=APPLE_COLOR):
        """Инициализирует яблоко."""
        super().__init__(position, body_color)

    def randomize_position(self, occupied_positions=None):
        """Устанавливает яблоко в случайную свободную клетку игрового поля."""
        occupied_positions = occupied_positions or []

        free_positions = [
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x * GRID_SIZE, y * GRID_SIZE) not in occupied_positions
        ]

        if free_positions:
            self.position = choice(free_positions)

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, position=DEFAULT_POSITION, body_color=SNAKE_COLOR):
        """Инициализирует начальное состояние змейки."""
        super().__init__(position, body_color)
        self.reset(position)

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает змейку на одну клетку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction

        new_head = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, new_head)

        self.last = (
            self.positions.pop()
            if len(self.positions) > self.length
            else None
        )

    def draw(self):
        """Метод draw класса Snake"""
        self.draw_cell(self.get_head_position())
        if self.last:
            self.draw_cell(
                self.last,
                fill_color=BOARD_BACKGROUND_COLOR,
                border_color=None,
            )

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self, position=DEFAULT_POSITION):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            else:
                turn = TURNS.get(event.key)
                if turn:
                    new_direction, opposite = turn
                    if game_object.direction != opposite:
                        game_object.next_direction = new_direction


def main():
    """Запускает основной игровой цикл."""
    pg.init()
    screen.fill(BOARD_BACKGROUND_COLOR)

    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[4:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple.randomize_position(snake.positions)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
