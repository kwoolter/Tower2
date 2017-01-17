import game_template.model as rpg_world_model
from .graphics_view import *
import pygame
from .colours import Colours


class FloorView(View):

    BG_COLOUR = Colours.WHITE

    def __init__(self, width : int, height : int):
        super(FloorView, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.floor = None

    def initialise(self, floor : rpg_world_model.Floor):
        self.floor = floor


    def draw(self):
        self.surface.fill(FloorView.BG_COLOUR)

        if self.floor is None:
            raise ("No Floor to view!")

