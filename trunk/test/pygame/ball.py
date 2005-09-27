import time
import sys, pygame

from bouncingball import BouncingBall

pygame.init()

size = width, height = 400, 300
black = 0, 0, 0
nb_balls = 10

screen = pygame.display.set_mode(size)
balls = [BouncingBall(screen) for i in range(nb_balls)]

count = 0
t1 = time.time()
finished = False

while not finished:
    screen.fill(black)

    for ball in balls:
        ball.animate()
        ball.draw()

    pygame.display.flip()

    count += 1
    if not (count % 100):
        print count

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True


t2 = time.time()
dt = t2 - t1
print "Average FPS = %f" % (count / float(dt))
