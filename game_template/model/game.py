import logging, random
from copy import deepcopy
import game_template.utils as utils
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
        self.weapon = 0
        self.shield = 0
        self.bombs = 0

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
        return self.kills + self.treasure + (self.trophies * 50)


class Game:

    LOADED = "LOADED"
    READY = "READY"
    PLAYING = "PLAYING"
    SHOPPING = "SHOPPING"
    PAUSED = "PAUSED"
    GAME_OVER = "GAME OVER"
    END = "END"
    MONSTER_MOVE_RATE = 3
    SHOP_LEVEL = 999

    def __init__(self, name : str):

        self.name = name
        self.players = None
        self._state = Game.LOADED
        self.game_start = None
        self.tick_count = 0
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

        return self._state

    @property
    def trophies(self):

        trophy_count = 0

        for level in self.level_factory.levels.values():
            trophy_count += level.trophies

        return trophy_count


    def get_current_floor(self):
        return self.level_factory.get_floor(self.current_floor_id)

    def get_current_level(self):
        return self.level_factory.get_level(self.current_level_id)

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

        level_ids = sorted(self.level_factory.levels.keys())
        index = level_ids.index(self.current_level_id)
        index += 1
        if index >= len(level_ids):
            index = 0

        self.current_level_id = level_ids[index]

        self.current_floor_id = min(self.get_current_level().floors.keys())

        self.get_current_floor().add_player(self.get_current_player(), position = Floor.ENTRANCE)

    def previous_level(self):

        level_ids = sorted(self.level_factory.levels.keys())
        index = level_ids.index(self.current_level_id)
        index -= 1
        if index < 0:
            index = 0

        self.current_level_id = level_ids[index]

        self.current_floor_id = max(self.get_current_level().floors.keys())

        self.get_current_floor().add_player(self.get_current_player(), position = Floor.EXIT)

    def enter_shop(self):
        self._state = Game.SHOPPING
        self.current_shop_keeper = self.shop.get_shop_keeper()

    def exit_shop(self):
        self._state = Game.PLAYING
        self.get_current_player().y += 1


    def initialise(self):

        logging.info("Initialising {0}...".format(self.name))

        self._state = Game.READY
        self.players = []
        self.player_scores = {}
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


    def add_player(self, new_player : Player):

        if self.state != Game.READY:
            raise Exception("Game is in state {0} so can't add new players!".format(self.state))

        logging.info("Adding new player {0} to game {1}...".format(new_player.name, self.name))

        self.players.append(new_player)
        self.player_scores[new_player.name] = 0

    def move_player(self, dx : int, dy : int):

        # If in a non-playing state then do nothing
        if self.state != Game.PLAYING:
            return

        current_floor = self.get_current_floor()

        current_player = self.get_current_player()

        current_floor.move_player(dx, dy)

        tile = current_floor.get_player_tile()

        if tile == Tiles.KEY:
            current_player.keys += 1
            current_floor.set_player_tile(Tiles.EMPTY)
            print("Found a key!")

        elif tile in Tiles.MONSTERS:
            current_player.HP -= 1
            print("Hit a monster!")

        elif tile in Tiles.TRAPS:
            current_player.HP -= 1
            current_floor.set_player_tile(Tiles.EMPTY)
            print("Hit a trap!")

        elif tile in Tiles.PLAYER_DOT_TILES:
            current_player.HP -= 1
            print("Stood in something nasty!")

        elif tile == Tiles.RED_POTION:
            current_player.HP += 1
            current_floor.set_player_tile(Tiles.EMPTY)
            print("Some HP restored")

        elif tile in Tiles.SWAP_TILES.keys():
            current_floor.set_player_tile(Tiles.SWAP_TILES[tile])
            print("You found a {0} to {1} swappable tile!!".format(tile,Tiles.SWAP_TILES[tile]))

        elif tile == Tiles.TREASURE:
            current_floor.set_player_tile(Tiles.EMPTY)
            current_player.treasure += 1
            print("You found some treasure!")

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
                print("...but the door is locked!")

        elif tile == Tiles.EXIT:
            print("You found the exit!")
            self.next_floor()

        elif tile == Tiles.ENTRANCE:
            print("You found the entrance!")
            self.previous_floor()

        elif tile == Tiles.NEXT_LEVEL:
            print("You found the entrance to the next level!")
            self.next_level()

        elif tile == Tiles.PREVIOUS_LEVEL:
            print("You found the entrance to the previous level!")
            self.previous_level()

        elif tile == Tiles.SHOP:
            self.enter_shop()

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

        self.get_current_floor().tick()

        # If the player is on a damage tile then take damage
        damage_tiles = Tiles.MONSTERS + Tiles.PLAYER_DOT_TILES
        if self.get_current_floor().get_player_tile() in damage_tiles:
            self.get_current_player().HP -= 1
            print("You took some damage")

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

        self.hst.add(self.get_current_player().name, self.get_current_player().score)

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

    def initialise(self):
        self.load_shop_keepers()

    def get_shop_keeper(self):
        shop_keeper_name = random.choice(list(self.shop_keepers.keys()))
        return self.shop_keepers[shop_keeper_name]

    def load_shop_keepers(self):

        shop_keeper = Player("Zordo")
        self.load_store_items(shop_keeper)
        self.shop_keepers[shop_keeper.name] = shop_keeper

        shop_keeper = Player("Baylur")
        self.load_store_items(shop_keeper)
        self.shop_keepers[shop_keeper.name] = shop_keeper

        shop_keeper = Player("Fenix")
        self.load_store_items(shop_keeper)
        self.shop_keepers[shop_keeper.name] = shop_keeper

    def load_store_items(self, shop_keeper : Player):

        shop_keeper.bombs = random.randint(0,5)
        shop_keeper.keys = random.randint(0,5)
        shop_keeper.red_potions = random.randint(0, 5)
        shop_keeper.weapon = random.randint(0, 5)
        shop_keeper.shield = random.randint(0, 5)


class Tiles:

    BEACH = "s"
    BOSS_DOOR = "d"
    BOSS_KEY = "$"
    BRAZIER = "B"
    DOOR = "D"
    DECORATION1 = "z"
    DECORATION2 = "Z"
    EMPTY = " "
    ENTRANCE = "-"
    START_POSITON = "="
    EXIT = "+"
    NEXT_LEVEL = "L"
    PREVIOUS_LEVEL = "l"
    EXIT_KEY = "%"
    TROPHY = "G"
    KEY = "?"
    SAFETY = "8"
    SECRET_WALL = ";"
    SHOP = "S"
    SKY = "~"
    SWITCH = ","
    SWITCH_LIT = "<"
    SWITCH_TILE = "_"
    TRAP1 = "^"
    TRAP2 = "&"
    TRAP3 = "("
    TREASURE = "*"
    TREASURE_CHEST = "j"
    TREE = "T"
    WALL = ":"
    WALL_TL = "/"
    WALL_TR = "\\"
    WALL_BL = "("
    WALL_BR = ")"
    WATER = "W"
    WEAPON = "|"
    SHIELD = "O"
    BOMB = "q"
    BOMB_LIT = "Q"
    MONSTER1 = "1"
    MONSTER2 = "2"
    MONSTER3 = "3"
    PLAYER = "P"
    RED_POTION = "R"
    DOT1 = "!"
    DOT2 = "£"
    HEART = "HP"

    MONSTERS = (MONSTER1, MONSTER2, MONSTER3)
    TRAPS = (TRAP1, TRAP2, TRAP3)
    MONSTER_EMPTY_TILES = (EMPTY, PLAYER)
    PLAYER_BLOCK_TILES = (WALL, WALL_BL, WALL_BR, WALL_TL, WALL_TR, TREE, BRAZIER)
    PLAYER_DOT_TILES = (DOT1, DOT2)
    SWAP_TILES = {SECRET_WALL: EMPTY, SWITCH : SWITCH_LIT, SWITCH_LIT : SWITCH}


class FloorPlan:

    def __init__(self, id : int, plan : list):

        self.id = id
        self.entrance = None
        self.exit = None
        self.height = len(plan)
        self.width = len(plan[0])
        self.plan = [[Tiles.EMPTY for x in range(self.height)] for x in range(self.width)]
        for y in range(0, len(plan)):
            row = plan[y]
            for x in range(0, min(self.width, len(row))):
                self.set_tile(row[x],x,y)

        if self.entrance is None:
            self.entrance = (1, 1)

        # Create safety zones around the entrance and exits
        if self.entrance is not None:
            self.safety_zone(self.entrance[0], self.entrance[1], 4, 4)

        if self.exit is not None:
            self.safety_zone(self.exit[0], self.exit[1], 4, 4)

    def get_tile(self, x : int, y : int):

        return self.plan[x][y]

    def set_tile(self, tile_name, x : int, y: int):

        self.plan[x][y] = tile_name

        if tile_name == Tiles.ENTRANCE:
            self.entrance = (x,y)
        elif tile_name == Tiles.START_POSITON and self.entrance is None:
            self.entrance = (x,y)
            self.plan[x][y] = Tiles.EMPTY
            print("Starting pos at ({0},{1})!!!".format(x,y))
        elif tile_name == Tiles.EXIT:
            self.exit = (x,y)
        elif tile_name == Tiles.NEXT_LEVEL and self.exit is None:
            self.exit = (x,y)
        elif tile_name == Tiles.PREVIOUS_LEVEL and self.entrance is None:
            self.entrance = (x,y)

    # Build a safety zone around a specified location
    def safety_zone(self, x, y, height, width):
        for dx in range(-1 * int(width / 2), int(width / 2) + 1):
            for dy in range(-1 * int(height / 2), int(height / 2) + 1):
                if (x + dx) < self.width and (x + dx) >= 0 and (y + dy) < self.height and (y + dy) >= 0:
                    if self.plan[x + dx][y + dy] == Tiles.EMPTY:
                        self.plan[x + dx][y + dy] = Tiles.SAFETY


class Floor:

    ENTRANCE = "Entrance"
    EXIT = "Exit"
    MONSTER_MOVE_RATE = 4

    def __init__(self, id : int, name : str,
                 treasure_count : int = 0,
                 trap_count : int = 0,
                 monster_count : int = 0):
        self.id = id
        self.name = name
        self.treasure_count = treasure_count
        self.trap_count = trap_count
        self.monster_count = monster_count
        self.tick_count = 0
        self.monsters = {}
        self.trophies = 0
        self.floor_plan = None
        self.player = None

    def initialise(self, floor_plan : FloorPlan):

        self.floor_plan = floor_plan
        self.tick_count = 0

        for y in range(self.floor_plan.height):
            for x in range(self.floor_plan.width):
                tile_name = self.floor_plan.get_tile(x,y)

                if tile_name in Tiles.MONSTERS:
                    self.floor_plan.set_tile(Tiles.EMPTY, x, y)
                    self.monsters[(x,y)] = tile_name

                elif tile_name == Tiles.TROPHY:
                    self.trophies += 1

        print(str(self))

        self.place_tiles(self.treasure_count, Tiles.TREASURE)
        self.place_tiles(self.trap_count, Tiles.TRAP1)

        m1,m2,m3 = self.monster_count
        self.place_tiles(m1, Tiles.MONSTER1)
        self.place_tiles(m2, Tiles.MONSTER2)
        self.place_tiles(m3, Tiles.MONSTER3)

    def tick(self):

        self.tick_count += 1

        if self.tick_count % Floor.MONSTER_MOVE_RATE == 0:
            self.move_monsters()

    def add_player(self, player, position = ENTRANCE):
        self.player = player
        if position == Floor.ENTRANCE and self.floor_plan.entrance is not None:
            x,y = self.floor_plan.entrance
            self.player.x = x
            self.player.y = y
            print("Adding player to entrance at  {0},{1}".format(x,y))
        elif position == Floor.EXIT and self.floor_plan.exit is not None:
            x,y = self.floor_plan.exit
            self.player.x = x
            self.player.y = y

    # Find empty tiles to place items
    def place_tiles(self, item_count, item_type, tries=20):

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

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
            print("Hit the boundary!")
        elif self.get_tile(new_x, new_y) in Tiles.PLAYER_BLOCK_TILES:
            print("Square blocked!")
        else:
            self.player.x = new_x
            self.player.y = new_y

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
            if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
                #print("Hit boundary")
                moved = False

            # ...if new square is not empty
            elif self.floor_plan.get_tile(new_x, new_y) not in Tiles.MONSTER_EMPTY_TILES:
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

    def get_tile(self, x : int, y: int):
        tile = self.floor_plan.get_tile(x,y)
        if (x,y) in self.monsters.keys():
            return self.monsters[(x,y)]
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

        floor_id = 1

        new_floor_plan = [

            '         =       :::',
            ' T           T   :S:',
            '     T /:D:\   T B8B',
            'T      :) (:     888',
            '   T   : ? : T      ',
            '       :   :      T ',
            '      /:B B:\       ',
            'T /::::)   (::::\   ',
            '  :)  B     B  (:   ',
            '  D      +      D   ',
            '  :\  B     B  /:   ',
            '  (::::\   /::::)   ',
            '      (:B B:)      T',
            '       :   :        ',
            ' T     :   :        ',
            '       :\ /:    T   ',
            ' T     (:;:)        ',
            '    T         T   T ',
            'T                   ',
            '   qQ|O T T      T  ',

        ]

        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        new_floor_plan = [

            'z:      :+:       :z',
            ':)      : :       (:',
            '       B: :B        ',
            '        (D)         ',
            '                    ',
            '                    ',
            '                    ',
            '                    ',
            '         B       /::',
            '        /:\     /:):',
            '       B:-:B    ; ?:',
            '        (D)     (:\:',
            '                 (::',
            '                    ',
            '                    ',
            '                    ',
            '                    ',
            '                    ',
            ':\                /:',
            'z:                :z',

        ]

        floor_id += 1

        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        new_floor_plan = [

            '::::::::::::::::::::',
            ':B        !!!    B(:',
            ':  B               :',
            ':                  :',
            ':         ^^     /::',
            ':      R         :z:',
            ':                (::',
            ':      T           :',
            'D   /::::\  *      D',
            ':   :z   :         :',
            ':   (::::)T   ,    :',
            ':                  :',
            ':                  :',
            ':     T            :',
            ':        *       , :',
            ':     ?            :',
            ':  G      T        :',
            ':            *     :',
            ':\  Z   +   Z    B/:',
            '::::::::::::::::::::',
        ]

        floor_id += 1

        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

        new_floor_plan = [

        '::::::::::::::::::::',
        ':                  :',
        ':       1          :',
        ':                  :',
        ':                  :',
        ':  -            2  :',
        ':                  :',
        ':                  :',
        '::::\    /\    /::::',
        'D        ()        D',
        '::::)          (::::',
        ':                  :',
        ':      3           :',
        ':                 +:',
        ':                  :',
        ':                  :',
        ':                  :',
        ':       1          :',
        ':                  :',
        '::::::::::::::::::::',
        ]

        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        floor_id += 1

        new_floor_plan = [

        '::::::::::::::::::::',
        ':                  :',
        ':       1          :',
        ':                  :',
        ':  :::::    :::::  :',
        ':  :   ;    :   :  :',
        ':  :   :     B  : L:',
        ':  :   :        :  :',
        ':  :   B        :  :',
        'D  :            :  D',
        '::::            ::::',
        ':       B:::B      :',
        ':        (:)       :',
        ':         :        :',
        ': -       : 1  1   :',
        ':         :        :',
        ':         :        :',
        ':       1 :        :',
        ':         :        :',
        '::::::::::::::::::::',
        ]

        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        floor_id += 1

        new_floor_plan = [

        '::::::::::::::::::::',
        ':                  :',
        ':                  :',
        ':      T   T       :',
        ':  T               :',
        ':    T T      z    :',
        ':                  :',
        ':    T      z      :',
        ':::Z      z     Z:::',
        '+ D              D  ',
        ':::Z            Z:::',
        ':                  :',
        ': z                :',
        ':            T     :',
        ':   T              :',
        ': T                :',
        ':     T       ?    :',
        ':                  :',
        ':                  :',
        '::::::::::::::::::::',
        ]

        floor_id = 100

        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        floor_id += 1


        self.floor_plans[floor_id] = FloorPlan(floor_id, deepcopy(new_floor_plan))

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
        ':         : G      :',
        '::::::::::::::::::::',
        )

        floor_id += 1

        self.floor_plans[floor_id] = FloorPlan(floor_id,deepcopy(new_floor_plan))

        logging.info("Finished loading floor plans. {0} floor plans loaded.".format(len(self.floor_plans.keys())))

    def load_floors(self):

        logging.info("Started loading floor configs...")

        # id,name,treasures,traps,monsters(1,2,3)

        new_floor_data = (1,"Chapel of the Damned",5,3,(0,5,0))
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (2,"Crypts of Eternity",2,3,(0,10,0))
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (3, "Zastaross", 2, 3, (0,0,10))
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (100,"Home straight",2,3,(1,1,1))
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (101,"End",2,3,(1,1,1))
        self.floor_configs[new_floor_data[0]] = new_floor_data

        new_floor_data = (200, "The Woods",7,4,(7,0,0))
        self.floor_configs[new_floor_data[0]] = new_floor_data

        logging.info("Finished loading floor configs. {0} floor configs loaded.".format(len(self.floor_configs.keys())))


    def build_floor(self):

        logging.info("Started building floors...")

        for floor_id in self.floor_configs.keys():
            floor_data = self.floor_configs[floor_id]

            if floor_id in self.floor_plans.keys():
                floor_plan = self.floor_plans[floor_id]

                id,name,treasures,traps,monsters = floor_data
                new_floor = Floor(id = floor_id, name=name, treasure_count=treasures, trap_count=traps, monster_count=monsters)
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

        new_level_data = (1, "Forest World", (1,2,3),"forest")
        self.level_data[1] = new_level_data

        new_level_data = (2, "Winter World", (100,101),"winter")
        self.level_data[2] = new_level_data

        new_level_data = (3, "Squirrel World", (200,200),"squirrel")
        self.level_data[3] = new_level_data

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

        return level

    def get_floor(self, floor_id : int):
        floor = None

        if floor_id in self.floor_builder.floors.keys():
            floor = self.floor_builder.floors[floor_id]

        return floor