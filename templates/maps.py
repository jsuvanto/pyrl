from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import const.game as GAME

from level_template import LevelTemplate
from world_template import WorldTemplate
from monster_template import MonsterTemplate
from const.colors import PURPLE


def World():

    L0 = LevelTemplate(
        danger_level=1,
        static_level=True,
        use_dynamic_monsters=False,
    )

    L0.add_monster_file(MonsterTemplate("The Crone", ('@', PURPLE)))

    L0.passage_locations[GAME.PASSAGE_UP] = (23, 15)
    L0.passage_locations[GAME.PASSAGE_DOWN] = (19, 81)
    L0.tilemap_template = list(
        "################################################################################################"
        "#######################..##################.#.#.#######.....####################################"
        "######...##############.#.################.#.#.#.#####.####.###......###########################"
        "######.##..############.##..#############.######.#..###.###.###.####.###########################"
        "#######.###...##.######.####.######.....##.#####.#.#.##.###.....###..###.#######################"
        "########.######...#####.#####.#####.###.###.####...##.##.##########.###.#.######################"
        "###.#####.####..#######.######.####...#.###.##########.#.##########.##.##.######################"
        "###.######.###.########.######.######.#.###.########...#.##########....##.######################"
        "###.#######.##.########.######.######.#.###.########.###.################.######################"
        "###..........##.#######.######.#####.##.....########.###.################.######################"
        "###.#######..###.######.##...#.####.################.....########.........######################"
        "###.######...####.#####.##.#...###.##############################.##############################"
        "###.#.###...######.####.##.######.###############################.###...########################"
        "####.#.##..########.###.###.####.################################.##.##........#################"
        "###.#.##.###########.##.####.##.#################################...##########.#################"
        "####.####.###########.#.#####..###############################################.#################"
        "##########.#########.##.######################################################...###############"
        "###########.#######.###.########################################################.###############"
        "############.#####.####........................................................##.##############"
        "#############.###.####.########################################################..>##############"
        "##############.#.##...##########################################################################"
        "###############.###.#.##########################################################################"
        "###############.###...##############################.....................#######################"
        "###############<...###...................................................#######################"
        "#######################################..................................#######################"
        "################################################################################################"
    )
    L0._add_walls()

    world = WorldTemplate()
    world.add_dungeon(GAME.DUNGEON)
    world.add_level(GAME.DUNGEON, L0)
    for x in range(GAME.LEVELS_PER_DUNGEON - 1):
        world.add_level(GAME.DUNGEON)

    return world

#first = [
    #"ggggggggggggggggggggggggggggg",
    #"ggggggggggggggggggg#########w",
    #"ggggggggggggggggggg#====#...w",
    #"ggggggggggggggggggg#..../...w",
    #"ggg##ooo############....#####",
    #"ggg#.cc.===#==cc=../.==./.==#",
    #"ggg#S....../.......####/#...#",
    #"ggg#O--...p#--.cc..<###.#...#",
    #"ggg#F--.--p###/##=.####.#.|.#",
    #"ggg#A..###.#s..T#=.>#####|C|#",
    #"ggg#.c.#.#.#=.tU#=.######|A|#",
    #"ggg#cTc###.####B##.######|R|#",
    #"ggg#cAc==TV..###==.#====#|^|#",
    #"ggg#cBc....../...../....#...#",
    #"gggocLc......#=...#=....#...#",
    #"gggocEc..cc.-#=..=#=.---#...#",
    #"ggg#.c.==...-#=..=#=.BED#+++#",
    #"ggg###########=..=#=.---#gggg",
    #"ggggggggggggg#=--=#=....#gggg",
    #"gggggggggggggo=--=#=.---ogggg",
    #"ggggggggggggg#ooo####ooo#gggg",
    #"ggggggggggggggggggggggggggggg",
#]
