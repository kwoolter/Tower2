import logging
from copy import deepcopy

class Tiles:

    BEACH = "s"
    BOSS_DOOR = "d"
    BOSS_KEY = "$"
    DOOR = "D"
    EMPTY = " "
    ENTRANCE = "-"
    EXIT = "+"
    EXIT_KEY = "%"
    GOAL = "G"
    KEY = "?"
    PLAYER = "&"
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

class FloorPlan:

    def __init__(self, id : int, plan : list):
        self.id = id
        self.plan = deepcopy(plan)

    def get_tile(self, x : int, y : int):
        return self.plan[x][y]

class Floor:

    def __init__(self, id : int, name : str):
        self.id = id
        self.name = name
        self.monsters = []
        self.traps = []
        self.floor_plan = None

    def initialise(self, floor_plan : FloorPlan):
        self.floor_plan = floor_plan

    def tick(self):
        pass

    def get_tile(self, x : int, y: int):
        return self.floor_plan.get_tile(x,y)

    def __str__(self):
        string = "Floor {1}: '{0}'".format(self.name, self.id)
        return string

class Level:

    def __init__(self, id : int, name : str):
        self.id = id
        self.name = name

    def initialise(self):

        self.floors = {}

    def add_floor(self, new_floor : Floor):

        self.floors[new_floor.id] = new_floor

    def __str__(self):

        string = "Level {1}: '{0}' - {2} floors.".format(self.name, self.id, len(self.floors))

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

        new_floor_plan = (

            '::::::::::::::::::::',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            ':                  :',
            '::::::::::::::::::::',

        )

        self.floor_plans[1] = deepcopy(new_floor_plan)
        self.floor_plans[2] = deepcopy(new_floor_plan)
        self.floor_plans[100] = deepcopy(new_floor_plan)
        self.floor_plans[101] = deepcopy(new_floor_plan)

        logging.info("Finished loading floor plans. {0} floor plans loaded.".format(len(self.floor_plans.keys())))

    def load_floors(self):

        logging.info("Started loading floor configs...")

        new_floor_data = (1,"Start",2,3,4)
        self.floor_configs[new_floor_data[0]] = new_floor_data
        new_floor_data = (2,"Middle",2,3,4)
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

        new_level_data = (1, "Level 1", (1,2,3))
        self.level_data[1] = new_level_data

        new_level_data = (2, "Level 2", (100,101))
        self.level_data[2] = new_level_data

        logging.info("Finished Loading Level Data. {0} levels loaded.".format(len(self.level_data.keys())))

    def build_levels(self):

        logging.info("Starting building levels...")

        for level_id in self.level_data.keys():
            id, name, floor_ids = self.level_data[level_id]
            new_level = Level(id=id, name=name)
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

    def get_floor(self, floor_id : int):
        floor = None

        if floor_id in self.floor_builder.floors.keys():
            floor = self.floor_builder.floors[floor_id]

        return floor