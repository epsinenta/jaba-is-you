import argparse

import settings
from classes.game_context import GameContext
from elements.global_classes import sound_manager
from elements.progressbar_menu import ProgressBarMenu


def main():
    parser = argparse.ArgumentParser(description='Jaba')
    parser.add_argument("-d", "--debug", help='Logs some useful information', action="store_true")
    parser.add_argument("-m", "--map", help='Opens the whole map', action="store_true")
    args = parser.parse_args()
    if args.debug:
        settings.DEBUG = True
        print("Debug on")
        print("Какой дебаг? Багов не бывает.")
    if args.map:
        settings.FREEMAP = True
        print("Вся карта открыта, но вы туда не ходите. Там опасно.")

    sound_manager.start_download()


if __name__ == '__main__':
    main()
    GameContext(ProgressBarMenu).run()
