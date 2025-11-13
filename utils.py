import parser
import structs
import random
import math
import params
import inputs

_nc_categories = parser.read_csv("data/NC_Categories.csv", structs.NCCategory)
# _nc_rules ?
_non_combat = parser.read_csv("data/NonCombat.csv", structs.NonCombat)


def chance(percent: float) -> bool:
    return random.random() <= clamp(percent, floor=0, ceil=1)


def logistic(x: float, *, L: float = 1.0, k: float = 1.0, x0: float = 0.0) -> float:
    return L / (1 + math.exp(-k * (x - x0)))


def skill_check(
    ratio: float,
    DC: float,
    steepness: float = 1.0,
) -> tuple[bool, float]:
    """
    Determine success probability based on ratio vs. DC using a logistic curve. When ratio == DC, then there is a 50% chance of success.

    Parameters:
        ratio     : player's effective power ratio or stat score
        DC        : difficulty (d20 roll)
        steepness : how quickly probability ramps up around equality

    Returns:
        (success, chance)
    """

    x = ratio - DC
    chance = logistic(x, L=1.0, k=steepness, x0=0.0)
    success = random.random() < chance
    return success, chance


def clamp(x: float, *, floor: float, ceil: float):
    return max(floor, min(ceil, x))

# levels provide a little bonus, but gear is the main driver of power
def power_ratio(player: structs.Player, world: structs.World) -> float:
    gear = max(0.0, player.equipment.get_score())
    recommended = max(
        1.0,
        inputs.BASE_RECOMMENDED_GEAR
        * (inputs.GEAR_GROWTH_PER_ZONE ** (world.ZoneLevel / inputs.ZONE_SCALE)),
    )

    # modest multiplicative benefit from level (keeps level relevant without overpowering gear)
    level_mult = 1.0 + (player.level * 0.035)

    effective_power = gear * level_mult

    # apply light diminishing returns so very large gear scores don't explode the ratio
    effective_power = effective_power ** 0.95

    ratio = effective_power / recommended

    # keep ratio within reasonable bounds
    return clamp(ratio, floor=0.01, ceil=10.0)


def stat_score(player: structs.Player, stat_key: str) -> float:
    stat = player.get_stat(stat_key)

    return (
        stat.Base
        + (player.level * stat.PerLevel)
        + (player.equipment.get_score() / max(1, inputs.GEAR_STAT_SCALING))
    )


def combat_chance(player: structs.Player, world: structs.World) -> float:
    # minimal per-encounter skill noise to reduce variation
    skill_noise = random.gauss(0, 1) * 0.12
    skill_difficulty = inputs.SKILL_DIFF_TIER_MULT + world.ZoneTier * skill_noise

    # base power ratio from gear; keep growth slightly superlinear so progression feels stronger
    base_power = max(0.01, power_ratio(player, world))
    scaled_power = (base_power ** 1.12) * (1.0 + player.level * 0.01)

    # map difficulty into comparable range
    difficulty_scale = (skill_difficulty / max(1.0, 10 * inputs.SKILL_DIFF_ST_DEV))

    advantage = scaled_power - difficulty_scale

    # if player skill (scaled_power) is above zone difficulty, give a significant advantage
    if advantage > 0:
        # boost scales with how far above difficulty the player is and grows more strongly with level
        level_boost = 1.0 + min(4.0, player.level * 0.05)
        advantage += advantage * (1.4 * level_boost)

    # increase logistic steepness with player level to reduce outcome variance as player progresses
    steepness = 2.0 + min(4.0, player.level * 0.06)
    success_chance = logistic(advantage, L=1.0, k=steepness, x0=0.0)

    # if player skill is close to zone difficulty, give an extra proximity bonus to increase odds
    # (applies regardless of slight positive/negative advantage)
    proximity_sigma = 0.5  # width of the "close" window in advantage units
    proximity_amplitude = 0.15 + min(0.35, player.level * 0.02)  # grows modestly with level
    proximity_boost = proximity_amplitude * math.exp(- (advantage ** 2) / (2 * proximity_sigma ** 2))
    success_chance += proximity_boost

    # very small jitter so outcomes are not perfectly deterministic
    jitter = random.gauss(0, 0.005)
    success_chance = clamp(
        success_chance + jitter,
        floor=params.FLOOR_SUCCESS,
        ceil=params.CEIL_SUCCESS,
    )

    return success_chance


def non_combat_chance(
    player: structs.Player, world: structs.World, category_key: str
) -> float:
    category = _nc_categories[0]
    for cat in _nc_categories:
        if cat.OutcomeCategory == category_key:
            category = cat

    tn = category.CategoryDC + world.BeatDC
    uni = clamp(
        (21 - (tn - stat_score(player, category.StatKey))) / 20,
        floor=0,
        ceil=1,
    )
    success_chance = clamp(
        1 / (1 + math.exp(-params.ATTEMPT_SLOPE * (tn - uni))),
        floor=params.FLOOR_SUCCESS,
        ceil=params.CEIL_SUCCESS,
    )

    return success_chance


def death_chance(player: structs.Player, world: structs.World) -> float:
    return (1 - combat_chance(player, world)) * inputs.DEATH_SEVERITY


def non_combat_category(world: structs.World) -> structs.NCCategory:
    rand = random.random()

    scenario = _non_combat[0]
    for s in _non_combat:
        thresh = 0
        if world.ZoneTier == 1:
            thresh = s.T1Threshold
        elif world.ZoneTier == 2:
            thresh = s.T2Threshold
        elif world.ZoneTier == 3:
            thresh = s.T3Threshold
        elif world.ZoneTier == 4:
            thresh = s.T4Threshold
        if rand <= thresh:
            scenario = s
            break

    category = _nc_categories[0]
    for cat in _nc_categories:
        if cat.OutcomeCategory == scenario.Category:
            category = cat

    return category


def skill_difficulty(player: structs.Player, world: structs.World) -> float:
    skill_noise = math.sqrt(-2 * math.log(random.random())) * math.cos(
        2 * math.pi * random.random()
    )
    skill_difficulty = inputs.SKILL_DIFF_TIER_MULT + world.ZoneTier * skill_noise
    return skill_difficulty
