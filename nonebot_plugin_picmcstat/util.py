import random
from string import ascii_letters, digits, punctuation
from typing import List, Union

from .const import CODE_COLOR, STROKE_COLOR, STYLE_BBCODE

RANDOM_CHAR_TEMPLATE = ascii_letters + digits + punctuation


def get_latency_color(delay: Union[int, float]) -> str:
    if delay <= 50:
        return "a"
    if delay <= 100:
        return "e"
    if delay <= 200:
        return "6"
    return "c"


def random_char(length: int) -> str:
    return "".join(random.choices(RANDOM_CHAR_TEMPLATE, k=length))


def format_code_to_bbcode(text: str) -> str:
    if not text:
        return text

    parts = text.split("§")
    parsed: List[str] = [parts[0]]
    color_tails: List[str] = []
    format_tails: List[str] = []

    for p in parts[1:]:
        char = p[0]
        txt = p[1:]

        if char in CODE_COLOR:
            parsed.extend(color_tails)
            color_tails.clear()
            parsed.append(f"[stroke={STROKE_COLOR[char]}][color={CODE_COLOR[char]}]")
            color_tails.append("[/color][/stroke]")

        elif char in STYLE_BBCODE:
            head, tail = STYLE_BBCODE[char]
            format_tails.append(tail)
            parsed.append(head)

        elif char == "r":  # reset
            parsed.extend(color_tails)
            parsed.extend(format_tails)

        elif char == "k":  # random
            txt = random_char(len(txt))

        else:
            txt = f"§{char}{txt}"

        parsed.append(txt)

    parsed.extend(color_tails)
    parsed.extend(format_tails)
    return "\n".join([x.strip() for x in "".join(parsed).splitlines()])


def format_list(sample: List[str], items_per_line=2, line_start_spaces=10, list_gap=2):
    if not sample:
        return ""

    max_width = max([len(x) for x in sample]) + list_gap

    line_added = 0
    tmp = []
    for name in sample:
        if line_added < items_per_line:
            name = name.ljust(max_width)

        tmp.append(name)
        line_added += 1

        if line_added >= items_per_line:
            tmp.append("\n")
            tmp.append(" " * line_start_spaces)
            line_added = 0

    return "".join(tmp)
