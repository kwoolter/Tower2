import logging

import game_template.controller as controller
import os

def main():

    os.environ["SDL_VIDEO_CENTERED"] = "1"
    c = controller.Controller()
    c.initialise()
    c.run()

    exit(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)

    main()
