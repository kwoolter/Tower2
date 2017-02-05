import os
import pygame
import sys
from pygame.locals import *

import game_template.model as model
import game_template.view as view


class Controller:

    INVENTORY = "Inventory"
    PLAYING = "Playing"
    SHOP = "Shop"

    KEY_INITIALISE = K_i
    KEY_PAUSE = K_ESCAPE
    KEY_START = K_SPACE
    KEY_GAME_OVER = K_BACKSPACE
    KEY_END = K_x
    KEY_INVENTORY = K_i
    KEY_SHOP = K_HOME

    def __init__(self):
        self.game = None
        self.view = None
        self._mode = None

    def initialise(self):

        self._mode = Controller.PLAYING

        self.game = model.Game("Adventure World")
        self.view = view.MainFrame(width=20*32, height=730)

        self.game.initialise()
        self.view.initialise(self.game)

        new_player = model.Player("Keith")
        self.game.add_player(new_player)

    @property
    def mode(self):
        controller_mode = self._mode

        if self.game.state == model.Game.SHOPPING:
            controller_mode = Controller.SHOP

        return controller_mode


    def run(self):

        os.environ["SDL_VIDEO_CENTERED"] = "1"

        FPSCLOCK = pygame.time.Clock()

        pygame.time.set_timer(USEREVENT + 1, 250)

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

                    # If we are in playing mode...
                    if self.mode == Controller.PLAYING:

                        if event.key == Controller.KEY_START:

                            try:
                                if self.game.state == model.Game.READY:
                                    self.game.start()
                                elif self.game.state == model.Game.GAME_OVER:
                                    self.initialise()
                            except Exception as err:
                                print(str(err))

                        elif event.key == Controller.KEY_PAUSE:
                            try:
                                self.game.pause()
                            except Exception as err:
                                print(str(err))

                        elif event.key == K_n:
                            try:
                                if self.game.state == model.Game.PLAYING:
                                    self.game.next_floor()
                            except Exception as err:
                                print(str(err))

                        elif event.key == K_l:
                            try:
                                if self.game.state == model.Game.PLAYING:
                                    self.game.next_level()
                            except Exception as err:
                                print(str(err))

                        elif event.key == Controller.KEY_INVENTORY:
                            try:
                                self.toggle_inventory_mode()

                            except Exception as err:
                                print(str(err))

                        elif event.key == Controller.KEY_SHOP:
                            try:
                                self.toggle_shop_mode()

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

                    # If we are in Inventory mode...
                    elif self.mode == Controller.INVENTORY:
                        if event.key in (Controller.KEY_INVENTORY, K_ESCAPE):
                            try:
                                self.toggle_inventory_mode()

                            except Exception as err:
                                print(str(err))

                        elif event.key in (K_UP, K_w):
                            self.view.inventory_manager.change_selection(-1)
                        elif event.key in (K_DOWN, K_s):
                            self.view.inventory_manager.change_selection(1)

                    # If we are in Shop mode...
                    elif self.mode == Controller.SHOP:
                        if event.key in (Controller.KEY_SHOP, K_ESCAPE):
                            try:
                                self.toggle_shop_mode()
                            except Exception as err:
                                print(str(err))
                        elif event.key in (K_UP, K_w):
                            self.view.shop_view.shop_keeper_inventory.change_selection(-1)
                        elif event.key in (K_DOWN, K_s):
                            self.view.shop_view.shop_keeper_inventory.change_selection(1)
                        elif event.key == K_RETURN:
                            try:
                                self.game.shop.buy_item(self.view.shop_view.shop_keeper_inventory.get_current_selection(), self.game.get_current_player())
                            except Exception as err:
                                print(str(err))

            FPSCLOCK.tick(30)

            self.view.draw()
            self.view.update()

        #Finish main game loop

        self.end()

        pygame.quit()
        sys.exit()

    def toggle_inventory_mode(self):

        if self.mode == Controller.PLAYING:
            self._mode = Controller.INVENTORY
        elif self.mode == Controller.INVENTORY:
            self._mode = Controller.PLAYING

        self.game.pause()
        self.view.toggle_inventory_view(self.game.get_current_player())

    def toggle_shop_mode(self):

        if self.game.state == model.Game.PLAYING:
            self.game.enter_shop()

        elif self.game.state == model.Game.SHOPPING:
            self.game.exit_shop()


    def end(self):
        self.view.end()
        self.game.end()
