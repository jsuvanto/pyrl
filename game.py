import ai
import const.game as GAME
import const.creature_actions as CC
import const.stats as STAT
import debug
import state_store
import rdg

from main import io
from const.player import Player
from level import Level
from user_input import UserInput
from world_file import WorldFile
from fov import get_light_set
from combat import get_melee_attack, get_combat_message
from generic_algorithms import add_vector
from itertools import imap


class Game(object):

	def __init__(self):
		"""pyrl; Python roguelike by Tapani Kiiskinen"""

		self.turn_counter = 0
		self.user_input = UserInput()
		self.current_vision = set()
		self.levels = {}
		self.world_file = WorldFile()
		self.player = Player()

		self.init_new_level(GAME.FIRST_LEVEL)
		first_level = self.levels[GAME.FIRST_LEVEL]
		first_level.add_creature(self.player, first_level.get_passage_coord(GAME.PASSAGE_UP))
		self.register_status_texts(self.player)
		self.vision_cache = None

	def is_player(self, creature):
		return self.player is creature

	def register_status_texts(self, creature):
		io.s.add_element(STAT.DMG, lambda: "{}D{}+{}".format(*creature.get_damage_info()))
		io.s.add_element("HP", lambda: "{}/{}".format(creature.hp, creature.max_hp))
		io.s.add_element(STAT.SIGHT, lambda: creature.sight)
		io.s.add_element(STAT.AR, lambda: creature.ar)
		io.s.add_element(STAT.DR, lambda: creature.dr)
		io.s.add_element(STAT.PV, lambda: creature.pv)
		io.s.add_element(STAT.SPEED, lambda: creature.speed)
		io.s.add_element(STAT.ST, lambda: creature.st)
		io.s.add_element(STAT.DX, lambda: creature.dx)
		io.s.add_element(STAT.TO, lambda: creature.to)
		io.s.add_element(STAT.LE, lambda: creature.le)
		io.s.add_element(STAT.PE, lambda: creature.pe)
		io.s.add_element("Wloc", lambda: "{}/{}".format(*self.player.level.world_loc))
		io.s.add_element("Loc", lambda: "{0:02},{1:02}".format(*creature.coord))
		io.s.add_element("Turns", lambda: self.turn_counter)

	def enter_passage(self, origin_world_loc, origin_passage):
		instruction, d, i = self.world_file.get_passage_info(origin_world_loc, origin_passage)
		if instruction == GAME.SET_LEVEL:
			self.change_level((d, i))
		else:
			d, i = self.player.level.world_loc
			if instruction == GAME.PREVIOUS_LEVEL:
				self.change_level((d, i - 1), GAME.PASSAGE_DOWN)
			elif instruction == GAME.NEXT_LEVEL:
				self.change_level((d, i + 1), GAME.PASSAGE_UP)

	def change_level(self, world_loc, passage):
		old_level = self.player.level
		try:
			new_level = self.levels[world_loc]
		except KeyError:
			self.init_new_level(world_loc)
			new_level = self.levels[world_loc]
		old_level.remove_creature(self.player)
		new_level.add_creature(self.player, new_level.get_passage_coord(passage))
		self.current_vision = set()
		self.redraw()

	def init_new_level(self, world_loc):
		level_file = self.world_file.pop_level_file(world_loc)
		if not level_file.static_level:
			rdg.add_generated_tilefile(level_file, GAME.LEVEL_TYPE)
		self.levels[world_loc] = Level(world_loc, level_file)

	def play(self):
		level = self.player.level
		if level.turn_scheduler.is_new_turn():
			pass

		creature = level.turn_scheduler.get()
		creature.recover_energy()
		if self.is_player(creature):
			if creature.can_act():
				self.player_act()
				self.turn_counter += 1
		else:
			ai.act_alert(self, creature, self.player.coord)

	def player_act(self):
		level = self.player.level
		if debug.show_map:
			io.draw(level.get_wallhack_data(level.get_coord_iter()))
		self.update_view(self.player.level, self.player)
		self.user_input.get_user_input_and_act(self, self.player)

	def creature_move(self, creature, direction):
		level = creature.level
		if level.creature_can_move(creature, direction) and creature.can_act():
			target_coord = add_vector(creature.coord, direction)
			creature.update_energy(level.movement_cost(direction, target_coord))
			level.move_creature(creature, target_coord)
			return True
		else:
			return False

	def creature_swap(self, creature, direction):
		target_coord = add_vector(creature.coord, direction)
		level = creature.level
		if creature.can_act() and level.creature_is_swappable(target_coord):
			target_creature = level.get_creature(target_coord)
			energy_cost = level.movement_cost(direction, target_coord)
			creature.update_energy(energy_cost)
			target_creature.update_energy(energy_cost)
			level.swap_creature(creature, target_creature)
			return True
		else:
			return False

	def creature_attack(self, creature, direction):
		level = creature.level
		if creature.can_act():
			creature.update_energy_action(CC.ATTACK)
			target_coord = add_vector(creature.coord, direction)
			if level.has_creature(target_coord):
				target = level.get_creature(target_coord)
			else:
				target = level.tiles[target_coord]
			succeeds, damage = get_melee_attack(creature.ar, creature.get_damage_info(), target.dr, target.pv)
			if damage:
				target.receive_damage(damage)
				died = target.is_dead()
			else:
				died = False
			player_matrix = imap(self.is_player, (creature, target))
			msg = get_combat_message(succeeds, damage, died, player_matrix, creature.name, target.name)
			if died:
				self.creature_death(target)
			io.msg(msg)
			return True
		else:
			return False

	def creature_death(self, creature):
		level = creature.level
		if self.is_player(creature):
			io.notify("You die...")
			self.endgame(False)
		level.remove_creature(creature)

	def endgame(self, ask=False, message=""):
		io.msg(message)
		if not ask:
			exit()
		if io.ask("Do you wish to end the game? [y/N]") in GAME.YES:
			exit()

	def savegame(self, ask=False):
		if not ask or io.ask("Do you wish to save the game? [y/N]") in GAME.YES:
			io.msg("Saving...")
			io.refresh()
			io.msg(state_store.save(self, "pyrl.svg"))

	def update_view(self, level, creature):
		old = self.current_vision if not debug.show_map else set()
		new = get_light_set(level.is_see_through, creature.coord, creature.sight, level.rows, level.cols)
		mod = level.pop_modified_locations()
		level.update_visited_locations(new - old)

		out_of_sight_memory_data = level.get_memory_data(old - new)
		io.draw(out_of_sight_memory_data)

		new_visible_data = level.get_visible_data(new - (old - mod))
		io.draw(new_visible_data, debug.reverse)

		self.current_vision = new

	def redraw(self):
		io.l.clear()
		level = self.player.level
		if debug.show_map:
			io.draw(level.get_wallhack_data(level.get_coord_iter()))
		memory_data = level.get_memory_data(level.visited_locations)
		io.draw(memory_data)
		vision_data = level.get_visible_data(self.current_vision)
		io.draw(vision_data, debug.reverse)
