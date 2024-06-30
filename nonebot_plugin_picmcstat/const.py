import re
from typing import Literal

from mcstatus.motd.components import Formatting, MinecraftColor

ServerType = Literal["je", "be"]

CODE_COLOR = {
    "0": "#000000",
    "1": "#0000AA",
    "2": "#00AA00",
    "3": "#00AAAA",
    "4": "#AA0000",
    "5": "#AA00AA",
    "6": "#FFAA00",
    "7": "#AAAAAA",
    "8": "#555555",
    "9": "#5555FF",
    "a": "#55FF55",
    "b": "#55FFFF",
    "c": "#FF5555",
    "d": "#FF55FF",
    "e": "#FFFF55",
    "f": "#FFFFFF",
    "g": "#DDD605",
}
STROKE_COLOR = {
    "0": "#000000",
    "1": "#00002A",
    "2": "#002A00",
    "3": "#002A2A",
    "4": "#2A0000",
    "5": "#2A002A",
    "6": "#2A2A00",
    "7": "#2A2A2A",
    "8": "#151515",
    "9": "#15153F",
    "a": "#153F15",
    "b": "#153F3F",
    "c": "#3F1515",
    "d": "#3F153F",
    "e": "#3F3F15",
    "f": "#3F3F3F",
    "g": "#373501",
}
CODE_COLOR_BEDROCK = {**CODE_COLOR, "g": "#FFAA00"}
STROKE_COLOR_BEDROCK = {**STROKE_COLOR, "g": "#2A2A00"}
STYLE_BBCODE = {
    "l": ["[b]", "[/b]"],
    "m": ["[del]", "[/del]"],
    "n": ["[u]", "[/u]"],
    "o": ["[i]", "[/i]"],
    "k": ["[obfuscated]", "[/obfuscated]"],  # placeholder
}
OBFUSCATED_PLACEHOLDER_REGEX = re.compile(
    r"\[obfuscated\](?P<inner>.*?)\[/obfuscated\]",
)

ENUM_CODE_COLOR = {MinecraftColor(k): v for k, v in CODE_COLOR.items()}
ENUM_STROKE_COLOR = {MinecraftColor(k): v for k, v in STROKE_COLOR.items()}
ENUM_CODE_COLOR_BEDROCK = {MinecraftColor(k): v for k, v in CODE_COLOR_BEDROCK.items()}
ENUM_STROKE_COLOR_BEDROCK = {
    MinecraftColor(k): v for k, v in STROKE_COLOR_BEDROCK.items()
}
ENUM_STYLE_BBCODE = {Formatting(k): v for k, v in STYLE_BBCODE.items()}

GAME_MODE_MAP = {"Survival": "生存", "Creative": "创造", "Adventure": "冒险"}
FORMAT_CODE_REGEX = r"§[0-9abcdefgklmnor]"
