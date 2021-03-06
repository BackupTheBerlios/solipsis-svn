
import random
import pygame

ball_image = None

def load_ball():
    global ball_image
    if ball_image is None:
        ball_image = pygame.image.load("ball.gif")
#         ball_image = pygame.image.load("toucan.png")
    return ball_image


class BouncingBall(object):
    max_speed = 2

    def __init__(self, target, image_path=None):
        self.target = target
        if image_path is None:
            self.image = load_ball()
        else:
            self.image = pygame.image.load(image_path)
        self.image = self.image.convert_alpha(self.target)
        self.image.set_alpha(255, pygame.RLEACCEL)
#         print self.target.get_masks(), self.image.get_masks()
        self.x, self.y = 0, 0
        self.vx, self.vy = [random.uniform(-self.max_speed, self.max_speed) for i in range(2)]

    def animate(self):
        width, height = self.image.get_size()
        lim_x, lim_y = self.target.get_size()
        self.x = self.x + self.vx
        self.y = self.y + self.vy
        if self.x < 0 or self.x + width > lim_x:
            self.vx = -self.vx
        if self.y < 0 or self.y + height > lim_y:
            self.vy = -self.vy

    def draw(self):
        self.target.blit(self.image, (self.x, self.y))

