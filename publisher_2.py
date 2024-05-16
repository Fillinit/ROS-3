import pygame
import zmq
import time

# Инициализация Pygame
pygame.init()

# Определение цветов
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Размеры экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SQUARE_SIZE = 50

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Publisher")

# Позиция и скорость квадрата
square_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
SQUARE_SPEED = 5

# Настройка ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")

# Основной игровой цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Получение состояния клавиш
    keys = pygame.key.get_pressed()

    # Обновление позиции квадрата
    if keys[pygame.K_LEFT]:
        square_pos[0] -= SQUARE_SPEED
    if keys[pygame.K_RIGHT]:
        square_pos[0] += SQUARE_SPEED
    if keys[pygame.K_UP]:
        square_pos[1] -= SQUARE_SPEED
    if keys[pygame.K_DOWN]:
        square_pos[1] += SQUARE_SPEED

    # Ограничение перемещения по границам экрана
    square_pos[0] = max(0, min(square_pos[0], SCREEN_WIDTH - SQUARE_SIZE))
    square_pos[1] = max(0, min(square_pos[1], SCREEN_HEIGHT - SQUARE_SIZE))

    # Отправка позиции через ZeroMQ
    socket.send_string(f"{square_pos[0]} {square_pos[1]}")

    # Очистка экрана
    screen.fill(WHITE)

    # Отрисовка квадрата
    pygame.draw.rect(screen, RED, (*square_pos, SQUARE_SIZE, SQUARE_SIZE))

    # Обновление экрана
    pygame.display.flip()

    # Ограничение кадров
    pygame.time.Clock().tick(30)

# Завершение работы Pygame
pygame.quit()
