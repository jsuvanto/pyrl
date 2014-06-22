from __future__ import absolute_import, division, print_function, unicode_literals

import const.directions as DIR
import const.game as GAME
import rdg
import templates.tiles as TILE
from generic_algorithms import add_vector
from templates.monsters import monster_templates


DEFAULT_LEVEL_TYPE = rdg.DUNGEON


class LevelTemplate(object):

    def __init__(self, danger_level=0, static_level=False,
                 use_dynamic_monsters=True, tilemap_template=None,
                 static_monster_seq=(), rows=GAME.LEVEL_HEIGHT,
                 cols=GAME.LEVEL_WIDTH):
        self.danger_level = danger_level
        self.tilemap_template = tilemap_template
        self.static_level = static_level
        self.use_dynamic_monsters = use_dynamic_monsters
        self.rows = rows
        self.cols = cols
        self.passage_locations = {}
        self.passage_destination_infos = {}
        self.static_monster_templates = list(static_monster_seq)
        self.tile_dict = {}

    def finalize(self):
        if self.static_level:
            self._finalize_manual_tilemap_template()
        else:
            rdg.generate_tilemap_template(self, DEFAULT_LEVEL_TYPE)

    def get_tile_handle(self, y, x):
        return self.tilemap_template[y * self.cols + x]

    def set_tile_handle(self, y, x, tile_id):
        self.tilemap_template[y * self.cols + x] = tile_id

    def get_tile_from_coord(self, y, x):
        return self._gettile(self.get_tile_handle(y, x))

    def tilemap(self):
        for handle in self.tilemap_template:
            yield self._gettile(handle)

    def add_monster_template(self, monster):
        self.static_monster_templates.append(monster)

    def legal_coord(self, coord):
        return (0 <= coord[0] < self.rows) and (0 <= coord[1] < self.cols)

    def get_dynamic_monster_spawn_list(self):
        monster_list = []
        for monster in monster_templates:
            start = monster.speciation_lvl
            if start <= self.danger_level:
                weight_coeff = self.danger_level - monster.speciation_lvl
                monster_list.extend((monster, ) * weight_coeff)
        return monster_list

    def _gettile(self, handle, tile_dict=None):
        if tile_dict is not None and handle in tile_dict:
            return tile_dict[handle]
        elif handle in self.tile_dict:
            return self.tile_dict[handle]
        elif handle in TILE.tiles:
            return TILE.tiles[handle]
        else:
            raise KeyError("Handle '{}' not in global tiles nor in '{}'".format(handle, tile_dict))

    def _finalize_manual_tilemap_template(self):
        for loc, tile in enumerate(self.tilemap_template):
            coord = loc // self.cols, loc % self.cols
            if tile == TILE.STAIRS_UP:
                self.passage_locations[GAME.PASSAGE_UP] = coord
            elif tile == TILE.STAIRS_DOWN:
                self.passage_locations[GAME.PASSAGE_DOWN] = coord

        self._add_walls()

    def _add_walls(self):
        self.tilemap_template = [TILE.WALL if self._tile_qualifies_as_wall(loc, tile)
                                 else tile for loc, tile in enumerate(self.tilemap_template)]

    def _tile_qualifies_as_wall(self, loc, tile_handle):
        if tile_handle != TILE.ROCK:
            return False
        coord = loc // self.cols, loc % self.cols
        neighbor_coords = (add_vector(coord, direction) for direction in DIR.ALL_MINUS_STOP)
        valid_handles = (self.get_tile_handle(*coord) for coord in neighbor_coords if self.legal_coord(coord))
        return any(handle not in (TILE.WALL, TILE.ROCK) for handle in valid_handles)
