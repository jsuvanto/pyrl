import sys
import code
import debug

import const.keys as KEY
import const.directions as DIR
import const.game as GAME
import const.colors as COLOR
import const.generated_level_types as LEVEL_TYPE
import const.slots as SLOT
import const.stats as STAT
import mappings as MAPPING

from main import io
from world_file import LevelNotFound
from generic_algorithms import add_vector, turn_vector_left, turn_vector_right
from inventory import equipment; equipment

class UserInput(object):
	def __init__(self):
		no_args, no_kwds = (), {}
		self.actions = {
			KEY.CLOSE_WINDOW: ("endgame", no_args, no_kwds),
			MAPPING.ASCEND: ("enter", (GAME.PASSAGE_UP, ), no_kwds),
			MAPPING.DESCEND: ("enter", (GAME.PASSAGE_DOWN, ), no_kwds),
			MAPPING.QUIT: ("endgame", no_args, no_kwds),
			MAPPING.SAVE: ("savegame", no_args, no_kwds),
			MAPPING.ATTACK: ("attack", no_args, no_kwds),
			MAPPING.REDRAW: ("redraw", no_args, no_kwds),
			MAPPING.HISTORY: ("print_history", no_args, no_kwds),
			MAPPING.WALK_MODE: ("walk_mode_init", (self, ), no_kwds),
			MAPPING.LOOK_MODE: ("look", no_args, no_kwds),
			MAPPING.INVENTORY: ("equipment", no_args, no_kwds),
			'z': ("z_command", no_args, no_kwds),
			'd': ("debug_action", (self, ), no_kwds),
			'+': ("sight_change", (1, ), no_kwds),
			'-': ("sight_change", (-1, ), no_kwds),
		}
		for key, value in MAPPING.DIRECTIONS.viewitems():
			self.actions[key] = ("act_to_dir", (value, ), no_kwds)

		self.walk_mode = None

	def get_user_input_and_act(self, game, creature):
		taken_action = False
		while not taken_action:
			if self.walk_mode is not None:
				taken_action = _walk_mode(game, creature, self)
			else:
				key = io.get_key()
				if key in self.actions:
					taken_action = self.execute_action(game, creature, self.actions[key])
				else:
					io.msg("Undefined key: {}".format(key))

	def execute_action(self, game, creature, act):
		function, args, keywords = act
		return getattr(sys.modules[__name__], function)(game, creature, *args, **keywords)

def walk_mode_init(game, creature, userinput):
	level = creature.level
	if not any(level.has_creature(coord) for coord in game.current_vision if coord != creature.coord):
		key_set = MAPPING.DIRECTIONS.viewkeys() | MAPPING.GROUP_CANCEL
		key = io.ask("Specify walking direction, {} to abort".format(MAPPING.CANCEL), key_set)
		if key in MAPPING.DIRECTIONS:
			direction = MAPPING.DIRECTIONS[key]
			left_coord = add_vector(add_vector(creature.coord, direction), turn_vector_left(direction))
			right_coord = add_vector(add_vector(creature.coord, direction), turn_vector_right(direction))
			userinput.walk_mode = ((direction, level.is_passable(left_coord), level.is_passable(right_coord)),
					io.get_future_time())
			return game.creature_move(creature, direction)
	else:
		io.msg("Not while there are creatures in the vicinity.")
	return False

def _walk_mode(game, creature, userinput):
	level = creature.level
	if not any(level.has_creature(coord) for coord in game.current_vision if coord != creature.coord):
		old_walk_data, timestamp = userinput.walk_mode
		old_direction = old_walk_data[0]
		new_walk_data = (
				level.is_passable(add_vector(creature.coord, old_direction)),
				level.is_passable(add_vector(creature.coord, turn_vector_left(old_direction))),
				level.is_passable(add_vector(creature.coord, turn_vector_right(old_direction))),
		)
		result = _walk_mode_logic(old_walk_data, new_walk_data)
		if result is not None:
			new_direction, new_left, new_right = result
			message = "Press {} to interrupt walk mode".format(MAPPING.WALK_MODE)
			key = io.ask_until_timestamp(message, timestamp, MAPPING.GROUP_CANCEL | {MAPPING.WALK_MODE})
			if key not in MAPPING.GROUP_CANCEL | {MAPPING.WALK_MODE}:
				walk_delay = io.get_future_time()
				userinput.walk_mode = (new_direction, new_left, new_right), walk_delay
				return game.creature_move(creature, new_direction)

	userinput.walk_mode = None
	return False

# the booleans all denote if something is passable
def _walk_mode_logic(old_walk_data, new_walk_data):
	old_direction, old_left, old_right = old_walk_data
	target, new_left, new_right = new_walk_data
	if target:
		if new_left == old_left and new_right == old_right:
			return old_direction, old_left, old_right
	elif not old_left and not old_right and new_left != new_right:
		if new_left:
			new_direction = turn_vector_left(old_direction)
		elif new_right:
			new_direction = turn_vector_right(old_direction)
		return new_direction, old_left, old_right

def act_to_dir(game, creature, direction):
	target_coord = add_vector(creature.coord, direction)
	if game.creature_move(creature, direction):
		return True
	elif creature.level.has_creature(target_coord):
		game.creature_attack(creature, direction)
		return True
	else:
		if not creature.can_act():
			io.msg("You're out of energy.")
		else:
			io.msg("You can't move there.")
		return False

def z_command(game, creature):
	c = io.get_key()
	if c == 'Q':
		game.endgame(ask=False)
	elif c == 'Z':
		game.savegame(ask=False)

def look(game, creature):
	coord = creature.coord
	level = creature.level
	drawline_flag = False
	direction = DIR.STOP
	while True:
		new_coord = add_vector(coord, direction)
		if level.legal_coord(new_coord):
			coord = new_coord
		io.msg(level.look_information(coord))
		if drawline_flag:
			io.drawline(creature.coord, coord, ("*", COLOR.YELLOW))
			io.drawline(coord, creature.coord, ("*", COLOR.YELLOW))
			io.msg("LoS: {}".format(level.check_los(creature.coord, coord)))
		if coord != creature.coord:
			char = level._get_visible_char(coord)
			char = char[0], (COLOR.BASE_BLACK, COLOR.BASE_GREEN)
			io.draw_char(coord, char)
			io.draw_char(creature.coord, level._get_visible_char(creature.coord), reverse=True)
		c = io.get_key()
		game.redraw()
		direction = DIR.STOP
		if c in MAPPING.DIRECTIONS:
			direction = MAPPING.DIRECTIONS[c]
		elif c == 'd':
			drawline_flag = not drawline_flag
		elif c == 'b':
			from generic_algorithms import bresenham
			for coord in bresenham(level.get_coord(creature.coord), coord):
				io.msg(coord)
		elif c == 's':
			if level.has_creature(coord):
				game.register_status_texts(level.get_creature(coord))
		elif c in MAPPING.GROUP_CANCEL or c == MAPPING.LOOK_MODE:
			break

def endgame(game, creature, *a, **k):
	game.endgame(*a, **k)

def savegame(game, creature, *a, **k):
	game.savegame(*a, **k)

def attack(game, creature):
	key = io.ask("Specify attack direction, {} to abort".format(MAPPING.CANCEL), MAPPING.DIRECTIONS.viewkeys() | MAPPING.GROUP_CANCEL)
	if key in MAPPING.DIRECTIONS:
		game.creature_attack(creature, MAPPING.DIRECTIONS[key])
		return True

def redraw(game, creature):
	game.redraw()

def enter(game, creature, passage):
	coord = game.player.coord
	level = creature.level
	if level.is_exit(coord) and level.get_exit(coord) == passage:
		try:
			game.enter_passage(level.world_loc, level.get_exit(coord))
		except LevelNotFound:
			io.msg("This passage doesn't seem to lead anywhere.")
	else:
		try:
			new_coord = level.get_passage_coord(passage)
		except KeyError:
			io.msg("This level doesn't seem to have a corresponding passage.")
		else:
			if not level.is_passable(new_coord):
				level.remove_creature(level.get_creature(new_coord))
			level.move_creature(game.player, new_coord)
	return True

def sight_change(game, creature, amount):
	from const.slots import BODY
	from const.stats import SIGHT
	creature.get_item(BODY).stats[SIGHT] += amount
	return True

def print_history(game, creature):
	io.m.print_history()

def debug_action(game, creature, userinput):
	level = creature.level
	c = io.get_key("Avail cmds: vclbdhkpors+-")
	if c == 'v':
		debug.show_map = not debug.show_map
		game.redraw()
		io.msg("Show map set to {}".format(debug.show_map))
	elif c == 'c':
		debug.cross = not debug.cross
		io.msg("Path heuristic cross set to {}".format(debug.cross))
	elif c == 'l':
		GAME.LEVEL_TYPE = LEVEL_TYPE.ARENA if GAME.LEVEL_TYPE == LEVEL_TYPE.DUNGEON else LEVEL_TYPE.DUNGEON
		io.msg("Level type set to {}".format(GAME.LEVEL_TYPE))
	elif c == 'b':
		io.draw_block((4,4))
	elif c == 'd':
		if not debug.path:
			debug.path = True
			io.msg("Path debug set")
		elif not debug.path_step:
			debug.path_step = True
			io.msg("Path debug and stepping set")
		else:
			debug.path = False
			debug.path_step = False
			io.msg("Path debug unset")
	elif c == 'h':
		debug.reverse = not debug.reverse
		game.redraw()
		io.msg("Reverse set to {}".format(debug.reverse))
	elif c == 'k':
		creature_list = level.creatures.values()
		creature_list.remove(creature)
		for i in creature_list:
			level.remove_creature(i)
		io.msg("Abrakadabra.")
	elif c == 'o':
		passage_down = level.get_passage_coord(GAME.PASSAGE_DOWN)
		io.draw_path(level.path(creature.coord, passage_down))
		game.redraw()
	elif c == 'p':
		passage_up = level.get_passage_coord(GAME.PASSAGE_UP)
		passage_down = level.get_passage_coord(GAME.PASSAGE_DOWN)
		io.draw_path(level.path(passage_up, passage_down))
		game.redraw()
	elif c == 's':
		io.suspend()
		code.interact(local=locals())
		io.resume()
	elif c == 'e':
		import curses
		io.msg(curses.COLORS, curses.COLOR_PAIRS, curses.can_change_color())
		io.msg(curses.A_ALTCHARSET, curses.A_BLINK, curses.A_BOLD, curses.A_DIM, curses.A_NORMAL,
				curses.A_REVERSE, curses.A_STANDOUT, curses.A_UNDERLINE)
	elif c == 'r':
		io.a.get_key(refresh=True)
	elif c == '+':
		creature.get_item(SLOT.BODY).stats[STAT.SIGHT] += 1
		while True:
			c2 = io.getch_print("[+-]")
			if c2 == "+":
				creature.get_item(SLOT.BODY).stats[STAT.SIGHT] += 1
			elif c2 == "-":
				creature.get_item(SLOT.BODY).stats[STAT.SIGHT] -= 1
			else:
				break
	elif c == '-':
		creature.get_item(SLOT.BODY).stats[STAT.SIGHT] -= 1
		while True:
			c2 = io.getch_print("[+-]")
			if c2 == "+":
				creature.get_item(SLOT.BODY).stats[STAT.SIGHT] += 1
			elif c2 == "-":
				creature.get_item(SLOT.BODY).stats[STAT.SIGHT] -= 1
			else:
				break
	elif c == 'm':
		io.msg("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam varius massa enim, id fermentum erat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In et enim ut nibh rutrum suscipit. Aenean a lacus eget justo dignissim tempus. Nunc venenatis congue erat vel adipiscing. Nam nulla felis, accumsan eu sagittis aliquet, fermentum at tortor. Suspendisse tortor risus, dapibus quis porta vel, mattis sit amet libero. Morbi vel metus eget metus ultricies ultrices placerat ac sapien. Lorem ipsum dolor sit amet, consectetur adipiscing elit.  Nulla urna erat, lacinia vitae pellentesque et, accumsan eget ante. Sed commodo molestie ipsum, a mattis sapien malesuada at. Integer et lorem magna. Sed nec erat orci. Donec id elementum elit. In hac habitasse platea dictumst. Duis id nisi ut felis convallis blandit id sit amet magna. Nam feugiat erat eget velit ullamcorper varius. Nunc tellus massa, fermentum eu aliquet non, fermentum a quam.  Pellentesque turpis erat, aliquam at feugiat in, congue nec urna. Nulla ut turpis dapibus metus blandit faucibus.  Suspendisse potenti. Proin facilisis massa vitae purus dignissim quis dapibus eros gravida. Vivamus ac sapien ante, ut euismod nunc. Pellentesque faucibus neque at tortor malesuada eu commodo nisl vehicula. Vivamus eu odio ut est egestas luctus. Duis orci magna, tincidunt id suscipit id, consectetur sodales nisl. Etiam justo lorem, molestie sit amet rutrum eget, consequat mattis magna.  Fusce eros est, tincidunt id consequat id, scelerisque ac sapien.  Donec lacus leo, adipiscing et vulputate in, pulvinar vitae sem. Suspendisse sem augue, adipiscing vitae tempor sit amet, egestas a neque. Donec nibh mauris, rutrum vitae dictum in, adipiscing in magna. Duis fringilla sem vel nisl tempus dignissim. Fusce vel felis ipsum. Sed risus ipsum, iaculis a mollis vel, viverra in nisi. Suspendisse est tellus, aliquet et vulputate vel, iaculis egestas nulla.  Praesent sed tortor sed neque varius consequat. Quisque interdum facilisis convallis. Aliquam eu nisi arcu. Proin convallis sagittis nisi id molestie. Aenean rutrum elementum mauris, vitae venenatis tellus semper et. Proin eu nisl ligula. Maecenas dui mi, varius eget adipiscing quis, commodo et libero.")
	else:
		io.msg("Undefined debug key: {}".format(chr(c) if 0 < c < 128 else c))
