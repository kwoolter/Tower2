import pygame
import logging
import os
import game_template.model as model


class Colours:
    # set up the colours
    BLACK = (0, 0, 0)
    BROWN = (128,64,0)
    WHITE = (255, 255, 255)
    RED = (237, 28, 36)
    GREEN = (34, 177, 76)
    BLUE = (63, 72, 204)
    DARK_GREY = (40, 40, 40)
    GREY = (128,128,128)
    GOLD = (255, 201, 14)
    YELLOW = (255, 255, 0)

class ImageManager:

    DEFAULT_SKIN = "default"
    RESOURCES_DIR = os.path.dirname(__file__) + "\\resources\\"

    image_cache = {}
    skins = {}
    initialised = False

    def __init__(self):
        pass

    def initialise(self):
        if ImageManager.initialised is False:
            self.load_skins()

    def get_image(self, image_file_name : str, width : int = 32, height : int =32):

        if image_file_name not in ImageManager.image_cache.keys():

            filename = ImageManager.RESOURCES_DIR + image_file_name
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
                                    model.Tiles.SHOP: "wooden_door.png",
                                    model.Tiles.HEART : "heart2.png",
                                    model.Tiles.PLAYER : ("player1.png","player.png","player2.png","player.png"),
                                    model.Tiles.DOOR : "winter_door.png",
                                    model.Tiles.TROPHY: "goal.png",
                                    model.Tiles.EXIT: "exit.png",
                                    model.Tiles.ENTRANCE: "entrance.png",
                                    model.Tiles.NEXT_LEVEL: "next_level.png",
                                    model.Tiles.PREVIOUS_LEVEL: "previous_level.png",
                                    model.Tiles.KEY : "key.png",
                                    model.Tiles.WEAPON: "sword.png",
                                    model.Tiles.SHIELD: "shield.png",
                                    model.Tiles.BOMB: "bomb.png",
                                    model.Tiles.BOMB_LIT: ("bomb_lit1.png","bomb_lit2.png"),
                                    model.Tiles.RED_POTION: "red_potion.png",
                                    model.Tiles.SWITCH: "switch.png",
                                    model.Tiles.SWITCH_LIT: "switch_lit.png",
                                    model.Tiles.TREASURE: "treasure.png",
                                    model.Tiles.TREASURE_CHEST: "treasure_chest.png",
                                    model.Tiles.TREE: "winter_tree.png",
                                    model.Tiles.MONSTER1: ("skeleton1.png", "skeleton2.png","skeleton1.png","skeleton3.png" ),
                                    model.Tiles.MONSTER2: ("goblin1.png", "goblin2.png"),
                                    model.Tiles.MONSTER3: ("skeleton1.png", "skeleton2.png"),
                                    model.Tiles.TRAP1: ("empty.png","spike0.png","spike1.png","spike2.png","spike3.png",
                                                        "spike2.png","spike1.png","spike0.png"),
                                    model.Tiles.TRAP2: ("trap.png"),
                                    model.Tiles.TRAP3: ("trap.png"),
                                    model.Tiles.DOT1: ("lava1.png", "lava2.png","lava3.png", "lava2.png"),
                                    model.Tiles.DOT2: ("lava.png"),
                                    model.Tiles.BRAZIER : ("brazier.png", "brazier_lit.png")})

        ImageManager.skins[new_skin_name] = new_skin

        new_skin_name = "winter"
        new_skin = (new_skin_name, {model.Tiles.WALL : "winter_wall.png",
                                    model.Tiles.SECRET_WALL: "winter_wall.png",
                                    model.Tiles.DOOR : "winter_door.png",
                                    model.Tiles.KEY : "key.png",
                                    model.Tiles.TREASURE: "treasure1.png",
                                    model.Tiles.DOT1: ("ice.png"),
                                    model.Tiles.TREE: "winter_tree.png",
                                    model.Tiles.BRAZIER : ("brazier.png", "brazier_lit.png")})

        ImageManager.skins[new_skin_name] = new_skin

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

        ImageManager.skins[new_skin_name] = new_skin

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

        ImageManager.skins[new_skin_name] = new_skin

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

        ImageManager.skins[new_skin_name] = new_skin

    def get_skin_image(self, tile_name: str, skin_name: str = DEFAULT_SKIN, tick=0):

        if skin_name not in ImageManager.skins.keys():
            raise Exception("Can't find specified skin {0}".format(skin_name))

        name, tile_map = ImageManager.skins[skin_name]

        if tile_name not in tile_map.keys():
            name, tile_map = ImageManager.skins[ImageManager.DEFAULT_SKIN]
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

class View:

    image_manager = ImageManager()

    def __init__(self):
        self.tick_count = 0
        View.image_manager.initialise()

    def initialise(self):
        self.tick_count = 0

    def tick(self):
        self.tick_count += 1

    def draw(self):
        pass

    def end(self):
        pass


def draw_icon(surface, x, y, icon_name, count : int = None, tick : int = 0):

    image = View.image_manager.get_skin_image(tile_name=icon_name, skin_name="default", tick=tick)
    iconpos = image.get_rect()
    iconpos.left = x
    iconpos.top = y
    surface.blit(image, iconpos)

    if count is not None:
        small_font = pygame.font.Font(None, 20)
        icon_count = small_font.render("{0:^3}".format(count), 1, Colours.BLACK, Colours.WHITE)
        count_pos = icon_count.get_rect()
        count_pos.bottom = iconpos.bottom
        count_pos.right = iconpos.right
        surface.blit(icon_count, count_pos)

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