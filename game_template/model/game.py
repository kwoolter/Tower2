import logging, random, os
from copy import deepcopy
import game_template.utils as utils
import game_template.utils.trpg as trpg
import time
from operator import itemgetter


class Player():
    def __init__(self, name, x : int = 1, y : int = 1):
        self.name = name
        self._x = x
        self._y = y
        self.old_x = x
        self.old_y = y
        self.initialise()

    # Set player's attributes back to starting values
    def initialise(self):
        self.keys = 0
        self.red_potions = 0
        self.exit_keys = 0
        self.boss_key = False
        self.treasure = 0
        self.trophies = 0
        self.kills = 0
        self.HP = 10
        self.weapon = 1
        self.shield = 1
        self.bombs = 0
        self.maps = 0
        self.treasure_maps = {}
        self.runes = {}
        self.equipment_slots=[]
        self.equipment_slots.append(Tiles.RED_POTION)
        self.equipment_slots.append(Tiles.WEAPON)
        self.equipment_slots.append(Tiles.SHIELD)
        self.equipment_slots.append(Tiles.BOMB_LIT)
        self.effects = {}

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

    @property
    def score(self):

        rune_count = 0
        for runes in self.runes.items():
            rune_count += len(runes)

        return self.kills + self.treasure + (self.trophies * 50) + (rune_count * 50)

    def collect_rune(self, rune : str, level_id : int):

        if level_id not in self.runes.keys():
            self.runes[level_id] = []

        level_runes = self.runes[level_id]
        level_runes.append(rune)

    def runes_collected(self, level_id : None):

        rune_count = 0

        if level_id is None:
            for runes in self.runes.values():
                rune_count += len(runes)

        elif level_id in self.runes.keys():
            rune_count = len(self.runes[level_id])

        return rune_count


class Game:

    LOADED = "LOADED"
    READY = "READY"
    PLAYING = "PLAYING"
    SHOPPING = "SHOPPING"
    PAUSED = "PAUSED"
    GAME_OVER = "GAME OVER"
    END = "END"
    EFFECT_COUNTDOWN_RATE = 4
    TARGET_RUNE_COUNT = 4
    MAX_STATUS_MESSAGES = 5
    STATUS_MESSAGE_LIFETIME = 8

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

        ##

    @property
    def state(self):

        if self._state == Game.PLAYING and self.get_current_player().HP <=0:
            self.game_over()

        elif self.is_game_complete() is True:
            self.game_over()

        return self._state

    @property
    def trophies(self):

        trophy_count = 0

        for level in self.level_factory.levels.values():
            trophy_count += level.trophies

        return trophy_count


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

            self.add_status_message("Leaving {0} level...!".format(self.get_current_level().name))

            # Get the id of the next level....
            level_ids = sorted(self.level_factory.levels.keys())
            index = level_ids.index(self.current_level_id)
            index += 1
            if index >= len(level_ids):
                index = 0

            self.current_level_id = level_ids[index]

            self.current_floor_id = min(self.get_current_level().floors.keys())

            self.get_current_floor().add_player(self.get_current_player(), position = Floor.ENTRANCE)

            self.add_status_message("Heading to {0} level...!".format(self.get_current_level().name))

        else:
            self.add_status_message("{0} level not yet completed!".format(self.get_current_level().name))
            self.get_current_player().back()

    def previous_level(self):

        self.add_status_message("Leaving {0} level...!".format(self.get_current_level().name))

        level_ids = sorted(self.level_factory.levels.keys())
        index = level_ids.index(self.current_level_id)
        index -= 1
        if index < 0:
            index = 0

        self.current_level_id = level_ids[index]

        self.current_floor_id = max(self.get_current_level().floors.keys())

        self.get_current_floor().add_player(self.get_current_player(), position = Floor.EXIT)

        self.add_status_message("Heading to {0} level...!".format(self.get_current_level().name))

    def is_level_complete(self, player : Player, level_id : int):
        complete = False

        if len(player.runes) >= Game.TARGET_RUNE_COUNT:
            complete = True

        return complete

    def is_game_complete(self):
        complete = False

        if self.get_current_player() is not None and self.get_current_player().trophies == self.trophies:
            complete = True

        return complete

    def enter_shop(self):
        self._state = Game.SHOPPING
        self.shop.get_random_shop_keeper()

    def get_current_shop_keeper(self):
        return self.shop.current_shop_keeper

    def exit_shop(self):
        self._state = Game.PLAYING
        self.get_current_player().y += 1


    def initialise(self):

        logging.info("Initialising {0}...".format(self.name))

        self._state = Game.READY
        self.players = []
        self.player_scores = {}
        self.effects = {}
        self.tick_count = 0
        self.hidden_runes = list(Tiles.RUNES)


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
            print("Found a key!")

        elif tile in Tiles.MONSTERS:
            print("Hit a monster!")

        elif tile in Tiles.TRAPS:
            current_player.HP -= 1
            current_floor.set_player_tile(Tiles.EMPTY)
            self.add_status_message("Ouch! You walked into a trap!")
            print("Hit a trap!")

        elif tile in Tiles.PLAYER_DOT_TILES:
            current_player.HP -= 1
            print("Stood in something nasty!")

        elif tile == Tiles.RED_POTION:
            self.use_item(tile, decrement = False)
            current_floor.set_player_tile(Tiles.EMPTY)
            self.add_status_message("You feel healthier!")
            print("Some HP restored")

        elif tile in Tiles.SWAP_TILES.keys():
            current_floor.set_player_tile(Tiles.SWAP_TILES[tile])
            print("You found a {0} to {1} swappable tile!!".format(tile,Tiles.SWAP_TILES[tile]))

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
            if current_player.keys > 0:
                current_player.keys -= 1
                current_floor.set_player_tile(random.choice([Tiles.KEY, Tiles.SHIELD, Tiles.WEAPON,
                                                            Tiles.MAP, Tiles.BOMB, Tiles.RED_POTION,
                                                             Tiles.TREASURE10, Tiles.TREASURE25]))
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

        elif tile == Tiles.TROPHY:
            current_floor.set_player_tile(Tiles.EMPTY)
            current_player.trophies += 1
            print("You found a trophy!")
            if current_player.trophies == self.trophies:
                self.game_over()

        elif tile == Tiles.DOOR:
            print("You found a door...")
            if current_player.keys > 0:
                current_player.keys -= 1
                current_floor.set_player_tile(Tiles.EMPTY)
                print("...and you opened it!")
            else:
                current_player.back()
                self.add_status_message("The door is locked!")
                print("...but the door is locked!")

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

            # See if the player has the exact map for the secret...
            # ...and there are still some runes to find...
            found_maps = current_player.treasure_maps[current_level.id]

            if (current_floor.id, (pos)) in found_maps and len(self.hidden_runes) > 0:

                found_rune = random.choice(self.hidden_runes)
                current_player.collect_rune(found_rune, current_level.id)
                current_player.back()
                self.hidden_runes.remove(found_rune)
                current_floor.treasure_found()
                current_player.treasure_maps[current_level.id].remove((current_floor.id, (pos)))
                print("You found the secret treasure {0} and you have now collected {1}.".format(found_rune,
                                                                                                 current_player.runes))

                self.add_status_message("You have found a hidden rune!")

            else:
                print("You haven't got the map for this secret yet.")

    def check_collision(self):

         # Check if the player has collided with an enemy?
        if self.get_current_floor().is_collision() is True:

            print("collision!")

            if Tiles.WEAPON in self.effects.keys():
                print("You killed an enemy with your sword")
                self.get_current_player().kills += 1
                self.get_current_floor().kill_monster()

            elif Tiles.SHIELD in self.effects.keys():
                print("You defended yourself with your shield")

            else:
                self.get_current_player().HP -= 1
                print("HP down to %i" % self.get_current_player().HP)

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

    def pause(self, pause : bool = True):

        if self.state not in (Game.PLAYING, Game.PAUSED):
            raise Exception("Game is in state {0} so can't be paused!".format(self.state))

        if self.state == Game.PLAYING:
            self._state = Game.PAUSED
        else:
            self._state = Game.PLAYING


    def tick(self):

        if self.state != Game.PLAYING:
            raise Exception("Game is in state {0} so can't be ticked!".format(self.state))

        if self.state in (Game.PAUSED, Game.SHOPPING):
            return

        logging.info("Ticking {0}...".format(self.name))

        self.tick_count += 1

        self.update_status_messages()

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

    def add_status_message(self, new_msg : str):
        self.status_messages[new_msg] = Game.STATUS_MESSAGE_LIFETIME

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

        logging.info("Game Over {0}...".format(self.name))
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
        self.current_shop_keeper = None
        self.item_prices = {}

    def initialise(self):
        self.load_shop_keepers()
        self.load_item_prices()

    def get_random_shop_keeper(self):
        shop_keeper_name = random.choice(list(self.shop_keepers.keys()))
        self.current_shop_keeper =  self.shop_keepers[shop_keeper_name]
        return self.current_shop_keeper

    def buy_item(self, item_type, player : Player):

        if item_type not in self.item_prices.keys():
            raise Exception("Item {0} not in stock!".format(item_type))

        item_price = self.item_prices[item_type]

        if self.item_prices[item_type] > player.treasure:
            raise Exception("Player {0} does not have enough money to buy {1} at {2}".format(player.name,item_type,item_price))

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

        shop_keeper_names = ("Zordo", "Bylur", "Fenix", "Thof", "Korgul")

        for shop_keeper_name in shop_keeper_names:

            shop_keeper = Player(shop_keeper_name)
            self.load_store_items(shop_keeper)
            self.shop_keepers[shop_keeper.name] = shop_keeper

    def load_item_prices(self):
        self.item_prices[Tiles.KEY] = random.randint(5,10)
        self.item_prices[Tiles.RED_POTION] = random.randint(5, 10)
        self.item_prices[Tiles.BOMB] = random.randint(5, 10)
        self.item_prices[Tiles.WEAPON] = random.randint(5, 10)
        self.item_prices[Tiles.SHIELD] = random.randint(5, 10)
        self.item_prices[Tiles.MAP] = random.randint(5, 10)

    def load_store_items(self, shop_keeper : Player):

        shop_keeper.bombs = random.randint(0,5)
        shop_keeper.keys = random.randint(0,5)
        shop_keeper.red_potions = random.randint(0, 5)
        shop_keeper.weapon = random.randint(0, 5)
        shop_keeper.shield = random.randint(0, 5)
        shop_keeper.maps = random.randint(0, 5)


class Tiles:

    # Define Tiles
    # Cut and Paste
    BANG = '$'
    TILE1 = '`'
    TILE2 = '¬'
    TILE3 = '.'
    TILE4 = '~'
    BOMB = 'q'
    BOMB_LIT = 'Q'
    BOSS_DOOR = 'd'
    BRAZIER = 'B'
    DECORATION1 = 'z'
    DECORATION2 = 'Z'
    DOOR = 'D'
    DOT1 = '!'
    DOT2 = '£'
    DOWN = '-'
    EAST = 'E'
    EMPTY = ' '
    EXIT_KEY = '%'
    HEART = 'HP'
    KEY = '?'
    MAP = 'M'
    MONSTER1 = '1'
    MONSTER2 = '2'
    MONSTER3 = '3'
    NEXT_LEVEL = 'L'
    NORTH = 'N'
    PLAYER = 'P'
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
    WEAPON = '|'
    WEST = 'W'

    MONSTERS = (MONSTER1, MONSTER2, MONSTER3)
    EXPLODABLES = (BOMB_LIT)
    FLOOR_TILES = (TILE1, TILE2, TILE3, TILE4)
    INDESTRUCTIBLE_ITEMS = (KEY, TREE, TROPHY, NORTH, SOUTH, EAST, WEST, UP, DOWN, SHOP)
    TRAPS = (TRAP1, TRAP2, TRAP3)
    RUNES = (RUNE1, RUNE2, RUNE3, RUNE4, RUNE5)
    MONSTER_EMPTY_TILES = (EMPTY, PLAYER) + FLOOR_TILES
    PLAYER_BLOCK_TILES = (WALL, WALL_BL, WALL_BR, WALL_TL, WALL_TR, TREE, WALL2, BRAZIER, RUNE)
    PLAYER_DOT_TILES = (DOT1, DOT2)
    PLAYER_EQUIPABLE_ITEMS = (WEAPON, SHIELD, RED_POTION, BOMB)
    SWAP_TILES = {SECRET_WALL: EMPTY, SWITCH : SWITCH_LIT, SWITCH_LIT : SWITCH}



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
            self.entrance = (1, 1)

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
    EXPLODABLE_COUNTDOWN_RATE = 4
    EXPLODABLE_COUNTDOWN = 10
    SECRET_COUNTDOWN = 4

    def __init__(self, id : int, name : str,
                 treasure_count : int = 0,
                 trap_count : int = 0,
                 key_count = 0,
                 monster_count : tuple = (0,0,0),
                 secret_count : int = 0):
        self.id = id
        self.name = name
        self.treasure_count = treasure_count
        self.trap_count = trap_count
        self.monster_count = monster_count
        self.key_count = key_count
        self.secret_count = secret_count
        self.tick_count = 0
        self.monsters = {}
        self.explodables = {}
        self.runes = {}
        self.trophies = 0
        self.floor_plan = None
        self.player = None
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

    def add_explodable(self, tile, x : int, y : int):

        if tile not in Tiles.EXPLODABLES:
            raise Exception("Trying to add explodable {0} that is not a valid explodable {1}!",format(tile, Tiles.EXPLODABLES))

        self.explodables[(x,y)] = (tile, Floor.EXPLODABLE_COUNTDOWN)

    # Find empty tiles to place items
    def place_tiles(self, item_count, item_type, tries=20):

        for i in range(0, item_count):
            attempts = 0
            while True:
                x = random.randint(1, self.width - 1)
                y = random.randint(1, self.height - 1)
                if self.floor_plan.get_tile(x,y) == Tiles.EMPTY:

                    logging.info("Placed a {0} at {1},{2}".format(item_type, x, y))

                    # if item_type in Tiles.MONSTERS:
                    #     self.monsters[(x, y)] = item_type
                    # else:
                    #     self.floor_plan.set_tile(item_type, x, y)

                    self.floor_plan.set_tile(item_type, x, y)

                    break
                attempts += 1

                # We tried several times to find an empty square, time to give up!
                if attempts > tries:
                    print("Can't find an empty tile to place {0} after {1} tries".format(item_type, attempts))
                    break


    def move_player(self, dx : int, dy : int):

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        if self.is_valid_xy(new_x, new_y) is False:
            print("Hit the boundary!")
        elif self.get_tile(new_x, new_y) in Tiles.PLAYER_BLOCK_TILES:
            print("Square blocked!")
        else:
            self.player.x = new_x
            self.player.y = new_y

    def is_collision(self):

        collision_items = list(Tiles.MONSTERS + Tiles.PLAYER_DOT_TILES)

        if self.get_tile(self.player.x, self.player.y) in collision_items:
            return True
        else:
            return False

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

    def kill_monster(self, x : int = None, y : int = None):

        if x is None:
            x = self.player.x

        if y is None:
            y = self.player.y

        if (x,y) in self.monsters.keys():
            del self.monsters[(x,y)]
            print("You killed a monster at ({0},{1})".format(x,y))

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

        new_floor_plan = [
            '         N          ',
            '                    ',
            '    T       T       ',
            ' T      T           ',
            '                T   ',
            '    T               ',
            '  T      T          ',
            'W                   ',
            '            T     T ',
            'T                   ',
            '    T    =         E',
            '                    ',
            '               T    ',
            ' T /:\              ',
            '   :s:    T         ',
            '   B8B              ',
            '   888  T    T   T  ',
            ' T                  ',
            '                    ',
            '         S          ',

        ]

        floor_id = 0
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))
        floor_id = 200
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))
        floor_id = 300
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        floor_id = 0

        # Chapel
        new_floor_plan = [
            '         N          ',
            ' T           T     T',
            '             T   T  ',
            'T    T /:D:\   T    ',
            '       :) (:        ',
            '   T   : ? : T    T ',
            '       :   :        ',
            'T     /:B B:\       ',
            '  /::::)   (::::\   ',
            '  :)  B     B  (:   ',
            '  D      -      D   ',
            '  :\  B     B  /:   ',
            '  (::::\   /::::)  T',
            '      (:B B:)       ',
            ' T     :   :        ',
            '       :   :        ',
            ' T     :\ /:    T   ',
            '       (:;:)      T ',
            'T                   ',
            '        T T      T  ',

        ]

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Crypt
        new_floor_plan = [

            ':::::::::N::::::::::',
            ':z:B    : :     B:z:',
            '::)    B: :B     (::',
            ':B      (D)       B:',
            ':                  :',
            ':   /\        /\   :',
            ':   ()        ()   :',
            ':                  :',
            '::\      B       /::',
            ':::     /:\     /:):',
            ':j:    B:+:B    ; ?:',
            ':::     : :     (:\:',
            '::)     (D)      (::',
            ':   /\        /\   :',
            ':   ()        ()   :',
            ':                  :',
            ':B      B B       B:',
            '::\   /:: ::\    /::',
            ':z:B =:z:j:z:   B:z:',
            '::::::::::::::::::::',

        ]

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        # Library
        new_floor_plan = [

            '::::::::::::::::::::',
            ':?                ?:',
            ':                  :',
            ':                  :',
            ':    \        /    :',
            ':   B::::::::::B   :',
            ':                :::',
            ':                Dx:',
            ':::              :::',
            'W D  ::::::::::  Dj:',
            ':::     :        :::',
            ':                Dx:',
            ':                :::',
            ':   B::::::::::B   :',
            ':    )        (    :',
            ':                  :',
            ':\     B   B      /:',
            ':: \ /::   ::\  / ::',
            ':j : :z:\=/:z:  : j:',
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
            ': (:)  (:)  (:)     ',
            'W  D         :   :\ ',
            ': /:\        :   (::',
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
            '::::D:::\      :   :',
            ':) 888 (:      :   :',
            ':       :     888  :',
            ':       :      :   :',
            ':      B:      :::::',
            '::     ::     /)   :',
            ':B      :     :    :',
            ':       :     :    :',
            ':       :     :8   :',
            ':   :   :    8D8   :',
            ':\ R:R /: :\B/:8   :',
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
            ': :    B) : (B   (:w',
            ':j:       D       :w',
            '::)       :       (:',
            ':    T  :::::  T    ',
            ':M      :www:      E',
            ':       :www:       ',
            '::\  T  :::::  T  /:',
            ':j:       :       :w',
            ': :       D      /:w',
            ':      B\ : /B   :ww',
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
            '                    ',
            '                :   ',
            '  T        T   :::\ ',
            '      ::\        (: ',
            '  T    -:   :T  T : ',
            ' T      :::::     : ',
            '\     /:) :w:     : ',
            ':     :   :w:       ',
            ':ww\  :     )     T ',
            '::::  (: T    /:\   ',
            ':  :\         :     ',
            ')  ::         :     ',
            '        /  \  (\    ',
            'T       :ww:   (:   ',
            '     /:::::::       ',
            '  T  :)         T   ',
            '     :              ',
            'T    (       T      ',
            '                 T  ',
            '         S          ',

        )

        floor_id = 30
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))


        # The Tomb
        new_floor_plan = (
            '::::::)  /wwww::::::',
            ':   D    :wwww:   (:',
            ':   :    :wwww:    :',
            ':   :    :wwww:    :',
            ':   ;    (::::)  /::',
            ':j  :           ::ww',
            '::::)           wwww',
            ':M`:          www::w',
            ':``:   :::   ww:::::',
            ':``:   :+:  www:```:',
            ':D::  /: :\   ww```:',
            ':  :   B B     ww``:',
            ':  (:          ww:::',
            ':              :wwww',
            ':              :::ww',
            ':      ::      ::www',
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
            'T T = T   T T   TT  ',
            'T                 T ',
            ' T       :::   T   T',
            'T   T   :::::     T ',
            'T      ::   ::   TT ',
            ' TT   ::     ::    T',
            'T   :::   :   :   T ',
            'TT    :   :   ::  T ',
            'W  ?  D ::::: +: T T',
            'T     :   :   ::   T',
            ' TT :::   :   :   T ',
            'T     ::     ::   T ',
            'T    T ::   ::  T  T',
            ' TT     :::::      T',
            'T     T  :::   T  T ',
            ' T  T            T  ',
            'T   T T T   T TT  T ',
            ' TTT T T TTT T  TTT ',

        )

        floor_id = 50
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))



        # Back and Forth
        new_floor_plan = (
            '::::::::::::::::::::',
            ':-                 :',
            ':                  :',
            ':                  :',
            ':                  :',
            '::::::::::::::\    :',
            ':             :    :',
            ':             :    :',
            ':       :::   :    :',
            ':  :::   :    :    :',
            ':   :    :   :::   :',
            ':   :   :::        :',
            ':   :              :',
            ':   :              :',
            ':   (::::::::;::::::',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                 +:',
            '::::::::::::::::::::'
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
            '~~~~:: j:-:j=::~.~~~',
            '~.~~:   : :   :~~~~~',
            '~~~~:  :: ::  :~~~.~',
            '~~~~:         :~~~~~',
            '~~~~:         :~~.~~',
            '~~~~:         :~~~~~',
            '~~.~:    M    :~.~~~',
            '.~~~: xx:+:xx :~~~.~',
            '~~~~:: ::::: ::~~~~~',
            '~~~~~:::::::::~~~~~~',
            '~~.~~~~~~~~~~~~~~.~~',
            '~~~~~~~.~~.~~~.~~~~~',
            '~~~~.~~~~~~~~~~~~~~~',
            '~.~~~~~~~~~.~~~~.~~~',
            '~~~~~~.~~~~~~~~~~~~~',

        )
        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        # Portal1
        new_floor_plan = [

            '::::::::::::::::::::',
            ':)     : j :      (:',
            ':      :   :       :',
            ':      (:D:)       :',
            ':                  :',
            ':R                 :',
            ':B  B              :',
            ':::::        B:\   :',
            ':````          (\ /:',
            ':````           (:::',
            ':`L``=           88E',
            ':````           /:::',
            ':````          /) (:',
            ':::::        B:)   :',
            ':B  B              :',
            ':x                 :',
            ':      /:D:\       :',
            ':      :   :       :',
            ':\     : j :      /:',
            '::::::::::::::::::::',

        ]

        floor_id = 99
        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))


        # The Start of ICE Level
        new_floor_plan = (
            '!!!!:::::N::     !!!',
            '!! !!:    :      :!!',
            '!           T   :::!',
            ' T      T        ::!',
            '                T : ',
            '    T               ',
            ': T      T         !',
            'W                  !',
            '::       :  T      w',
            ':       /:\      www',
            '!   T   wlw        E',
            '!      ww=ww     www',
            '        w w    T  !w',
            ' T /:\            !!',
            '   wsw    T       !:',
            '   w8w            ::',
            '   B8B  T    T   T !',
            '!                  !',
            '::     !:       :  !',
            ':::   !!:S::   :::!!',

        )

        floor_id = 100
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        new_floor_plan = (

        '::::::::::::::::::::',
        ':                  :',
        ':       1          :',
        ':                  :',
        ':  :::::     ::::  :',
        ':  :   :     : -:  :',
        ':  :   :     B  :  :',
        ':  :   :        :  :',
        ':  :   B        :  :',
        'D  :            :  D',
        '::::            ::::',
        ':       B:::B      :',
        ':         :        :',
        ':         :        :',
        ':         : 1  1   :',
        ':         :        :',
        ':         :        :',
        ':       1 :        :',
        ':         :        :',
        '::::::::::::::::::::',
        )

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        floor_id = 201
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        floor_id += 1
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))


        new_floor_plan = (

            '::::::::::::::::::::',
            ':        :         :',
            ':        :         :',
            ':       /:\        :',
            ':     /::L::\      :',
            ':     : ``` :      :',
            ':     B ``` B      :',
            ':       ```        :',
            ':     B ``` B      :',
            ':       ```        :',
            ':     B ``` B      :',
            ':       ```        :',
            ':     B ``` B      :',
            ':       ```        :',
            ':       ```        :',
            ':     /\```/\      :',
            ':     :`````:      :',
            ':     :`````:      :',
            ':    /:``G``:\     :',
            '::::::::::::::::::::',

        )

        floor_id = 1000
        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))


        logging.info("Finished loading floor plans. {0} floor plans loaded.".format(len(self.floor_plans.keys())))

    def load_floors(self):

        logging.info("Started loading floor configs...")



        # id,name,treasures,traps,keys,monsters(1,2,3),secrets


        # Forest World - Start
        new_floor_data = (0,"Ancient Woods",5,0,0,(0,5,2),0)

        # The Chapel
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (1,"Chapel of the Damned",5,5,0,(0,5,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (2,"Crypts of Eternity",5,3,0,(0,7,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (3, "Library of Zastaross",2,3,2,(4,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (99,"Portal Between Worlds",5,3,0,(0,5,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        # The Temple
        new_floor_data = (20,"The Forest Temple",5,2,1,(6,0,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (21,"The Colonnade",5,4,1,(6,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (22,"The Shrine of the Snake God",5,4,1,(6,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (23,"Priest Quarters",5,4,1,(6,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (24,"Altar of Sacrifice",5,4,1,(6,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        # The Ruins
        new_floor_data = (30,"The Ruins",4,5,1,(0,5,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (31,"Tomb of the Fallen Knight",4,5,0,(0,5,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        # The Old Tower
        new_floor_data = (50,"The Old Tower",0,0,0,(0,3,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (51,"Back and Forth",3,3,0,(5,0,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (52,"The Maze",3,3,0,(5,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (53,"The Guard House",3,3,0,(5,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (54,"The Tower Top",0,0,0,(0,0,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data


        # id,name,treasures,traps,keys,monsters(1,2,3),secrets

        new_floor_data = (100,"Frozen Forest",2,3,1,(1,1,1),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (101,"End",2,3,0,(1,1,1),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data


        new_floor_data = (200, "The Woods",7,4,0,(7,0,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (201, "The Copse",7,4,0,(2,7,0),1)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        new_floor_data = (1000, "The END",0,0,0,(0,0,0),0)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        logging.info("Finished loading floor configs. {0} floor configs loaded.".format(len(self.floor_configs.keys())))


    def build_floor(self):

        logging.info("Started building floors...")

        for floor_id in self.floor_configs.keys():
            floor_data = self.floor_configs[floor_id]

            if floor_id in self.floor_plans.keys():
                floor_plan = self.floor_plans[floor_id]

                id,name,treasures,traps,keys,monsters,secrets = floor_data
                new_floor = Floor(id = floor_id, name=name, treasure_count=treasures, key_count=keys,
                                  trap_count=traps, monster_count=monsters, secret_count=secrets)
                new_floor.initialise(floor_plan)
                self.floors[floor_id] = new_floor

            else:
                logging.warn("Unable to find a floor plan for floor '{0}' (id={1}).".format(name, floor_id))

        logging.info("Finished building floors. {0} floors built".format(len(self.floors.keys())))


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

        new_level_data = (1, "Forest World", (0,1,2,3,20,21,22,23,24,30,31,50,51,52,53,54,99),"forest")
        self.level_data[1] = new_level_data

        new_level_data = (2, "Winter World", (100,101),"winter")
        self.level_data[2] = new_level_data

        new_level_data = (3, "Squirrel World", (200,201),"squirrel")
        self.level_data[3] = new_level_data

        new_level_data = (100, "The End", (1000,1000),"forest")
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