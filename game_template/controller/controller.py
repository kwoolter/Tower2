import os
import pygame
import sys
from pygame.locals import *

import game_template.model as model
import game_template.view as view
import pickle
import logging

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
    KEY_ITEM1 = K_1
    KEY_ITEM2 = K_2
    KEY_ITEM3 = K_3
    KEY_ITEM4 = K_4
    KEY_HINT = K_h

    def __init__(self):
        self.game = None
        self.view = None
        self._mode = None

    def initialise(self):

        self._mode = Controller.PLAYING
        self._test_mode = False

        self.game = model.Game("Adventure World")
        self.view = view.MainFrame(width=20*32, height=730)

        self.game.initialise()
        self.view.initialise(self.game)

        new_player = model.Player("Player1")
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

                        elif event.key in (K_UP, K_w):
                            self.game.move_player(0, -1)
                        elif event.key in (K_DOWN, K_s):
                            self.game.move_player(0, 1)
                        elif event.key in (K_LEFT, K_a):
                            self.game.move_player(-1, 0)
                        elif event.key in (K_RIGHT, K_d):
                            self.game.move_player(1, 0)

                        elif event.key == Controller.KEY_PAUSE:
                            try:
                                self.game.pause()
                            except Exception as err:
                                print(str(err))

                        elif event.key == K_n and self._test_mode is True:
                            try:
                                if self.game.state == model.Game.PLAYING:
                                    self.game.next_floor()
                            except Exception as err:
                                print(str(err))

                        elif event.key == K_l and self._test_mode is True:
                            try:
                                if self.game.state == model.Game.PLAYING:
                                    self.game.next_level()
                            except Exception as err:
                                print(str(err))

                        elif event.key == Controller.KEY_HINT and self._test_mode is True:
                            self.game.hint()

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

                        elif event.key == Controller.KEY_ITEM1:
                            try:
                                self.game.use_item(self.game.get_current_player().equipment_slots[0])
                            except Exception as err:
                                print(str(err))

                        elif event.key == Controller.KEY_ITEM2:
                            try:
                                self.game.use_item(self.game.get_current_player().equipment_slots[1])
                            except Exception as err:
                                print(str(err))

                        elif event.key == Controller.KEY_ITEM3:
                            try:
                                self.game.use_item(self.game.get_current_player().equipment_slots[2])
                            except Exception as err:
                                print(str(err))

                        elif event.key == Controller.KEY_ITEM4:
                            try:
                                self.game.use_item(self.game.get_current_player().equipment_slots[3])
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

                        elif event.key == K_F8:
                            try:
                                if self.game.state == model.Game.PAUSED:
                                    self.save()
                                    print("Game saved")
                            except Exception as err:
                                print(str(err))

                        elif event.key == K_F9:
                            try:
                                if self.game.state == model.Game.PAUSED:
                                    self.load()
                                    print("Game loaded")
                            except Exception as err:
                                print(str(err))

                        elif event.key == K_F12:
                            try:

                                if self._test_mode is False:
                                    print("Test mode ON")
                                    self._test_mode = True
                                    model.Game.TARGET_RUNE_COUNT = 0
                                else:
                                    print("Test mode OFF")
                                    self._test_mode = False
                                    model.Game.TARGET_RUNE_COUNT = 4

                            except Exception as err:
                                print(str(err))

                        elif event.key == K_t:
                           self.game.talk()

                        elif event.key == K_p:
                            try:
                                if self.game.state == model.Game.READY:
                                    print("enter your name")
                                    width = 300
                                    main_rect = self.view.surface.get_rect()
                                    x = int(main_rect.centerx - width/2)
                                    enter_name = view.EnterNameView(self.view.surface, x=x,y=20, width=width, height=50)
                                    new_name = enter_name.run()
                                    print("Player name = '{0}'".format(new_name))
                                    if new_name != "":
                                        self.game.get_current_player().name = new_name

                            except Exception as err:
                                print(str(err))

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
                        elif event.key in (K_RIGHT, K_d):
                            self.game.get_current_player().next_armour()
                        elif event.key in (K_LEFT, K_a):
                            self.game.get_current_player().next_armour(next = False)

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
                                self.game.shop.buy_item(self.view.shop_view.shop_keeper_inventory.get_current_selection(),
                                                        self.game.get_current_player())
                            except Exception as err:
                                self.game.add_status_message(str(err))
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

    def save(self):

        self.game.save()


    def load(self):

        new_game = self.game.load()

        del self.game

        self.game = new_game
        self.view.initialise(self.game)

    def end(self):
        self.view.end()
        self.game.end()
