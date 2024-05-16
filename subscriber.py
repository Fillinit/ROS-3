import pygame
import zmq
import time
import math
import random  # Импортируем модуль random

# Инициализация Pygame
pygame.init()

# Определение цветов
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Размеры экрана (уменьшенные)
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
SQUARE_SIZE = 50

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Subscriber")

# Позиции квадратов
square_positions = [
    [random.randint(0, SCREEN_WIDTH - SQUARE_SIZE), random.randint(0, SCREEN_HEIGHT - SQUARE_SIZE)],
    [random.randint(0, SCREEN_WIDTH - SQUARE_SIZE), random.randint(0, SCREEN_HEIGHT - SQUARE_SIZE)],
    [random.randint(0, SCREEN_WIDTH - SQUARE_SIZE), random.randint(0, SCREEN_HEIGHT - SQUARE_SIZE)]
]

# Цвета квадратов
square_colors = [GREEN, YELLOW, BLUE]

# Настройка ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt_string(zmq.SUBSCRIBE, '')

# Параметры скорости
LINEAR_SPEED = 3
SPEEDS = [LINEAR_SPEED / 2, LINEAR_SPEED / 4, LINEAR_SPEED / 8]  # Скорости для зеленого, желтого и синего


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
target_pos = [0, 0]
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    try:
        # Получение позиции красного квадрата через ZeroMQ
        message = socket.recv_string(flags=zmq.NOBLOCK)
        target_pos = list(map(int, message.split()))
    except zmq.Again:
        pass

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

    # Отрисовка квадратов
    for pos, color in zip(square_positions, square_colors):
        pygame.draw.rect(screen, color, (*pos, SQUARE_SIZE, SQUARE_SIZE))

    # Отрисовка красного квадрата (цель)
    pygame.draw.rect(screen, (255, 0, 0), (*target_pos, SQUARE_SIZE, SQUARE_SIZE))

    # Обновление экрана
    pygame.display.flip()

    # Ограничение кадров
    pygame.time.Clock().tick(30)

# Завершение работы Pygame
pygame.quit()
