import argparse
import cProfile
import state_store
from const.game import NCURSES
from window.window_system import WindowSystem

# Global object for the input and output window system
# Check the WindowSystem class for the implementation
io = None


def init_window_system(cursor_library):
    global io
    io = WindowSystem(cursor_library)


def start():
    if io.cursor_lib.get_implementation() == NCURSES:
        # check to see the window is big enough
        io.cursor_lib._window_resized()

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--load", action="store_true")
    parser.add_argument("-p", "--profile", action="store_true")
    options = parser.parse_args()

    from game import Game

    if options.load:
        game = load("pyrl.svg")
        game.register_status_texts(game.player)
        game.redraw()
    else:
        game = Game()

    if options.profile:
        cProfile.run("game.main_loop()")
    else:
        game.main_loop()


def load(name):
    return state_store.load(name)
