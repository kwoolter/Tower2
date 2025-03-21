import pygame
import game_template.model as model
import os
import game_template.utils as utils
import time, logging
from .graphics_utils import *
from pygame.locals import *
from copy import deepcopy
import math

class MainFrame(View):

    TITLE_HEIGHT = 80
    STATUS_HEIGHT = 50

    INVENTORY = "Inventory"
    PLAYING = "Playing"
    SHOPPING = "Shopping"

    RESOURCES_DIR = os.path.dirname(__file__) + "\\resources\\"

    def __init__(self, width: int = 600, height: int = 600):

        super(MainFrame, self).__init__()

        self.state = None
        self.game = None

        height = MainFrame.TITLE_HEIGHT + MainFrame.STATUS_HEIGHT + (32*20)
        playing_area_height = height - MainFrame.TITLE_HEIGHT - MainFrame.STATUS_HEIGHT
        playing_area_width = width

        self.surface = pygame.display.set_mode((width, height))

        self.title = TitleBar(width=width, height=MainFrame.TITLE_HEIGHT)
        self.status = StatusBar(width=width, height=MainFrame.STATUS_HEIGHT)

        self.game_view = GameView(width=playing_area_width, height=playing_area_height)
        self.game_ready = GameReadyView(width=playing_area_width, height=playing_area_height)
        self.game_over = GameOverView(width=playing_area_width, height=playing_area_height)
        self.inventory_manager = InventoryView(width=playing_area_width, height=playing_area_height)
        self.shop_view = ShopView(width=playing_area_width, height=playing_area_height)
        self.character_view = CharacterView(width=playing_area_width, height=playing_area_height)


    def initialise(self, game: model.Game):

        super(MainFrame, self).initialise()

        self.state = MainFrame.PLAYING
        self.game = game

        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.display.set_caption(self.game.name)
        filename = MainFrame.RESOURCES_DIR + "icon.png"

        try:
            image = pygame.image.load(filename)
            image = pygame.transform.scale(image, (32, 32))
            pygame.display.set_icon(image)
        except Exception as err:
            print(str(err))

        self.title.initialise(self.game)
        self.status.initialise(self.game)
        self.game_view.initialise(self.game)
        self.game_ready.initialise(self.game)
        self.game_over.initialise(self.game)
        self.character_view.initialise(self.game)
        self.shop_view.initialise(self.game)


    def toggle_inventory_view(self, player : model.Player = None):

        if self.state == MainFrame.PLAYING:
            self.inventory_manager.player = player
            self.state = MainFrame.INVENTORY
        elif self.state == MainFrame.INVENTORY:
            self.state = MainFrame.PLAYING

    def tick(self):

        super(MainFrame, self).tick()

        self.title.tick()
        self.status.tick()
        self.game_view.tick()
        self.game_ready.tick()
        self.game_over.tick()
        self.inventory_manager.tick()
        self.shop_view.tick()

    def draw(self):

        super(MainFrame, self).draw()

        self.surface.fill(Colours.BLACK)

        pane_rect = self.surface.get_rect()

        self.title.draw()
        self.status.draw()

        x = 0
        y = 0

        self.surface.blit(self.title.surface, (x, y))

        y += MainFrame.TITLE_HEIGHT

        x = 0
        y = pane_rect.bottom - MainFrame.STATUS_HEIGHT

        self.surface.blit(self.status.surface, (x, y))

        if self.game.state in (model.Game.PLAYING, model.Game.PAUSED):

            x = 0
            y = MainFrame.TITLE_HEIGHT

            if self.state == MainFrame.PLAYING:
                self.game_view.draw()
                self.surface.blit(self.game_view.surface, (x, y))

            elif self.state == MainFrame.INVENTORY:
                self.character_view.initialise(self.game)
                self.character_view.draw()
                self.surface.blit(self.character_view.surface, (x, y))

        elif self.game.state == model.Game.SHOPPING:
            x = 0
            y = MainFrame.TITLE_HEIGHT
            self.shop_view.initialise(self.game)
            self.shop_view.draw()
            self.surface.blit(self.shop_view.surface, (x, y))

        elif self.game.state == model.Game.READY:

            self.game_ready.draw()
            x = 0
            y = MainFrame.TITLE_HEIGHT

            self.surface.blit(self.game_ready.surface, (x, y))

        elif self.game.state == model.Game.GAME_OVER:

            self.game_over.draw()
            x = 0
            y = MainFrame.TITLE_HEIGHT

            self.surface.blit(self.game_over.surface, (x, y))

    def update(self):
        pygame.display.update()

    def end(self):

        super(MainFrame, self).end()

        self.shop_view.end()
        self.inventory_manager.end()
        self.game_over.end()
        self.game_ready.end()
        self.game_view.end()
        self.title.end()
        self.status.end()


class TitleBar(View):
    FILL_COLOUR = Colours.BLACK
    TEXT_FG_COLOUR = Colours.GOLD
    TEXT_BG_COLOUR = None

    def __init__(self, width: int, height: int):

        super(TitleBar, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.title = None
        self.title_image = None
        self.game = None

    def initialise(self, game: model.Game):

        super(TitleBar, self).initialise()

        self.game = game
        self.title = game.name

        try:
            filename = MainFrame.RESOURCES_DIR + "title.png"
            image = pygame.image.load(filename)
            self.title_image = pygame.transform.scale(image, (self.surface.get_width(), self.surface.get_height()))
        except Exception as err:
            print(str(err))


    def draw(self):

        super(TitleBar, self).draw()

        self.surface.fill(TitleBar.FILL_COLOUR)
        pane_rect = self.surface.get_rect()

        if self.title_image is not None:
            self.surface.blit(self.title_image, (0, 0))

        if self.game.state == model.Game.PLAYING:
            msg = "  {0} - {1}  ".format(self.game.get_current_level().name,
                                             self.game.get_current_floor().name)

        elif self.title is not None:
            msg = self.title


        pane_rect = self.surface.get_rect()
        draw_text(self.surface,
                  msg=msg,
                  x=pane_rect.centerx,
                  y=int(pane_rect.height / 2),
                  fg_colour=TitleBar.TEXT_FG_COLOUR,
                  bg_colour=TitleBar.TEXT_BG_COLOUR,
                  size=int(pane_rect.height/2))

class StatusBar(View):
    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.BLACK
    ICON_WIDTH = 40
    PADDING = 40
    STATUS_TEXT_FONT_SIZE = 18
    MESSAGE_TICK_DURATION = 8

    def __init__(self, width: int, height: int):

        super(StatusBar, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.text_box = pygame.Surface((width/2, height-4))
        self.status_messages = []
        self.game = None

    def initialise(self, game: model.Game):

        super(StatusBar, self).initialise()

        self.game = game
        self.title = game.name
        self.current_message_number = 0


    def tick(self):

        super(StatusBar, self).tick()

        self.status_messages = list(self.game.status_messages.keys())

        if self.tick_count % StatusBar.MESSAGE_TICK_DURATION == 0:

            self.current_message_number += 1
            if self.current_message_number >= len(self.status_messages):
                self.current_message_number = 0

    def draw(self):


        self.surface.fill(StatusBar.BG_COLOUR)

        if len(self.status_messages) == 0 or self.current_message_number >= len(self.status_messages):
            msg = "{0}".format(self.game.state)
        else:
            msg = self.status_messages[self.current_message_number]

        pane_rect = self.surface.get_rect()

        text_rect = pygame.Rect(0,0,pane_rect.width/2-4,pane_rect.height-4)

        self.text_box.fill(StatusBar.BG_COLOUR)

        drawText(surface=self.text_box,
                 text=msg,
                 color=StatusBar.FG_COLOUR,
                 rect = text_rect,
                 font=pygame.font.SysFont(pygame.font.get_default_font(), StatusBar.STATUS_TEXT_FONT_SIZE),
                 bkg=StatusBar.BG_COLOUR)

        self.surface.blit(self.text_box, (pane_rect.width/4,4))

        if self.game.state == model.Game.PLAYING:

            player = self.game.get_current_player()

            y = 8
            x = 0

            for equipped_item in player.equipment_slots:

                count = self.game.items_in_inventory(equipped_item)
                draw_icon(self.surface, x=x, y=y, icon_name=equipped_item, count = count)

                if equipped_item in self.game.effects.keys():
                    count = self.game.effects[equipped_item]
                    draw_text(self.surface,msg="{0:^3}".format(count),x=x+4,y=y+4,size=18,
                              bg_colour=Colours.GOLD, fg_colour=Colours.BLACK)

                x += StatusBar.ICON_WIDTH

            y = 8
            x = int(pane_rect.width*3/4)

            draw_icon(self.surface, x=x,y=y,icon_name=model.Tiles.HEART, count=player.HP)

            x += StatusBar.ICON_WIDTH
            draw_icon(self.surface, x=x, y=y, icon_name=model.Tiles.KEY, count=player.keys)

            x += StatusBar.ICON_WIDTH
            draw_icon(self.surface, x=x, y=y, icon_name=model.Tiles.TREASURE, count=player.treasure)

            x += StatusBar.ICON_WIDTH
            draw_icon(self.surface, x=x, y=y, icon_name=model.Tiles.RUNE, count=player.runes_collected(self.game.get_current_level().id))

        elif self.game.state == model.Game.PAUSED:
            msg = "F8:Save   F9:Load   Esc:Resume"
            draw_text(self.surface,
                      msg=msg,
                      x=10,
                      y=int(pane_rect.height / 2),
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=StatusBar.STATUS_TEXT_FONT_SIZE,
                      centre=False)

        elif self.game.state == model.Game.READY:
            msg = "P:Change Name   SPACE:Start"
            draw_text(self.surface,
                      msg=msg,
                      x=10,
                      y=int(pane_rect.height / 2),
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=StatusBar.STATUS_TEXT_FONT_SIZE,
                      centre=False)



class HighScoreTableView(View):

    TITLE_HEIGHT = 26
    TITLE_TEXT_SIZE = 30
    SCORE_HEIGHT = 23
    SCORE_TEXT_SIZE = 22
    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.BLACK

    def __init__(self, width: int, height: int = 500):

        super(HighScoreTableView, self).__init__()

        self.hst = None
        self.surface = pygame.Surface((width, height))

    def initialise(self, hst: utils.HighScoreTable):

        super(HighScoreTableView, self).initialise()

        self.hst = hst

    def draw(self):

        if self.hst is None:
            raise ("No High Score Table to view!")

        self.surface.fill(HighScoreTableView.BG_COLOUR)

        pane_rect = self.surface.get_rect()

        y = HighScoreTableView.TITLE_HEIGHT
        x = pane_rect.centerx

        draw_text(self.surface, msg="High Score Table", x=x, y=y,
                  size=HighScoreTableView.TITLE_TEXT_SIZE,
                  fg_colour=Colours.GOLD)

        if len(self.hst.table) == 0:

            y += HighScoreTableView.SCORE_HEIGHT

            draw_text(self.surface, msg="No high scores recorded",
                      x=x, y=y,
                      size=HighScoreTableView.SCORE_TEXT_SIZE,
                      fg_colour=HighScoreTableView.FG_COLOUR,
                      bg_colour=HighScoreTableView.BG_COLOUR)
        else:
            rank = 1
            for entry in self.hst.table:
                y += HighScoreTableView.SCORE_HEIGHT

                name, score = entry
                draw_text(self.surface, msg="{0}. {1} - {2}".format(rank, name, score), x=x, y=y,
                          size=HighScoreTableView.SCORE_TEXT_SIZE,
                          fg_colour=HighScoreTableView.FG_COLOUR,
                          bg_colour=HighScoreTableView.BG_COLOUR)
                rank += 1


class GameReadyView(View):

    FG_COLOUR = Colours.GOLD
    BG_COLOUR = Colours.DARK_GREY

    def __init__(self, width: int, height: int = 500):
        super(GameReadyView, self).__init__()

        self.game = None
        self.hst = HighScoreTableView(width=width, height=300)

        self.surface = pygame.Surface((width, height))

    def initialise(self, game: model.Game):
        self.game = game
        self.hst.initialise(self.game.hst)


    def draw(self):
        if self.game is None:
            raise ("No Game to view!")

        self.surface.fill(GameReadyView.BG_COLOUR)

        pane_rect = self.surface.get_rect()

        x = pane_rect.centerx
        y = 20

        msg = "R E A D Y !"
        current_player = self.game.get_current_player()
        if current_player is not None:
            msg="Ready {0}  !".format(current_player.name)

        draw_text(self.surface,
                  msg=msg,
                  x=x,
                  y=y,
                  size=40,
                  fg_colour=GameReadyView.FG_COLOUR,
                  bg_colour=GameReadyView.BG_COLOUR)


        image_width = 200
        image_height = 200

        image = View.image_manager.get_skin_image(model.Tiles.PLAYER, tick=self.tick_count)

        x = pane_rect.centerx - int(image_width/2)
        y += 40
        image = pygame.transform.scale(image, (image_width,image_height))
        self.surface.blit(image,(x,y))

        image = View.image_manager.get_skin_image(model.Tiles.MONSTER2, tick=self.tick_count)
        image = pygame.transform.scale(image, (image_width,image_height))

        x = int(pane_rect.width*1/5 - image_width/2)
        self.surface.blit(image,(x,y))

        x = int(pane_rect.width*4/5 - image_width/2)
        self.surface.blit(image,(x,y))

        x = pane_rect.centerx
        y += image_height + 50

        draw_text(self.surface,
                  msg="F I N D   T H E    C H A L I C E !",
                  x=x,
                  y=y,
                  size=44,
                  fg_colour=GameReadyView.FG_COLOUR,
                  bg_colour=GameReadyView.BG_COLOUR)

        x = 0
        y = pane_rect.bottom - self.hst.surface.get_height()
        self.hst.draw()
        self.surface.blit(self.hst.surface, (x, y))


class GameOverView(View):

    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.DARK_GREY
    SCORE_TEXT_SIZE = 22

    def __init__(self, width: int, height: int = 500):

        super(GameOverView, self).__init__()

        self.game = None
        self.hst = HighScoreTableView(width=width, height=300)

        self.surface = pygame.Surface((width, height))

    def initialise(self, game: model.Game):

        self.game = game
        self.hst.initialise(self.game.hst)

    def draw(self):

        self.surface.fill(GameOverView.BG_COLOUR)

        if self.game is None:
            raise ("No Game to view!")

        pane_rect = self.surface.get_rect()

        y = 20
        x = pane_rect.centerx

        if self.game.is_game_complete() is True:
            text = "A D V E N T U R E     C O M P L E T E D"
            fg_colour = Colours.GOLD
        else:
            text = "G A M E    O V E R"
            fg_colour = GameOverView.FG_COLOUR

        draw_text(self.surface,
                  msg=text,
                  x=x,
                  y=y,
                  size=30,
                  fg_colour=fg_colour,
                  bg_colour=GameOverView.BG_COLOUR)

        y += 30

        draw_text(self.surface,
                  msg="Final Scores",
                  x=x,
                  y=y,
                  size=GameOverView.SCORE_TEXT_SIZE,
                  fg_colour=GameOverView.FG_COLOUR,
                  bg_colour=GameOverView.BG_COLOUR)

        y += GameOverView.SCORE_TEXT_SIZE

        rank = 1
        scores = self.game.get_scores()
        for score in scores:
            player, score = score

            if self.game.is_high_score(score):
                fg_colour = Colours.GOLD
                text = "{0}. {1} : {2} ** High Score **".format(rank, player, score)
            else:
                fg_colour = GameOverView.FG_COLOUR
                text = "{0}. {1} : {2}".format(rank, player, score)

            draw_text(self.surface,
                      x=x,
                      y=y,
                      msg=text,
                      fg_colour=fg_colour,
                      bg_colour=GameOverView.BG_COLOUR,
                      size=GameOverView.SCORE_TEXT_SIZE
                      )
            y += GameOverView.SCORE_TEXT_SIZE
            rank += 1

        image_width = 200
        image_height = 200

        if self.game.is_game_complete() is True:
            tile_name = model.Tiles.PLAYER_GOLD
            tile_name2 = model.Tiles.TROPHY
        else:
            tile_name = model.Tiles.MONSTER1
            tile_name2 = model.Tiles.MONSTER2

        image = View.image_manager.get_skin_image(tile_name, tick=self.tick_count)

        x = pane_rect.centerx - int(image_width/2)
        y += 5
        image = pygame.transform.scale(image, (image_width,image_height))
        self.surface.blit(image,(x,y))

        image = View.image_manager.get_skin_image(tile_name2, tick=self.tick_count)
        image = pygame.transform.scale(image, (image_width,image_height))

        y = 20 + GameOverView.SCORE_TEXT_SIZE

        x = int(pane_rect.width*1/5 - image_width/2)
        self.surface.blit(image,(x,y))

        x = int(pane_rect.width*4/5 - image_width/2)
        self.surface.blit(image,(x,y))

        x = 0
        y = pane_rect.bottom - self.hst.surface.get_height()

        self.hst.draw()
        self.surface.blit(self.hst.surface, (x, y))


class GameView(View):

    BG_COLOUR = Colours.GREEN
    FG_COLOUR = Colours.WHITE
    TILE_WIDTH = 32
    TILE_HEIGHT = 32

    def __init__(self, width: int, height: int):
        super(GameView, self).__init__()

        self.surface = pygame.Surface((width, height))

        self.rpg_view = FloorView(self.surface.get_width(),
                                  self.surface.get_height(),
                                  tile_width=GameView.TILE_WIDTH,
                                  tile_height=GameView.TILE_HEIGHT)

        self.game = None

    def initialise(self, game: model.Game):

        super(GameView, self).initialise()

        self.game = game
        self.rpg_view.initialise(self.game.get_current_floor())

    def tick(self):
        super(GameView, self).tick()
        self.rpg_view.tick()

    def draw(self):

        self.surface.fill(GameView.BG_COLOUR)

        if self.game is None:
            raise ("No Game to view!")

        self.rpg_view.floor = self.game.get_current_floor()
        self.rpg_view.skin_name = self.game.get_current_level().skin_name

        self.rpg_view.draw()
        self.surface.blit(self.rpg_view.surface,(0,0))

    def end(self):

        super(GameView, self).end()

class FloorView(View):

    BG_COLOUR = Colours.DARK_GREY
    TILE_WIDTH = 32
    TILE_HEIGHT = 32

    def __init__(self, width : int, height : int, tile_width : int = TILE_WIDTH, tile_height : int = TILE_HEIGHT):

        super(FloorView, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.floor = None
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.skin_name = None

    def initialise(self, floor : model.Floor):
        self.floor = floor

    def draw(self):

        self.surface.fill(FloorView.BG_COLOUR)

        if self.floor is None:
            raise ("No Floor to view!")

        width = self.floor.width
        height = self.floor.height

        for y in range(height):
            for x in range (width):
                tile = self.floor.get_tile(x, y)
                image = View.image_manager.get_skin_image(tile_name=tile, skin_name=self.skin_name,
                                                          tick=self.tick_count)

                if image is not None:
                    self.surface.blit(image,(x * self.tile_width, y * self.tile_height, self.tile_width, self.tile_height))

                if tile == model.Tiles.BOMB_LIT:
                    if (x, y) in self.floor.explodables.keys():
                        tile, count = self.floor.explodables[(x, y)]
                        draw_text(self.surface, str(count), (x + 0.5) * self.tile_width, (y + 0.75) * self.tile_height,size=20)



        if self.floor.boss is not None:

            tile = model.Tiles.BOSS

            image = View.image_manager.get_skin_image(tile_name=tile,
                                                      skin_name=self.skin_name,
                                                      tick=self.tick_count,
                                                      width=self.floor.boss.width * self.tile_width,
                                                      height=self.floor.boss.height * self.tile_height)

            # image = pygame.transform.scale(image, (self.floor.boss.width * self.tile_width,
            #                                        self.floor.boss.height * self.tile_height))

            if image is not None:
                self.surface.blit(image, (self.floor.boss.x * self.tile_width,
                                          self.floor.boss.y * self.tile_height))

                HP = self.floor.boss.HP
                HP_pct = int(HP*100/self.floor.boss._HP)

                x = int(((self.floor.boss.x + self.floor.boss.width/2) * self.tile_width) - HP/2)
                y = int((self.floor.boss.y + self.floor.boss.height) * self.tile_height) - 6

                if HP_pct > 60:
                    colour = Colours.GREEN
                elif HP_pct > 35:
                    colour = Colours.YELLOW
                else:
                    colour = Colours.RED

                pygame.draw.line(self.surface,
                            colour,
                            (x, y),
                            (x + HP, y),
                            4)

        if self.floor.npc is not None:

            tile = self.floor.npc.tile

            image = View.image_manager.get_skin_image(tile_name=tile,
                                                      skin_name=self.skin_name,
                                                      tick=self.tick_count,
                                                      width=self.floor.npc.width * self.tile_width,
                                                      height=self.floor.npc.height * self.tile_height)

            if image is not None:
                self.surface.blit(image, (self.floor.npc.x * self.tile_width,
                                          self.floor.npc.y * self.tile_height))

        tile = self.floor.player.armour

        image = View.image_manager.get_skin_image(tile_name=tile, skin_name=self.skin_name, tick=self.tick_count)

        if self.floor.player is not None and image is not None:
            self.surface.blit(image, (self.floor.player.x * self.tile_width,
                                      self.floor.player.y * self.tile_height,
                                      self.tile_width,
                                      self.tile_height))


class TreasureMapView(View):

    BG_COLOUR = Colours.DARK_GREY
    BORDER_COLOUR = Colours.GOLD
    BORDER_WIDTH = 4
    TILE_WIDTH = 16
    TILE_HEIGHT = 16

    def __init__(self, width : int, height : int, tile_width : int = TILE_WIDTH, tile_height : int = TILE_HEIGHT):

        super(TreasureMapView, self).__init__()


        self.floor = None
        self.map = None
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.skin_name = None
        self.surface = None

    def initialise(self, floor : model.Floor, skin = "default"):
        self.floor = floor
        self.skin = skin
        map = self.floor.get_treasure_map()

        if map is None:
            raise Exception("No Secret Map to view for floor {0}!".format(self.floor.id))

        width = len(map[0])
        height = len(map)

        self.surface = pygame.Surface((width * TreasureMapView.TILE_WIDTH + TreasureMapView.BORDER_WIDTH *2,
                                       height * TreasureMapView.TILE_HEIGHT + TreasureMapView.BORDER_WIDTH *2))

    def draw(self):

        self.surface.fill(TreasureMapView.BG_COLOUR)
        pygame.draw.rect(self.surface,
                         TreasureMapView.BORDER_COLOUR,
                         self.surface.get_rect(),
                         TreasureMapView.BORDER_WIDTH)


        if self.floor is None:
            raise Exception("No Floor to view!")

        map = self.floor.get_treasure_map()

        if map is None:
            raise Exception("No Secret Map to view!")

        width = len(map[0])
        height = len(map)

        for y in range(height):
            row = map[y]
            for x in range(width):
                tile = row[x]
                image = View.image_manager.get_skin_image(tile_name=tile, tick=0, skin_name=self.skin)

                if image is not None:
                    image = pygame.transform.scale(image, (TreasureMapView.TILE_WIDTH, TreasureMapView.TILE_HEIGHT))
                    self.surface.blit(image,(x * self.tile_width + TreasureMapView.BORDER_WIDTH,
                                             y * self.tile_height + TreasureMapView.BORDER_WIDTH,
                                             self.tile_width,
                                             self.tile_height))

class InventoryView(View):

    BG_COLOUR = Colours.DARK_GREY
    FG_COLOUR = Colours.WHITE

    SELECTION_BG_COLOUR = Colours.GREY
    ARMOUR_SELECTION_BG_COLOUR = Colours.BLACK
    SELECTION_BORDER_COLOUR = Colours.GOLD

    ICON_WIDTH = 32
    ICON_HEIGHT = 32
    ICON_PADDING = 6
    ICON_PRICE_PADDING = ICON_WIDTH + 20

    ITEMS = (model.Tiles.TREASURE, model.Tiles.KEY, model.Tiles.RED_POTION,
             model.Tiles.WEAPON, model.Tiles.SHIELD, model.Tiles.BOMB)

    def __init__(self, width : int, height : int, tile_width : int = ICON_WIDTH, tile_height : int = ICON_HEIGHT, selection : bool = True):

        super(InventoryView, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.player = None
        self.current_selected_item = -1
        self.selection = selection

    def initialise(self, player : model.Player, item_prices : dict = None):

        super(InventoryView, self).initialise()

        self.player = player
        self.item_prices = item_prices

    def change_selection(self, delta : int = 0):
        self.current_selected_item += delta
        if self.current_selected_item < 0:
            self.current_selected_item = 0
        elif self.current_selected_item >= len(InventoryView.ITEMS):
            self.current_selected_item = len(InventoryView.ITEMS) - 1

    def get_current_selection(self):
        return InventoryView.ITEMS[self.current_selected_item]

    def draw(self):

        self.surface.fill(InventoryView.BG_COLOUR)

        if self.player is None:
            raise Exception("No Player to view!")

        if self.item_prices is None:
            is_shop_keeper = False
            name = self.player.name + "'s Inventory"
        else:
            is_shop_keeper = True
            name = "Shopkeeper " + self.player.name

        pane_rect = self.surface.get_rect()

        y = 20
        x = pane_rect.centerx

        draw_text(self.surface,
                  msg="{0}".format(name),
                  x=x,
                  y=y,
                  size=30,
                  fg_colour=InventoryView.FG_COLOUR,
                  bg_colour=InventoryView.BG_COLOUR)

        image_width = 80
        image_height = 80

        if is_shop_keeper is True:
            armour = model.Tiles.SHOP_KEEPER
            available_armour = []
            available_armour.append(armour)
        elif self.selection is False:
            armour = self.player.armour
            available_armour = []
            available_armour.append(armour)
        else:
            armour = self.player.armour
            available_armour = deepcopy(self.player.available_armour)

        y += 20
        x = int(pane_rect.centerx - (image_width * len(available_armour)) / 2)

        for i in range(0, len(available_armour)):

            image_name = available_armour[i]

            if is_shop_keeper is True:

                image_scale = 1.0

            elif image_name == armour and self.selection is True:
                pygame.draw.rect(self.surface,
                                 InventoryView.ARMOUR_SELECTION_BG_COLOUR,
                                 [x,y,int(image_width * 7/8),image_height],
                                 0)
                pygame.draw.rect(self.surface,
                                 InventoryView.SELECTION_BORDER_COLOUR,
                                 [x,y,int(image_width * 7/8),image_height],
                                 2)
                image_scale = 1
            else:
                image_scale = 0.75

            image = View.image_manager.get_skin_image(image_name, tick=self.tick_count)
            image = pygame.transform.scale(image, (int(image_width * image_scale), int(image_height * image_scale)))
            self.surface.blit(image,(x,y))

            x += image_width

        x = int(pane_rect.centerx - InventoryView.ICON_WIDTH/2)
        y += image_height + InventoryView.ICON_PADDING

        icon_starty = y

        if is_shop_keeper is True and self.current_selected_item >= 0:
            selection_rect = pygame.Rect(0,icon_starty + self.current_selected_item*38,pane_rect.width,InventoryView.ICON_HEIGHT + int(InventoryView.ICON_PADDING/2))
            pygame.draw.rect(self.surface, InventoryView.SELECTION_BG_COLOUR,selection_rect, 0)
            pygame.draw.rect(self.surface, InventoryView.SELECTION_BORDER_COLOUR,selection_rect, 3)

        item_index = 0
        item_type = InventoryView.ITEMS[item_index]

        draw_icon(self.surface, x=x, y=y, icon_name=item_type, count=self.player.treasure)
        if self.item_prices is not None and item_type in self.item_prices.keys():
            item_price = self.item_prices[item_type]
            draw_icon(self.surface, x=x + InventoryView.ICON_PRICE_PADDING, y=y, icon_name=model.Tiles.TREASURE, count=item_price)

        item_index += 1
        item_type = InventoryView.ITEMS[item_index]
        y += InventoryView.ICON_HEIGHT + InventoryView.ICON_PADDING
        draw_icon(self.surface, x=x, y=y, icon_name=item_type, count=self.player.keys)
        if self.item_prices is not None and item_type in self.item_prices.keys():
            item_price = self.item_prices[item_type]
            draw_icon(self.surface, x=x + InventoryView.ICON_PRICE_PADDING, y=y, icon_name=model.Tiles.TREASURE, count=item_price)

        item_index += 1
        item_type = InventoryView.ITEMS[item_index]
        y += InventoryView.ICON_HEIGHT + InventoryView.ICON_PADDING
        draw_icon(self.surface, x=x, y=y, icon_name=item_type, count=self.player.red_potions)
        if self.item_prices is not None and item_type in self.item_prices.keys():
            item_price = self.item_prices[item_type]
            draw_icon(self.surface, x=x + InventoryView.ICON_PRICE_PADDING, y=y, icon_name=model.Tiles.TREASURE, count=item_price)

        item_index += 1
        item_type = InventoryView.ITEMS[item_index]
        y += InventoryView.ICON_HEIGHT + InventoryView.ICON_PADDING
        draw_icon(self.surface, x=x, y=y, icon_name=item_type, count=self.player.weapon)
        if self.item_prices is not None and item_type in self.item_prices.keys():
            item_price = self.item_prices[item_type]
            draw_icon(self.surface, x=x + InventoryView.ICON_PRICE_PADDING, y=y, icon_name=model.Tiles.TREASURE, count=item_price)

        item_index += 1
        item_type = InventoryView.ITEMS[item_index]
        y += InventoryView.ICON_HEIGHT + InventoryView.ICON_PADDING
        draw_icon(self.surface, x=x, y=y, icon_name=item_type, count=self.player.shield)
        if self.item_prices is not None and item_type in self.item_prices.keys():
            item_price = self.item_prices[item_type]
            draw_icon(self.surface, x=x + InventoryView.ICON_PRICE_PADDING, y=y, icon_name=model.Tiles.TREASURE, count=item_price)

        item_index += 1
        item_type = InventoryView.ITEMS[item_index]
        y += InventoryView.ICON_HEIGHT + InventoryView.ICON_PADDING
        draw_icon(self.surface, x=x, y=y, icon_name=item_type, count=self.player.bombs)
        if self.item_prices is not None and item_type in self.item_prices.keys():
            item_price = self.item_prices[item_type]
            draw_icon(self.surface, x=x + InventoryView.ICON_PRICE_PADDING, y=y, icon_name=model.Tiles.TREASURE, count=item_price)


class CharacterView(View):

    BG_COLOUR = Colours.DARK_GREY
    FG_COLOUR = Colours.WHITE

    ICON_WIDTH = 32
    ICON_HEIGHT = 32
    ICON_PADDING = 6

    MAP_PADDING = 6

    def __init__(self, width : int, height : int, tile_width : int = ICON_WIDTH, tile_height : int = ICON_HEIGHT):

        super(CharacterView, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.player = None

        self.width = width
        self.height = height

        self.surface = pygame.Surface((width, height))

        self.inventory_view = InventoryView(width = self.width, height=(self.height*3/5))
        self.secret_map_view = TreasureMapView(10, 10)


    def initialise(self, game : model.Game):

        super(CharacterView, self).initialise()

        self.game = game
        self.player = self.game.get_current_player()

        self.inventory_view.initialise(self.player)

    def draw(self):

        self.surface.fill(CharacterView.BG_COLOUR)

        if self.player is None:
            raise Exception("No Player to view!")

        pane_rect = self.surface.get_rect()

        # x = pane_rect.centerx
        # y = 20
        #
        # draw_text(self.surface,
        #           msg="Character View",
        #           x=x,
        #           y=y,
        #           size=30,
        #           fg_colour=CharacterView.FG_COLOUR,
        #           bg_colour=CharacterView.BG_COLOUR)

        y = 0
        x = 0

        self.inventory_view.draw()
        self.surface.blit(self.inventory_view.surface, (x, y))

        x=pane_rect.centerx
        y+=self.inventory_view.surface.get_height()
        y+=20


        current_level = self.game.get_current_level()
        draw_text(self.surface,
                  msg="{0} - Secret Maps".format(current_level.name),
                  x=x,
                  y=y,
                  size=30,
                  fg_colour=CharacterView.FG_COLOUR,
                  bg_colour=CharacterView.BG_COLOUR)

        y += 14

        if current_level.id in self.player.treasure_maps.keys() and len(self.player.treasure_maps[current_level.id]) > 0:

            number_of_maps_found = len(self.player.treasure_maps[current_level.id])
            secret_treasures = self.player.treasure_maps[current_level.id]

            x = pane_rect.centerx - int(number_of_maps_found*80 + CharacterView.MAP_PADDING)/2

            for secret in secret_treasures:

                floor_id, (a, b) = secret

                self.secret_map_view.initialise(self.game.get_floor(floor_id),
                                                skin=self.game.get_level(current_level.id).skin_name)
                self.secret_map_view.draw()
                self.surface.blit(self.secret_map_view.surface, (x, y))

                x += self.secret_map_view.surface.get_width() + CharacterView.MAP_PADDING

        x = pane_rect.centerx
        y+=104

        draw_text(self.surface,
                  msg="Runes Collected",
                  x=x,
                  y=y,
                  size=30,
                  fg_colour=CharacterView.FG_COLOUR,
                  bg_colour=CharacterView.BG_COLOUR)

        y+=20

        runes_collected = self.game.get_current_player().runes_collected(current_level.id)

        if runes_collected > 0:
            x = pane_rect.centerx - int(runes_collected * (CharacterView.ICON_WIDTH + CharacterView.ICON_PADDING)) / 2
            for rune in self.player.runes[current_level.id]:
                image = self.image_manager.get_skin_image(rune, skin_name=self.game.get_level(current_level.id).skin_name)
                self.surface.blit(image, (x, y))
                x += CharacterView.ICON_WIDTH + CharacterView.ICON_PADDING

class ShopView(View):

    BG_COLOUR = Colours.BROWN
    FG_COLOUR = Colours.WHITE

    TILE_WIDTH = 32
    TILE_HEIGHT = 32

    def __init__(self, width : int, height : int, tile_width : int = TILE_WIDTH, tile_height : int = TILE_HEIGHT):

        super(ShopView, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.game = None

        self.player_inventory = InventoryView(height=height*3/4,width=width/2, selection=False)
        self.shop_keeper_inventory = InventoryView(height=height*3/4,width=width/2)
        self.shop_keeper_inventory.current_selected_item = 0

    def initialise(self, game : model.Game):

        super(ShopView, self).initialise()

        self.game = game

        self.player_inventory.initialise(self.game.get_current_player())
        self.shop_keeper_inventory.initialise(self.game.shop.get_shop_keeper(game.get_current_level().id), game.shop.item_prices)

    def draw(self):

        self.surface.fill(ShopView.BG_COLOUR)

        if self.game is None:
            raise Exception("No Game to view!")

        pane_rect = self.surface.get_rect()

        y = 20
        x = pane_rect.centerx

        draw_text(self.surface,
                  msg="{0}'s Shop".format(self.game.shop.get_shop_keeper(self.game.get_current_level().id).name),
                  x=x,
                  y=y,
                  size=30,
                  fg_colour=ShopView.FG_COLOUR,
                  bg_colour=ShopView.BG_COLOUR)

        self.player_inventory.draw()
        self.shop_keeper_inventory.draw()

        y+=20
        x=0

        self.surface.blit(self.player_inventory.surface, (x, y))

        x=int(pane_rect.width/2)

        self.surface.blit(self.shop_keeper_inventory.surface, (x, y))


class EnterNameView:

    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.DARK_GREY
    BORDER_COLOUR = Colours.GOLD
    BORDER_WIDTH = 4
    FONT_SIZE = 26

    def __init__(self, surface, x, y, width = 200, height = 50):
        self.text_box = pygame.Surface((width,height))
        self.surface = surface
        self.x = x
        self.y = y

    def run(self):
        txtbx = utils.eztext.Input(maxlength=10, color=EnterNameView.FG_COLOUR,
                                   font=pygame.font.SysFont(pygame.font.get_default_font(),EnterNameView.FONT_SIZE), \
                             x=8,
                             y=6,
                             prompt='Name? ')

        # create the pygame clock
        clock = pygame.time.Clock()

        # main loop!
        loop = True
        while loop:
            # make sure the program is running at 30 fps
            clock.tick(30)

            # events for txtbx
            events = pygame.event.get()
            # process other events
            for event in events:
                # close it x button is pressed
                if event.type == QUIT:
                    loop = False
                    break
                elif event.type == KEYDOWN and event.key in (K_RETURN, K_ESCAPE):
                    loop = False
                    break

            # update txtbx
            txtbx.update(events)

            # blit txtbx on the screen
            self.text_box.fill(EnterNameView.BG_COLOUR)

            txtbx.draw(self.text_box)

            border = self.text_box.get_rect()
            border.width -= EnterNameView.BORDER_WIDTH
            border.height -= EnterNameView.BORDER_WIDTH

            pygame.draw.rect(self.text_box,
                             EnterNameView.BORDER_COLOUR,
                             border,
                             EnterNameView.BORDER_WIDTH)

            self.surface.blit(self.text_box,(self.x,self.y))

            # refresh the display
            pygame.display.flip()

        return txtbx.value









