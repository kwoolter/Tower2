import game_template.model as rpg_world_model
from game_template.view import *
import pygame


class FloorView(View):

    def __init__(self, width : int, height : int):
        super(FloorView, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.floor = None

    def initialise(self, floor : rpg_world_model.Floor):
        self.floor = floor


    def draw(self):
        pass

