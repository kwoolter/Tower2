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
        self.exit_keys = 0
        self.boss_key = False
        self.treasure = 0
        self.trophies = 0
        self.kills = 0
        self.HP = 10
        self.sword = False
        self.shield = False

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


class Game:

    LOADED = "LOADED"
    READY = "READY"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    GAME_OVER = "GAME OVER"
    END = "END"

    def __init__(self, name : str):
        self.name = name
        self.players = None
        self.state = Game.LOADED
        self.game_start = None

        self.hst = utils.HighScoreTable(self.name)

        #
        ##


        self.levels = LevelBuilder()
        self.current_level_id = 1
        self.current_floor_id = 1


        ##

    def get_current_floor(self):
        return self.levels.get_floor(self.current_floor_id)

    def get_current_level(self):
        return self.levels.get_level(self.current_level_id)

    def get_current_player(self):
        return self.players[0]


    def next_floor(self):

        current_level = self.levels.get_level(self.current_level_id)

        floor_ids = sorted(current_level.floors.keys())

        index = floor_ids.index(self.current_floor_id)
        index += 1
        if index >= len(floor_ids):
            index = 0

        self.current_floor_id = floor_ids[index]

    def next_level(self):

        level_ids = sorted(self.levels.levels.keys())
        index = level_ids.index(self.current_level_id)
        index += 1
        if index >= len(level_ids):
            index = 0

        self.current_level_id = level_ids[index]

        self.current_floor_id = min(self.get_current_level().floors.keys())

    def initialise(self):

        logging.info("Initialising {0}...".format(self.name))

        self.state = Game.READY

        self.players = []
        self.player_scores = {}

        self.hst.load()

        #
        #
        self.floors = FloorBuilder()
        self.floors.initialise()

        self.levels = LevelBuilder()
        self.levels.initialise(self.floors)



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

        self.get_current_floor().player = self.get_current_player()

        self.get_current_floor().move_player(dx, dy)

    def start(self):

        if self.state != Game.READY:
            raise Exception("Game is in state {0} so can't be started!".format(self.state))

        logging.info("Starting {0}...".format(self.name))

        self.state = Game.PLAYING
        self.game_start = time.time()

    def pause(self, pause : bool = True):

        if self.state not in (Game.PLAYING, Game.PAUSED):
            raise Exception("Game is in state {0} so can't be paused!".format(self.state))

        if self.state == Game.PLAYING:
            self.state = Game.PAUSED
        else:
            self.state = Game.PLAYING


    def tick(self):

        if self.state != Game.PLAYING:
            raise Exception("Game is in state {0} so can't be ticked!".format(self.state))

        if self.state == Game.PAUSED:
            return

        logging.info("Ticking {0}...".format(self.name))

        self.get_current_floor().tick()

    def get_scores(self):

        scores = []

        for player_name, score in self.player_scores.items():

            scores.append((player_name, score))

        return sorted(scores,key=itemgetter(1, 0), reverse=True)

    @property
    def elapsed_time(self):
        elapsed_seconds = time.time() - self.game_start
        return time.gmtime(elapsed_seconds)

    def game_over(self):

        logging.info("Game Over {0}...".format(self.name))

        self.state=Game.GAME_OVER

    def end(self):

        logging.info("Ending {0}...".format(self.name))

        self.state=Game.END

        self.hst.save()

    def print(self):

        print("Printing {0}...".format(self.name))


class Tiles:

    BEACH = "s"
    BOSS_DOOR = "d"
    BOSS_KEY = "$"
    BRAZIER = "B"
    DOOR = "D"
    EMPTY = " "
    ENTRANCE = "-"
    EXIT = "+"
    EXIT_KEY = "%"
    GOAL = "G"
    KEY = "?"
    SAFETY = "8"
    SECRET_WALL = ";"
    SKY = "~"
    SWITCH = ","
    SWITCH_LIT = "<"
    SWITCH_TILE = "_"
    TRAP = "^"
    TREASURE = "*"
    TREASURE_CHEST = "j"
    TREE = "T"
    WALL = ":"
    WATER = "W"
    MONSTER1 = "1"
    MONSTER2 = "2"
    MONSTER3 = "3"
    PLAYER = "P"

    MONSTERS = (MONSTER1, MONSTER2, MONSTER3)
    MONSTER_EMPTY_TILES = (EMPTY)
    PLAYER__EMPTY_TILES = (EMPTY)

class FloorPlan:

    def __init__(self, id : int, plan : list):

        self.id = id
        self.height = len(plan)
        self.width = len(plan[0])
        self.plan = [[Tiles.EMPTY for x in range(self.height)] for x in range(self.width)]
        for y in range(0, len(plan)):
            row = plan[y]
            for x in range(0, min(self.width, len(row))):
                self.set_tile(row[x],x,y)

    def get_tile(self, x : int, y : int):

        return self.plan[x][y]

    def set_tile(self, tile_name, x : int, y: int):

        self.plan[x][y] = tile_name


class Floor:

    def __init__(self, id : int, name : str):
        self.id = id
        self.name = name
        self.monsters = {}
        self.traps = []
        self.floor_plan = None
        self.player = None

    def initialise(self, floor_plan : FloorPlan):

        self.floor_plan = floor_plan

        for y in range(self.floor_plan.height):
            for x in range(self.floor_plan.width):
                tile_name = self.floor_plan.get_tile(x,y)

                if tile_name in Tiles.MONSTERS:
                    self.floor_plan.set_tile(Tiles.EMPTY, x, y)
                    self.monsters[(x,y)] = tile_name

    def tick(self):
        self.move_monsters()

    def move_player(self, dx : int, dy : int):

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
            print("Hit the boundary!")
        elif self.get_tile(new_x, new_y) not in Tiles.PLAYER__EMPTY_TILES:
            print("Square blocked)")
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
                print("Hit boundary")
                moved = False

            # ...if new square is not empty
            elif self.floor_plan.get_tile(new_x, new_y) not in Tiles.MONSTER_EMPTY_TILES:
                print("Square blocked")
                moved = False

            # ...if the new square contains an enemy
            elif (new_x, new_y) in new_monsters:
                print("Square occupied")
                moved = False

            if moved == True:
                new_monsters[(new_x,new_y)] = monster_type
            else:
                new_monsters[(x, y)] = monster_type

        self.monsters = new_monsters


    def get_tile(self, x : int, y: int):
        tile = self.floor_plan.get_tile(x,y)
        if (x,y) in self.monsters.keys():
            return self.monsters[(x,y)]
        return tile

    def __str__(self):
        string = "Floor {1}: '{0}'".format(self.name, self.id)
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

            '::::::::::::::::::::',
            ':B                B:',
            ':  B               :',
            ':             3    :',
            ':                  :',
            ':            1     :',
            ':                  :',
            ':      T           :',
            'D                  D',
            ':                  :',
            ':         T        :',
            ':  2               :',
            ':                  :',
            ':     T       1    :',
            ':                  :',
            ':                  :',
            ':         T        :',
            ':                  :',
            ':B                B:',
            '::::::::::::::::::::',
        ]

        self.floor_plans[1] = FloorPlan(1, deepcopy(new_floor_plan))

        new_floor_plan = [

        '::::::::::::::::::::',
        ':                  :',
        ':       1          :',
        ':                  :',
        ':                  :',
        ':               2  :',
        ':                  :',
        ':                  :',
        '::::            ::::',
        'D                  D',
        '::::            ::::',
        ':                  :',
        ':      3           :',
        ':                  :',
        ':                  :',
        ':                  :',
        ':                  :',
        ':       1          :',
        ':                  :',
        '::::::::::::::::::::',
        ]

        self.floor_plans[2] = FloorPlan(2,deepcopy(new_floor_plan))

        new_floor_plan = [

        '::::::::::::::::::::',
        ':                  :',
        ':       1          :',
        ':                  :',
        ':  :::::     ::::  :',
        ':  :   :     :  :  :',
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
        ]

        self.floor_plans[3] = FloorPlan(3,deepcopy(new_floor_plan))

        new_floor_plan = [

        '::::::::::::::::::::',
        ':                  :',
        ':                  :',
        ':      T   T       :',
        ':  T               :',
        ':    T T           :',
        ':                  :',
        ':    T     1  2  3 :',
        ':                  :',
        'D                  D',
        ':          T T     :',
        ':                  :',
        ':                  :',
        ':            T     :',
        ':   T              :',
        ': T                :',
        ':     T            :',
        ':                  :',
        ':                  :',
        '::::::::::::::::::::',
        ]

        self.floor_plans[100] = FloorPlan(100,deepcopy(new_floor_plan))

        new_floor_plan = (

        '::::::::::::::::::::',
        ':                  :',
        ':       1          :',
        ':                  :',
        ':  :::::     ::::  :',
        ':  :   :     :  :  :',
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


        self.floor_plans[101] = FloorPlan(101,deepcopy(new_floor_plan))

        logging.info("Finished loading floor plans. {0} floor plans loaded.".format(len(self.floor_plans.keys())))

    def load_floors(self):

        logging.info("Started loading floor configs...")

        new_floor_data = (1,"Start",2,3,4)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (2,"Middle",2,3,4)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (3, "Zastaross", 2, 3, 4)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (100,"Home straight",2,3,4)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (101,"End",2,3,4)
        self.floor_configs[new_floor_data[0]] = new_floor_data

        logging.info("Finished loading floor configs. {0} floor configs loaded.".format(len(self.floor_configs.keys())))


    def build_floor(self):

        logging.info("Started building floors...")

        for floor_id in self.floor_configs.keys():
            floor_data = self.floor_configs[floor_id]

            if floor_id in self.floor_plans.keys():
                floor_plan = self.floor_plans[floor_id]

                id,name,a,b,c = floor_data
                new_floor = Floor(id = floor_id, name=name)
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

    def load_levels(self):

        logging.info("Starting loading Level Data...")

        new_level_data = (1, "Forest World", (1,2,3),"forest")
        self.level_data[1] = new_level_data

        new_level_data = (2, "Winter World", (100,101),"winter")
        self.level_data[2] = new_level_data

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