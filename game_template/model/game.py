import logging
import game_template.utils as utils
import time

class Player:

    def __init__(self, name : str):
        self.name = name


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


    def initialise(self):

        logging.info("Initialising {0}...".format(self.name))

        self.state = Game.READY

        self.players = []
        self.player_scores = {}

        self.hst.load()

    def add_player(self, new_player : Player):

        if self.state != Game.READY:
            raise Exception("Game is in state {0} so can't add new players!".format(self.state))

        logging.info("Adding new player {0} to game {1}...".format(new_player.name, self.name))

        self.players.append(new_player)
        self.player_scores[new_player.name] = 0

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
