from unittest import TestCase
import game_template.model.rpg_world as model
import logging

class TestLevelBuilder(TestCase):
    def test_initialise(self):

        logging.basicConfig(level=logging.INFO)

        levels = model.LevelBuilder()
        levels.initialise()

        self.fail()

    def test_load_levels(self):

        logging.basicConfig(level=logging.INFO)

        floors = model.FloorBuilder()
        floors.initialise()

        levels = model.LevelBuilder()
        levels.initialise(floors)

        for level in levels.levels.values():
            print(str(level)+"\n")

        self.fail()

    def test_build_levels(self):
        self.fail()
