"""
import pygame
import sys

# 初始化 Pygame
pygame.init()

# 创建窗口和两个 Surface
screen = pygame.display.set_mode((400, 400))
source_surface = pygame.Surface((200, 200))
source_surface.fill((255, 0, 0))  # 红色的源 Surface
destination_surface = pygame.Surface((100, 100))
destination_surface.fill((173, 216, 230))
# 定义要绘制的区域 (area)
area = pygame.Rect(50, 50, 70, 70)  # 从源 Surface 中选择一个 100x100 的矩形区域

# 在目标 Surface 上绘制源 Surface 的一部分
destination_surface.blit(source_surface, (0, 0), area)

# 渲染目标 Surface 到屏幕
screen.blit(destination_surface, (150, 150))

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.flip()

# 退出 Pygame
pygame.quit()
sys.exit()
"""