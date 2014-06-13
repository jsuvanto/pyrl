from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import const.game as GAME
import const.maps as MAP

from level_template import LevelTemplate


class LevelNotFound(Exception):
    pass


class WorldFile(object):

    def __init__(self):
        self.level_templates = {}
        self.level_passageways = {}
        self.dungeon_lengths = {}

        self.add_dungeon(GAME.DUNGEON)
        self.add_level(GAME.DUNGEON, MAP.L0)
        for x in range(GAME.LEVELS_PER_DUNGEON - 1):
            self.add_level(GAME.DUNGEON)

    def add_dungeon(self, dungeon_key):
        self.dungeon_lengths[dungeon_key] = 1

    def add_level(self, dungeon_key, level_template=None):
        level_i = self.dungeon_lengths[dungeon_key]
        if level_template is None:
            self.level_templates[dungeon_key, level_i] = LevelTemplate(level_i)
        else:
            self.level_templates[dungeon_key, level_i] = level_template
        self.level_passageways[dungeon_key, level_i] = {GAME.PASSAGE_UP: GAME.UP,
                                                        GAME.PASSAGE_DOWN: GAME.DOWN}
        self.dungeon_lengths[dungeon_key] += 1

    def get_level_template(self, world_loc):
        try:
            return self.level_templates[world_loc]
        except KeyError:
            raise LevelNotFound("Nonexistant level key: {}".format(world_loc))

    def pop_level_template(self, world_loc):
        try:
            level_template = self.level_templates[world_loc]
        except KeyError:
            raise LevelNotFound("Nonexistant level key: {}".format(world_loc))
        else:
            del self.level_templates[world_loc]
            return level_template

    def get_passage_info(self, world_loc, passage):
        return self.level_passageways[world_loc][passage]
