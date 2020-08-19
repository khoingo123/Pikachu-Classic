import pygame
pygame.init()
pygame.display.set_mode((0,0),pygame.FULLSCREEN)
width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
print(width, height)