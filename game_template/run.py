import game_template.controller as controller
import logging


def main():
    c = controller.Controller()
    c.initialise()
    c.run()

    exit(0)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    main()