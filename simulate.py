import structs
import story
import loot
import log
import utils
import inputs
import math


def combat(
    player: structs.Player,
    world: structs.World,
    stats: structs.Statistics,
):
    chance = utils.combat_chance(player, world)
    success = utils.chance(chance)
    stats.SuccessChanceCombat = chance
    stats.Success = success

    if success:
        chance = utils.death_chance(player, world)
        death = utils.chance(chance)
        stats.DeathChance = chance
        stats.Death = death

        if not death:
            exp = math.floor(
                utils.skill_difficulty(player, world) * inputs.BASE_XP_COMBAT
            )
            player.award_exp(exp)
            stats.XP_Earned = exp

            gold = inputs.GOLD_PER_COMBAT_STEP
            player.award_gold(gold * player.level) #Gold scales with level. Gold = 25 * level.
            stats.Gold_Earned = gold * player.level

            drop = loot.get_drop(world)
            if drop is not None:
                player.award_loot(drop)
                stats.DropID = drop.ItemID


def non_combat(
    player: structs.Player,
    world: structs.World,
    stats: structs.Statistics,
):
    category = utils.non_combat_category(world)
    stats.OutcomeCategory = category.OutcomeCategory
    stats.SkillDifficulty = category.CategoryDC

    stat = player.get_stat(category.StatKey)
    stats.BaseStat = stat.Base
    stats.PerLevel = stat.PerLevel

    chance = utils.non_combat_chance(player, world, category.OutcomeCategory)
    success = utils.chance(chance)
    stats.StatScore = utils.stat_score(player, category.StatKey)
    stats.SuccessChance_NonCombat = chance
    stats.Success = success

    exp = math.floor(utils.skill_difficulty(player, world) * inputs.BASE_XP_NON_COMBAT)
    player.award_exp(exp)
    stats.XP_Earned = exp

    if success:
        # maybe use nc_rules.csv
        gold = inputs.GOLD_PER_NON_COMBAT_STEP
        player.award_gold(int(gold * (player.level * 1.5))) #Gold scales with level. Gold = 10 * (level * 1.5).
        stats.Gold_Earned = int(gold * (player.level * 1.5))


def simulate(turns: int):
    player = structs.Player()
    world = story.create_world()

    for turn in range(turns):
        stats = structs.Statistics()

        # decide action
        if utils.chance(inputs.COMBAT_CHANCE):
            combat(player, world, stats)
        else:
            non_combat(player, world, stats)

        # change stage
        world = story.progress_story(turn, world)

        # record results
        log.record_turn(turn, player, world, stats)
