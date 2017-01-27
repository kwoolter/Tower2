import pygame
import game_template.model as model
from .colours import Colours
import os
import game_template.utils as utils
import time, logging

class View:
    def __init__(self):
        self.tick_count = 0

    def initialise(self):
        self.tick_count = 0

    def tick(self):
        self.tick_count += 1

    def draw(self):
        pass

    def end(self):
        pass


class MainFrame(View):

    TITLE_HEIGHT = 80
    STATUS_HEIGHT = 40

    RESOURCES_DIR = os.path.dirname(__file__) + "\\resources\\"

    def __init__(self, width: int = 600, height: int = 600):

        super(MainFrame, self).__init__()

        self.game = None

        height = MainFrame.TITLE_HEIGHT + MainFrame.STATUS_HEIGHT + (32*20)

        self.surface = pygame.display.set_mode((width, height))

        self.title = TitleBar(width=width, height=MainFrame.TITLE_HEIGHT)
        self.status = StatusBar(width=width, height=MainFrame.STATUS_HEIGHT)
        self.hst = HighScoreTableView(width=width, height=300)
        self.game_view = GameView(width=width, height=height - MainFrame.TITLE_HEIGHT - MainFrame.STATUS_HEIGHT)
        self.game_ready = GameReadyView(width=width, height=height - MainFrame.TITLE_HEIGHT - MainFrame.STATUS_HEIGHT)
        self.game_over = GameOverView(width=width, height=height - MainFrame.TITLE_HEIGHT - MainFrame.STATUS_HEIGHT)

    def initialise(self, game: model.Game):

        super(MainFrame, self).initialise()

        self.game = game

        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.display.set_caption(self.game.name)
        filename = MainFrame.RESOURCES_DIR + "icon.jpg"
        try:
            image = pygame.image.load(filename)
            image = pygame.transform.scale(image, (32, 32))
            pygame.display.set_icon(image)
        except Exception as err:
            print(str(err))

        self.title.initialise(self.game)
        self.status.initialise(self.game)
        self.hst.initialise(self.game.hst)
        self.game_view.initialise(self.game)
        self.game_ready.initialise(self.game)
        self.game_over.initialise(self.game)

    def tick(self):

        super(MainFrame, self).tick()

        self.title.tick()
        self.status.tick()
        self.game_view.tick()
        self.game_ready.tick()
        self.game_over.tick()

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

            self.game_view.draw()
            x = 0
            y = MainFrame.TITLE_HEIGHT

            self.surface.blit(self.game_view.surface, (x, y))

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

        self.game_view.end()
        self.title.end()
        self.status.end()
        self.hst.end()


class TitleBar(View):
    FILL_COLOUR = Colours.BLACK
    TEXT_FG_COLOUR = Colours.WHITE
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
    BG_COLOUR = Colours.GREY
    ICON_WIDTH = 40
    PADDING = 40

    def __init__(self, width: int, height: int):

        super(StatusBar, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.status_messages = []
        self.game = None

        self.image_manager = ImageManager()

    def initialise(self, game: model.Game):

        super(StatusBar, self).initialise()

        self.game = game
        self.title = game.name
        self.current_message_number = 0
        for i in range(4):
            self.status_messages.append("Msg {0}".format(i))

        self.image_manager.initialise()

    def tick(self):

        super(StatusBar, self).tick()

        self.current_message_number += 1
        if self.current_message_number >= len(self.status_messages):
            self.current_message_number = 0

    def draw(self):

        self.surface.fill(StatusBar.BG_COLOUR)

        self.status_messages = []
        self.status_messages.append("Game {0}".format(self.game.state))

        pane_rect = self.surface.get_rect()

        msg = self.status_messages[self.current_message_number]

        draw_text(self.surface,
                  msg=msg,
                  x=pane_rect.centerx,
                  y=int(pane_rect.height / 2),
                  fg_colour=StatusBar.FG_COLOUR,
                  bg_colour=StatusBar.BG_COLOUR,
                  size=pane_rect.height)

        if self.game.state == model.Game.PLAYING:
            draw_text(self.surface,
                      msg=time.strftime("%H:%M:%S", self.game.elapsed_time),
                      x=StatusBar.PADDING, y=int(pane_rect.height / 2),
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=int(pane_rect.height*3/4))

            player = self.game.get_current_player()

            y = pane_rect.top + 4
            x = int(pane_rect.width*3/4)

            self.draw_icon(self.surface, x=x,y=y,icon_name=model.Tiles.HEART, count=player.HP)

            x += StatusBar.ICON_WIDTH
            self.draw_icon(self.surface, x=x, y=y, icon_name=model.Tiles.KEY, count=player.keys)

            x += StatusBar.ICON_WIDTH
            self.draw_icon(self.surface, x=x, y=y, icon_name=model.Tiles.TREASURE, count=player.treasure)

            x += StatusBar.ICON_WIDTH
            self.draw_icon(self.surface, x=x, y=y, icon_name=model.Tiles.TROPHY, count=player.trophies)


    def draw_icon(self, surface, x, y, icon_name, count=None):

        image = self.image_manager.get_skin_image(tile_name=icon_name, skin_name="default", tick=self.tick_count)
        iconpos = image.get_rect()
        iconpos.left = x
        iconpos.top = y
        surface.blit(image, iconpos)

        if count is not None:
            small_font = pygame.font.Font(None, 20)
            icon_count = small_font.render("{0:>2}".format(count), 1, Colours.BLACK, Colours.WHITE)
            count_pos = icon_count.get_rect()
            count_pos.bottom = iconpos.bottom
            count_pos.right = iconpos.right
            surface.blit(icon_count, count_pos)



class HighScoreTableView(View):
    TITLE_HEIGHT = 24
    TITLE_TEXT_SIZE = 30
    SCORE_HEIGHT = 20
    SCORE_TEXT_SIZE = 20

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
    BG_COLOUR = Colours.GREY

    def __init__(self, width: int, height: int = 500):
        super(GameReadyView, self).__init__()

        self.game = None
        self.hst = HighScoreTableView(width=width, height=300)

        self.surface = pygame.Surface((width, height))

        self.image_manager = ImageManager()

    def initialise(self, game: model.Game):
        self.game = game
        self.hst.initialise(self.game.hst)
        self.image_manager.initialise()

    def draw(self):
        if self.game is None:
            raise ("No Game to view!")

        self.surface.fill(GameReadyView.BG_COLOUR)

        pane_rect = self.surface.get_rect()

        x = pane_rect.centerx
        y = 20

        draw_text(self.surface,
                  msg="R E A D Y !",
                  x=x,
                  y=y,
                  size=30,
                  fg_colour=GameReadyView.FG_COLOUR,
                  bg_colour=GameReadyView.BG_COLOUR)


        image_width = 200
        image_height = 200

        image = self.image_manager.get_skin_image(model.Tiles.PLAYER, tick=self.tick_count)

        x = pane_rect.centerx - int(image_width/2)
        y += 40
        image = pygame.transform.scale(image, (image_width,image_height))
        self.surface.blit(image,(x,y))

        image = self.image_manager.get_skin_image(model.Tiles.MONSTER2, tick=self.tick_count)
        image = pygame.transform.scale(image, (image_width,image_height))

        x = int(pane_rect.width*1/5 - image_width/2)
        self.surface.blit(image,(x,y))

        x = int(pane_rect.width*4/5 - image_width/2)
        self.surface.blit(image,(x,y))

        x = 0
        y = pane_rect.bottom - self.hst.surface.get_height()
        self.hst.draw()
        self.surface.blit(self.hst.surface, (x, y))


class GameOverView(View):
    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.GREY
    SCORE_TEXT_SIZE = 25

    def __init__(self, width: int, height: int = 500):

        super(GameOverView, self).__init__()

        self.game = None
        self.hst = HighScoreTableView(width=width, height=300)

        self.surface = pygame.Surface((width, height))

        self.image_manager = ImageManager()

    def initialise(self, game: model.Game):

        self.game = game
        self.hst.initialise(self.game.hst)
        self.image_manager.initialise()

    def draw(self):

        if self.game is None:
            raise ("No Game to view!")

        self.surface.fill(GameOverView.BG_COLOUR)

        pane_rect = self.surface.get_rect()

        y = 20
        x = pane_rect.centerx

        draw_text(self.surface,
                  msg="G A M E    O V E R",
                  x=x,
                  y=y,
                  size=30,
                  fg_colour=GameOverView.FG_COLOUR,
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
            draw_text(self.surface,
                      x=x,
                      y=y,
                      msg="{0}. {1} : {2}".format(rank, player, score),
                      fg_colour=GameOverView.FG_COLOUR,
                      bg_colour=GameOverView.BG_COLOUR,
                      size=GameOverView.SCORE_TEXT_SIZE
                      )
            y += GameOverView.SCORE_TEXT_SIZE
            rank += 1

        image_width = 200
        image_height = 200

        image = self.image_manager.get_skin_image(model.Tiles.PLAYER, tick=self.tick_count)

        x = pane_rect.centerx - int(image_width/2)
        y += 5
        image = pygame.transform.scale(image, (image_width,image_height))
        self.surface.blit(image,(x,y))

        image = self.image_manager.get_skin_image(model.Tiles.MONSTER2, tick=self.tick_count)
        image = pygame.transform.scale(image, (image_width,image_height))

        y = 20

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


def draw_text(surface, msg, x, y, size=32, fg_colour=Colours.WHITE, bg_colour=Colours.BLACK, alpha : int = 255):
    font = pygame.font.Font(None, size)
    if bg_colour is not None:
        text = font.render(msg, 1, fg_colour, bg_colour)
    else:
        text = font.render(msg, 1, fg_colour)
    textpos = text.get_rect()
    textpos.centerx = x
    textpos.centery = y
    surface.blit(text, textpos)
    surface.set_alpha(alpha)


class FloorView(View):

    BG_COLOUR = Colours.GREY

    TILE_WIDTH = 32
    TILE_HEIGHT = 32

    def __init__(self, width : int, height : int, tile_width : int = TILE_WIDTH, tile_height : int = TILE_HEIGHT):
        super(FloorView, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.floor = None
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.skin_name = None

        self.image_manager = ImageManager()

    def initialise(self, floor : model.Floor):
        self.floor = floor
        self.image_manager.initialise()


    def draw(self):
        self.surface.fill(FloorView.BG_COLOUR)

        if self.floor is None:
            raise ("No Floor to view!")

        width = self.floor.width
        height = self.floor.height

        for y in range(height):
            for x in range (width):
                tile = self.floor.get_tile(x, y)
                image = self.image_manager.get_skin_image(tile_name=tile, skin_name=self.skin_name,
                                                          tick=self.tick_count)

                if image is not None:
                    self.surface.blit(image,(x * self.tile_width, y * self.tile_height, self.tile_width, self.tile_height))

        tile = model.Tiles.PLAYER
        image = self.image_manager.get_skin_image(tile_name=tile, skin_name=self.skin_name, tick=self.tick_count)

        if self.floor.player is not None and image is not None:
            self.surface.blit(image, (self.floor.player.x * self.tile_width,
                                      self.floor.player.y * self.tile_height,
                                      self.tile_width,
                                      self.tile_height))

class ImageManager:

    DEFAULT_SKIN = "default"

    image_cache = {}

    def __init__(self):
        self.skins = {}

    def initialise(self):
        self.load_skins()


    def get_image(self, image_file_name : str, width : int = 32, height : int =32):

        if image_file_name not in ImageManager.image_cache.keys():

            filename = MainFrame.RESOURCES_DIR + image_file_name
            try:
                logging.info("Loading image {0}...".format(filename))
                image = pygame.image.load(filename)
                image = pygame.transform.scale(image, (width, height))
                ImageManager.image_cache[image_file_name] = image
                logging.info("Image {0} loaded and cached.".format(filename))
            except Exception as err:
                print(str(err))



        return self.image_cache[image_file_name]


    def load_skins(self):


        new_skin_name = ImageManager.DEFAULT_SKIN
        new_skin = (new_skin_name, {model.Tiles.WALL : "forest_wall.png",
                                    model.Tiles.SECRET_WALL: "forest_wall.png",
                                    model.Tiles.WALL: "forest_wall.png",
                                    model.Tiles.WALL_TR: "forest_wall_tr.png",
                                    model.Tiles.WALL_TL: "forest_wall_tl.png",
                                    model.Tiles.WALL_BR: "forest_wall_br.png",
                                    model.Tiles.WALL_BL: "forest_wall_bl.png",
                                    model.Tiles.DECORATION1: ("eyes.png", "eyes.png","eyes1.png","eyes.png",
                                                              "eyes1.png", "eyes3.png", "eyes3.png", "eyes3.png"),
                                    model.Tiles.DECORATION2: ("pyre1.png","pyre2.png","pyre3.png","pyre4.png"),
                                    model.Tiles.EMPTY : None,
                                    model.Tiles.SAFETY: None,
                                    model.Tiles.HEART : "heart2.png",
                                    model.Tiles.PLAYER : ("player1.png","player.png","player2.png","player.png"),
                                    model.Tiles.DOOR : "winter_door.png",
                                    model.Tiles.TROPHY: "goal.png",
                                    model.Tiles.EXIT: "exit.png",
                                    model.Tiles.ENTRANCE: "entrance.png",
                                    model.Tiles.NEXT_LEVEL: "next_level.png",
                                    model.Tiles.PREVIOUS_LEVEL: "previous_level.png",
                                    model.Tiles.KEY : "key.png",
                                    model.Tiles.RED_POTION: "red_potion.png",
                                    model.Tiles.SWITCH: "switch.png",
                                    model.Tiles.SWITCH_LIT: "switch_lit.png",
                                    model.Tiles.TREASURE: "treasure1.png",
                                    model.Tiles.TREE: "winter_tree.png",
                                    model.Tiles.MONSTER1 : ("squirrel1.png","squirrel2.png"),
                                    model.Tiles.MONSTER2: ("goblin1.png", "goblin2.png"),
                                    model.Tiles.MONSTER3: ("skeleton1.png", "skeleton2.png"),
                                    model.Tiles.TRAP1: ("trap.png"),
                                    model.Tiles.TRAP2: ("trap.png"),
                                    model.Tiles.TRAP3: ("trap.png"),
                                    model.Tiles.DOT1: ("lava1.png", "lava2.png","lava3.png", "lava2.png"),
                                    model.Tiles.DOT2: ("lava.png"),
                                    model.Tiles.BRAZIER : ("brazier.png", "brazier_lit.png")})

        self.skins[new_skin_name] = new_skin

        new_skin_name = "winter"
        new_skin = (new_skin_name, {model.Tiles.WALL : "winter_wall.png",
                                    model.Tiles.SECRET_WALL: "winter_wall.png",
                                    model.Tiles.DOOR : "winter_door.png",
                                    model.Tiles.KEY : "key.png",
                                    model.Tiles.TREASURE: "treasure1.png",
                                    model.Tiles.DOT1: ("ice.png"),
                                    model.Tiles.TREE: "winter_tree.png",
                                    model.Tiles.BRAZIER : ("brazier.png", "brazier_lit.png")})

        self.skins[new_skin_name] = new_skin

        new_skin_name = "forest"
        new_skin = (new_skin_name, {model.Tiles.WALL: "forest_wall.png",
                                    model.Tiles.WALL_TR: "forest_wall_tr.png",
                                    model.Tiles.WALL_TL: "forest_wall_tl.png",
                                    model.Tiles.WALL_BR: "forest_wall_br.png",
                                    model.Tiles.WALL_BL: "forest_wall_bl.png",
                                    model.Tiles.SECRET_WALL: "forest_wall.png",
                                    model.Tiles.DOOR: "door.png",
                                    model.Tiles.TREASURE: ("treasure.png","treasure2.png","treasure3.png","treasure2.png"),
                                    model.Tiles.TREE: "forest_tree.png",
                                    model.Tiles.MONSTER1: ("goblin1.png", "goblin2.png"),
                                    model.Tiles.MONSTER2: ("skeleton1.png", "skeleton2.png","skeleton1.png","skeleton3.png" ),
                                    model.Tiles.MONSTER3: ("eye1.png", "eye2.png", "eye3.png", "eye2.png","eye4.png", "eye2.png"),
                                    model.Tiles.BRAZIER: ("fire1.png", "fire2.png", "fire3.png", "fire4.png")})

        self.skins[new_skin_name] = new_skin

        new_skin_name = "desert"
        new_skin = (new_skin_name, {model.Tiles.WALL: "forest_wall.png",
                                    model.Tiles.SECRET_WALL: "forest_wall.png",
                                    model.Tiles.PLAYER: "player.png",
                                    model.Tiles.DOOR: "door.png",
                                    model.Tiles.KEY: "key.png",
                                    model.Tiles.RED_POTION: "red_potion.png",
                                    model.Tiles.TREASURE: "treasure.png",
                                    model.Tiles.TREE: "forest_tree.png",
                                    model.Tiles.MONSTER1: ("fire1.png", "fire2.png", "fire3.png", "fire4.png"),
                                    model.Tiles.BRAZIER: ("brazier.png", "brazier_lit.png")})

        self.skins[new_skin_name] = new_skin

        new_skin_name = "squirrel"
        new_skin = (new_skin_name, {model.Tiles.WALL: "stone_wall.png",
                                    model.Tiles.SECRET_WALL: "forest_wall.png",
                                    model.Tiles.PLAYER: "squirrel1.png",
                                    model.Tiles.DOOR: "wooden_door.png",
                                    model.Tiles.KEY: "key.png",
                                    model.Tiles.DECORATION1: "flower.png",
                                    model.Tiles.DECORATION2: ("pyre1.png", "pyre2.png", "pyre3.png", "pyre4.png"),
                                    model.Tiles.RED_POTION: "red_potion.png",
                                    model.Tiles.TREASURE: "treasure_nut.png",
                                    model.Tiles.TREE: "squirrel_tree.png",
                                    model.Tiles.MONSTER1: ("devil1.png", "devil2.png"),
                                    model.Tiles.BRAZIER: ("brazier.png", "brazier_lit.png")})

        self.skins[new_skin_name] = new_skin

    def get_skin_image(self, tile_name: str, skin_name: str = DEFAULT_SKIN, tick=0):

        if skin_name not in self.skins.keys():
            raise Exception("Can't find specified skin {0}".format(skin_name))

        name, tile_map = self.skins[skin_name]

        if tile_name not in tile_map.keys():
            name, tile_map = self.skins[ImageManager.DEFAULT_SKIN]
            if tile_name not in tile_map.keys():
                raise Exception("Can't find tile name '{0}' in skin '{1}'!".format(tile_name, skin_name))

        tile_file_names = tile_map[tile_name]

        image = None

        if tile_file_names is None:
            image = None
        elif isinstance(tile_file_names, tuple):
            if tick == 0:
                tile_file_name = tile_file_names[0]
            else:
                tile_file_name = tile_file_names[tick % len(tile_file_names)]

            image = self.get_image(tile_file_name)

        else:
            image = self.get_image(tile_file_names)


        return image

