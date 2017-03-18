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
        new_skin = (new_skin_name, {
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
                                    model.Tiles.START_POSITION: None,
                                    model.Tiles.NORTH: "north.png",
                                    model.Tiles.SOUTH: "south.png",
                                    model.Tiles.EAST: "east.png",
                                    model.Tiles.WEST: "west.png",
                                    model.Tiles.WALL2: ("water.png", "water2.png", "water3.png", "water4.png"),
                                    model.Tiles.TILE1: "tile1.png",
                                    model.Tiles.TILE2: "tile2.png",
                                    model.Tiles.TILE4: "sky.png",
                                    model.Tiles.TILE3: "cloud.png",
                                    model.Tiles.RUNE1: "rune1.png",
                                    model.Tiles.RUNE2: "rune2.png",
                                    model.Tiles.RUNE3: "rune3.png",
                                    model.Tiles.RUNE4: "rune4.png",
                                    model.Tiles.RUNE5: "rune5.png",
                                    model.Tiles.SHOP: "door.png",
                                    model.Tiles.HEART : "heart2.png",
                                    model.Tiles.REPLENISH: ("replenish1.png","replenish2.png","replenish3.png","replenish4.png",\
                                                            "replenish1.png","replenish4.png","replenish3.png","replenish2.png"),
                                    model.Tiles.PLAYER : ("player1.png","player.png","player2.png","player.png"),
                                    model.Tiles.SHOP_KEEPER : "shop_keeper.png",
                                    model.Tiles.DOOR : "door.png",
                                    model.Tiles.DOOR_OPEN: "door_open.png",
                                    model.Tiles.BOSS_DOOR: "boss_door.png",
                                    model.Tiles.BOSS_DOOR_OPEN: "boss_door_open.png",
                                    model.Tiles.BOSS_KEY: "boss_key.png",
                                    model.Tiles.TROPHY: "goal.png",
                                    model.Tiles.UP: "exit.png",
                                    model.Tiles.DOWN: "entrance.png",
                                    model.Tiles.NEXT_LEVEL: "next_level.png",
                                    model.Tiles.PREVIOUS_LEVEL: "previous_level.png",
                                    model.Tiles.KEY : "key.png",
                                    model.Tiles.MAP : "treasure_map.png",
                                    model.Tiles.WEAPON: "sword.png",
                                    model.Tiles.SHIELD: "shield.png",
                                    model.Tiles.BANG: ("bang1.png","bang2.png"),
                                    model.Tiles.BOMB: "bomb.png",
                                    model.Tiles.BOMB_LIT: ("bomb_lit1.png","bomb_lit2.png"),
                                    model.Tiles.RED_POTION: "red_potion.png",
                                    model.Tiles.RUNE: "rune.png",
                                    model.Tiles.SWITCH: "switch.png",
                                    model.Tiles.SWITCH_LIT: "switch_lit.png",
                                    model.Tiles.SWITCH_TILE: None,
                                    model.Tiles.TREASURE: "treasure.png",
                                    model.Tiles.TREASURE10: "treasure10.png",
                                    model.Tiles.TREASURE25: "treasure25.png",
                                    model.Tiles.SECRET_TREASURE: "treasure_chest.png",
                                    model.Tiles.TREASURE_CHEST: "treasure_chest.png",
                                    model.Tiles.TREE: "forest_tree.png",
                                    model.Tiles.MONSTER1: ("skeleton1.png", "skeleton2.png","skeleton1.png","skeleton3.png" ),
                                    model.Tiles.MONSTER2: ("goblin1.png", "goblin2.png","goblin1.png", "goblin3.png"),
                                    model.Tiles.MONSTER3: ("eye1.png", "eye2.png", "eye3.png", "eye2.png", "eye4.png", "eye2.png"),
                                    model.Tiles.BOSS: ("eye1.png", "eye2.png", "eye3.png", "eye2.png", "eye4.png", "eye2.png"),
                                    model.Tiles.TRAP1: ("empty.png","spike0.png","spike1.png","spike2.png","spike3.png",
                                                        "spike2.png","spike1.png","spike0.png"),
                                    model.Tiles.TRAP2: ("trap.png"),
                                    model.Tiles.TRAP3: ("trap.png"),
                                    model.Tiles.DOT1: ("lava1.png", "lava2.png","lava3.png", "lava2.png"),
                                    model.Tiles.DOT2: ("lava.png"),
                                    model.Tiles.BRAZIER: ("fire1.png", "fire2.png", "fire3.png", "fire4.png")})

        ImageManager.skins[new_skin_name] = new_skin

        new_skin_name = "winter"
        new_skin = (new_skin_name, {
                                    model.Tiles.SECRET_WALL: "stone_wall.png",
                                    model.Tiles.DOOR : "winter_door.png",
                                    model.Tiles.DOOR_OPEN: "winter_door_open.png",
                                    model.Tiles.SHOP: "winter_door.png",
                                    model.Tiles.KEY : "key_silver.png",
                                    model.Tiles.TILE2: "tile4.png",
                                    model.Tiles.DECORATION1: "frost_tree.png",
                                    model.Tiles.WALL: "stone_wall.png",
                                    model.Tiles.WALL2: "snow.png",
                                    model.Tiles.WALL_TR: "stone_wall_tr.png",
                                    model.Tiles.WALL_TL: "stone_wall_tl.png",
                                    model.Tiles.WALL_BR: "stone_wall_br.png",
                                    model.Tiles.WALL_BL: "stone_wall_bl.png",
                                    model.Tiles.TREASURE: "treasure_blue.png",
                                    model.Tiles.MONSTER1: ("snow_beast.png", "snow_beast2.png","snow_beast.png", "snow_beast3.png"),
                                    model.Tiles.MONSTER2: ("skeleton1.png", "skeleton2.png", "skeleton1.png", "skeleton3.png"),
                                    model.Tiles.DOT1: ("ice_wall.png"),
                                    model.Tiles.TREE: "winter_tree.png"
                                    })
        ImageManager.skins[new_skin_name] = new_skin


        new_skin_name = "forest"
        new_skin = (new_skin_name, {model.Tiles.WALL: "forest_wall.png",
                                    model.Tiles.WALL_TR: "forest_wall_tr.png",
                                    model.Tiles.WALL_TL: "forest_wall_tl.png",
                                    model.Tiles.WALL_BR: "forest_wall_br.png",
                                    model.Tiles.WALL_BL: "forest_wall_bl.png",
                                    model.Tiles.SECRET_WALL: "forest_wall.png",
                                    model.Tiles.DOOR: "door.png",
                                    model.Tiles.DOOR_OPEN: "door_open.png",
                                    model.Tiles.DECORATION2: "grave1.png",
                                    model.Tiles.TILE2: "tile4.png",
                                    model.Tiles.TREASURE: ("treasure_red.png"),
                                    model.Tiles.TREE: "forest_tree.png",
                                    model.Tiles.MONSTER1: ("goblin1.png", "goblin2.png","goblin1.png", "goblin3.png"),
                                    model.Tiles.MONSTER2: ("skeleton1.png", "skeleton2.png","skeleton1.png","skeleton3.png" ),
                                    model.Tiles.MONSTER3: ("biter.png", "biter1.png", "biter.png","biter2.png","biter.png"),
                                    })

        ImageManager.skins[new_skin_name] = new_skin

        new_skin_name = "desert"
        new_skin = (new_skin_name, {model.Tiles.WALL: "sand_wall.png",
                                    model.Tiles.WALL2: "sand.png",
                                    model.Tiles.WALL3: "water.png",
                                    model.Tiles.WALL_TR: "sand_wall_tr.png",
                                    model.Tiles.WALL_TL: "sand_wall_tl.png",
                                    model.Tiles.WALL_BR: "sand_wall_br.png",
                                    model.Tiles.WALL_BL: "sand_wall_bl.png",
                                    model.Tiles.SECRET_WALL: "sand_wall.png",
                                    model.Tiles.DECORATION1: "palm_tree.png",
                                    model.Tiles.DOOR: "desert_door.png",
                                    model.Tiles.DOOR_OPEN: "desert_door_open.png",
                                    model.Tiles.KEY: "key_orange.png",
                                    model.Tiles.TREASURE: "treasure_orange.png",
                                    model.Tiles.TREE: "cactus.png",
                                    model.Tiles.TILE1: "tile3.png",
                                    model.Tiles.DOT1: ("oil.png"),
                                    model.Tiles.TRAP1: ("spear_trap1.png", "spear_trap2.png", "spear_trap3.png",
                                    "spear_trap4.png", "spear_trap4.png","spear_trap3.png","spear_trap2.png","spear_trap1.png"),
                                    model.Tiles.MONSTER1: ("snake1.png", "snake2.png"),
                                    model.Tiles.MONSTER2: ("devil1.png", "devil2.png"),
                                    model.Tiles.MONSTER3: ("beholder.png", "beholder2.png", "beholder.png", "beholder3.png"),
                                    })

        ImageManager.skins[new_skin_name] = new_skin

        new_skin_name = "cave"
        new_skin = (new_skin_name, {model.Tiles.WALL: "cave_wall.png",
                                    model.Tiles.WALL2: "forest_wall.png",
                                    model.Tiles.WALL3: ("water.png", "water2.png", "water3.png", "water4.png"),
                                    model.Tiles.WALL_TR: "cave_wall_tr.png",
                                    model.Tiles.WALL_TL: "cave_wall_tl.png",
                                    model.Tiles.WALL_BR: "cave_wall_br.png",
                                    model.Tiles.WALL_BL: "cave_wall_bl.png",
                                    model.Tiles.SECRET_WALL: "cave_wall.png",
                                    model.Tiles.DECORATION1: "goal.png",
                                    model.Tiles.DOOR: "cave_door.png",
                                    model.Tiles.DOOR_OPEN: "cave_door_open.png",
                                    model.Tiles.KEY: "key.png",
                                    model.Tiles.TREASURE: "treasure_red.png",
                                    model.Tiles.TREE: "tree.png",
                                    model.Tiles.TILE1: "tile3.png",
                                    model.Tiles.TILE2: "tile5.png",
                                    model.Tiles.DOT1: ("lava1.png", "lava2.png","lava3.png", "lava4.png"),
                                    model.Tiles.DOT2: "ice_wall.png",
                                    model.Tiles.TRAP1: ("spear_trap1.png", "spear_trap2.png", "spear_trap3.png",
                                                        "spear_trap4.png", "spear_trap4.png", "spear_trap3.png",
                                                        "spear_trap2.png", "spear_trap1.png"),
                                    model.Tiles.MONSTER1: ("biter.png", "biter1.png", "biter.png","biter2.png","biter.png"),
                                    model.Tiles.MONSTER2: ("skeleton1.png", "skeleton2.png", "skeleton1.png", "skeleton3.png"),
                                    model.Tiles.MONSTER3: ("goblin1.png", "goblin2.png", "goblin1.png", "goblin3.png"),
                                    })

        ImageManager.skins[new_skin_name] = new_skin

        new_skin_name = "chaos"
        new_skin = (new_skin_name, {model.Tiles.WALL: "chaos_wall.png",
                                    model.Tiles.WALL2: "stone_wall.png",
                                    model.Tiles.WALL3: "wall.png",
                                    model.Tiles.WALL_TR: "chaos_wall_tr.png",
                                    model.Tiles.WALL_TL: "chaos_wall_tl.png",
                                    model.Tiles.WALL_BR: "chaos_wall_br.png",
                                    model.Tiles.WALL_BL: "chaos_wall_bl.png",
                                    model.Tiles.SECRET_WALL: "chaos_wall.png",
                                    model.Tiles.DECORATION1: "palm_tree.png",
                                    model.Tiles.DOOR: "chaos_portal.png",
                                    model.Tiles.DOOR_OPEN: "chaos_portal_open.png",
                                    model.Tiles.KEY: "chaos_key.png",
                                    model.Tiles.TREASURE: "treasure_purple.png",
                                    model.Tiles.TRAP2: ("treasure_map.png"),
                                    model.Tiles.TREE: "chaos_tree.png",
                                    model.Tiles.TILE1: "tile6.png",
                                    model.Tiles.TILE2: "tile5.png",
                                    model.Tiles.DOT1: ("lava1.png", "lava2.png","lava3.png", "lava4.png"),
                                    model.Tiles.MONSTER1: ("chaos_beast1.png", "chaos_beast2.png"),
                                    model.Tiles.MONSTER2: ("shadow_ghost1.png", "shadow_ghost2.png"),
                                    model.Tiles.MONSTER3: ("beholder.png", "beholder2.png", "beholder.png", "beholder3.png"),
                                    })

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

        new_skin_name = "runes"
        new_skin = (new_skin_name, {model.Tiles.RUNE1: "rune1.png",
                                    model.Tiles.RUNE2: "rune2.png",
                                    model.Tiles.RUNE3: "rune3.png",
                                    model.Tiles.RUNE4: "rune4.png",
                                    model.Tiles.RUNE5: "rune5.png"})

        ImageManager.skins[new_skin_name] = new_skin

        new_skin_name = "end"
        new_skin = (new_skin_name, {
                                    model.Tiles.TILE2: "tile4.png",
                                    model.Tiles.WALL: "stone_wall.png",
                                    model.Tiles.WALL_TR: "stone_wall_tr.png",
                                    model.Tiles.WALL_TL: "stone_wall_tl.png",
                                    model.Tiles.WALL_BR: "stone_wall_br.png",
                                    model.Tiles.WALL_BL: "stone_wall_bl.png",
                                    })

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

def draw_text(surface, msg, x, y, size=32, fg_colour=Colours.WHITE, bg_colour=Colours.BLACK, alpha : int = 255, centre : bool = True):

    font = pygame.font.Font(None, size)
    if bg_colour is not None:
        text = font.render(msg, 1, fg_colour, bg_colour)
    else:
        text = font.render(msg, 1, fg_colour)
    textpos = text.get_rect()

    if centre is True:
        textpos.centerx = x
    else:
        textpos.x = x

    textpos.centery = y
    surface.blit(text, textpos)
    surface.set_alpha(alpha)