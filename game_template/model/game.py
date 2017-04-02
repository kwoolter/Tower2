import logging, random, os
from copy import deepcopy
import game_template.utils as utils
import game_template.utils.trpg as trpg
import time
from operator import itemgetter
import pickle


class Tiles:

    # Define Tiles
    # Cut and Paste
    BANG = '$'
    BOMB = 'q'
    BOMB_LIT = 'Q'
    BOSS_DOOR = 'F'
    BOSS_DOOR_OPEN = 'f'
    BRAZIER = 'B'
    DECORATION1 = 'z'
    DECORATION2 = 'Z'
    DOOR = 'D'
    DOOR_OPEN = 'd'
    DOT1 = '!'
    DOT2 = '£'
    DOWN = '-'
    EAST = 'E'
    EMPTY = ' '
    EXIT_KEY = '%'
    HEART = 'HP'
    REPLENISH = "H"
    REPLENISH_SPENT = "h"
    KEY = '?'
    MAP = 'M'
    MONSTER1 = '1'
    MONSTER2 = '2'
    MONSTER3 = '3'
    BOSS = '4'
    BOSS_KEY = 'K'
    NEXT_LEVEL = 'L'
    NORTH = 'N'
    PLAYER = 'P'
    PLAYER_KNIGHT = 'p'
    PLAYER_GOLD = 'g'
    PLAYER_SPIKE = 'A'
    PLAYER_THIEF = 'a'
    PLAYER_SKY = 'U'
    NPC1 = 'Y'
    NPC2 = 'y'
    NPC3 = 'U'
    PREVIOUS_LEVEL = 'l'
    RED_POTION = 'R'
    RUNE = 'u'
    RUNE1 = 'R1'
    RUNE2 = 'R2'
    RUNE3 = 'R3'
    RUNE4 = 'R4'
    RUNE5 = 'R5'
    SAFETY = '8'
    SECRET_TREASURE = 'J'
    SECRET_WALL = ';'
    SHIELD = 'O'
    SHOP = 's'
    SHOP_KEEPER = 'SHOP'
    SOUTH = 'S'
    START_POSITION = '='
    SWITCH = ','
    SWITCH_LIT = '<'
    SWITCH_TILE = '_'
    TILE1 = '`'
    TILE2 = '¬'
    TILE3 = '.'
    TILE4 = '~'
    TRAP1 = '^'
    TRAP2 = '&'
    TRAP3 = '['
    TREASURE = '*'
    TREASURE_CHEST = 'j'
    TREASURE10 = 'x'
    TREASURE25 = 'X'
    TREE = 'T'
    TROPHY = 'G'
    UP = '+'
    WALL = ':'
    WALL_BL = '('
    WALL_BR = ')'
    WALL_TL = '/'
    WALL_TR = '\\'
    WALL2 = 'w'
    WALL3 = 'e'
    WEAPON = '|'
    WEST = 'W'

    MONSTERS = (MONSTER1, MONSTER2, MONSTER3)
    NPCS = (NPC1, NPC2, NPC3)
    EXPLODABLES = (BOMB_LIT)
    FLOOR_TILES = (TILE1, TILE2, TILE3, TILE4)
    INDESTRUCTIBLE_ITEMS = (KEY, TREE, TROPHY, NORTH, SOUTH, EAST, WEST, UP, DOWN, SHOP, DOOR, RUNE)
    TRAPS = (TRAP1, TRAP2, TRAP3)
    RUNES = (RUNE1, RUNE2, RUNE3, RUNE4, RUNE5)
    MONSTER_EMPTY_TILES = (EMPTY, PLAYER, DOOR_OPEN) + FLOOR_TILES
    PLAYER_BLOCK_TILES = (WALL, WALL_BL, WALL_BR, WALL_TL, WALL_TR, TREE, WALL2, WALL3, BRAZIER, RUNE, DECORATION1, DECORATION2, REPLENISH_SPENT)
    PLAYER_DOT_TILES = (DOT1, DOT2)
    PLAYER_EQUIPABLE_ITEMS = (WEAPON, SHIELD, RED_POTION, BOMB)
    PLAYER_ARMOUR = (PLAYER_KNIGHT, PLAYER_SPIKE, PLAYER_GOLD, PLAYER_THIEF, PLAYER_SKY)
    SWAP_TILES = {SECRET_WALL: EMPTY, SWITCH : SWITCH_LIT, SWITCH_LIT : SWITCH}

class Character():

    def __init__(self, name : str, x : int = 1, y : int = 1, width : int = 1, height : int = 1, HP : int = 20):
        self.name = name
        self._HP = HP
        self._x = x
        self._y = y
        self.height = height
        self.width = width
        self.old_x = x
        self.old_y = y
        self.initialise()

    def initialise(self):
        self.HP = self._HP

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, new_x):
        self.old_x = self._x
        self._x = new_x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, new_y):
        self.old_y = self._y
        self._y = new_y

    def moved(self):
        return (self._x, self._y) != (self.old_x, self.old_y)

    # Go back to old position
    def back(self):
        self._x = self.old_x
        self._y = self.old_y

class Player(Character):
    def __init__(self, name : str, x : int = 1, y : int = 1, HP : int = 10):
        super(Player, self).__init__(name=name, x=x, y=y, HP=HP)
        self.initialise()

    # Set player's attributes back to starting values
    def initialise(self):
        super(Player, self).initialise()
        self.keys = 1
        self.red_potions = 0
        self.exit_keys = 0
        self.boss_keys = 0
        self.treasure = 0
        self.trophies = 0
        self.kills = 0
        self.boss_kills = 0
        self.weapon = 1
        self.shield = 1
        self.bombs = 0
        self.maps = 0
        self.armour = Tiles.PLAYER_SKY
        self.available_armour = [Tiles.PLAYER]
        self.treasure_maps = {}
        self.runes = {}
        self.equipment_slots=[]
        self.equipment_slots.append(Tiles.RED_POTION)
        self.equipment_slots.append(Tiles.WEAPON)
        self.equipment_slots.append(Tiles.SHIELD)
        self.equipment_slots.append(Tiles.BOMB_LIT)
        self.effects = {}

    @property
    def score(self):

        rune_count = 0
        for runes in self.runes.items():
            rune_count += len(runes)

        return self.kills + (self.boss_kills * 20) + self.treasure + (self.trophies * 50) + (rune_count * 20)

    def collect_rune(self, rune : str, level_id : int):

        if level_id not in self.runes.keys():
            self.runes[level_id] = []

        level_runes = self.runes[level_id]
        level_runes.append(rune)

    def runes_collected(self, level_id : int = None):

        rune_count = 0

        if level_id is None:
            for runes in self.runes.values():
                rune_count += len(runes)

        elif level_id in self.runes.keys():
            rune_count = len(self.runes[level_id])

        return rune_count

    def maps_collected(self, level_id : int):

        maps = []

        if level_id in self.treasure_maps.keys():
            maps = self.treasure_maps[level_id]

        return maps


    # How much damage does a player take from a monster collision?
    def damage_multiplier(self):
        multiplier = 1

        if self.armour in (Tiles.PLAYER_SPIKE, Tiles.PLAYER_THIEF):
            multiplier = 2
        elif self.armour == Tiles.PLAYER_KNIGHT and random.randint(1,10) > 7:
            multiplier = 0
            print("Your armour protects you!")

        return multiplier

    # How much damage does a player take from a damage over time tile?
    def dot_multiplier(self):
        multiplier = 1

        if self.armour == Tiles.PLAYER_GOLD:
            multiplier = 0

        return multiplier

    # How much damage does a monster take from a player collision?
    def monster_damage_multiplier(self):
        multiplier = 0

        if self.armour == Tiles.PLAYER_SPIKE:
            multiplier = 1

        return multiplier

class Boss(Character):

    NORMAL = "Normal"
    ANGRY = "Angry"
    ANGRY_PCT = 60
    RAGE = "Rage"
    RAGE_PCT = 30

    HP_PCT_TO_STATE = {}

    def __init__(self, name : str, x : int = 1, y : int = 1, width : int = 1, height : int = 1, HP : int = 30, speed : int = 3):
        super(Boss, self).__init__(name=name, x=x, y=y, HP=HP, width=width, height=height)
        self.speed = speed
        self.initialise()

    def initialise(self):
        super(Boss,self).initialise()
        self.state = Boss.NORMAL

    def change_state(self):
        HP_pct = int(self.HP*100/self._HP)
        if HP_pct <= Boss.RAGE_PCT:
            new_state = Boss.RAGE
        elif HP_pct <= Boss.ANGRY_PCT:
            new_state = Boss.ANGRY
        else:
            new_state = Boss.NORMAL

        if new_state != self.state:
            self.state = new_state
            return True
        else:
            return False


class NPC(Character):

    def __init__(self, name : str, x : int = 1, y : int = 1, width : int = 1, height : int = 1, HP : int = 30, tile = Tiles.NPC1, reward = None):
        super(NPC, self).__init__(name=name, x=x, y=y, HP=HP, width=width, height = height)
        self.tile = tile
        self.reward = reward
        self.initialise()


    def initialise(self):
        super(NPC,self).initialise()

class Game:

    LOADED = "LOADED"
    READY = "READY"
    PLAYING = "PLAYING"
    SHOPPING = "SHOPPING"
    PAUSED = "PAUSED"
    GAME_OVER = "GAME OVER"
    END = "END"
    EFFECT_COUNTDOWN_RATE = 4
    DOT_DAMAGE_RATE = 3
    ENEMY_DAMAGE_RATE = 2
    TARGET_RUNE_COUNT = 4
    MAX_STATUS_MESSAGES = 5
    STATUS_MESSAGE_LIFETIME = 16

    DATA_FILES_DIR = os.path.dirname(__file__) + "\\data\\"

    def __init__(self, name : str):

        self.name = name
        self.players = None
        self._state = Game.LOADED
        self.game_start = None
        self.tick_count = 0
        self.status_messages = {}
        self.current_shop_keeper = None

        self.hst = utils.HighScoreTable(self.name)

        ##

        self.level_factory = LevelBuilder()
        self.shop = Shop()
        self._conversations = trpg.ConversationFactory(Game.DATA_FILES_DIR + "conversations.xml")

        ##

    @property
    def state(self):

        if self._state == Game.PLAYING and self.get_current_player().HP <=0:
            self.game_over()

        elif self.is_game_complete() is True:
            self._state = Game.GAME_OVER

        return self._state

    @property
    def trophies(self):

        trophy_count = 0

        for level in self.level_factory.levels.values():
            trophy_count += level.trophies

        return trophy_count

    def save(self, file_name : str = None):

        self.pause(pause = True)

        if file_name is None:
            file_name = "RPGWorld_" + self.get_current_player().name + ".rpg"

        game_file = open(file_name, "wb")
        pickle.dump(self, game_file)
        game_file.close()

        self.add_status_message("Game Saved")

        logging.info("%s saved." % file_name)

    def load(self, file_name : str = None):

        self.pause(pause = True)

        if file_name is None:
            file_name = "RPGWorld_" + self.get_current_player().name + ".rpg"
        try:
            game_file = open(file_name, "rb")
            new_game = pickle.load(game_file)
            game_file.close()

            self.add_status_message("Game Loaded")

            logging.info("\n%s loaded.\n" % file_name)

        except IOError:

            logging.warning("High Score Table file %s not found." % file_name)

        return new_game

    def get_current_floor(self):
        return self.level_factory.get_floor(self.current_floor_id)

    def get_floor(self, floor_id : int):
        return self.level_factory.get_floor(floor_id)

    def get_current_level(self):
        return self.level_factory.get_level(self.current_level_id)

    def get_level(self, level_id : int):
        return self.level_factory.get_level(level_id)

    def get_current_player(self):
        if len(self.players) > 0:
            return self.players[0]
        else:
            return None

    def next_floor(self):

        current_level = self.level_factory.get_level(self.current_level_id)

        floor_ids = sorted(current_level.floors.keys())

        index = floor_ids.index(self.current_floor_id)
        index += 1
        if index >= len(floor_ids):
            index = 0

        self.current_floor_id = floor_ids[index]

        self.get_current_floor().add_player(self.get_current_player())

    def previous_floor(self):
        current_level = self.level_factory.get_level(self.current_level_id)

        floor_ids = sorted(current_level.floors.keys())

        index = floor_ids.index(self.current_floor_id)
        index -= 1
        if index < 0:
            index = len(floor_ids) - 1

        self.current_floor_id = floor_ids[index]

        self.get_current_floor().add_player(self.get_current_player(), position = Floor.EXIT)


    def next_level(self):

        # If you have completed the current level...
        if self.is_level_complete(self.get_current_player(), self.current_level_id) == True:

            self.add_status_message("Leaving {0}...!".format(self.get_current_level().name))

            # Get the id of the next level....
            level_ids = sorted(self.level_factory.levels.keys())
            index = level_ids.index(self.current_level_id)
            index += 1
            if index >= len(level_ids):
                index = 0

            self.current_level_id = level_ids[index]

            self.current_floor_id = min(self.get_current_level().floors.keys())

            self.get_current_floor().add_player(self.get_current_player(), position = Floor.ENTRANCE)

            self.add_status_message("Heading to {0}...!".format(self.get_current_level().name))

        else:
            self.add_status_message("{0} not completed yet!".format(self.get_current_level().name))
            self.get_current_player().back()

    def previous_level(self):

        self.add_status_message("Leaving {0}...!".format(self.get_current_level().name))

        level_ids = sorted(self.level_factory.levels.keys())
        index = level_ids.index(self.current_level_id)
        index -= 1
        if index < 0:
            index = 0

        self.current_level_id = level_ids[index]

        self.current_floor_id = max(self.get_current_level().floors.keys())

        self.get_current_floor().add_player(self.get_current_player(), position = Floor.EXIT)

        self.add_status_message("Heading to {0}...!".format(self.get_current_level().name))

    def is_level_complete(self, player : Player, level_id : int):

        complete = False

        if player.runes_collected(level_id) >= Game.TARGET_RUNE_COUNT:
            complete = True

        return complete

    def is_game_complete(self):
        complete = False

        if self.get_current_player() is not None and self.get_current_player().trophies == self.trophies:
            complete = True

        return complete

    def enter_shop(self):
        self._state = Game.SHOPPING
        self.shop.get_shop_keeper(self.get_current_level().id)

    def get_current_shop_keeper(self):
        return self.shop.current_shop_keeper

    def exit_shop(self):
        self._state = Game.PLAYING
        self.get_current_player().y += 1

    def talk(self, npc : NPC):

        self.clear_status_messages()

        life = 20

        # talk to them...
        # msg = "You talk to {0}".format(npc.name)
        # self.add_status_message(msg)
        conversation = self._conversations.get_conversation(npc.name)

        # If they don't have a conversation then raise failure message
        if conversation is None:
            msg = "{0} has nothing to say to you.".format(npc.name)

        elif conversation.is_completed() and npc.reward is not None:
            msg = "{0} vanishes and leaves behind a reward!".format(npc.name)
            self.get_current_floor().vanish_npc()

        elif conversation.is_completed() and random.randint(1,10) > 7:
            msg = "{0} vanishes and leaves without a trace.".format(npc.name)
            self.get_current_floor().vanish_npc()

        # Otherwise attempt the conversation
        else:
            # Get the next line in the conversation
            next_line = conversation.get_next_line()

            # Attempt it and if it succeeds...
            if next_line.attempt():

                # Print what the NPC has to say
                msg = "{0}:'{1}'".format(npc.name, next_line.text)

        self.add_status_message(msg, life)


    def initialise(self):

        logging.info("Initialising {0}...".format(self.name))

        self._state = Game.READY
        self.players = []
        self.player_scores = {}
        self.effects = {}
        self.tick_count = 0

        self.hst.load()

        #
        #
        self.shop.initialise()

        self.floors = FloorBuilder()
        self.floors.initialise()

        self.level_factory = LevelBuilder()
        self.level_factory.initialise(self.floors)

        self.current_level_id = self.level_factory.level1
        self.current_floor_id = self.get_current_level().floor1

        # Load in the map
        self.locations = trpg.LocationFactory(Game.DATA_FILES_DIR + "locations.csv")
        self.locations.load()
        self.maps = trpg.MapFactory(self.locations)
        self.maps.load("RuneQuest", 1, Game.DATA_FILES_DIR + "maplinks.csv")
        self.current_map = self.maps.get_map(1)

        self._conversations.load()

    def add_player(self, new_player : Player):

        if self.state != Game.READY:
            raise Exception("Game is in state {0} so can't add new players!".format(self.state))

        logging.info("Adding new player {0} to game {1}...".format(new_player.name, self.name))

        self.players.append(new_player)
        self.player_scores[new_player.name] = 0

    def items_in_inventory(self, tile_name):

        count = 0
        player = self.get_current_player()

        if tile_name == Tiles.BOMB:
            count =  player.bombs
        if tile_name == Tiles.BOMB_LIT:
            count =  player.bombs
        elif tile_name == Tiles.TREASURE:
            count =  player.treasure
        elif tile_name == Tiles.SHIELD:
            count =  player.shield
        elif tile_name == Tiles.WEAPON:
            count = player.weapon
        elif tile_name == Tiles.KEY:
            count = player.keys
        elif tile_name == Tiles.RED_POTION:
            count = player.red_potions
        else:
            logging.warn("Don't know how to find item {0} in a player's inventory.".format(tile_name))

        return count

    def move_player(self, dx : int, dy : int):

        # If in a non-playing state then do nothing
        if self.state != Game.PLAYING:
            return

        current_level = self.get_current_level()
        current_floor = self.get_current_floor()
        current_player = self.get_current_player()

        current_floor.move_player(dx, dy)
        self.check_collision()

        tile = current_floor.get_player_tile()

        if tile == Tiles.EMPTY:
            pass

        elif tile in FloorPlan.EXIT_TO_DIRECTION.keys():

            print("You found the exit {}!".format(FloorPlan.EXIT_TO_DIRECTION[tile]))

            try:
                self.check_exit(FloorPlan.EXIT_TO_DIRECTION[tile])
            except Exception as err:
                print(err)
                self.get_current_player().back()

        elif tile == Tiles.KEY:
            current_player.keys += 1
            current_floor.set_player_tile(Tiles.EMPTY)
            self.add_status_message("You found a key!")
            print("Found a key!")

        elif tile == Tiles.BOSS_KEY:
            current_player.boss_keys += 1
            current_floor.set_player_tile(Tiles.EMPTY)
            self.add_status_message("You found a Boss Key!")
            print("Found a boss key!")

        elif tile in Tiles.MONSTERS:
            print("Hit a monster!")

        elif tile in Tiles.NPCS:
            current_player.back()
            if current_floor.npc is not None:
                self.talk(current_floor.npc)

        elif tile in Tiles.TRAPS:
            success = False

            if current_player.armour == Tiles.PLAYER_KNIGHT and random.randint(1,10) > 5:
                success = True
                self.add_status_message("Your armour protects you from the trap!")

            elif current_player.armour == Tiles.PLAYER_THIEF and random.randint(1,10) > 5:
                success = True
                self.add_status_message("You disabled the trap!")

            if success is False:
                current_player.HP -= 1
                current_floor.set_player_tile(Tiles.EMPTY)
                self.add_status_message("Ouch! You walked into a trap!")

            elif success is True:
                current_floor.set_player_tile(Tiles.EMPTY)

        elif tile in Tiles.PLAYER_DOT_TILES:
            print("You stood in something nasty!")

        elif tile == Tiles.RED_POTION:
            self.use_item(tile, decrement = False)
            current_floor.set_player_tile(Tiles.EMPTY)
            self.add_status_message("You feel healthier!")
            print("Some HP restored")

        elif tile == Tiles.REPLENISH:

            if current_player.HP < 10:
                current_player.HP = 10
                self.add_status_message("You are fully healed!")
                current_floor.set_player_tile(Tiles.REPLENISH_SPENT)
            else:
                self.add_status_message("You have full health!")

            current_player.back()


        elif tile in Tiles.SWAP_TILES.keys() and self.get_current_player().moved() is True:
            current_floor.set_player_tile(Tiles.SWAP_TILES[tile])
            print("You found a {0} to {1} swappable tile!!".format(tile,Tiles.SWAP_TILES[tile]))

            if tile in (Tiles.SWITCH, Tiles.SWITCH_LIT):
                self.get_current_floor().switch()
                self.add_status_message("You operated the switch.")
                print("You operated the switch. Switch on = {0}".format(self.get_current_floor().switch_on))

        elif tile in (Tiles.TREASURE, Tiles.TREASURE10, Tiles.TREASURE25):
            current_floor.set_player_tile(Tiles.EMPTY)
            if tile == Tiles.TREASURE10:
                current_player.treasure += 10
            elif tile == Tiles.TREASURE25:
                current_player.treasure += 25
            else:
                current_player.treasure += 1
            self.add_status_message("You found some treasure!")
            print("You found some treasure!")

        elif tile == Tiles.TREASURE_CHEST:
            print("You found a treasure chest...")
            success = False

            if current_player.keys > 0:
                current_player.keys -= 1
                success = True
            elif current_player.armour == Tiles.PLAYER_THIEF and random.randint(1,10) > 5:
                success = True
                print("You picked the lock!")

            if success is True:
                rewards = [Tiles.KEY, Tiles.SHIELD, Tiles.WEAPON,Tiles.BOMB, Tiles.RED_POTION, \
                                                                 Tiles.TREASURE10, Tiles.TREASURE25]

                # #  If the progress allows the add a map as an optional reward
                # level_progress = current_player.runes_collected(current_level.id) + \
                #                  len(current_player.maps_collected(current_level.id))
                #
                # if level_progress < Game.TARGET_RUNE_COUNT:
                #     rewards.append(Tiles.MAP)

                current_floor.set_player_tile(random.choice(rewards))
                self.add_status_message("You opened the treasure chest!")
                print("...and you opened it!")

            else:
                print("You don't have a key to open it!")
                self.add_status_message("You don't have a key to open it!")

            current_player.back()

        elif tile == Tiles.WEAPON:
            current_floor.set_player_tile(Tiles.EMPTY)
            current_player.weapon += 1
            print("You found a weapon!")

        elif tile == Tiles.SHIELD:
            current_floor.set_player_tile(Tiles.EMPTY)
            current_player.shield += 1
            print("You found a shield!")

        elif tile == Tiles.BOMB:
            current_floor.set_player_tile(Tiles.EMPTY)
            current_player.bombs += 1
            print("You found a bomb!")

        elif tile in Tiles.PLAYER_ARMOUR:
            current_floor.set_player_tile(Tiles.EMPTY)
            current_player.armour = tile
            self.add_status_message("You found some armour!")
            print("You found some armour!")

        elif tile == Tiles.TROPHY:
            current_floor.set_player_tile(Tiles.EMPTY)
            current_player.trophies += 1
            print("You found a trophy!")
            self.add_status_message("You found a chalice!")
            if current_player.trophies == self.trophies:
                self.game_over()

        elif tile == Tiles.DOOR:
            print("You found a door...")
            success = False

            # First see if we can pick the lock...
            if current_player.armour == Tiles.PLAYER_THIEF and random.randint(1,10) > 5:
                success = True
                print("You picked the lock!")

            # Then see if we have a key...
            elif current_player.keys > 0:
                current_player.keys -= 1
                success = True

            if success is True:
                current_floor.set_player_tile(Tiles.DOOR_OPEN)
                print("...and you opened it!")
            else:
                current_player.back()
                self.add_status_message("The door is locked!")
                print("...but the door is locked!")

        elif tile == Tiles.BOSS_DOOR:
            print("You found a boss door...")
            if current_player.boss_keys > 0:
                current_player.boss_keys -= 1
                current_floor.set_player_tile(Tiles.BOSS_DOOR_OPEN)
                self.add_status_message("You opened the Boss Door!")
                print("...and you opened it!")
            else:
                current_player.back()
                self.add_status_message("The Boss Door is locked!")
                print("...but the boss door is locked!")

        elif tile == Tiles.NEXT_LEVEL:
            print("You found the entrance to the next level!")
            self.next_level()

        elif tile == Tiles.PREVIOUS_LEVEL:
            print("You found the entrance to the previous level!")
            self.previous_level()

        elif tile == Tiles.SHOP:
            self.enter_shop()
            self.add_status_message("Welcome to the shop!")

        elif tile == Tiles.MAP:
            level_secrets = current_level.secrets

            if len(level_secrets) > 0:

                if current_level.id not in current_player.treasure_maps.keys():
                    current_player.treasure_maps[current_level.id] = []

                found_secrets = current_player.treasure_maps[current_level.id]

                unfound_secrets = set(level_secrets) - set(found_secrets)

                if len(unfound_secrets) > 0:

                    secret = random.choice(list(unfound_secrets))
                    current_player.treasure_maps[current_level.id].append(secret)
                    current_floor.set_player_tile(Tiles.EMPTY)
                    print("You found a secret treasure map!")
                    self.add_status_message("You found a secret treasure map!")

                else:
                    print("No more secrets to find for this level!")

        self.check_secret()

        #print("Player move={0}".format(self.get_current_player().moved()))

    def check_exit(self, direction):

        # Check if a direction was even specified
        if direction is "":
            raise (Exception("You need to specify a direction e.g. NORTH"))

        # Check if the direction is a valid one
        direction = direction.upper()
        if direction not in trpg.MapLink.valid_directions:
            raise (Exception("Direction %s is not valid" % direction.title()))

        # Now see if the map allows you to go in that direction
        links = self.current_map.get_location_links_map(self.get_current_floor().id)

        # OK stat direction is valid...
        if direction in links.keys():
            link = links[direction]

            # ..but see if it is currently locked...
            if link.is_locked() is True:
                raise (Exception("You can't go %s - %s" % (direction.title(), link.locked_description)))

            # If all good move to the new location
            print("You go %s %s..." % (direction.title(), link.description))

            self.add_status_message("You go {0} {1}...".format(direction.title(), link.description))

            self.current_floor_id = link.to_id
            self.get_current_floor().add_player(self.get_current_player(), FloorPlan.REVERSE_DIRECTION[direction])

        else:
            raise(Exception("You can't go {0} from here!".format(direction)))

    def check_secret(self):

        current_level = self.get_current_level()
        current_floor = self.get_current_floor()
        current_player = self.get_current_player()

        pos = current_floor.get_treasure_xy()

        # If there is a secret treasure on this floor...
        # ...and the player is currently at the same location..
        # ...and the player has some treasure maps for this level...
        if pos is not None and \
            pos == (current_player.x, current_player.y) \
            and current_level.id in current_player.treasure_maps.keys():

            self.hint()

            # See if the player has the exact map for the secret...
            # ...and there are still some runes to find on the current level...
            found_maps = current_player.treasure_maps[current_level.id]

            if (current_floor.id, (pos)) in found_maps and len(current_level.hidden_runes) > 0:

                found_rune = random.choice(current_level.hidden_runes)
                current_player.collect_rune(found_rune, current_level.id)
                current_player.back()
                current_level.hidden_runes.remove(found_rune)
                current_floor.treasure_found()
                current_player.treasure_maps[current_level.id].remove((current_floor.id, (pos)))
                print("You found the secret treasure {0} and you have now collected {1}.".format(found_rune,
                                                                                                 current_player.runes))

                self.add_status_message("You have found a hidden rune!")

            else:
                pass
                #print("You haven't got the map for this secret yet.")

    def hint(self):

        current_level = self.get_current_level()
        current_floor = self.get_current_floor()
        current_player = self.get_current_player()

        pos = current_floor.get_treasure_xy()

        print("Floor {3}.  Player is at ({0},{1}\nRune is at {2}".format(current_player.x,current_player.y,pos, current_floor.id))
        print("Player's maps for level {0}: {1}".format(current_level.id, current_player.maps_collected(current_level.id)))


    def check_collision(self):

         # Check if the player has collided with something?
        if self.get_current_floor().is_collision() is True:

            print("collision!")
            current_tile = self.get_current_floor().get_player_tile()

            if current_tile in Tiles.MONSTERS:

                if Tiles.WEAPON in self.effects.keys():
                    print("You killed an enemy with your sword")
                    self.get_current_player().kills += 1
                    self.get_current_floor().kill_monster()

                elif Tiles.SHIELD in self.effects.keys():
                    print("You defended yourself with your shield")

                elif self.tick_count % Game.ENEMY_DAMAGE_RATE == 0:
                    self.get_current_player().HP -= 1 * self.get_current_player().damage_multiplier()
                    print("HP down to %i" % self.get_current_player().HP)

                    if self.get_current_player().monster_damage_multiplier() > 0:
                        self.get_current_player().kills += 1
                        self.get_current_floor().kill_monster()
                        print("You killed an enemy when you collided with it!")

            elif current_tile in Tiles.PLAYER_DOT_TILES:

                if Tiles.SHIELD in self.effects.keys():
                    print("You defended yourself with your shield")
                elif self.tick_count % Game.DOT_DAMAGE_RATE == 0:
                    self.get_current_player().HP -= 1  * self.get_current_player().dot_multiplier()
                    print("HP down to %i" % self.get_current_player().HP)

            elif self.get_current_floor().hit_boss() is True:
                if Tiles.WEAPON in self.effects.keys():
                    self.get_current_floor().boss.HP -= 1
                elif Tiles.SHIELD in self.effects.keys():
                    print("You defended yourself with your shield")
                elif self.tick_count % Game.ENEMY_DAMAGE_RATE == 0:
                    damage = self.get_current_player().damage_multiplier()
                    self.get_current_player().HP -= damage
                    self.get_current_floor().boss.HP += damage
                    print("HP down to %i" % self.get_current_player().HP)

                if self.get_current_floor().boss.HP <= 0:
                    self.get_current_player().boss_kills += 1
                    self.add_status_message("You killed {0}!".format(self.get_current_floor().boss.name))
                    self.get_current_floor().kill_boss()


    def use_item(self, item_type, decrement : bool = True):

        player = self.get_current_player()

        if self.items_in_inventory(item_type) == 0 and decrement == True:
            logging.info("Player {0} does not have any items of type {1} in their inventory to use!".format(player.name, item_type))
            return

        current_tile = self.get_current_floor().get_player_tile()

        print("Player {0} using item {1}".format(player.name, item_type))

        if item_type == Tiles.RED_POTION:
            if decrement is True:
                player.red_potions -=1
                player.HP += 1
            elif decrement is False:
                player.HP += 1

        elif item_type in Tiles.EXPLODABLES:
            if current_tile == Tiles.EMPTY and decrement is True:
                player.bombs -= 1
                self.add_expodable(item_type, self.get_current_player().x,
                                   self.get_current_player().y)
            elif decrement is False:
                self.add_expodable(item_type, self.get_current_player().x,
                                   self.get_current_player().y)

        elif item_type == Tiles.WEAPON:
            if decrement is True:
                self.add_effect(item_type)
                player.weapon -= 1
            elif decrement is False:
                self.get_current_floor().set_player_tile(Tiles.EMPTY)
                self.add_effect(item_type)

        elif item_type == Tiles.SHIELD:
            if decrement is True:
                self.add_effect(item_type)
                player.shield -= 1
            elif decrement is False:
                self.get_current_floor().set_player_tile(Tiles.EMPTY)
                self.add_effect(item_type)

    def add_effect(self, effect_type, effect_count = 20):
        print("Starting effect {0} for {1} ticks".format(effect_type, effect_count))

        if effect_type in self.effects.keys():
            raise Exception("Effect {0} already active for another {1} ticks.".format(effect_type, self.effects[effect_type]))

        self.effects[effect_type] = effect_count

    def add_expodable(self, tile, x, y):
        self.get_current_floor().add_explodable(tile, x, y)

    def start(self):

        if self.state != Game.READY:
            raise Exception("Game is in state {0} so can't be started!".format(self.state))

        logging.info("Starting {0}...".format(self.name))

        self.get_current_floor().add_player(self.get_current_player())

        self._state = Game.PLAYING
        self.game_start = time.time()

    def pause(self, pause : bool = None):

        if self.state not in (Game.PLAYING, Game.PAUSED):
            raise Exception("Game is in state {0} so can't be paused!".format(self.state))

        if pause is True:
            self._state = Game.PAUSED
        elif pause is False:
            self._state = Game.PLAYING
        elif self.state == Game.PLAYING:
            self._state = Game.PAUSED
        else:
            self._state = Game.PLAYING


    def tick(self):

        if self.state != Game.PLAYING:
            raise Exception("Game is in state {0} so can't be ticked!".format(self.state))

        logging.info("Ticking {0}...".format(self.name))

        self.update_status_messages()

        if self.state in (Game.PAUSED, Game.SHOPPING):
            return

        self.tick_count += 1

        self.get_current_floor().tick()

        # If the player has collided then take damage
        self.check_collision()

        if self.tick_count % Game.EFFECT_COUNTDOWN_RATE == 0:
            expired_effects = []
            for effect in self.effects.keys():
                if self.effects[effect] > 0:
                    self.effects[effect] -= 1
                elif self.effects[effect] == 0:
                    print("Stopping %s effect." % effect)
                    expired_effects.append(effect)

            for effect in expired_effects:
                del self.effects[effect]

    def add_status_message(self, new_msg : str, life : int = STATUS_MESSAGE_LIFETIME):
        self.status_messages[new_msg] = life

    def clear_status_messages(self):
        self.status_messages = {}

    def update_status_messages(self):

        expired_msgs = []

        for msg, count in self.status_messages.items():
            count -= 1
            if count < 0:
                expired_msgs.append(msg)
            else:
                self.status_messages[msg] = count

        for msg in expired_msgs:
            del self.status_messages[msg]



    def get_scores(self):

        scores = []

        for player_name, score in self.player_scores.items():

            scores.append((player_name, score))

        return sorted(scores,key=itemgetter(1, 0), reverse=True)

    def is_high_score(self, score: int):
        return self.hst.is_high_score(score)

    @property
    def elapsed_time(self):
        elapsed_seconds = time.time() - self.game_start
        return time.gmtime(elapsed_seconds)

    def game_over(self):

        if self._state != Game.GAME_OVER:

            logging.info("Game Over {0}...".format(self.name))

            print("Game Over")

            self.status_messages = {}

            player = self.get_current_player()

            self.player_scores[player.name] = player.score

            self.hst.add(player.name, player.score)
            self.hst.save()

            self._state=Game.GAME_OVER

    def end(self):

        logging.info("Ending {0}...".format(self.name))

        self._state=Game.END

        self.hst.save()

    def print(self):

        print("Printing {0}...".format(self.name))


class Shop:

    def __init__(self):
        self.shop_keepers = {}
        self.shop_keepers_by_level = {}
        self.item_prices = {}
        self.current_shop_keeper = None


    def initialise(self):
        self.load_shop_keepers()
        self.load_item_prices()

    def get_shop_keeper(self, level_id : int = 1):

        if level_id not in self.shop_keepers_by_level.keys():

            shop_keeper_name = random.choice(list(self.shop_keepers.keys()))
            self.shop_keepers_by_level[level_id] = self.shop_keepers[shop_keeper_name]
            del self.shop_keepers[shop_keeper_name]

        self.current_shop_keeper = self.shop_keepers_by_level[level_id]

        return self.current_shop_keeper

    def buy_item(self, item_type, player : Player):

        if item_type not in self.item_prices.keys():
            raise Exception("Item {0} not in stock!".format(item_type))

        item_price = self.item_prices[item_type]

        if self.item_prices[item_type] > player.treasure:
            raise Exception("Player {0} does not have enough money to buy that!".format(player.name))

        if item_type == Tiles.BOMB and self.current_shop_keeper.bombs > 0:
            player.bombs += 1
            player.treasure -= item_price
            self.current_shop_keeper.bombs -=1
            self.current_shop_keeper.treasure += item_price

        elif item_type == Tiles.KEY and self.current_shop_keeper.keys > 0:
            player.keys += 1
            player.treasure -= item_price
            self.current_shop_keeper.keys -=1
            self.current_shop_keeper.treasure += item_price

        elif item_type == Tiles.RED_POTION and self.current_shop_keeper.red_potions > 0:
            player.red_potions += 1
            player.treasure -= item_price
            self.current_shop_keeper.red_potions -=1
            self.current_shop_keeper.treasure += item_price

        elif item_type == Tiles.WEAPON and self.current_shop_keeper.weapon > 0:
            player.weapon += 1
            player.treasure -= item_price
            self.current_shop_keeper.weapon -=1
            self.current_shop_keeper.treasure += item_price

        elif item_type == Tiles.SHIELD and self.current_shop_keeper.shield > 0:
            player.shield += 1
            player.treasure -= item_price
            self.current_shop_keeper.shield -=1
            self.current_shop_keeper.treasure += item_price

        elif item_type == Tiles.MAP and self.current_shop_keeper.maps > 0:
            player.maps += 1
            player.treasure -= item_price
            self.current_shop_keeper.maps -=1
            self.current_shop_keeper.treasure += item_price


    def load_shop_keepers(self):

        shop_keeper_names = ("Zordo", "Bylur", "Fenix", "Thof", "Korgul", "Trodh", "Ogbog", "Lasar", "Xenux", "Kaylor")

        for shop_keeper_name in shop_keeper_names:

            shop_keeper = Player(shop_keeper_name)
            self.load_store_items(shop_keeper)
            self.shop_keepers[shop_keeper.name] = shop_keeper

    def load_item_prices(self):
        self.item_prices[Tiles.KEY] = random.randint(5,10)
        self.item_prices[Tiles.RED_POTION] = random.randint(5, 10)
        self.item_prices[Tiles.BOMB] = random.randint(8, 15)
        self.item_prices[Tiles.WEAPON] = random.randint(8, 15)
        self.item_prices[Tiles.SHIELD] = random.randint(8, 15)
        self.item_prices[Tiles.MAP] = random.randint(5, 10)

    def load_store_items(self, shop_keeper : Player):

        shop_keeper.bombs = random.randint(1,4)
        shop_keeper.keys = random.randint(1,5)
        shop_keeper.red_potions = random.randint(3, 6)
        shop_keeper.weapon = random.randint(1, 5)
        shop_keeper.shield = random.randint(1, 5)
        shop_keeper.maps = random.randint(0, 5)


class FloorPlan:

    EXIT_NORTH = "NORTH"
    EXIT_SOUTH = "SOUTH"
    EXIT_EAST = "EAST"
    EXIT_WEST = "WEST"
    EXIT_UP = "UP"
    EXIT_DOWN = "DOWN"

    EXIT_TO_DIRECTION = { Tiles.WEST : EXIT_WEST,
                          Tiles.EAST : EXIT_EAST,
                          Tiles.NORTH : EXIT_NORTH,
                          Tiles.SOUTH : EXIT_SOUTH,
                          Tiles.UP : EXIT_UP,
                          Tiles.DOWN : EXIT_DOWN}

    REVERSE_DIRECTION = { EXIT_WEST : EXIT_EAST,
                          EXIT_EAST : EXIT_WEST,
                          EXIT_NORTH : EXIT_SOUTH,
                          EXIT_SOUTH : EXIT_NORTH,
                          EXIT_UP : EXIT_DOWN,
                          EXIT_DOWN : EXIT_UP}

    def __init__(self, id : int, plan : list):

        self.id = id
        self.entrance = None
        self.exits = {}
        self.exit = None
        self.secret = None
        self.height = len(plan)
        self.width = len(plan[0])
        self.plan = [[Tiles.EMPTY for x in range(self.height)] for x in range(self.width)]
        for y in range(0, len(plan)):
            row = plan[y]
            for x in range(0, min(self.width, len(row))):
                self.set_tile(row[x],x,y)

        for exit in self.exits.values():
            x,y = exit
            self.safety_zone(x, y, 4, 4)

        if self.entrance is None:
            self.random_entrance()

        # Create safety zones around the entrance and exits
        if self.entrance is not None:
            self.safety_zone(self.entrance[0], self.entrance[1], 4, 4)

        if self.exit is not None:
            self.safety_zone(self.exit[0], self.exit[1], 4, 4)



    def is_valid_xy(self, x : int, y : int):
        result = False

        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            result = True

        return result

    def get_tile(self, x : int, y : int):

        if self.is_valid_xy(x,y) is False:
            raise Exception("Trying to get tile at ({0},{1}) which is outside of the floorplan!".format(x,y))

        return self.plan[x][y]

    def set_tile(self, tile_name, x : int, y: int):

        if self.is_valid_xy(x,y) is False:
            raise Exception("Trying to set tile {0} at ({1},{2}) which is outside of the floorplan!".format(tile_name,x,y))

        self.plan[x][y] = tile_name

        if tile_name in FloorPlan.EXIT_TO_DIRECTION.keys():
            self.exits[FloorPlan.EXIT_TO_DIRECTION[tile_name]] = (x, y)
            #print("Floor Plan {0} - set {1} exit at ({2},{3}).".format(self.id, FloorPlan.EXIT_TO_DIRECTION[tile_name], x,y))
        elif tile_name == Tiles.START_POSITION and self.entrance is None:
            self.entrance = (x,y)
            self.plan[x][y] = Tiles.EMPTY
        elif tile_name == Tiles.NEXT_LEVEL and self.exit is None:
            self.exit = (x,y)
        elif tile_name == Tiles.PREVIOUS_LEVEL and self.entrance is None:
            self.entrance = (x,y)
        elif tile_name == Tiles.SECRET_TREASURE:
            self.secret = (x,y)
            #print("Floor Plan {2} - set secret at {0},{1}".format(x,y, self.id))

    def random_entrance(self):

        tries = 30

        self.entrance = (1, 1)

        attempts = 0
        while True:
            x = random.randint(0,self.width - 1)
            y = random.randint(0,self.height - 1)
            if self.get_tile(x,y) == Tiles.EMPTY:

                logging.info("Placed entrance at {0},{1}".format(x, y))

                self.entrance = (x, y)
                break

            attempts += 1

            # We tried several times to find an empty square, time to give up!
            if attempts > tries:
                print("Can't find an empty tile to place entrance after {0} tries".format(attempts))
                break


    # Build a safety zone around a specified location
    def safety_zone(self, x, y, height, width):
        for dx in range(-1 * int(width / 2), int(width / 2) + 1):
            for dy in range(-1 * int(height / 2), int(height / 2) + 1):
                if self.is_valid_xy(x + dx,y + dy) is True:
                    if self.plan[x + dx][y + dy] == Tiles.EMPTY:
                        self.plan[x + dx][y + dy] = Tiles.SAFETY


    def get_secret_map(self, width : int = 5, height : int = 5):

        map = None

        if self.secret is not None:
            x, y = self.secret
            map = []
            row = 0
            for dy in range(-1 * int(width / 2), int(width / 2) + 1):
                map.append([])
                for dx in range(-1 * int(height / 2), int(height / 2) + 1):
                    if self.is_valid_xy(x + dx, y + dy) is True:
                        map[row] += self.get_tile(x + dx, y + dy)
                    else:
                        map[row] += Tiles.EMPTY
                row += 1

        return map

    def treasure_found(self):
        if self.secret is not None:
            x,y = self.secret
            self.set_tile(Tiles.RUNE, x, y)
            self.secret = None


class Floor:

    ENTRANCE = "Entrance"
    EXIT = "Exit"
    MONSTER_MOVE_RATE = 3
    BOSS_MOVE_RATE = 1
    EXPLODABLE_COUNTDOWN_RATE = 4
    EXPLODABLE_COUNTDOWN = 10
    SECRET_COUNTDOWN = 4

    def __init__(self, id : int, name : str,
                 treasure_count : int = 0,
                 trap_count : int = 0,
                 key_count = 0,
                 monster_count : tuple = (0,0,0),
                 secret_count : int = 0,
                 switch_tiles : list = None):

        self.id = id
        self.name = name
        self.treasure_count = treasure_count
        self.trap_count = trap_count
        self.monster_count = monster_count
        self.key_count = key_count
        self.secret_count = secret_count
        self.tick_count = 0
        self.switch_on = False
        self.switch_tiles = switch_tiles
        self.monsters = {}
        self.explodables = {}
        self.runes = {}
        self.trophies = 0
        self.floor_plan = None
        self.player = None
        self.boss = None
        self.npc = None
        self.exits = {}

    def initialise(self, floor_plan : FloorPlan):

        self.floor_plan = floor_plan
        self.tick_count = 0

        self.place_tiles(self.secret_count, Tiles.SECRET_TREASURE)
        self.place_tiles(self.key_count, Tiles.KEY)
        self.place_tiles(self.treasure_count, Tiles.TREASURE)
        self.place_tiles(self.trap_count, Tiles.TRAP1)

        m1,m2,m3 = self.monster_count
        self.place_tiles(m1, Tiles.MONSTER1)
        self.place_tiles(m2, Tiles.MONSTER2)
        self.place_tiles(m3, Tiles.MONSTER3)

        for y in range(self.floor_plan.height):
            for x in range(self.floor_plan.width):
                tile_name = self.floor_plan.get_tile(x,y)

                if tile_name in Tiles.MONSTERS:
                    self.floor_plan.set_tile(Tiles.EMPTY, x, y)
                    if (x,y) not in self.monsters.keys():
                        self.monsters[(x,y)] = tile_name

                elif tile_name in Tiles.EXPLODABLES:
                    self.floor_plan.set_tile(Tiles.EMPTY, x, y)
                    self.add_explodable(tile_name, x, y)

                elif tile_name == Tiles.TROPHY:
                    self.trophies += 1

        print(str(self))


    def is_valid_xy(self, x : int, y : int):
        result = False

        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            result = True

        return result

    def tick(self):

        self.tick_count += 1

        if self.tick_count % Floor.MONSTER_MOVE_RATE == 0:
            self.move_monsters()

        if self.tick_count % Floor.BOSS_MOVE_RATE == 0:
            self.move_boss()

        if self.tick_count % Floor.EXPLODABLE_COUNTDOWN_RATE == 0:
            self.tick_explodables()

        if self.tick_count % Floor.SECRET_COUNTDOWN == 0:
            complete_counts = []
            for pos, count in self.runes.items():
                count -=1
                if count > 0:
                    self.runes[pos] = count
                else:
                    x,y = pos
                    complete_counts.append(self.runes[pos])
                    self.floor_plan.set_tile(Tiles.EMPTY, x, y)

            for complete in complete_counts:
                if complete in self.runes.keys():
                    del self.runes[complete]


    def add_player(self, player, position = ENTRANCE):
        self.player = player
        x = self.player.x
        y = self.player.y

        print("Adding player {0} to Floor {1} at position {2}".format(player.name, self.name, position))

        if position == Floor.ENTRANCE and self.floor_plan.entrance is not None:
            x,y = self.floor_plan.entrance
            self.player.x = x
            self.player.y = y

        elif position == Floor.EXIT and self.floor_plan.exit is not None:
            x,y = self.floor_plan.exit
            self.player.x = x
            self.player.y = y

        elif position in self.floor_plan.exits.keys():
            x,y = self.floor_plan.exits[position]
            self.player.x = x
            self.player.y = y

        elif self.floor_plan.entrance is not None:
            x, y = self.floor_plan.entrance
            self.player.x = x
            self.player.y = y

        print("Adding player to entrance at {0},{1}".format(x, y))

    def add_boss(self, boss : Boss):

        print("Adding boss {0} to Floor {1}...".format(boss.name, self.name))

        tries = 30
        attempts = 0
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            boss.x = x
            boss.y = y

            if self.is_empty(boss) is True:
                self.boss = boss
                logging.info("Placed {0} at {1},{2}".format(self.boss.name, x, y))
                print("Placed {0} at {1},{2}".format(self.boss.name, x, y))
                break

            attempts += 1

            # We tried several times to find an empty square, time to give up!
            if attempts > tries:
                print("Can't find an empty tile to place boss {0} after {1} tries".format(boss.name, attempts))
                break
    def add_npc(self, npc : NPC, xy : tuple = None):

        print("Adding NPC {0} to Floor {1}...".format(npc.name, self.name))

        if xy is not None:
            x,y = xy
            npc.x = x
            npc.y = y
            self.npc = npc
            logging.info("Placed {0} at {1},{2}".format(self.npc.name, x, y))
            print("Placed {0} at {1},{2}".format(self.npc.name, x, y))

        else:
            tries = 30
            attempts = 0
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                npc.x = x
                npc.y = y

                if self.is_empty(npc) is True:
                    self.npc = npc
                    logging.info("Placed {0} at {1},{2}".format(self.npc.name, x, y))
                    print("Placed {0} at {1},{2}".format(self.npc.name, x, y))
                    break

                attempts += 1

                # We tried several times to find an empty square, time to give up!
                if attempts > tries:
                    print("Can't find an empty tile to place npc {0} after {1} tries".format(npc.name, attempts))
                    break

    def add_explodable(self, tile, x : int, y : int):

        if tile not in Tiles.EXPLODABLES:
            raise Exception("Trying to add explodable {0} that is not a valid explodable {1}!",format(tile, Tiles.EXPLODABLES))

        self.explodables[(x,y)] = (tile, Floor.EXPLODABLE_COUNTDOWN)

    # Find empty tiles to place items
    def place_tiles(self, item_count, item_type, tries=30):

        for i in range(0, item_count):
            attempts = 0
            while True:
                x = random.randint(1, self.width - 1)
                y = random.randint(1, self.height - 1)
                if self.floor_plan.get_tile(x,y) == Tiles.EMPTY:

                    logging.info("Placed a {0} at {1},{2}".format(item_type, x, y))

                    if item_type in Tiles.MONSTERS:
                        self.monsters[(x, y)] = item_type
                    else:
                        self.floor_plan.set_tile(item_type, x, y)

                    break
                attempts += 1

                # We tried several times to find an empty square, time to give up!
                if attempts > tries:
                    print("Can't find an empty tile to place {0} after {1} tries".format(item_type, attempts))
                    break


    def move_player(self, dx : int, dy : int):

        self.player.x += dx
        self.player.y += dy

        if self.is_valid_xy(self.player.x, self.player.y) is False:
            self.player.back()
            print("Hit the boundary!")

        elif self.get_tile(self.player.x, self.player.y) in Tiles.PLAYER_BLOCK_TILES:
            self.player.back()
            print("Square blocked!")

    def is_collision(self):

        collision = False

        collision_items = list(Tiles.MONSTERS + Tiles.PLAYER_DOT_TILES)

        if self.get_tile(self.player.x, self.player.y) in collision_items:
            collision = True
        elif self.hit_boss() is True:
            collision = True
        elif self.hit_npc() is True:
            collision = True

        return collision

    def is_empty(self, char : Character):
        empty = True

        if isinstance(char, Player) is True:
            block_tiles = Tiles.PLAYER_BLOCK_TILES
            for x in range(char.x, char.x + char.width):
                for y in range(char.y, char.y + char.height):
                    if self.is_valid_xy(x,y) == False:
                        empty = False
                    elif self.get_tile(x,y) in block_tiles:
                        empty = False
                        break

        if isinstance(char, NPC) is True:
            empty_tiles = Tiles.MONSTER_EMPTY_TILES
            for x in range(char.x, char.x + char.width):
                for y in range(char.y, char.y + char.height):
                    if self.is_valid_xy(x,y) == False:
                        empty = False
                    elif self.get_tile(x,y) not in empty_tiles:
                        empty = False
                        break

        elif isinstance(char, Boss) is True:
            empty_tiles = Tiles.MONSTER_EMPTY_TILES
            for x in range(char.x, char.x + char.width):
                for y in range(char.y, char.y + char.height):
                    if self.is_valid_xy(x,y) == False:
                        empty = False
                    elif self.get_tile(x,y) not in empty_tiles:
                        empty = False
                        break

        return empty

    def hit_boss(self):
        hit = False

        if self.boss is not None:
            if self.player.x >= self.boss.x and \
                self.player.x <= (self.boss.x + self.boss.width - 1) and \
                self.player.y >= self.boss.y and \
                self.player.y <= (self.boss.y + self.boss.height -1 ):
                hit = True

        return hit

    def hit_npc(self):
        hit = False

        if self.npc is not None:
            pass

        return hit

    # NPC vanishes and is replaced by a reward if they had one to give
    def vanish_npc(self):
        if self.npc is not None:
            if self.npc.reward is None:
                tile = Tiles.EMPTY
            else:
                tile = self.npc.reward

            self.floor_plan.set_tile(x=self.npc.x, y=self.npc.y, tile_name=tile)
            self.npc = None

    def move_monsters(self):

        new_monsters = {}

        for monster_position in self.monsters.keys():
            x,y = monster_position
            monster_type = self.monsters[monster_position]

            # ..look at a random square around the enemy...
            new_x, new_y = random.choice(((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)))
            new_x += x
            new_y += y

            moved = True

            # If new square is out of bounds...
            if self.is_valid_xy(new_x,new_y) is False:
                #print("Hit boundary")
                moved = False

            # ...if new square is not empty
            elif self.get_tile(new_x, new_y) not in Tiles.MONSTER_EMPTY_TILES:
                #print("Square blocked")
                moved = False

            # ...if the new square contains an enemy
            elif (new_x, new_y) in new_monsters or (new_x, new_y) in self.monsters:
                #print("Square occupied")
                moved = False

            if moved == True:
                new_monsters[(new_x,new_y)] = monster_type
            else:
                new_monsters[(x, y)] = monster_type

        if len(new_monsters) != len(self.monsters):
            print("HELLLLP we have lost a monster")
            raise Exception("We lost a monster x={0},y={1},type={2}".format(x,y,monster_type))

        self.monsters = new_monsters

    def move_boss(self):

        if self.boss is None:
            return

        if self.tick_count % self.boss.speed !=0:
            return

        attempts = 2

        if self.boss.HP <=10:
            attempts = 6
        elif self.boss.HP <=20:
            attempts = 3

        while attempts > 0:

            # ..look at a random square around the boss...
            new_x, new_y = random.choice(((-1, 0), (1, 0), (0, -1), (0, 1)))
            self.boss.x += new_x
            self.boss.y += new_y

            if self.is_empty(self.boss) is False:
                self.boss.back()
                attempts -= 1
            else:
                break

        if self.boss.change_state() is True:
            print("adding difficulties...")
            self.place_tiles(item_count=5,item_type=Tiles.TRAP1)
            self.place_tiles(item_count=5, item_type=Tiles.MONSTER1)

    def kill_monster(self, x : int = None, y : int = None):

        if x is None:
            x = self.player.x

        if y is None:
            y = self.player.y

        if (x,y) in self.monsters.keys():
            del self.monsters[(x,y)]
            print("You killed a monster at ({0},{1})".format(x,y))

    def kill_boss(self):
        if self.boss is not None:
            self.floor_plan.set_tile(x=self.boss.x, y=self.boss.y, tile_name=Tiles.BOSS_KEY)
            self.boss = None

    def tick_explodables(self):

        new_explodables = {}

        for key,value in self.explodables.items():

            x,y = key
            tile, count = value

            count -= 1
            if count > 0:
                new_explodables[key] = (tile,count)

            else:

                for area_y in range(y - 1, y + 2):
                    for area_x in range(x - 1, x + 2):

                        if self.is_valid_xy(area_x, area_y):

                            tile = self.floor_plan.get_tile(area_x,area_y)

                            if (area_x, area_y) in self.monsters.keys():
                                self.player.kills += 1
                                del self.monsters[(area_x,area_y)]
                                print("You killed an enemy with a bomb!")

                            elif (self.player.x, self.player.y) == (area_x, area_y):
                                self.player.HP -= 3
                                print("You were hit by the bomb blast and lost health!")

                            elif tile not in Tiles.INDESTRUCTIBLE_ITEMS:
                                self.floor_plan.set_tile(Tiles.EMPTY, area_x, area_y)

        self.explodables = new_explodables

    def switch(self, setting=None):
        if setting is None:
            self.switch_on = not self.switch_on
        else:
            self.switch_on = setting


    def get_tile(self, x : int, y: int):

        if self.is_valid_xy(x,y)is False:
            raise Exception("Trying to get a tile outside at {0}{1} which is outside of teh floor plan area!".format(x,y))

        tile = self.floor_plan.get_tile(x,y)

        if (x,y) in self.monsters.keys():
            tile = self.monsters[(x,y)]

        elif (x,y) in self.explodables.keys():
            tile, count = self.explodables[(x,y)]
            if count == 1:
                tile = Tiles.BANG

        elif tile == Tiles.SWITCH_TILE and self.switch_tiles is not None:
            if self.switch_on == True:
                tile = self.switch_tiles[1]
            else:
                tile = self.switch_tiles[0]

        elif self.npc is not None and (x,y) == (self.npc.x, self.npc.y):
            tile = self.npc.tile

        if tile == Tiles.SECRET_TREASURE:
            tile = Tiles.EMPTY

        return tile

    def get_player_tile(self):
        return self.get_tile(self.player.x, self.player.y)

    def set_player_tile(self, new_tile):
        self.floor_plan.set_tile(new_tile, self.player.x, self.player.y)

    def __str__(self):
        string = "Floor {1}: '{0} (treasures:{2}, traps:{3})'".format(self.name, self.id, self.treasure_count, self.trap_count)
        if self.floor_plan is not None:
            string += " ({0}x{1})".format(self.floor_plan.width,self.floor_plan.height)

        return string

    def get_treasure_map(self):
        return self.floor_plan.get_secret_map()

    def get_treasure_xy(self):
        return self.floor_plan.secret

    def treasure_found(self):
        x,y = self.floor_plan.secret
        self.runes[(x,y)] = Floor.SECRET_COUNTDOWN
        self.floor_plan.treasure_found()

    @property
    def width(self):
        return self.floor_plan.width

    @property
    def height(self):
        return self.floor_plan.height

class Level:

    DEFAULT_SKIN = "Default"

    def __init__(self, id : int, name : str, skin_name : str = DEFAULT_SKIN):
        self.id = id
        self.name = name
        self.skin_name = skin_name

    def initialise(self):

        self.floors = {}
        self.hidden_runes = list(Tiles.RUNES)

    @property
    def trophies(self):
        trophy_count = 0

        for floor in self.floors.values():
            trophy_count += floor.trophies

        return trophy_count

    @property
    def secrets(self):
        secrets = []
        for floor in self.floors.values():
            secret_pos = floor.get_treasure_xy()
            if secret_pos is not None:
                secrets.append((floor.id, secret_pos))

        return secrets

    @property
    def floor1(self):
        return min(self.floors.keys())


    def add_floor(self, new_floor : Floor):

        self.floors[new_floor.id] = new_floor

    def __str__(self):

        string = "Level {1}: '{0}' ({3}) - {2} floors.".format(self.name, self.id, len(self.floors), self.skin_name)

        for floor in self.floors.values():
            string += "\n\t" + str(floor)

        return string

class FloorBuilder:

    def __init__(self):
        self.floor_plans = {}
        self.floor_configs = {}
        self.floors = {}

    def initialise(self):
        self.floor_plans = {}
        self.floor_configs = {}
        self.floors = {}

        self.load_floor_plans()
        self.load_floors()
        self.build_floor()

    def load_floor_plans(self):

        logging.info("Starting loading floor plans...")

        arena = [
            '/)     (:N:)      (\\',
            ')       888        (',
            '                    ',
            '                    ',
            '                    ',
            '!                  !',
            '!                  !',
            '!\   !       !    /!',
            ':)8  !   !   !   8(:',
            'R88  !   !   !   88R',
            ':\8  !   !   !   8/:',
            '!)   !       !    (!',
            '!                  !',
            '!                  !',
            '                    ',
            '                    ',
            '                    ',
            '        888         ',
            '\       /F\        /',
            '(\     j:S:j      /)',
        ]

        # Start of the Game - Forest Level
        new_floor_plan = [
            '        TNT         ',
            'T        `       T  ',
            '    T    `  T       ',
            ' T      T`         1',
            '         `      Z T ',
            '    T    `          ',
            '  Z     Z`   T      ',
            'W`````````          ',
            '      T  `  T     T ',
            'T       ```         ',
            '    T   `=`````````E',
            '        ``` `Z      z',
            '            `  T    ',
            ' Z /:\      `    T  ',
            '   :s:    T `       ',
            'T  B`B      `       ',
            '   8`8  T   `T   T  ',
            ' T  `````````       ',
            '         `         T',
            '     T   ST T   T   ',

        ]

        floor_id = 0
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))


        # Chapel
        new_floor_plan = [
            '         N          ',
            ' T           T     T',
            '             T   Z  ',
            'T Z  T /:D:\   T    ',
            '       :) (:        ',
            '   T   : ? : T    T ',
            '       :   :        ',
            'T     /:B B:\       ',
            '  /::::)   (::::\   ',
            '  :)  Z  `  Z  (:   ',
            '  D     `-`     D   ',
            '  :\  Z  `  Z  /:   ',
            '  (::::\   /::::)  T',
            '      (:B B:)       ',
            ' T     :   :        ',
            '       :   :  Z     ',
            ' T  Z  :\ /:    T   ',
            '       (:;:)      T ',
            'Z                   ',
            '        T T      T  ',

        ]

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Crypt
        new_floor_plan = [

            ':::::::::N::::::::::',
            ':z:B    :`:     B:z:',
            '::)    Z:`:Z     (::',
            ':B      (D)       B:',
            ':                  :',
            ':   /\        /\   :',
            ':   ()        ()   :',
            ';                  :',
            ';:\      Z       /::',
            ';;:     /:\     /:):',
            ':j:    B:+:B    ;`?:',
            ':::     :`:     (:\:',
            '::)     (D)      (::',
            ':Z  /\        /\   :',
            ':   ()        ()   :',
            ':                  :',
            ':B      B B       B:',
            '::\   /::`::\    /::',
            ':z:B =:z:j:z:   B:z:',
            '::::::::::::::::::::',

        ]

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Library
        new_floor_plan = [

            '::::::::::::::::::::',
            ':,D     (:)        :',
            ':::                :',
            ':                  :',
            ':    \        /    :',
            ':   B::::::::::B  /:',
            ':                :::',
            ':\               _x:',
            ':::              :::',
            'W`D  ::::::::::  _j:',
            ':::              :::',
            ':)               _x:',
            ':                :::',
            ':   B::::::::::B  (:',
            ':    )        (    :',
            ':                  :',
            ':\     B   B      /:',
            '::`:   :   :    :`::',
            ':j`:   :\ /:    :`j:',
            ':::::::::S::::::::::',

        ]

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # The Forest Temple
        new_floor_plan = (
            '             T      ',
            ' T   wwwww      T T ',
            '   wwwwwwwwww       ',
            'T ww::::::::w  T    ',
            ' ww:)     (:w      ',
            'ww:)       :ww /\   ',
            'ww:        :wwww:B  ',
            'w::\    :  ::www::  ',
            '::::::  :  (:::::)  ',
            'W````:  :  ``````` E',
            '`````:  (\ ```````  ',
            '::::D: 88(:::::::\  ',
            'w::) (\888(::www::  ',
            'ww:   (:   :wwww:B  ',
            ' w:\ 8     :ww ()   ',
            'Tww:\     /:w T     ',
            '  ww::::::::w   T   ',
            '   wwwwwwwwww       ',
            ' T    wwww     T  T ',
            '                    ',

        )

        floor_id = 20
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # The Colonnade
        new_floor_plan = (
            ':::::::::::N::::::::',
            ':                /::',
            ':               /) :',
            ': /:\  /:\  /:\/)  :',
            ': :z:  :z:  :z:)   :',
            ': (::  (:)  (:)    :',
            ':   :   :         /:',
            ':   :  B:B       /::',
            ':   :   :        :) ',
            ':\M/:  /:\  /:\     ',
            ':::::  :z:  :z:    E',
            ':`(:)  (:)  (:)     ',
            'W``D         :   :\ ',
            ':`/:\        :   (::',
            ':::::  /:\  /:\   (:',
            ':ww::  :z::::z:    :',
            ':www:\ (:)  (:)    :',
            ':wwww:             :',
            ':wwww:             :',
            ':::::::::S::::::::::',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # The Shrine of the Snake God
        new_floor_plan = (
            '/:::wwww:N:wwww::::\\',
            ': (:www:) (:www:)  :',
            ':  :ww:)   (:ww:   :',
            ':  (::)     (::)   :',
            ':                  :',
            ':                  :',
            ':  /::\     /::\   :',
            ':  :ww:\   /:ww:   :',
            ':  :wB:     :Bw:   :',
            ':  (::)     (::)   :',
            '(\      /:\       /)',
            '8:     /:w:\      :8',
            '8(\     :w:      /)8',
            '88:     :w:      :88',
            '88:     :w:      :88',
            '88(\   /:w:\    /)88',
            ':\8(\ /):w:(\  /)8/:',
            'ww\8:/)8:w:8(\ :8/ww',
            'ww:8()88(:)88(\:8:ww',
            'ww:88888888888()8:ww',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # Priest Quarters
        new_floor_plan = (
            '::::::::::::::::::::',
            ':  ?:   :       :ww:',
            ':   :   :       :ww:',
            ':   :   :     /::ww:',
            ':88 : 8 :  888: (:::',
            ':8::::8:::::8:)    :',
            ':88         8      :',
            ':   8          /::::',
            '::::D:::\      :```:',
            ':) ``` (:      :```:',
            ':   `   :     88``j:',
            ':       :      :```:',
            ':      B:      :::::',
            '::     ::     /)   :',
            ':B      :     :    :',
            ':       :     :    :',
            ':       :     :8   :',
            ':   :   :    8D8   :',
            ':\ R:R /:`:\B/:8   :',
            ':::::::::S::::::::::',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # Altar of Sacrifice
        new_floor_plan = (
            'www::::::::::::::www',
            'ww:)      :   (z:www',
            'w:)       :    (:www',
            ':)        :     (:ww',
            ':    T  /:::\    :ww',
            ': :    B)`:`(B   (:w',
            ':j:      `D`      :w',
            '::)      `:`      (:',
            ':``  T  :::::  T  ``',
            ':M`     :www:     `E',
            ':``     :www:     ``',
            '::\  T  :::::  T  /:',
            ':j:      `:`      :w',
            ': :      `D`     /:w',
            ':      B\`:`/B   :ww',
            ':    T  (:::)   /:ww',
            ':\        :     :www',
            'w:\       :    /:www',
            'ww:\      :   /z:www',
            'www::::::::::::::www',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # The Ruins
        new_floor_plan = (
            'z:                  ',
            '::              :   ',
            ')   T \    T   :::\ ',
            '      ::\        (: ',
            '  T   `-:   :T  T : ',
            ' T    ``:::::     : ',
            '\     /:) :w:  Z  : ',
            ':     :   :w:       ',
            ':ww\  :     )     T ',
            '::::  (: Z    /:\   ',
            ':  :\         :     ',
            ')  ::         :    Z',
            '        /  \  (\    ',
            'T       :ww:   (:   ',
            '     /:::::::       ',
            '  T  :)     )   T   ',
            '     :              ',
            'T    (   `   Z      ',
            '        ```      T  ',
            '       ``S``        ',

        )

        floor_id = 30
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))


        # The Tomb of Fallen Knight
        new_floor_plan = (
            '::::::)  /wwww::::::',
            ':   D    :wwww:Z  (:',
            ':   :    :wwww:    :',
            ':   :    :wwww:    :',
            ':   ;    (::::)  /::',
            ':j  :           ::ww',
            '::::)           wwww',
            ':M`:    Z     www::w',
            ':``:   :::   ww:::::',
            ':``:   :+:  www:```:',
            ':D::  /:`:\   ww``j:',
            ':  :   B`B    :ww``:',
            ':  (:         :ww:::',
            ':             (:wwww',
            ':              (::ww',
            ':      ::      /:www',
            ':       :     /:ww::',
            ':   :\  :     :ww:::',
            ':   ::  :    /:ww:z:',
            ':::::::::::::::ww:::',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # The old Tower
        new_floor_plan = (
            ' T  T  T T   TT  TT ',
            'T TT TT T TT T TT  T',
            'T T   T   T T   TT  ',
            'T                 T ',
            ' T       /:\   T   T',
            'T   T   /:::\     T ',
            'T      /)   (\   TT ',
            ' TT   /)     (\    T',
            'T   :::   /   :   T ',
            'TT  ``:   :   :\  T ',
            'W  ?``D (:::\ +: T T',
            'T   ``:   :   :)   T',
            ' TT :::   )   :   T ',
            'T     (\     /)   T ',
            'T    T (\   /)  T  T',
            ' TT     (:::)     =T',
            'T     T  (:)   T  T ',
            ' T  T            T  ',
            'T   T T T   T TT  T ',
            ' TTT T T TTT T  TTT ',

        )

        floor_id = 50
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # Back and Forth
        new_floor_plan = (
            '/::::::::::::::::::\\',
            ':-`  :             :',
            ':``  :             :',
            ':        :         :',
            ':        :         :',
            '::::::::::::::\  :::',
            ':             :    :',
            ':             :    :',
            ':       :::   :    :',
            ':  :::   :    :    :',
            ':   :    :   :::   :',
            ':   :   :::        :',
            ':   :              :',
            ':   :              :',
            ':   (::::::::;::::::',
            ':        :         :',
            ':        :         :',
            ':   :         :  ``:',
            ':   :         :  `+:',
            '(::::::::::::::::::)',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # The Maze
        new_floor_plan = (
            '~~~.~~~~~~~~~.~~~~~~',
            '~~~~~~~~~.~~~~~~~~~.',
            '~~:::::::::::::::~~~',
            '.~:          :  :.~~',
            '~~:  /::\    :  :~~~',
            '~~:  :- :    :  :~~~',
            '~.:  :          :~~~',
            '~~:  (::\     :::~~~',
            '.~:     (\      :~.~',
            '~~:      (\     :~~~',
            '~~::;:    (:\   :~~~',
            '.~: O:      :   :~~~',
            '~~::::   :  :   :.~~',
            '~~:  :   : +:   :~~~',
            '~~:  :   (::)   :~~.',
            '~.:             :~~~',
            '~~:::::::::::::::~~~',
            '~~~~~~~~~~~~~~~~~~.~',
            '~~.~~~.~~~~~~.~~~~~~',
            '~~~~~~~~~.~~~~~~~~~~',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))


        # The Guard House
        new_floor_plan = (
        '~~~.~~~~~.~.~~~~.~~~',
        '.~~~~~~.~~~~~~.~~~~.',
        '~~:::::::::::::::~~~',
        '~~:             :~.~',
        '~~:             :~~~',
        '.~:  /:     :\  :.~~',
        '~~:  ::     ::  :~~~',
        '~~:  :  : :  :  :~~.',
        '~.:     :+:     :~~~',
        '~~:     :::     :.~~',
        '~.:     :-:     :~~~',
        '~~:  :  : :  :  :~.~',
        '.~:  ::     ::  :~~~',
        '~~:  (:     :)  :~~.',
        '~~:             :~~~',
        '~.:             :.~~',
        '~~:::::::::::::::~~~',
        '~~~~.~~~~~~.~~~.~~~.',
        '~~.~~~.~~~~~~~~~~~~~',
        '.~~~~~~~~~.~~.~~~.~~',
        )
        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # The Tower Top
        new_floor_plan = (
            '~~~~~~~~~~~.~~~~~~~~',
            '~~.~~~~~.~~~~~~.~~~~',
            '~~~~~.~~~~~~.~~~~~~~',
            '~~~~~~~~~~~~~~~~~.~~',
            '.~~~~:::::::::~~~~~~',
            '~~~~:) j:-:j (:~.~~~',
            '~.~~:   :`:   :~~~~~',
            '~~~~:  ::`::  :~~~.~',
            '~~~~:    `    :~~~~~',
            '~~~~:    `    :~~.~~',
            '~~~~:    `    :~~~~~',
            '~~.~:    M    :~.~~~',
            '.~~~:  x/+\\x  :~~~.~',
            '~~~~:\\x:::::x/:~~~~~',
            '~~~~~:::::::::~~~~~~',
            '~~.~~~~~~~~~~~~~~.~~',
            '~~~~~~~.~~.~~~.~~~~~',
            '~~~~.~~~~~~~~~~~~~~~',
            '~.~~~~~~~~~.~~~~.~~~',
            '~~~~~~.~~~~~~~~~~~~~',

        )
        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # Arena
        new_floor_plan = (
            'j       (:R:)      j',
            '!                  !',
            '!                  !',
            '!                  (',
            ')                   ',
            '        !    !      ',
            '        !    !     /',
            '\       !    !     :',
            ':::\              /:',
            ':``:8            8::',
            'W``F8            8`E',
            ':``:8            8::',
            ':::)              (:',
            ')       !    !     :',
            '        !    !     (',
            '\       !    !      ',
            '!                   ',
            '!                   ',
            '!      /\  /\       ',
            'j   /!!!::R:!!!!\  j',

        )

        floor_id = 98
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # Portal1
        new_floor_plan = [
            '::::::::::::::::::::',
            ':)     :`j`:      (:',
            ':      :```:       :',
            ':      (:D:)       :',
            ':       888        :',
            ':R                 :',
            ':B  B              :',
            ':::::```     B:\   :',
            ':`````¬```     (\ /:',
            ':````¬¬````     (:::',
            ':`L`¬¬¬¬¬¬`````````E',
            ':````¬¬````     /:::',
            ':`````¬```     /) (:',
            ':::::```     B:)   :',
            ':B  B              :',
            ':x      888        :',
            ':      /:D:\       :',
            ':      :```:       :',
            ':\     :```:      /:',
            '::::::::::::::::::::',

        ]

        floor_id = 99
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))


        # The Start of ICE Level
        new_floor_plan = (
            '!!!!:::::N::wwwww!!!',
            '!! !!:  ( )     w:!!',
            '!           z   (::!',
            ' T      T        (:!',
            '                z (w',
            ':   T              w',
            ':\       T    z    !',
            'W                  !',
            '::    z  :  T     /:',
            ':)      /:\      :::',
            '!   T   :l:      ``E',
            '!      ::`::     :::',
            '       (```)   T  !:',
            ' T /:\            !!',
            '   :s:    T       !:',
            '   z8z            ::',
            '    8   T    T  z  !',
            '!                  !',
            ':\    !!:`:    /:\H!',
            ':::www!::S::www:::!!',

        )

        floor_id = 100
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # Ice Cave
        new_floor_plan = (
            'wwwwwwwwwwwwwwwwwwww',
            'ww!! www  !!!   wwww',
            'w!!  ww    !!    www',
            'ww    w     !!    ww',
            'ww           !    ww',
            'ww                w:',
            'www      /     Z  w:',
            'w!      Z:        ::',
            'w!     /::!w      `E',
            'w  Z  www!!ww   !!::',
            '!      wwwww   !!!!:',
            '!         w   !!  !:',
            '!   \             !w',
            'w   :       Z      w',
            'w   :\Z       ww   w',
            'w   (::w      w:   w',
            'w     www   www:   w',
            'ww    ww: Zwwww:!  w',
            'ww!!!www:`:wwww:!! w',
            'wwwwwwww:S:wwww:wwww',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # Castle Black
        new_floor_plan = (

            '   T  !!::::::::::::',
            '     !!!:  :     !!:',
            ' T   !!:)  :      !:',
            '     !!:   D      !:',
            'T  T  !:   :     !!:',
            '     !!:j  :    /:::',
            '  ::!!!:::::   /:  :',
            ' /:::::)   B  B:)  :',
            '       ````````:```:',
            'W      ````````D```E',
            '       ````````:```:',
            ' (:::::\   B  B:\  :',
            '  ::!!!:::::   (:  :',
            '     !!:j  :    (:::',
            'T     !:   :     !!:',
            '  T   !:   :      !:',
            '     !!:   D      !:',
            '    !!!:\  :     !!:',
            ' T  !!!!: -:    !!!:',
            '     !!!::::::::::::',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))


        # Frost Bite Dungeon
        new_floor_plan = (

            '::::::::::::::::::::',
            ':1   :``?:?``:    j:',
            ':    D`  :  `D     :',
            ':    :`  :  `: 1   :',
            ':    :` B:B `:     :',
            ':    :`  :  `:     :',
            ':!   :`  :  `:::::;:',
            ':!   :` /:\ `:     :',
            ':!!  :` :+: `:     :',
            '::::::` :`: `D     :',
            ':    :` (`) `:  2  :',
            ':    D`     `:     :',
            ':    :`     `:!    :',
            ': 2  :```B```:!!  j:',
            ':::::::D:::D::::::::',
            ':        :       !!:',
            ':        :        !:',
            ':       !:!  2   ``:',
            ':1    !!!:!!     `-:',
            '::::::::::::::::::::',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # Oubliette
        new_floor_plan = (

            'wwwwwwwwwwwwwwwwwwww',
            'ww:::::::wMw::::::ww',
            'w::     (w`w)   j::w',
            'w:              !!:w',
            'w:               !:w',
            'w:!     !!!!!    !:w',
            'w:!    !!!!!!!    :w',
            'w:!   !!:::::!!   :w',
            'w:!!  !!:```:!!   :w',
            'w:!   !!:`+`:!!   :w',
            'w:    !!:```:!!   :w',
            'w:    !!::D::!!   :w',
            'w: ``  !!!`!!!    :w',
            'w:  `    !`!      :w',
            'w:  `     `      !:w',
            'w:  ````  `      !:w',
            'w:   ` ``````   !!:w',
            'w::         `  !!::w',
            'ww::::::::::::::::ww',
            'wwwwwwwwwwwwwwwwwwww',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # Shard Throne
        new_floor_plan = (

            'wwwwwwwwwwwwwwwwwwww',
            'wwwwwwwwwwwwwwwwwwww',
            '::::::::::::::::::ww',
            ':      (:)      (:ww',
            ':       `        :ww',
            ':j:     `        :ww',
            '::)   /\`/\     /:ww',
            ':)   B::;::  B::::ww',
            ':`      `    ¬```::w',
            'W``     `    ¬¬¬¬M:w',
            ':`      `    ¬```::w',
            ':\   B:::::  B::::ww',
            '::\   ()`()     (:ww',
            ':j:     `        :ww',
            ':       `        :ww',
            ':       `        :ww',
            ':      /:\      /:ww',
            '::::::::::::::::::ww',
            'wwwwwwwwwwwwwwwwwwww',
            'wwwwwwwwwwwwwwwwwwww',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # Dwarf Hall
        new_floor_plan = (
            'wwwwwwwwwwwwwwwwwwww',
            'wwwwwwwwwwwwwwwwwwww',
            'wwwwww::::::::::::ww',
            'wwwwww:!! :  : !!:ww',
            'wwwwww:!        !:ww',
            ':::::w:!        !:ww',
            ':   :w:          :ww',
            ':   ::)        :::ww',
            ':  /:````````````:ww',
            'W  D````````````M:ww',
            ':  (:````````````:ww',
            ':   ::\        :::ww',
            ':   :w:          :ww',
            ':::::w:          :ww',
            'wwwwww:!         :ww',
            'wwwwww:!  :  :  j:ww',
            'wwwwww::::::::::::ww',
            'wwwwwwwwwwwwwwwwwwww',
            'wwwwwwwwwwwwwwwwwwww',
            'wwwwwwwwwwwwwwwwwwww',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # The Crevasse
        new_floor_plan = (
            '!wwwwww     wwwwww!!',
            '! wwww      www!!w!!',
            '!  w    z  www   ww!',
            '        wjww!w   ww!',
            'w      wwwww!w    ww',
            'ww    wwwww        w',
            'ww      www     z  w',
            ' ww      ww  z      ',
            '         ww         ',
            'W      z w         E',
            '    w    w    w     ',
            '    w        www  z ',
            '   www       wwwwww ',
            '   www      wwwwwwww',
            '   wwww    wwww  www',
            'w   www   ww  w  www',
            'w   wwww      w   ww',
            'w   !w!w          ww',
            'ww  !w!w!!  z    jww',
            'ww !!w!!w!!    !!www',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # Shard Mountain
        new_floor_plan = (
            'wwwwwwwwwwwwwwwwwwww',
            'wwwwwww!!j:ww: !!!ww',
            'wwwww!!!  ::::   !ww',
            'wwww      :  :    ww',
            'wwww         :     w',
            'ww:::\       :     w',
            'w::  :   :   ::    w',
            'w:)  :   :         w',
            'w:```::  :          ',
            'w:M``D8  :          ',
            'w:```::  :     Z   E',
            'w:\  :   :Z    :    ',
            'ww:::)   ::    :    ',
            'wwwww          :   w',
            'www                w',
            'ww                 w',
            'ww     Z    :    !!w',
            'ww!!   :  :::   !!ww',
            'www!!! ::::wwwZ!!www',
            'wwwwwwwwwwwwwwwwwwww',
        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        floor_id = 198
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(arena))

        # Frozen End
        new_floor_plan = (

            ':::::::::N::::::::::',
            ':)      (`)       (:',
            ':                  :',
            ':                  :',
            ':      /:::\       :',
            ':    /:)```(::\    :',
            ':  /:)  `L`   (:\  :',
            ':  :B   ```    B:  :',
            ':  :)   `¬`    (:  :',
            ':  :    `¬`     :  :',
            ':  :    `¬`     :  :',
            ':  (:   `¬`    :)  :',
            ':   (:  `¬`   :)   :',
            ':    (:  ¬   :)    :',
            ':     :  ¬   :     :',
            ':     B ¬¬¬  B    w:',
            ':        ¬        w:',
            ':w               ww:',
            ':www            www:',
            '::::::::::::::::::::',

        )

        floor_id = 199
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))


        # Desert Level Start
        new_floor_plan = (

            'www:     N       www',
            'ww:)              ww',
            'ww:   z        T   w',
            '::)                :',
            ')                 /:',
            '       /www\    T (:',
            '     (:::::::)     :',
            '  T    :```:       w',
            '       )`l`(      ww',
            'W       ```        E',
            '              z   ww',
            '    z              w',
            '        T       T  w',
            ' T                 w',
            '              T   ww',
            '                  ww',
            'w       T T        w',
            'w                  w',
            'ww      :D:    wwwHw',
            'wwww   /:S:\  wwwwww',

        )

        floor_id = 200
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Tomb Entrance
        new_floor_plan = (

            'wwwwww::`N`::wwwwwww',
            'wwwwwww:```:wwwwwwww',
            'wwwwwww:```:wwwwwwww',
            'ww:::::::D::::::::ww',
            'ww:    : ` :     :ww',
            'ww:    : ` :     :ww',
            'ww:    z ` z     :ww',
            'ww:      `       (::',
            '::)8     `         (',
            ')  8/:::::::::\     ',
            '        ```         ',
            '        ```         ',
            '   /   \```/   \    ',
            '   :   :```:   :    ',
            '   )   (```)   (    ',
            'w       ```       w ',
            'ww      ```       ww',
            'w      z```z     www',
            'w      w```w       w',
            'ww  wwww`S`www     w',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # Tomb of the Pharoah
        new_floor_plan = (

            '::::::::::::::::::::',
            ':  :            : j:',
            ':  D            D  :',
            ':  :     -      :  :',
            '::::\  \   /   /::::',
            ':ww)   (:::)    (ww:',
            ':w       :        w:',
            ':    /   :    \    :',
            ':   /)   :    (\   :',
            ':  /)   (:)    (\  :',
            ':        `         :',
            ':        `         :',
            ':     \  `  /      :',
            ':w    (\ ` /)     w:',
            ':ww    : ` :     ww:',
            '::::   ( ` )    ::::',
            ':  :     `      :  :',
            ':  D     `      D  :',
            ':  :    /`\     :  :',
            ':::::::::S::::::::::',

        )




        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))


        # Chamber of the Sarcophagus
        new_floor_plan = (

            'wwww::::::::::::wwww',
            'ww::)          (::ww',
            'w:)              (:w',
            'w:       +        :w',
            ':)      (:)       (:',
            ':   B   !!     B   :',
            ':        !!!       :',
            ':                  :',
            '::::::\      /::::::',
            'wwwwww:``````:wwwwww',
            'wwwwww:``````:wwwwww',
            '::::::)  `   (::::::',
            ':j       `        j:',
            ':        `         :',
            ':   B    `     B   :',
            ':\       `        /:',
            'w:     /)`(\      :w',
            'w:\    :```:     /:w',
            'ww::\  :`M`:   /::ww',
            'wwww::::::::::::wwww',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))


        # Oasis
        new_floor_plan = (

            '                    ',
            '                    ',
            ' /:\  T        /:\  ',
            ' :s:         T :j:  ',
            '       wwww         ',
            'z  z   weeww     z  ',
            '      wweeew        ',
            '    wwweeeew        ',
            'w wwweeeewww        ',
            'wwweeeeeww         E',
            'eeeeeewww    T      ',
            'eeeeeww             ',
            'eeeeww              ',
            'eewww      z        ',
            'eew   /:\           ',
            'eew   : :     T     ',
            'www   z z        T  ',
            'w         T         ',
            'w   T         T     ',
            'ww     S            ',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Pyramid entrance
        new_floor_plan = (

            '       N            ',
            '                    ',
            '                T   ',
            ' T    ``            ',
            '   :  ``  :  T      ',
            '   (: `` :)         ',
            'T   : `` :        T ',
            '   w: `` :w         ',
            ' www: `` :www       ',
            '::::) `` (::::::\   ',
            ')     ``       (:   ',
            '     ````       :   ',
            '     ```` \     :www',
            '     ```` :  \  :www',
            'W /:::::::)  :::::::',
            '  :          )  :  :',
            '  (             :  :',
            '                D  :',
            '                :  :',
            '\   /:S:\       ::::',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Western Sanctum
        new_floor_plan = (

            'wwww::::::::::::wwww',
            'wwww:          :wwww',
            'wwww:          :wwww',
            'wwww: !        :wwww',
            'wwww:          :::::',
            'wwww:   :::::      :',
            ':::::   B : B      :',
            ':   :     :    !   :',
            ':   :\    :   !!  ::',
            ':   :` !  :       `E',
            ':   D`    :       ::',
            ':   :`    :   (:   :',
            ':   :)    ;    :   :',
            ':M  :   B : B  :   :',
            ':::::   :::::  :   :',
            'wwww:          :   :',
            'wwww: !        :\  :',
            'wwww:              :',
            'wwww:              :',
            'wwww::::::::::::::::',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Inner Temple
        new_floor_plan = (
            ':::::::::N::::::::::',
            ':)     :```:      (:',
            ':      (```)       :',
            ':  !   88888   !!  :',
            ':  !!    B     !   :',
            ':                  :',
            ':                  :',
            '::::::)  B  (:::::::',
            ':)                (:',
            ':                  :',
            ':        B         :',
            ':      /:::\       :',
            ':  ::::)```(::::   :',
            ':       ```        :',
            ':       ```        :',
            ':   !   `M`   !!   :',
            ':  !!  /:::\   !!  :',
            ':     /:eee:\      :',
            ':\    :eeeee:     /:',
            ':::::::eeeee::::::::',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Wadi
        new_floor_plan = (

            'wwwwwwwww      wwwww',
            'ww   ww           ww',
            'w     w            w',
            '      w             ',
            '  z        z       /',
            '             :``:``:',
            '             ``````E',
            '    !!z !!   :``:``:',
            '     !!!!    ww    (',
            'W      !!  wwwww    ',
            '   z         wwww   ',
            '               www  ',
            '          z         ',
            '     z           z  ',
            '                    ',
            ' z                  ',
            'w   z   w          w',
            'w       w  z       w',
            'ww     ww       wwww',
            'wwww  wwwww   wwwwww',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Ancient City
        new_floor_plan = (

            '   wwww::::::       ',
            '      w:j   :       ',
            '       :    :       ',
            '\      :::D::       ',
            ':          z  ::::  ',
            ':             :ee:  ',
            ':     z  z    :ee:  ',
            ':`:`:       :::ee:::',
            'W````       :eeeeee:',
            ':`:`:       :eeeeee:',
            ':     z  z  :::ee:::',
            ':             :ee:  ',
            ':             :ee:  ',
            ')          z  :::: E',
            '                    ',
            '  ::::D:::          ',
            ' w:R     :         w',
            ' w:      :w        w',
            'ww:      :ww      ww',
            'ww::::::::www   wwww',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Palace
        new_floor_plan = (

            '             wwwwwww',
            'z    z     wwwwwwwww',
            '         wwwww::::::',
            '        ww:::::!! R:',
            ' z  :::::::!  :    :',
            '    :     :   :    :',
            '    :     :   :    :',
            '  /::B   ::  ::)  /:',
            '         (   (`````:',
            'W   !!     !  ````M:',
            '       !      `````:',
            '         /   /`````:',
            '  (::B   ::  ::\  (:',
            '    :     :   :    :',
            '    :     :!  :    :',
            ' z  :::;:::!! :    :',
            '        ww:::::   j:',
            '         wwwww::::::',
            'z    z     wwwwwwwww',
            '            wwwwwwww',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        floor_id = 298
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(arena))

        # Desert Level End
        new_floor_plan = (
            '::::::ww:N:ww:::::::',
            ':)  (:::) (:::)   (:',
            ':                  :',
            ':                  :',
            ':                  :',
            ':    /:\   /::\    :',
            ':  /:: :   :  ::\  :',
            ':  :   )```(    :  :',
            ':  :    ```     :  :',
            ':  :    ```     :  :',
            ': /:    ```     :\j:',
            ':::::   ```    :::::',
            ':www::  ```   ::www:',
            ':wwww:: ```  ::wwww:',
            ':wwwww: ```  :wwwww:',
            ':wwwww: ```  :wwwww:',
            ':wwwww: ```  :wwww::',
            ':wwww:) :`:  (:ww:::',
            ':www:)  :L:   (ww:::',
            '::::::::::::::::::::',

        )

        floor_id = 299
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Cave Level Start
        new_floor_plan = (
            '::::)(:::)(::N::::::',
            ':)         () ()  (:',
            ':   l              :',
            ')                /::',
            '\      /\    Z   :ee',
            ':      (::\      :ee',
            ':  /\   :::      (::',
            ':  ::\  (::\       :',
            ')  (:)    ()      /:',
            'W             /\   E',
            ':\            ()  (:',
            '::                 :',
            ':)    /:\          (',
            ':   Z (:)          /',
            ')           /:\    :',
            '\           ::)   /:',
            ':           :)    ::',
            ':  /:\     /:H   /::',
            ':\ :::\   /::\   :::',
            ':::::::\S/::::::::::',

        )

        floor_id = 300
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))


        # Canal
        new_floor_plan = (
            '::::)(:weew:::::::::',
            ':::)  (weew)   (::::',
            '::)    weew-     (::',
            '::    wwwwww      ::',
            ':)                (:',
            ':             www  (',
            ':     wwwwww  wsw  /',
            ')      weew   ```  :',
            'W      weew       /:',
            '\      weewwwwwwwwww',
            ':  Z   weeeeeeeeeeee',
            ':      weeeeeeeeeeee',
            ':      wwwwwwwwwwwww',
            ':       (:)    (::::',
            ': /\            ::::',
            ':::)            (:::',
            '::)             /:::',
            '::\             ::::',
            ':::\  Z /\    Z/::::',
            ':::::::::::\S/::::::',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Cathedral
        new_floor_plan = (
            ':::::::)N(::::::::::',
            ':::::)      (:::::::',
            '::)             (:::',
            ':      Z          (:',
            ':\        Z        :',
            ':w   B             :',
            ':w              B  :',
            'ww`      /:\       :',
            'W``    /:::::\     :',
            'ww`    ::::::)  Z  :',
            ':w     (:::)      /:',
            ':w Z    (:)      /::',
            ':)       :\   /:::::',
            ':        (:   (:::::',
            ':   B    /:       (:',
            ':      Z (:\       :',
            ')        /::    Z  -:',
            '\        :::       :',
            ':\     Z/:::\     /:',
            '::::\/::::::::::::::',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Goblin Prison
        new_floor_plan = (
            '::wwwwww:::wwwww(:::',
            '::wj   w)(:w  Rw (::',
            ')(w    w  (w   w  (:',
            '\ w    w   wwDww   :',
            ': wwDwww           :',
            ':                 /:',
            ':\                (:',
            'wwwwwwB            :',
            'w````ww     ````Bw (',
            'wM```D      `````www',
            'w````ww     ```````E',
            'wwwwwwB     `````www',
            '::)         ````Bw(:',
            ':)                 :',
            ')  wwDww          /:',
            '\  w   w          ::',
            ':  w   w    wwDww ::',
            ') /w   w\  /w   w/::',
            '\/:wO  w:\/:w  |w:::',
            ':::wwwww::::wwwww:::',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Goblin King Hall
        new_floor_plan = (
            ':::)(::)(www:::)((::',
            ':-   ()  www      (:',
            ')         B        (',
            '\                  /',
            ':\   Z         Z   (',
            'w:                 /',
            'w: B               :',
            'w:jw   ww   ww    /:',
            'wwww   ww   ww  ww::',
            'w```   ``   ``  `www',
            'wj`````````````````E',
            'w```   ``   ``  `www',
            'wwww   ww   ww  ww::',
            'w:jw   ww   ww    (:',
            'w: B               :',
            'w:                 (',
            ':)              Z  /',
            ':\        B        :',
            '::\/\    www      /:',
            ':::::\/::www:\/:\/::',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Treasure Room
        new_floor_plan = (
            '::::::::::::::::::::',
            ':z: (w)  (::)(w) :z:',
            '::)  w    ()  w  (::',
            ':    w        w    :',
            ')    D        D    :',
            '\    w        w    (',
            ':    wwwwwwwDww    /',
            ':\   w        w  /;:',
            ':wwDww        wwww;:',
            ':)   w  wwwwwww  (;:',
            ':    w  w+w   w    (',
            ')    w  ```   w    /',
            '\    w        w  ` :',
            ':\   w        w``` :',
            '::   wwwwwwwwww  ` :',
            ':(\    (:w:)       (',
            ') D     (:)        /',
            '\ :     /:\      /::',
            ':M:\   /:::\     :z:',
            ':::::\/:::::::::::::',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))


        # Guard's Quarters
        new_floor_plan = (
            '::::N:::::::::::::::',
            ':)      (w)   ()  j:',
            ':        w         :',
            ':        D        /:',
            ':        w        (:',
            ')     wwwwwww      :',
            '\   Z/w)    w      :',
            ':\ /::w ``` w\    /:',
            '::;:::w ``` wwwwwww:',
            '::;) (w  `  w)    (:',
            ':)    ww ` ww      :',
            ')      B ` B       :',
            '\        `     Z   :',
            ':   w    `         (',
            ':\  w    `         /',
            ':wwww   B`B  Z   /::',
            ':)      w`w     /:ee',
            ':       w`w     :eee',
            ':\     /w`w\    :eee',
            ':::\/:::wSw:::\/:eee',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Stone Crypt
        new_floor_plan = (
            ':::::::::::::)(:::::',
            ':wwwww:z::)     (:::',
            ':w+  (:::)         (',
            ':w    (:)          /',
            ':w     B     /\    (',
            ':w           ::R   /',
            ':w\        /::::\  :',
            ':::\  ```` (::::)  :',
            ':::)         ::    :',
            ':)           ()    :',
            ')       /\         :',
            '\       ::         (',
            ':\    /::::\ ````  /',
            '::B   (::::)    `  :',
            ':)  `  R::      ` /:',
            ':   `   ()     wDww:',
            ':j  `          w```:',
            ':   ```        w`M`:',
            ':\            /w```:',
            '::\/:::\/::\/:::::::',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Grotto
        new_floor_plan = (
            'eeee:::::::)(:::::::',
            'eee:)  ()    (:::ee:',
            'e::)         /::eeee',
            ':)         /:::eeeee',
            ':      Z  /:eeeeewwe',
            ')  Z     B:eeeewwwww',
            '\         ()   w  Bw',
            '::\          ¬    Rw',
            ' (:\   B    ¬¬¬¬¬  w',
            '+¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬¬Mw',
            ' /:)   B    ¬¬¬¬¬  w',
            '::)          ¬    Rw',
            ':         /\   w  Bw',
            ')        B:eeeewwwww',
            '\  Z  Z   (:eeeeewww',
            ':          (::eeewwe',
            ':\          (::eeeee',
            'e::\         (::eeee',
            'eee:::\Z =    ::eee:',
            'eeeeee:::::\/:::::::',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Chasm
        new_floor_plan = (
            '::::::wwwNwww::)(:::',
            ':::)(::w¬¬¬w::)   (:',
            ':)    (w¬¬¬w)      :',
            ':     Bw¬¬¬wB      :',
            ':              Z   (',
            ':\                 /',
            '::\   /w!!!w\    /::',
            '!!!!!!!!!!!!!!!!!!!!',
            '!!!!!!!!!!!!!!!!!!!!',
            '!!!!!!!!!!!!!!!!!!!!',
            '::)   (:w!w:)     (:',
            ':)     ww`ww       (',
            ':       w`w      Z /',
            ':       w`w        :',
            ') Z      `    Z    :',
            '\     Z  `         :',
            ':        `        /:',
            ':       w`w      /::',
            ':\  Z  ww`ww Z   ;=:',
            '::\/::::wSw:::\/::::',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Hoard
        new_floor_plan = (
            ':!!!wwwwwwwwwww!!!!!',
            '!!!!!w!!!!!!!w!!!!!!',
            '!:::!!!wwwww!!!:::::',
            ':)j(:::) j (:::::)_(',
            ':   (w       w)    /',
            ':    w  ¬¬¬  w     :',
            ':    w  ¬¬¬  w    R:',
            ':    w  ¬¬¬  w     :',
            ') R  wB ¬¬¬ Bw     :',
            '\    ww¬¬¬¬¬ww     :',
            ':\  ,ww¬¬¬¬¬ww    /:',
            'wwDwwwB¬¬w¬¬BwwwDwww',
            ':)     ¬¬w¬¬      (:',
            ':      ¬www¬       :',
            ':      ¬¬w¬¬       (',
            ':     B¬¬w¬¬B      /',
            ')     w¬¬¬¬¬w     /:',
            '\     w¬¬¬¬¬w   /:::',
            ':\= /:w¬¬¬¬¬w:\ ::::',
            ':::::wwwwSwwww::::::',

        )

        floor_id +=1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        floor_id = 398
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(arena))

        # Cave Level End
        new_floor_plan = (
            ':::::::::N::::::::::',
            '() (:::)```   (:::::',
            '\   (:) ```     ::::',
            ':               (::)',
            ':                  /',
            ':                 /:',
            ':\     wwwww     /::',
            'wwwww  w£££w  wwwwww',
            '!!!!w  w£££w  weeeee',
            '!!!!w  w£££w  weeeee',
            '!!!!w  wwwww  weeeee',
            '!!!!w         weeeee',
            'wwwww         wwwwww',
            ':)     B   B     (::',
            ')      w   w       (',
            '\      w`¬`w       /',
            ':   /::w`¬`w       :',
            ':   :::w`¬`w\      :',
            ':\ /:::w`L`w:\    /:',
            ':::::::::::::::\/:::',
        )

        floor_id = 399
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Chaos Level Start
        new_floor_plan = (
            ':\    (:::::)  N  (:',
            '::      (:)        (',
            ':)       :          ',
            ')       /:\   /\   /',
            '   /\   :::   ()   :',
            '   ()   (:)        (',
            '        `l`        /',
            '\       ```        :',
            'W``````````` ` ``  :',
            ')        `      ` /:',
            '             /\ ` ::',
            '             () ` ()',
            ' /\    /\/\     `  /',
            ' ()    ::::   `````E',
            '       (::)   `    (',
            '              ` /\  ',
            '         `````` ()  ',
            '         `          ',
            '\/\     /D\         ',
            ':::\    :S:        H',

        )

        floor_id = 900
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Chamber of the Deceiver
        new_floor_plan = (
            '/:)(::::)(:)(::::::\\',
            ':)        :       (:',
            ':        /:\       :',
            ':      wwwwwww     :',
            ':      w`````w     :',
            ')    _ w  _  w _  /:',
            '\                www',
            ':\        B       `w',
            'ww`     /:::\     `w',
            'W````  8D`,`D8    `E',
            'ww`     (:::)     `w',
            ':)        B       `w',
            ')                www',
            '\                 (:',
            ':    _ w  _  w _   :',
            ':      w`````w     (',
            ':      wwwwwww     /',
            ':        (:)       :',
            ':\        :     - /:',
            '(:::::::\/:\/::::::)',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Pool of the Miasma
        new_floor_plan = (
            'ww!!!!!!!!!!!!!!!!!!',
            'w!!!!!!!!!!!!!!!!!!!',
            '!!!!:)()()(::)(:!!!!',
            '!!!:)          (:!!!',
            '!!:)            (:!!',
            '!!:    Z    Z    :!!',
            '!!w\     `      /w!!',
            '!!wwwB   `    Bwww!!',
            '!ww     ```      ww!',
            '!w`   ```+```    `w!',
            '!w`     ```      `w!',
            '!ww\     `      Zww!',
            '!!wwwB   `    Bwww!!',
            '!!w)            jw!!',
            '!!\              :!!',
            '!!:\     M      /:!!',
            '!!!:\  Z       /:!!!',
            '!!!!:\/:\/\/:\/:!!!!',
            'w!!!!!!!!!!!!!!!!!!!',
            'ww!!!!!!!!!!!!!!!!!!',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Desolation
        new_floor_plan = (
            ':!!!:::wwNww::::::::',
            ': !!  (w```w)    j(:',
            ': !!   `````      !!',
            ':  !!! ww`ww    !!!!',
            ':   !!!!w`w!!  !!! !',
            ':    !!!w`w!!!!!   :',
            ':\     !w`w!!!!    :',
            'ww     ww`ww      /:',
            'w`  Z    `        ww',
            'W`       `        `w',
            'w`  ``````  Z   ```E',
            'ww   ww  `        `w',
            ':)   ww  `        ww',
            ':        `  ````  (:',
            ':        `  `ww    :',
            ':   Z    ````ww    :',
            '!        `         :',
            '!!!      `         :',
            '!!!!!  ww`ww\     /:',
            '!::!!!!!wSw:::\j/::)',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Maze
        new_floor_plan = (
            '/:::::::)N(::::::::\\',
            ':)                (:',
            ':                  :',
            ':        T         :',
            ':   T          Z   :',
            ':                  :',
            ':      Z```      Z :',
            ':     ww```ww      :',
            ':      w```w       :',
            ') T  `````````     (',
            'W    ````,````  T  E',
            '\    `````````     /',
            ':      w```w       :',
            ':  T  ww`_`ww    T :',
            ':       ```        :',
            ':                  :',
            ':   T    T     T   :',
            ':                  :',
            ':\ Z  Z      Z   Z/:',
            '(:::::::\S/::::::::)',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))
        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))
        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))
        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Pilgrim's Reach
        new_floor_plan = (
            'wwww)(::)N(:::)(wwww',
            'wR`w     `      w`|w',
            'w``w     `      w``w',
            'wwDw     ` Z    wDww',
            ':)       `        (:',
            ')        `         (',
            '\       B`B        /',
            ':      ww`ww    Z  :',
            ':  Z  Bw```wB      :',
            ':      ``M``       :',
            ':\    Bw```wB      :',
            ':)     ww`ww       :',
            ':       B B        :',
            ':  Z             ? (',
            ':                  /',
            ':      Z          /:',
            ')               wDww',
            '\_/\            w``w',
            '::::\  Z /\   Z/w`,w',
            ':::::\/:::::\/::wwww',

        )

        floor_id = 910
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Shadow Cave
        new_floor_plan = (
            '/::::::!!!!!!!:::::\\',
            ':)    (:::!!!:)   (:',
            ':        (:::)    /:',
            ')               T ::',
            '\-/ww  T          (:',
            ':::ww       T      (',
            ':::)               /',
            ':)      /\    /:\  :',
            ')       ww    www  :',
            '\       ww\   wsw  :',
            ')  T     ()   B`B  :',
            '\             ```  (',
            ':    T     T  ```  /',
            ':                  (',
            ': T             T  /',
            ')       ```        :',
            '\    T  w`w  T     (',
            ':        `         /',
            ':\       `        /:',
            '(:::\/::\S/::\/::::)',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Divide
        new_floor_plan = (
            '/:)    (wNw)     (:\\',
            ':)      w`w       (:',
            ')        `    Z    (',
            '   Z     `         /',
            '       ww`ww      /:',
            '\  Z  /w```w\     (:',
            'wwwwwwww`M`wwwwwwwww',
            '!!!!!!!w```w!!!!!!!!',
            '!!!!!!!wwwww!!!!!!!!',
            '!!!!!!!w```w!!!!!!!!',
            'wwwwwwww`+`wwwwwwwww',
            ':)    (w```w)    (::',
            ')      ww`ww      (:',
            '         `    Z    :',
            '  Z      `         (',
            '         `Z         ',
            '     Z   `          ',
            '\        `     Z   /',
            ':\      w`w       /:',
            '(:\    /wSw\     /:)',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # tunnel
        new_floor_plan = (
            '/:)(::::)N(:::::)(:\\',
            ':)  (::) ` (:::)  (:',
            ')    ::  `  (::\   (',
            '  Z  :: ```  (:)    ',
            '     ()  `          ',
            '                   /',
            '                   (',
            '        /:\         ',
            '    /\ /:::\ /:\    ',
            '  /:::::::::::::\  Z',
            '  :::::)R:::)j(::   ',
            '  (::)  /::)  /::   ',
            '   (:   :::\  (:)   ',
            '    :R  ()()        ',
            '    :\              ',
            '    ()   `   Z  /\  ',
            '        ```     ()  ',
            '\        `         /',
            ':\     /w`w\      /:',
            '(:\ Z /:wSw::\/:\/:)',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Map Room
        new_floor_plan = (
            '/::::)(wwwwww)(::::\\',
            ':)                (:',
            ':                  :',
            ':   _    M   _  Z  :',
            ':                  :',
            ':\     _           :',
            ':w        _     _ /:',
            ':wZ _        _    ww',
            'www     Z         `w',
            'W``            ````w',
            'www    _  _  _ ¬¬¬_w',
            ':w             ````w',
            ':w                `w',
            ':)  _             ww',
            ':                 (:',
            ':     Z wDw  _  _  :',
            ':  _    wDw        :',
            ':       wDw        :',
            ':\     /w,w\   Z  /:',
            '(:::\/::::::\/:::::)',

        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        floor_id = 998
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(arena))

        # Chaos Level End
        new_floor_plan = (
            '/:::::::)N(::::::::\\',
            ':)       `        (:',
            ':       ```        :',
            ':   Z   ```    Z   (',
            '\      ww`ww       /',
            ':\     ww`ww      /:',
            ':::\   (w`w)     /::',
            ':::)     `      /:::',
            ':)       `      (:::',
            ')        &        (:',
            '\        `         (',
            ':     `&```&`      /',
            ') j      &      j  :',
            '\        `         (',
            ':     Z  `  Z      /',
            ':       `¬`    /:\ (',
            ')/:\    `¬`   /:!:\/',
            '/:!:\   `¬`  /:!!!::',
            '!!!!!\ ``L`` :!!!!!!',
            '(::::)/:\`/:\(:::::)',

        )

        floor_id = 999
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))


        new_floor_plan = (

            ':::::)  /:\  (::::::',
            ':)       :        (:',
            ':        :         :',
            ':       /:\        :',
            ':     /::l::\      :',
            ':     : `¬` :      :',
            ':  B    `¬`     B  :',
            ':       `¬`        :',
            ':  B    `¬`     B  :',
            ':       `¬`        :',
            ':  B    `¬`     B  :',
            ':       `¬`        :',
            ':  B    `¬`     B  :',
            ':       `¬`        :',
            ':       `¬`        :',
            ':   /\   ¬   /\    :',
            ':   :    ¬    :    :',
            ':   :         :    :',
            ':\ /:    G    :\  /:',
            '::::::::::::::::::::',

        )

        floor_id = 1000
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))


        logging.info("Finished loading floor plans. {0} floor plans loaded.".format(len(self.floor_plans.keys())))

    def load_floors(self):

        logging.info("Started loading floor configs...")

        # id,name,treasures,traps,keys,monsters(1,2,3),secrets,swap tiles


        # Forest World - Start
        new_floor_data = (0,"Ancient Woods",5,0,0,(0,0,5),1)


        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (1,"Chapel of the Damned",5,5,0,(0,5,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (2,"Crypts of Eternity",5,3,0,(0,5,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (3, "Library of Zastaross",2,3,2,(4,0,0),1,(Tiles.DOOR,Tiles.DOOR_OPEN))
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (98,"Arena",0,5,0,(0,5,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (99,"Portal Between Worlds",5,3,0,(0,5,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        new_floor_data = (20,"The Forest Temple",5,2,1,(5,0,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (21,"The Colonnade",5,4,1,(6,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (22,"The Shrine of the Snake God",5,4,1,(5,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (23,"Priest Quarters",5,4,1,(5,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (24,"Altar of Sacrifice",5,4,1,(5,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        # The Ruins
        new_floor_data = (30,"The Ruins",4,5,1,(0,5,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (31,"Tomb of the Fallen Knight",4,5,0,(0,5,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        # The Old Tower
        new_floor_data = (50,"The Old Tower",0,0,0,(0,5,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (51,"Back and Forth",3,6,0,(5,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (52,"The Maze",3,3,0,(5,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (53,"The Guard House",3,3,0,(5,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (54,"The Tower Top",0,0,0,(0,0,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data


        # id,name,treasures,traps,keys,monsters(1,2,3),secrets

        new_floor_data = (100,"Frozen Forest",2,3,1,(2,3,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (101, "Cave of Ice", 2, 3, 1, (5, 0, 0), 1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (102, "Castle Black", 6, 3, 1, (0, 0, 5), 1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (103, "Frost Bite Dungeon", 6, 3, 4, (2, 2, 2), 1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (104, "Oubliette", 4, 3, 1, (0, 4, 4), 1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (105, "Shard Throne", 4, 3, 1, (4, 4, 0), 1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (106, "Dwarf Hall", 4, 3, 1, (4, 4, 0), 1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (107, "The Crevasse", 4, 3, 1, (4, 4, 0), 1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (108, "Shard Mountain", 4, 3, 1, (4, 4, 0), 1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (198, "Arena", 0, 5, 0, (0, 5, 0), 0)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (199,"Frozen End",2,3,0,(0,0,5),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        # id,name,treasures,traps,keys,monsters(1,2,3),secrets

        new_floor_data = (200,"Shifting Sands",2,3,1,(2,3,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (201,"Tomb Entrance",2,2,0,(6,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (202,"Tomb of the Pharoah",2,5,0,(5,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (203,"Chamber of the Sarcophagus",2,2,0,(0,0,6),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (204,"Oasis",2,2,0,(6,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (205,"Pyramid Rises",2,4,1,(3,3,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (206,"Western Sanctum",2,4,1,(0,0,6),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (207,"Inner Temple",2,4,1,(0,6,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (208,"Bone Dry Wadi",2,4,1,(3,3,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (209,"Ancient City",2,4,1,(3,3,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (210,"Palace of the Djinn",2,4,1,(0,0,6),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (298, "Arena", 0, 5, 0, (0, 5, 0), 0)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (299,"Sanctum of the Sands",2,3,1,(2,3,2),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        # id,name,treasures,traps,keys,monsters(1,2,3),secrets

        new_floor_data = (300,"Cavern Entrance",2,5,0,(5,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (301,"Underground Canal",2,5,0,(4,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (302,"Catherdral of Granite",2,5,0,(4,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (303,"Goblin Prison",2,3,3,(0,0,4),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (304,"Hall of the Goblin King",2,3,2,(0,0,4),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (305,"Treasure Room",2,3,5,(0,0,4),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (306,"Guard's Quarters",2,3,2,(4,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (307,"Stone Crypt",2,3,0,(0,5,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (308,"Grotto of the Wizard",2,3,0,(0,5,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (309,"Chasm of Fire",2,3,0,(0,5,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (310,"Dragon Hoard",2,3,0,(0,5,0),1,(Tiles.TREASURE_CHEST,Tiles.DOWN))
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (398, "Arena", 0, 5, 0, (0, 5, 0), 0)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (399,"Elemental Vault",2,3,0,(2,0,2),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        # id,name,treasures,traps,keys,monsters(1,2,3),secrets, switch tiles

        new_floor_data = (900, "Edge of Reality",2,5,2,(2,2,2),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (901, "Chamber of the Deceiver",2,5,0,(2,2,2),1,(Tiles.TREASURE, Tiles.RED_POTION))
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (902, "Pool of the Miasma",2,5,0,(4,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (903, "Bridge of Desolation",2,5,0,(6,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (904, "Maze of Insanity",6,5,0,(6,0,1),1,(Tiles.UP,Tiles.DOWN))
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (905, "Maze of Insanity",6,5,0,(6,1,0),1,(Tiles.UP,Tiles.DOWN))
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (906, "Maze of Insanity",6,5,0,(2,4,0),1,(Tiles.UP,Tiles.DOWN))
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (907, "Maze of Insanity",6,5,0,(3,2,2),1,(Tiles.UP,Tiles.DOWN))
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (910, "Pilgrim's Reach",10,5,2,(6,0,0),1,(Tiles.EMPTY,Tiles.DOWN))
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (911, "Shadow Cave",10,5,2,(2,3,3),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (912, "Great Divide",10,5,2,(2,3,3),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (913, "Tunnel of Illusion",10,5,2,(2,3,3),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (914, "Map Room",5,0,0,(2,3,3),1,(Tiles.TRAP2, Tiles.TRAP1))
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (998,"Arena",0,5,0,(0,5,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        new_floor_data = (999, "Escape the Asylum",0,10,0,(5,5,5),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        new_floor_data = (1000, "Great Sword & Chalice",0,0,0,(0,0,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        logging.info("Finished loading floor configs. {0} floor configs loaded.".format(len(self.floor_configs.keys())))


    def build_floor(self):

        logging.info("Started building floors...")

        for floor_id in self.floor_configs.keys():
            floor_data = self.floor_configs[floor_id]

            if floor_id in self.floor_plans.keys():
                floor_plan = self.floor_plans[floor_id]

                # I'm lazy and didn't want to add switch tiles to each floor data :)
                try:
                    id,name,treasures,traps,keys,monsters,secrets,swap_tiles = floor_data
                except ValueError as e:
                    id,name,treasures,traps,keys,monsters,secrets = floor_data
                    swap_tiles = None

                new_floor = Floor(id = floor_id, name=name, treasure_count=treasures, key_count=keys,
                                  trap_count=traps, monster_count=monsters, secret_count=secrets, switch_tiles=swap_tiles)

                new_floor.initialise(floor_plan)
                self.floors[floor_id] = new_floor

            else:
                logging.warn("Unable to find a floor plan for floor '{0}' (id={1}).".format(name, floor_id))

        logging.info("Finished building floors. {0} floors built".format(len(self.floors.keys())))

        self.add_bosses()
        self.add_npcs()

    def add_bosses(self):

        boss = Boss("The Fallen Knight", width = 3, height = 3, speed = 4)
        self.floors[98].add_boss(boss)

        boss = Boss("The Ice Dragon", width = 2, height = 2, HP = 35, speed = 3)
        self.floors[198].add_boss(boss)

        boss = Boss("The Evil Scorpion", width = 3, height = 3, HP = 45, speed = 2)
        self.floors[298].add_boss(boss)

        boss = Boss("The Goblin King", width = 3, height = 3, HP = 60, speed =2)
        self.floors[398].add_boss(boss)

        boss = Boss("The Mind Master", width = 3, height = 3, HP = 80, speed = 1)
        self.floors[998].add_boss(boss)

    def add_npcs(self):

        npc = NPC("Imprisoned One", width=3, height=3)
        self.floors[0].add_npc(npc, xy=(0,19))

        npc = NPC("Rosie", tile=Tiles.NPC2, reward=Tiles.PLAYER_KNIGHT)
        self.floors[99].add_npc(npc,xy=(9,18))

        npc = NPC("Oliver")
        self.floors[100].add_npc(npc,xy=(18,5))

        npc = NPC("Skids", tile=Tiles.NPC2)
        self.floors[199].add_npc(npc,xy=(13,12))

        npc = NPC("Monty", tile=Tiles.NPC1)
        self.floors[200].add_npc(npc)

        npc = NPC("The Old One", tile=Tiles.NPC2, reward=Tiles.PLAYER_SPIKE)
        self.floors[299].add_npc(npc, xy=(13,6))

        npc = NPC("Golum", tile=Tiles.NPC1)
        self.floors[300].add_npc(npc, xy=(16,18))

        npc = NPC("Baylor", tile=Tiles.NPC2, reward=Tiles.PLAYER_GOLD)
        self.floors[399].add_npc(npc, xy=(15,2))

        npc = NPC("The Wretched", tile=Tiles.NPC1)
        self.floors[900].add_npc(npc, xy=(7,19))

        npc = NPC("The Warlock", tile=Tiles.NPC2)
        self.floors[999].add_npc(npc, xy=(1,14))

        npc = NPC("The Master Thief", tile=Tiles.NPC3, reward=Tiles.PLAYER_THIEF)
        self.floors[305].add_npc(npc, xy=(18,14))

        npc = NPC("The Guardian", tile=Tiles.NPC1)
        self.floors[1000].add_npc(npc, xy=(9,9))

class LevelBuilder:

    def __init__(self):
        self.levels = {}
        self.level_data = {}

    def initialise(self, floors : FloorBuilder):

        self.floor_builder = floors
        self.load_levels()
        self.build_levels()

    @property
    def level1(self):
        return min(self.levels.keys())

    def load_levels(self):

        logging.info("Starting loading Level Data...")

        new_level_data = (1, "Forest World", (0,1,2,3,20,21,22,23,24,30,31,50,51,52,53,54,98,99),"forest")
        self.level_data[1] = new_level_data

        new_level_data = (2, "Winter World", (100,101,102,103,104,105,106,107,108,198,199),"winter")
        self.level_data[2] = new_level_data

        new_level_data = (3, "Desert World", (200,201,202,203,204,205,206,207,208,209,210,298,299),"desert")
        self.level_data[3] = new_level_data

        new_level_data = (4, "Underground World", (300,301,302,303,304,305,306,307,308,309,310,398,399),"cave")
        self.level_data[4] = new_level_data

        new_level_data = (90, "Chaos World", (900,901,902,903,904,905,906,907,910,911,912,913,914,998,999),"chaos")
        self.level_data[90] = new_level_data


        # new_level_data = (3, "Squirrel World", (200,201),"squirrel")
        # self.level_data[3] = new_level_data

        new_level_data = (100, "The End", (1000,1000),"end")
        self.level_data[100] = new_level_data

        logging.info("Finished Loading Level Data. {0} levels loaded.".format(len(self.level_data.keys())))

    def build_levels(self):

        logging.info("Starting building levels...")

        for level_id in self.level_data.keys():
            id, name, floor_ids, skin_name = self.level_data[level_id]
            new_level = Level(id=id, name=name, skin_name=skin_name)
            new_level.initialise()
            for floor_id in floor_ids:
                if floor_id in self.floor_builder.floors.keys():
                    floor = self.floor_builder.floors[floor_id]
                    new_level.add_floor(floor)
                else:
                    logging.warn("Can't find floor {0} to add to level '{1}.{2}'.".format(floor_id,
                                                                                        new_level.id,
                                                                                        new_level.name))

            self.levels[level_id] = new_level

        logging.info("Finished building levels. {0} levels built.".format(len(self.levels.keys())))

    def get_level(self, level_id):
        level = None

        if level_id in self.levels.keys():
            level = self.levels[level_id]
        else:
            raise Exception("Level {0} does not exist!".format(level_id))

        return level

    def get_floor(self, floor_id : int):
        floor = None

        if floor_id in self.floor_builder.floors.keys():
            floor = self.floor_builder.floors[floor_id]

        else:
            raise Exception("Floor {0} does not exist!".format(floor_id))

        return floor