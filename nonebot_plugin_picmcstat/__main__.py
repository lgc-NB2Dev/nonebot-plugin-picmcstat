from typing import Awaitable, Callable, NoReturn

from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import RawCommand

from .config import ShortcutType, config
from .draw import ServerType, draw

BE_SVR_PREFIX = ["pe", "be"]


motd_handler = on_command("motd", aliases={"!motd", "！motd"})


@motd_handler.handle()
async def _(matcher: Matcher, event: MessageEvent, cmd: str = RawCommand()):
    arg = event.get_plaintext().lstrip().replace(cmd, "", 1)

    svr_type: ServerType = "je"
    if p := next((p for p in BE_SVR_PREFIX if arg.startswith(p)), None):
        arg = arg.replace(p, "", 1)
        svr_type = "be"

    arg = arg.strip()
    await matcher.finish(await draw(arg, svr_type))


def get_shortcut_handler(
    host: str,
    svr_type: ServerType,
) -> Callable[..., Awaitable[NoReturn]]:
    async def shortcut_handler(matcher: Matcher):
        await matcher.finish(await draw(host, svr_type))

    return shortcut_handler


def append_shortcut_handler(shortcut: ShortcutType):
    async def rule(event: MessageEvent):
        if (wl := shortcut.whitelist) and isinstance(event, GroupMessageEvent):
            return event.group_id in wl
        return True

    on_regex(shortcut.regex, rule=rule).append_handler(
        get_shortcut_handler(shortcut.host, shortcut.type),
    )


def startup():
    if s := config.mcstat_shortcuts:
        for v in s:
            append_shortcut_handler(v)


startup()
