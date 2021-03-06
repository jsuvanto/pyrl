from collections import Counter, namedtuple

from enums.level_location import LevelLocation
from world.level import Level


class LevelNotFound(Exception): pass


LevelKey = namedtuple("LevelKey", ("dungeon, index"))
WorldPoint = namedtuple("WorldPoint", ("level_key, level_location"))


class World(object):

    def __init__(self, player):
        self.levels = {}
        self.level_connections = {}
        self.dungeon_lengths = Counter()
        self.player = player
        self.start_level_key = None

    def add_level(self, dungeon_key, level=None):
        self.dungeon_lengths[dungeon_key] += 1
        level_i = self.dungeon_lengths[dungeon_key]
        curr_level_key = LevelKey(dungeon_key, level_i)
        prev_level_key = LevelKey(dungeon_key, level_i - 1)

        if level is None:
            level = Level(level_i)

        self.levels[curr_level_key] = level
        if level_i != 1:
            previous_level = self.levels[prev_level_key]

            passage_down = LevelLocation.Passage_Down
            passage_up = LevelLocation.Passage_Up
            if previous_level.will_have_location(passage_down) and level.will_have_location(passage_up):
                self.set_two_way_connection(WorldPoint(prev_level_key, passage_down), WorldPoint(curr_level_key, passage_up))

    def get_level(self, level_key):
        if level_key not in self.levels:
            raise LevelNotFound("Nonexistant level key: {}".format(level_key))

        level = self.levels[level_key]
        if not level.is_finalized:
            level.finalize(level_key)
        return level

    def has_destination(self, world_point):
        return world_point in self.level_connections

    def get_destination(self, world_point):
        return self.level_connections[world_point]

    def set_two_way_connection(self, world_point_A, world_point_B, do_Assert=True):

        if do_Assert:
            level_A = self.levels[world_point_A.level_key]
            level_B = self.levels[world_point_B.level_key]
            assert level_A.will_have_location(world_point_A.level_location), \
                "{} doesn't have location {}.".format(level_A, world_point_A.level_location)
            assert level_B.will_have_location(world_point_B.level_location), \
                "{} doesn't have location {}.".format(level_B, world_point_B.level_location)

        self.set_connection(world_point_A, world_point_B)
        self.set_connection(world_point_B, world_point_A)

    def set_connection(self, world_point_A, world_point_B):
        self.level_connections[world_point_A] = world_point_B
