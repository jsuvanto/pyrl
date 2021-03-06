from creature.stats import Stat
from dice import dice_str


def register_status_texts(io, game, creature):
    add_element = io.status_bar.add_element
    add_element("Dmg",                      lambda: dice_str(*creature.get_damage_info()))
    add_element("HP",                       lambda: "{}/{}".format(creature.hp, creature.max_hp))
    add_element(Stat.sight.value,           lambda: creature.sight)
    add_element(Stat.accuracy.value,        lambda: creature.accuracy)
    add_element(Stat.defense.value,         lambda: creature.defense)
    add_element(Stat.armor.value,           lambda: creature.armor)
    add_element(Stat.speed.value,           lambda: creature.speed)
    add_element(Stat.strength.value,        lambda: creature.strength)
    add_element(Stat.dexterity.value,       lambda: creature.dexterity)
    add_element(Stat.intelligence.value,    lambda: creature.intelligence)
    add_element(Stat.endurance.value,       lambda: creature.endurance)
    add_element(Stat.perception.value,      lambda: creature.perception)
    add_element("Wloc",                     lambda: "{}/{}".format(*creature.level.key))
    add_element("Loc",                      lambda: "{0:02},{1:02}".format(*creature.coord))
    add_element("Turns",                    lambda: game.turn_counter)
    add_element("Game Time",                lambda: game.time)
    add_element("Level Time",               lambda: creature.level.turn_scheduler.time)
