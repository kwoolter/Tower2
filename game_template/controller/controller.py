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
        self.game = model.Game("MyGame")
        self.view = view.MainFrame()

        self.game.initialise()
        self.view.initialise(self.game)

        new_player = model.Player("Keith")
        self.game.add_player(new_player)

        new_player = model.Player("Jack")
        self.game.add_player(new_player)

    def run(self):

        os.environ["SDL_VIDEO_CENTERED"] = "1"

        FPSCLOCK = pygame.time.Clock()

        pygame.time.set_timer(USEREVENT + 1, 1000)

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

            FPSCLOCK.tick(30)

            self.view.draw()
            self.view.update()

        self.end()

        pygame.quit()
        sys.exit()

    def end(self):
        self.view.end()
        self.game.end()
