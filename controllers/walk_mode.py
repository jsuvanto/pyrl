from __future__ import absolute_import, division, print_function, unicode_literals

from config.game import GameConf
from enums.directions import Dir
from generic_algorithms import add_vector, get_vector, clockwise, anticlockwise, reverse_vector, clockwise_45, anticlockwise_45
from config.bindings import Bind
from enums.keys import Key
from controllers.user_controller import UserControllerProxy


WALK_IN_PLACE = (None, None)
CORRIDOR      = (False, False)
LEFT          = (True, False)
RIGHT         = (False, True)
OPEN          = (True, True)

INTERRUPT_MSG_TIME = 1


class WalkMode(UserControllerProxy):

    def __init__(self, user_controller):
        super().__init__(user_controller)
        self.state = None

    def is_walk_mode_active(self):
        return self.state is not None

    def init_walk_mode(self, direction=None):
        if self._any_creatures_visible():
            self.io.msg("Not while there are creatures in the vicinity.")
            return None

        if direction is None:
            user_query = "Specify walking direction, {} to cancel.".format(Bind.Cancel.key)
            key_seq = tuple(Bind.action_direction.keys()) + Bind.Cancel
            key = self.io.ask(user_query, key_seq)
            if key in Bind.action_direction:
                direction = Bind.action_direction[key]
            else:
                return None

        error, walk_mode_data = self._init_walk_mode(direction)
        if walk_mode_data is not None:
            self.state = walk_mode_data
        return error

    def continue_walk(self):
        if not self._any_creatures_visible():
            old_direction, old_walk_type, timestamp, msg_time = self.state
            if old_walk_type == WALK_IN_PLACE:
                result = old_direction, old_walk_type
            elif old_walk_type == CORRIDOR:
                result = self._corridor_walk_type(old_direction)
            else:
                result = self._normal_walk_type(old_direction, old_walk_type)

            if result is not None:
                new_direction, new_walk_type = result
                if msg_time < self.io.get_current_time():
                    message = "Press {} or {} to interrupt walk mode.".format(Bind.Walk_Mode.key, Bind.Cancel.key)
                else:
                    message = ""
                key_seq = Bind.Walk_Mode + Bind.Cancel
                key = self.io.selective_ask_until_timestamp(message, timestamp, key_seq)
                if key == Key.NO_INPUT:
                    error = self.game_actions.move(new_direction)
                    if not error:
                        walk_delay = self.io.get_future_time(GameConf.animation_period)
                        self.state = new_direction, new_walk_type, walk_delay, msg_time
                    return error

        self.state = None

    def _init_walk_mode(self, direction):
        error = self.game_actions.move(direction)
        if error:
            return error, None
        else:
            walk_type = self._get_walk_type(direction)
            if walk_type != WALK_IN_PLACE:
                (forward, upper_left, upper_right, left, right, lower_left,
                        lower_right) = self._get_neighbor_passables(direction)
                if forward:
                    if (left and not upper_left and not lower_left or
                            right and not upper_right and not lower_right):
                        return None, None
                else:
                    if left and lower_left or right and lower_right:
                        return None, None
                    walk_type = CORRIDOR

            return (error, (direction, walk_type,
                    self.io.get_future_time(GameConf.animation_period),
                    self.io.get_future_time(INTERRUPT_MSG_TIME)))

    def _corridor_walk_type(self, origin_direction):
        forward_dirs, orthogonal_dirs, ignored_dirs = self._get_corridor_candidate_dirs(origin_direction)
        if len(forward_dirs) == 1:
            direction = forward_dirs.pop()
            return direction, CORRIDOR
        elif len(forward_dirs) > 1 and len(orthogonal_dirs) == 1:
            direction = orthogonal_dirs.pop()
            if all(get_vector(direction, other) in Dir.AllPlusStay for other in forward_dirs):
                return direction, CORRIDOR

    def _get_corridor_candidate_dirs(self, direction):
        reverse = reverse_vector(direction)
        back_sides = {anticlockwise_45(reverse), clockwise_45(reverse)}
        candidate_dirs = set(self.level.get_passable_neighbors(self.creature.coord)) - {reverse}
        candidate_forward_dirs = candidate_dirs - back_sides
        candidate_orthogonal_dirs = candidate_dirs & set(Dir.Orthogonals)
        ignored_dirs = candidate_dirs & back_sides
        return candidate_forward_dirs, candidate_orthogonal_dirs, ignored_dirs

    def _normal_walk_type(self, direction, old_walk_type):
        forward = self._passable(direction)
        new_walk_type = self._get_walk_type(direction)
        if forward and old_walk_type == new_walk_type:
            return direction, new_walk_type

    def _passable(self, direction):
        return self.level.is_passable(add_vector(self.creature.coord, direction))

    def _get_neighbor_passables(self, direction):
            upper_left_dir = anticlockwise_45(direction)
            upper_right_dir = clockwise_45(direction)

            forward = self._passable(direction)
            left = self._passable(anticlockwise(direction))
            right = self._passable(clockwise(direction))
            upper_left = self._passable(upper_left_dir)
            lower_left = self._passable(anticlockwise(upper_left_dir))
            upper_right = self._passable(upper_right_dir)
            lower_right = self._passable(clockwise(upper_right_dir))
            return forward, upper_left, upper_right, left, right, lower_left, lower_right

    def _get_walk_type(self, direction):
        if direction in Dir.Orthogonals:
            left = self._passable(anticlockwise(direction))
            right = self._passable(clockwise(direction))
        elif direction in Dir.Diagonals:
            left = self._passable(anticlockwise_45(direction))
            right = self._passable(clockwise_45(direction))
        elif direction == Dir.Stay:
            left, right = WALK_IN_PLACE
        else:
            raise Exception("Not a valid direction: {0}".format(direction))
        return left, right

    def _any_creatures_visible(self):
        not_self = lambda coord: coord != self.creature.coord
        return any(coord in self.level.creatures for coord in self.creature.vision if not_self(coord))
