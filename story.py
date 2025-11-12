import structs
import parser

_story_beats = parser.read_csv("data/StoryBeats.csv", structs.World)


def create_world() -> structs.World:
    return _story_beats[0]


def progress_story(turn: int, world: structs.World, player: structs.Player) -> structs.World:
    for i in range(len(_story_beats) - 1):
        if _story_beats[i].BeatNum == world.BeatNum:
            if turn >= _story_beats[i + 1].BeatStartStep and player.level >= int(_story_beats[i + 1].BeatLevelReq):
                return _story_beats[i + 1]  # progress stages
    return world  # stay on current stage
