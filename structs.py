import parser


class World(parser.CSVRow):
    BeatNum: int = 0
    Stage: str = ""
    BeatName: str = ""
    BeatStartStep: int = 0
    ZoneLevel: int = 0
    BeatDC: int = 0
    ZoneTier: int = 1


class NonCombat(parser.CSVRow):
    Category: str = ""
    T1: float = 0.0
    T2: float = 0.0
    T3: float = 0.0
    T4: float = 0.0
    T1Threshold: float = 0.0
    T2Threshold: float = 0.0
    T3Threshold: float = 0.0
    T4Threshold: float = 0.0
    BaseXPMult: float = 1.0
    GoldMult: float = 1.0
    RepDeltaOnSuccess: float = 0.0
    RepDeltaOnFail: float = 0.0
    TimeMult: float = 1.0
    FailRisk: float = 0.0


class Stats(parser.CSVRow):
    StatKey: str = ""
    Base: int = 0
    PerLevel: float = 0


class Loot(parser.CSVRow):
    ItemID: int
    Slot: str
    Quality: str
    BaseItemPower: int
    SellValue: int


class Equipment:
    weapon: int = 0
    helm: int = 0
    chest: int = 0
    legs: int = 0
    accessory: int = 0

    def get_score(self) -> int:
        return self.weapon + self.helm + self.chest + self.legs + self.accessory

    def equip_best(self, loot: list[Loot]):
        for l in loot:
            match l.Slot:
                case "Weapon":
                    self.weapon = max(self.weapon, l.BaseItemPower)
                case "Helm":
                    self.helm = max(self.helm, l.BaseItemPower)
                case "Chest":
                    self.chest = max(self.chest, l.BaseItemPower)
                case "Boots":
                    self.legs = max(self.legs, l.BaseItemPower)
                case _:
                    self.accessory = max(self.accessory, l.BaseItemPower)


class Progression(parser.CSVRow):
    Level: int
    XP_to_Next: int
    Gold_Combat: int
    Gold_NonCombat: int


class Player:
    _exp: int = 0
    level: int = 1

    _loot: list[Loot] = []
    equipment = Equipment()

    gold: int = 0

    _progression: list[Progression]
    _stats: list[Stats]

    def __init__(self):
        self._progression = parser.read_csv("data/Progression.csv", Progression)
        self._stats = parser.read_csv("data/Stats.csv", Stats)

    def award_exp(self, amount: int):
        self._exp += amount

        for p in self._progression:
            if p.Level == self.level:
                if self._exp >= p.XP_to_Next and self.gold >= (self.level * 250): #Leveling up now costs gold based on current level
                    self.level += 1
                    self._exp -= p.XP_to_Next
                    self.gold -= self.level * 250
                    Statistics.Gold_Spent += self.level * 250

    def award_gold(self, amount: int):
        self.gold += amount

    def award_loot(self, loot: Loot):
        self._loot.append(loot)
        self.equipment.equip_best(self._loot)

    def culumative_exp(self) -> int:
        total = self._exp

        for p in self._progression:
            if p.Level < self.level:
                total += p.XP_to_Next

        return total

    def get_stat(self, stat_key: str) -> Stats:
        for stat in self._stats:
            if stat.StatKey == stat_key:
                return stat
        return self._stats[0]


class NCCategory(parser.CSVRow):
    OutcomeCategory: str
    StatKey: str
    CategoryDC: int


class Statistics:
    Success: bool = False
    Death: bool = False
    XP_Earned: int = 0
    Gold_Earned: int = 0
    DropID: int = 0
    Gold_Spent: int = 0

    Power_Ratio: float = 0
    SuccessChanceCombat: float = 0
    DeathChance: float = 0
    StatScore: float = 0
    SuccessChance_NonCombat: float = 0
    OutcomeCategory: str = ""
    SkillDifficulty: int = 0
    CatStatKey: str = ""
    CategoryDC: int = 0
    BaseStat: int = 0
    PerLevel: float = 0
