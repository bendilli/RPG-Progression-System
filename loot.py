import structs
import parser
import utils
import random

_loot_table = parser.read_csv("data/LootTable.csv", structs.Loot)

# Updated weights so that higher tier zones have better drop quality
QualityWeights = {
    "T1": {
        "Common": 0.7,
        "Rare": 0.22,
        "Epic": 0.07,
        "Legendary": 0.01,
    },
    "T2": {
        "Common": 0.5,
        "Rare": 0.35,
        "Epic": 0.1,
        "Legendary": 0.05,
    },
    "T3": {
        "Common": 0.2,
        "Rare": 0.4,
        "Epic": 0.3,
        "Legendary": 0.2,
    },
    "T4": {
        "Common": 0.03,
        "Rare": 0.07,
        "Epic": 0.4,
        "Legendary": 0.5,
    },
}

# Equal chance for all gear types
PieceWeights = {
    "Weapon": 0.2,
    "Chest": 0.2,
    "Helm": 0.2,
    "Legs": 0.2,
    "Accessory": 0.2,
}


def weighted_choice(weight_dict: dict[str, float]) -> str:
    r = random.random() * sum(weight_dict.values())

    for key, weight in weight_dict.items():
        r -= weight
        if r <= 0:
            return key

    return list(weight_dict.keys())[-1]  # Fallback


def get_drop(world: structs.World) -> structs.Loot | None:
    if utils.chance(.50):
        return None  # no drop

    slot = weighted_choice(PieceWeights)
    quality = weighted_choice(QualityWeights[f"T{world.ZoneTier}"])

    possible_drops = [x for x in _loot_table if x.Slot == slot and x.Quality == quality]
    if not possible_drops:
        return None

    return random.choice(possible_drops)
