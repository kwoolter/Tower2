import os
import pygame
import sys
from pygame.locals import *

import game_template.model as model
import game_template.view as view


class Controller:
    KEY_INITIALISE = K_i
    KEY_PAUSE = K_ESCAPE
    KEY_START = K_SPACE
    KEY_GAME_OVER = K_BACKSPACE
    KEY_END = K_x

    def __init__(self):
        self.game = None
        self.view = None

    def initialise(self):
        self.game = model.Game("Adventure World")
        self.view = view.MainFrame(width=20*32, height=730)

        self.game.initialise()
        self.view.initialise(self.game)

        new_player = model.Player("Keith")
        self.game.add_player(new_player)

        new_player = model.Player("Jack")
        self.game.add_player(new_player)

    def run(self):

        os.environ["SDL_VIDEO_CENTERED"] = "1"

        FPSCLOCK = pygame.time.Clock()

        pygame.time.set_timer(USEREVENT + 1, 500)

        loop = True

        # main game_template loop
        while loop == True:

            for event in pygame.event.get():
                if event.type == QUIT:
                    loop = False
                elif event.type == USEREVENT + 1:
                    try:
                        if self.game.state == model.Game.PLAYING:
                            self.game.tick()
                        self.view.tick()

                    except Exception as err:
                        print(str(err))
                elif event.type == KEYUP:

                    if event.key == Controller.KEY_INITIALISE:

                        try:
                            self.game.initialise()
                        except Exception as err:
                            print(str(err))

                    elif event.key == Controller.KEY_START:
                        try:
                            self.game.start()
                        except Exception as err:
                            print(str(err))

                    elif event.key == Controller.KEY_PAUSE:
                        try:
                            self.game.pause()
                        except Exception as err:
                            print(str(err))

                    elif event.key == K_n:
                        try:
                            self.game.next_floor()
                        except Exception as err:
                            print(str(err))

                    elif event.key == K_l:
                        try:
                            self.game.next_level()
                        except Exception as err:
                            print(str(err))

                    elif event.key == Controller.KEY_GAME_OVER:
                        try:
                            self.game.game_over()
                        except Exception as err:
                            print(str(err))

                    elif event.key == Controller.KEY_END:
                        try:
                            self.game.end()
                        except Exception as err:
                            print(str(err))

                    elif event.key in (K_UP, K_w):
                        self.game.move_player(0, -1)
                    elif event.key in (K_DOWN, K_s):
                        self.game.move_player(0, 1)
                    elif event.key in (K_LEFT, K_a):
                        self.game.move_player(-1, 0)
                    elif event.key in (K_RIGHT, K_d):
                        self.game.move_player(1, 0)

            FPSCLOCK.tick(30)

            self.view.draw()
            self.view.update()

        self.end()

        pygame.quit()
        sys.exit()

    def end(self):
        self.view.end()
        self.game.end()
