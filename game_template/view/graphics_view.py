import pygame
import game_template.model as model
from .colours import Colours
import os
import game_template.utils as utils
import time


class View:

    def __init__(self):
        self.tick_count = 0

    def initialise(self):
        self.tick_count = 0

    def tick(self):
        self.tick_count += 1

    def draw(self):
        pass

    def end(self):
        pass


class MainFrame(View):
    TITLE_HEIGHT = 30
    STATUS_HEIGHT = 30

    RESOURCES_DIR = os.path.dirname(__file__) + "\\resources\\"

    def __init__(self, width: int = 600, height: int = 600):

        super(MainFrame, self).__init__()

        self.game = None

        self.surface = pygame.display.set_mode((width, height))

        self.title = TitleBar(width=width, height=MainFrame.TITLE_HEIGHT)
        self.status = StatusBar(width=width, height=MainFrame.STATUS_HEIGHT)
        self.hst = HighScoreTableView(width=width, height=300)
        self.game_view = GameView(width=width, height=height - MainFrame.TITLE_HEIGHT - MainFrame.STATUS_HEIGHT)
        self.game_ready = GameReadyView(width=width, height=height - MainFrame.TITLE_HEIGHT - MainFrame.STATUS_HEIGHT)
        self.game_over = GameOverView(width=width, height=height - MainFrame.TITLE_HEIGHT - MainFrame.STATUS_HEIGHT)

    def initialise(self, game: model.Game):

        super(MainFrame,self).initialise()

        self.game = game

        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.display.set_caption(self.game.name)
        filename = MainFrame.RESOURCES_DIR + self.game.name + ".jpg"
        image = pygame.image.load(filename)
        image = pygame.transform.scale(image, (32, 32))
        pygame.display.set_icon(image)

        self.title.initialise(self.game)
        self.status.initialise(self.game)
        self.hst.initialise(self.game.hst)
        self.game_view.initialise(self.game)
        self.game_ready.initialise(self.game)
        self.game_over.initialise(self.game)

    def tick(self):

        super(MainFrame,self).tick()

        self.title.tick()
        self.status.tick()
        self.game_view.tick()
        self.game_ready.tick()
        self.game_over.tick()

    def draw(self):

        super(MainFrame,self).draw()

        self.surface.fill(Colours.BLACK)

        pane_rect = self.surface.get_rect()

        self.title.draw()
        self.status.draw()

        x = 0
        y = 0

        self.surface.blit(self.title.surface, (x, y))

        y += MainFrame.TITLE_HEIGHT

        self.surface.blit(self.game_view.surface, (x, y))

        x = 0
        y = pane_rect.bottom - MainFrame.STATUS_HEIGHT

        self.surface.blit(self.status.surface, (x, y))

        if self.game.state in (model.Game.PLAYING, model.Game.PAUSED):

            self.game_view.draw()
            x = 0
            y = MainFrame.STATUS_HEIGHT

            self.surface.blit(self.game_view.surface, (x, y))

        elif self.game.state == model.Game.READY:

            self.game_ready.draw()
            x = 0
            y = MainFrame.STATUS_HEIGHT

            self.surface.blit(self.game_ready.surface, (x, y))

        elif self.game.state == model.Game.GAME_OVER:

            self.game_over.draw()
            x = 0
            y = MainFrame.STATUS_HEIGHT

            self.surface.blit(self.game_over.surface, (x, y))



    def update(self):
        pygame.display.update()

    def end(self):

        super(MainFrame,self).end()

        self.game_view.end()
        self.title.end()
        self.status.end()
        self.hst.end()


class TitleBar(View):
    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.BLUE

    def __init__(self, width: int, height: int):

        super(TitleBar, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.title = "Title"
        self.game = None

    def initialise(self, game: model.Game):

        super(TitleBar,self).initialise()

        self.game = game
        self.title = game.name

    def draw(self):

        super(TitleBar,self).draw()

        self.surface.fill(TitleBar.BG_COLOUR)
        pane_rect = self.surface.get_rect()

        if self.title is not None:
            draw_text(self.surface,
                      msg=self.title,
                      x=pane_rect.centerx,
                      y=int(pane_rect.height / 2),
                      fg_colour=TitleBar.FG_COLOUR,
                      bg_colour=TitleBar.BG_COLOUR,
                      size=pane_rect.height)


class StatusBar(View):

    FG_COLOUR = Colours.BLACK
    BG_COLOUR = Colours.RED
    PADDING = 4

    def __init__(self, width: int, height: int):

        super(StatusBar, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.status_messages = []
        self.game = None

    def initialise(self, game: model.Game):

        super(StatusBar,self).initialise()

        self.game = game
        self.title = game.name
        self.current_message_number = 0
        for i in range(4):
            self.status_messages.append("Msg {0}".format(i))


    def tick(self):

        super(StatusBar, self).tick()

        self.current_message_number += 1
        if self.current_message_number >= len(self.status_messages):
            self.current_message_number = 0


    def draw(self):

        self.surface.fill(StatusBar.BG_COLOUR)

        pane_rect = self.surface.get_rect()

        msg = self.status_messages[self.current_message_number]

        draw_text(self.surface,
                  msg=msg,
                  x=pane_rect.centerx,
                  y=int(pane_rect.height / 2),
                  fg_colour=StatusBar.FG_COLOUR,
                  bg_colour=StatusBar.BG_COLOUR,
                  size=pane_rect.height)

        if self.game.state == model.Game.PLAYING:
            draw_text(self.surface,
                      msg=time.strftime("Time:%H:%M:%S", self.game.elapsed_time),
                      x=StatusBar.PADDING, y=int(pane_rect.height / 2),
                      fg_colour=StatusBar.FG_COLOUR,
                      bg_colour=StatusBar.BG_COLOUR,
                      size=pane_rect.height)


class HighScoreTableView(View):

    TITLE_HEIGHT = 24
    TITLE_TEXT_SIZE = 30
    SCORE_HEIGHT = 20
    SCORE_TEXT_SIZE = 20

    FG_COLOUR = Colours.WHITE
    BG_COLOUR = Colours.BLACK

    def __init__(self, width: int, height: int = 500):

        super(HighScoreTableView, self).__init__()

        self.hst = None
        self.surface = pygame.Surface((width, height))

    def initialise(self, hst: utils.HighScoreTable):

        super(HighScoreTableView,self).initialise()

        self.hst = hst

    def draw(self):

        if self.hst is None:
            raise ("No High Score Table to view!")

        self.surface.fill(HighScoreTableView.BG_COLOUR)

        pane_rect = self.surface.get_rect()

        y = HighScoreTableView.TITLE_HEIGHT
        x = pane_rect.centerx

        draw_text(self.surface, msg="High Score Table", x=x, y=y,
                  size=HighScoreTableView.TITLE_TEXT_SIZE,
                  fg_colour=Colours.GOLD)

        if len(self.hst.table) == 0:

            y += HighScoreTableView.SCORE_HEIGHT

            draw_text(self.surface, msg="No high scores recorded",
                      x=x, y=y,
                      size=HighScoreTableView.SCORE_TEXT_SIZE,
                      fg_colour=HighScoreTableView.FG_COLOUR,
                      bg_colour=HighScoreTableView.BG_COLOUR)
        else:
            rank = 1
            for entry in self.hst.table:
                y += HighScoreTableView.SCORE_HEIGHT

                name, score = entry
                draw_text(self.surface, msg="{0}. {1} - {2}".format(rank, name, score), x=x, y=y,
                          size=HighScoreTableView.SCORE_TEXT_SIZE,
                          fg_colour=HighScoreTableView.FG_COLOUR,
                          bg_colour=HighScoreTableView.BG_COLOUR)
                rank += 1



class GameReadyView(View):

    FG_COLOUR = Colours.GOLD
    BG_COLOUR = Colours.GREY

    def __init__(self, width: int, height: int = 500):

        super(GameReadyView, self).__init__()

        self.game = None
        self.hst = HighScoreTableView(width=width, height=300)

        self.surface = pygame.Surface((width, height))

    def initialise(self, game : model.Game):

        self.game = game
        self.hst.initialise(self.game.hst)

    def draw(self):

        if self.game is None:
            raise ("No Game to view!")

        self.surface.fill(GameReadyView.BG_COLOUR)

        pane_rect = self.surface.get_rect()

        x=pane_rect.centerx
        y=20

        draw_text(self.surface,
                  msg="G A M E    R E A D Y",
                  x=x,
                  y=y,
                  size = 30,
                  fg_colour=GameReadyView.FG_COLOUR,
                  bg_colour=GameReadyView.BG_COLOUR)

        x=0
        y=pane_rect.bottom - self.hst.surface.get_height()
        self.hst.draw()
        self.surface.blit(self.hst.surface, (x, y))


class GameOverView(View):

    FG_COLOUR = Colours.GOLD
    BG_COLOUR = Colours.GREY

    def __init__(self, width: int, height: int = 500):

        super(GameOverView, self).__init__()

        self.game = None

        self.surface = pygame.Surface((width, height))

    def initialise(self, game : model.Game):

        self.game = game

    def draw(self):

        if self.game is None:
            raise ("No Game to view!")

        self.surface.fill(GameOverView.BG_COLOUR)

        pane_rect = self.surface.get_rect()

        draw_text(self.surface,
                  msg="G A M E    O  V E R",
                  x=pane_rect.centerx,
                  y=pane_rect.centery,
                  size = 30,
                  fg_colour=GameOverView.FG_COLOUR,
                  bg_colour=GameOverView.BG_COLOUR)

class GameView(View):

    BG_COLOUR = Colours.GREEN
    FG_COLOUR = Colours.WHITE

    def __init__(self, width: int, height: int):

        super(GameView, self).__init__()

        self.surface = pygame.Surface((width, height))
        self.game = None

    def initialise(self, game: model.Game):

        super(GameView,self).initialise()

        self.game = game

    def tick(self):

        super(GameView,self).tick()


    def draw(self):

        self.surface.fill(GameView.BG_COLOUR)

        if self.game is None:
            raise ("No Game to view!")

    def end(self):

        super(GameView,self).end()



def draw_text(surface, msg, x, y, size=32, fg_colour=Colours.WHITE, bg_colour=Colours.BLACK):
    font = pygame.font.Font(None, size)
    text = font.render(msg, 1, fg_colour, bg_colour)
    textpos = text.get_rect()
    textpos.centerx = x
    textpos.centery = y
    surface.blit(text, textpos)
