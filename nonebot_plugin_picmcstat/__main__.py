from typing import Any, Awaitable, Callable, NoReturn

from nonebot import on_command, on_regex, require
from nonebot.internal.adapter import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .config import config

require("nonebot_plugin_imageutils")

from .draw import ServerType, draw

motd_handler = on_command("motd", aliases={"!motd", "！motd"})


@motd_handler.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    arg = arg.extract_plain_text()

    svr_type: ServerType = "je"
    be_svr_prefix = ["pe", "be"]
    for p in be_svr_prefix:
        if arg.startswith(p):
            arg = arg.replace(p, "", 1)
            svr_type = "be"
            break

    arg = arg.strip()
    await matcher.finish(await draw(arg, svr_type))


def get_shortcut_handler(
    host: str, svr_type: ServerType
) -> Callable[[Any], Awaitable[NoReturn]]:
    async def shortcut_handler(matcher: Matcher):
        await matcher.finish(await draw(host, svr_type))

    return shortcut_handler


def startup():
    if s := config.mcstat_shortcuts:
        for shortcut in s:
            on_regex(shortcut["regex"]).append_handler(
                get_shortcut_handler(shortcut["host"], shortcut["type"])
            )


startup()
