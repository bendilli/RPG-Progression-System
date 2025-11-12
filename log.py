import structs
import datetime
import utils

output_file = "data/output.csv"
debug_file = "data/debug.csv"


def record_turn(
    turn: int,
    player: structs.Player,
    world: structs.World,
    stats: structs.Statistics,
):
    # TODO make some of these columns debug, this is an excessive amount of information

    # write csv headers
    if turn == 0:
        with open(output_file, mode="w") as file:
            file.write(
                "Step,PlayerLevel,ActiveBeat#,ActiveBeatName,ZoneLevel,PowerRatio,BeatType,RandCat,OutcomeCategory,SkillDifficulty,Success?,RepDelta,XP_Earned,Gold_Earned,DropID,SuccessChanceCombat,DeathChance,Death?,RepairCost,Respec?,RespecCost,VendorTaxPct,Gold_Spent,NetGoldChange,CumulativeGold,CumulativeXP,CumulativeRep,Eq_Weapon,Eq_Chest,Eq_Helm,Eq_Legs,Eq_Accessory,GearScore,CatStatKey,CategoryDC,BeatDC_lookup,BaseStat,PerLevel,StatScore,SuccessChance_NonCombat\n"
            )

        with open(debug_file, mode="w") as file:
            file.write(
                "Timestamp,Step,PlayerLevel,ActiveBeat#,ActiveBeatName,ZoneLevel,PowerRatio,GearScore,LootRoll,Outcome,AssertFail,FailNote,SC_Combat,SC_UNI,SC_NonCombat\n"
            )

    # write data
    with open(output_file, mode="a") as file:
        file.write(
            f"{turn + 1},{player.level},{world.BeatNum},{world.BeatName},{world.ZoneLevel},{utils.power_ratio(player, world):.3f},BeatType,RandCat,{stats.OutcomeCategory},{stats.SkillDifficulty},{stats.Success},RepDelta,{stats.XP_Earned},{stats.Gold_Earned},{stats.DropID},{stats.SuccessChanceCombat:.2f},{stats.DeathChance:.2f},{stats.Death},RepairCost,Respec?,RespecCost,VendorTaxPct,{stats.Gold_Spent},{stats.Gold_Earned - stats.Gold_Spent},{player.gold},{player.culumative_exp()},CumulativeRep,{player.equipment.weapon},{player.equipment.chest},{player.equipment.helm},{player.equipment.legs},{player.equipment.accessory},{player.equipment.get_score()},{stats.CatStatKey},{stats.CategoryDC},{world.BeatDC},{stats.BaseStat},{stats.PerLevel},{stats.StatScore:.3f},{stats.SuccessChance_NonCombat:.2f}\n"
        )

    with open(debug_file, mode="a") as file:
        file.write(
            f"{datetime.datetime.now().isoformat()},{turn},{player.level},{world.BeatNum},{world.BeatName},{world.ZoneLevel},{utils.power_ratio(player, world):.3f},{player.equipment.get_score()},LootRoll,Outcome,AssertFail,FailNote,{stats.SuccessChanceCombat:.2f},\n"
        )
