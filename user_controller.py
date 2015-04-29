from __future__ import absolute_import, division, print_function, unicode_literals

from functools import partial

from config.mappings import Mapping
from enums.colors import Color, Pair
from enums.directions import Dir
from enums.keys import Key
from game_actions import ActionError
from generic_algorithms import add_vector
from interface.debug_action import debug_action
from interface.help_screen import help_screen
from interface.inventory import equipment
from interface.walk_mode import WalkMode
from level_template import LevelLocation


class UserController(object):
    error_messages = {
        ActionError.AlreadyActed:         "You already acted.",
        ActionError.IllegalMove:          "You can't move there.",
        ActionError.IllegalTeleport:      "You can't teleport there.",
        ActionError.SwapTargetResists:    "The creature resists your swap attempt.",
        ActionError.NoSwapTarget:         "There isn't a creature there to swap with.",
        ActionError.PassageLeadsNoWhere:  "This passage doesn't seem to lead anywhere.",
        ActionError.NoPassage:            "This location doesn't have a passage.",
        ActionError.PlayerAction:         "Only the player can do this action.",
    }

    def __init__(self, game_actions, io_system):
        self.game_actions = game_actions
        self.creature = game_actions.creature
        self.io = io_system
        self.walk_mode = WalkMode(self)
        self.action_mapping = {
            'd':  self.debug_action,
            '+':  partial(self.sight_change, 1),
            '-':  partial(self.sight_change, -1),

            Key.CLOSE_WINDOW:   self.quit,
            Mapping.Quit:       self.quit,
            Mapping.Save:       self.save,
            Mapping.Attack:     self.attack,
            Mapping.Redraw:     self.redraw,
            Mapping.History:    self.print_history,
            Mapping.Look_Mode:  self.look,
            Mapping.Help:       self.help_screen,
            Mapping.Inventory:  self.equipment,
            Mapping.Walk_Mode:  self.init_walk_mode,
            Mapping.Ascend:     partial(self.enter, LevelLocation.Passage_Up),
            Mapping.Descend:    partial(self.enter, LevelLocation.Passage_Down),
        }
        for key, direction in Mapping.Directions.items():
            self.action_mapping[key] = partial(self.act_to_dir, direction)
        for key, direction in Mapping.Instant_Walk_Mode.items():
            self.action_mapping[key] = partial(self.init_walk_mode, direction)

    def get_user_input_and_act(self):
        while True:
            if self.walk_mode.is_walk_mode_active():
                error = self.walk_mode.continue_walk()
            else:
                key = self.io.get_key()
                if key not in self.action_mapping:
                    self.io.msg("Undefined key: {}".format(key))
                    continue

                error = self.action_mapping[key]()

            if error is not None:
                if error == ActionError.AlreadyActed:
                    raise AssertionError("Player attempted to act twice.")
                elif error == ActionError.PlayerAction:
                    raise AssertionError("Player was denied a player only action.")
                elif error in self.error_messages:
                    self.io.msg(self.error_messages[error])
                else:
                    self.io.msg(error)

            if self.game_actions.already_acted():
                return

    def act_to_dir(self, direction):
        target_coord = add_vector(self.creature.coord, direction)
        level = self.creature.level
        error = None
        if level.creature_can_move(self.creature, direction):
            error = self.game_actions.move(direction)
        elif level.has_creature(target_coord):
            error = self.game_actions.attack(direction)
        else:
            error = ActionError.IllegalMove
        return error

    def look(self):
        coord = self.creature.coord
        level = self.creature.level
        drawline_flag = False
        direction = Dir.Stay
        while True:
            new_coord = add_vector(coord, direction)
            if level.legal_coord(new_coord):
                coord = new_coord
            self.io.msg(level.look_information(coord))
            if drawline_flag:
                self.io.draw_line(self.creature.coord, coord, ("*", Pair.Yellow))
                self.io.draw_line(coord, self.creature.coord, ("*", Pair.Yellow))
                self.io.msg("LoS: {}".format(level.check_los(self.creature.coord, coord)))
            if coord != self.creature.coord:
                char = level.get_visible_char(coord)
                char = char[0], (Color.Black, Color.Green)
                self.io.draw_char(coord, char)
                self.io.draw_char(self.creature.coord, level.get_visible_char(self.creature.coord), reverse=True)
            c = self.io.get_key()
            self.game_actions.redraw()
            direction = Dir.Stay
            if c in Mapping.Directions:
                direction = Mapping.Directions[c]
            elif c == 'd':
                drawline_flag = not drawline_flag
            elif c == 'b':
                from generic_algorithms import bresenham
                for coord in bresenham(level.get_coord(self.creature.coord), coord):
                    self.io.msg(coord)
            elif c == 's':
                if level.has_creature(coord):
                    self.game_actions.game.register_status_texts(level.get_creature(coord))
            elif c in Mapping.Group_Cancel or c == Mapping.Look_Mode:
                break

    def quit(self):
        self.game_actions.quit()

    def save(self):
        self.game_actions.save()

    def attack(self):
        msg = "Specify attack direction, {} to abort".format(Mapping.Cancel)
        key = self.io.ask(msg, Mapping.Directions.keys() | Mapping.Group_Cancel)
        if key in Mapping.Directions:
            return self.game_actions.attack(Mapping.Directions[key])

    def redraw(self):
        self.game_actions.redraw()

    def enter(self, passage):
        coord = self.creature.coord
        level = self.creature.level
        if level.has_exit(coord) and level.get_exit(coord) == passage:
            return self.game_actions.enter_passage()
        else:
            # debug use
            try:
                new_coord = level.get_passage_coord(passage)
            except KeyError:
                self.io.msg("This level doesn't seem to have a passage that way.")
            else:
                if not level.is_passable(new_coord):
                    level.remove_creature(level.get_creature(new_coord))
                error = self.game_actions.teleport(new_coord)
                return error

    def sight_change(self, amount):
        self.creature.base_perception += amount

    def print_history(self):
        self.io.m.print_history()

    def debug_action(self):
        debug_action(self.io, self.game_actions)

    def equipment(self):
        return equipment(self.io, self.creature.equipment)

    def init_walk_mode(self, instant_direction=None):
        return self.walk_mode.init_walk_mode(instant_direction)

    def help_screen(self):
        help_screen(self.io)
        self.game_actions.redraw()