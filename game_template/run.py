import logging

import game_template.controller as controller


def main():
    c = controller.Controller()
    c.initialise()
    c.run()

    exit(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)

    main()
