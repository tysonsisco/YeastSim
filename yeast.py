# YEAST DOT PY
# A simple yeast simulator

import sys
import time
import random
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
from pymunk import Vec2d
import pymunk.pygame_util

width,height = 1000,1000

collision_types = {"yeast": 1, "glucose": 2, "other": 3}


def add_elem(space, pos, dir, name):
    size = random.randint(3,9)
    color = random.choice([THECOLORS['blue'],THECOLORS['purple'],THECOLORS['yellow'],THECOLORS['black']])
    if name == 'yeast':
        size = 15
        color = THECOLORS['green']
    elif name == 'glucose':
        size = 10
        color = THECOLORS['red']
    elif name == 'co2':
        size = 5
        color = THECOLORS['orange']
    elif name == 'ethanol':
        size = 5
        color = THECOLORS['pink']
    body = pymunk.Body(1, pymunk.inf)
    body.position = pos
    shape = pymunk.Circle(body, size)
    shape.color = color
    shape.elasticity = 1
    shape.collision_type = collision_types[name] if name in ('yeast', 'glucose') else collision_types['other']
    body.apply_impulse_at_local_point(Vec2d(dir))
    space.add(body, shape)

def main():
    v = 5 # velocity scale
    if len(sys.argv) != 4:
        print(sys.argv)
        sys.exit()
    ycount, gcount, ocount = [int(x) for x in sys.argv[1:]]


    pygame.init()
    screen = pygame.display.set_mode((width,height))
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont('Arial', 16)
    space = pymunk.Space()
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    # Walls around sim area
    corners = [(25,25),(25,975),(975,975),(975,25)]
    walls = []
    for i in range(4):
        walls.append(pymunk.Segment(space.static_body, corners[i], corners[(i+1)%4],2))
    for wall in walls:
        wall.color = THECOLORS['black']
        wall.elasticity = 1.0
    space.add(walls)
    
    # Add handler for yeast collision with glucose
    def glucose_collide(arbiter, space, data):
        glucose = arbiter.shapes[0]
        g_pos = glucose.body.position
        space.remove(glucose, glucose.body)
        add_elem(space, g_pos + (5,5), (random.randint(-5,5)*v, random.randint(-5,5)*v), 'co2')
        add_elem(space, g_pos - (5,5), (random.randint(-5,5)*v, random.randint(-5,5)*v), 'ethanol')
    h = space.add_collision_handler(collision_types['glucose'], collision_types['yeast'])
    h.separate = glucose_collide

    # Add yeast, macronutrients
    for i in range(ycount):
        add_elem(space, (random.randint(50,950),random.randint(50,950)), (random.randint(-5,5)*v, random.randint(-5,5)*v), 'yeast')
    for i in range(ocount):
        add_elem(space, (random.randint(50,950),random.randint(50,950)), (random.randint(-5,5)*v, random.randint(-5,5)*v), 'other')
    for i in range(gcount):
        add_elem(space, (random.randint(50,950),random.randint(50,950)), (random.randint(-5,5)*v, random.randint(-5,5)*v), 'glucose')
 

    # Run main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_q:
                running = False
        screen.fill(THECOLORS['white'])
        space.debug_draw(draw_options)
        fps = 60
        dt = 1./fps
        space.step(dt)

        # Print info, calculate and show statistics
        gcount = 0
        ycount = 0
        ocount = 0
        for element in space.shapes:
            if element.radius == 15:
                ycount += 1
            elif element.radius == 10:
                gcount += 1
            else:
                ocount += 1
        if gcount == 0:
            running = False

        screen.blit(font.render('Glucose count: {}'.format(gcount), 1, THECOLORS['black']), (60,60))

        pygame.display.flip()
        clock.tick(fps)

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print('lifespan: {}'.format(end - start))
