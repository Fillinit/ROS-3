import pygame
import zmq
import time
import math
import random

# Инициализация Pygame
pygame.init()

# Определение цветов
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Размеры экрана
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
SQUARE_SIZE = 50

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Combined")

# Позиция и скорость красного квадрата
red_square_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
RED_SQUARE_SPEED = 5

# Позиции остальных квадратов
square_positions = [
    [random.randint(0, SCREEN_WIDTH - SQUARE_SIZE), random.randint(0, SCREEN_HEIGHT - SQUARE_SIZE)],
    [random.randint(0, SCREEN_WIDTH - SQUARE_SIZE), random.randint(0, SCREEN_HEIGHT - SQUARE_SIZE)],
    [random.randint(0, SCREEN_WIDTH - SQUARE_SIZE), random.randint(0, SCREEN_HEIGHT - SQUARE_SIZE)]
]

# Цвета остальных квадратов
square_colors = [GREEN, YELLOW, BLUE]

# Настройка ZeroMQ
context = zmq.Context()
socket_pub = context.socket(zmq.PUB)
socket_pub.bind("tcp://*:5555")
socket_sub = context.socket(zmq.SUB)
socket_sub.connect("tcp://localhost:5555")
socket_sub.setsockopt_string(zmq.SUBSCRIBE, '')

# Параметры скорости
LINEAR_SPEED = 3
GREEN_SPEED = LINEAR_SPEED / 2
YELLOW_SPEED = GREEN_SPEED / 2
BLUE_SPEED = YELLOW_SPEED / 2 * 1.5
SPEEDS = [GREEN_SPEED, YELLOW_SPEED, BLUE_SPEED]

# Функция для вычисления направления движения
def compute_velocity(pos, target, speed):
    dx = target[0] - pos[0]
    dy = target[1] - pos[1]
    distance = math.hypot(dx, dy)
    if distance == 0:
        return 0, 0
    vx = (dx / distance) * speed
    vy = (dy / distance) * speed
    return vx, vy

# Основной игровой цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Получение состояния клавиш
    keys = pygame.key.get_pressed()

    # Обновление позиции красного квадрата
    if keys[pygame.K_LEFT]:
        red_square_pos[0] -= RED_SQUARE_SPEED
    if keys[pygame.K_RIGHT]:
        red_square_pos[0] += RED_SQUARE_SPEED
    if keys[pygame.K_UP]:
        red_square_pos[1] -= RED_SQUARE_SPEED
    if keys[pygame.K_DOWN]:
        red_square_pos[1] += RED_SQUARE_SPEED

    # Ограничение перемещения по границам экрана
    red_square_pos[0] = max(0, min(red_square_pos[0], SCREEN_WIDTH - SQUARE_SIZE))
    red_square_pos[1] = max(0, min(red_square_pos[1], SCREEN_HEIGHT - SQUARE_SIZE))

    # Отправка позиции красного квадрата через ZeroMQ
    socket_pub.send_string(f"{red_square_pos[0]} {red_square_pos[1]}")

    # Получение позиции красного квадрата через ZeroMQ
    try:
        message = socket_sub.recv_string(flags=zmq.NOBLOCK)
        target_pos = list(map(int, message.split()))
    except zmq.Again:
        target_pos = red_square_pos

    # Обновление позиций остальных квадратов
    previous_pos = target_pos
    for i, pos in enumerate(square_positions):
        speed = SPEEDS[i]  # Использование соответствующей скорости для каждого квадрата
        vx, vy = compute_velocity(pos, previous_pos, speed)
        pos[0] += vx
        pos[1] += vy
        # Ограничение перемещения по границам экрана
        pos[0] = max(0, min(pos[0], SCREEN_WIDTH - SQUARE_SIZE))
        pos[1] = max(0, min(pos[1], SCREEN_HEIGHT - SQUARE_SIZE))
        previous_pos = pos

    # Очистка экрана
    screen.fill(WHITE)

    # Отрисовка остальных квадратов
    for pos, color in zip(square_positions, square_colors):
        pygame.draw.rect(screen, color, (*pos, SQUARE_SIZE, SQUARE_SIZE))

    # Отрисовка красного квадрата
    pygame.draw.rect(screen, RED, (*red_square_pos, SQUARE_SIZE, SQUARE_SIZE))

    # Обновление экрана
    pygame.display.flip()

    # Ограничение кадров
    pygame.time.Clock().tick(30)

# Завершение работы Pygame
pygame.quit()
