from typing import Awaitable, Callable, NoReturn

from nonebot import logger, on_command, on_regex
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot_plugin_saa import Image, MessageFactory

from .config import ShortcutType, config
from .draw import ServerType, draw

motdpe_matcher = on_command(
    "motdpe",
    aliases={"motdbe", "!motdpe", "！motdpe", "!motdbe", "！motdbe"},
    state={"svr_type": "be"},
)
motd_matcher = on_command(
    "motd",
    aliases={"!motd", "！motd"},
    priority=2,
    state={"svr_type": "je"},
)


@motd_matcher.handle()
@motdpe_matcher.handle()
async def _(state: T_State, arg_msg: Message = CommandArg()):
    arg = arg_msg.extract_plain_text().strip()
    svr_type: ServerType = state["svr_type"]

    pic = await draw(arg, svr_type)
    await MessageFactory(Image(pic)).send(reply=config.mcstat_reply_target)


try:
    from nonebot.adapters.onebot.v11 import (
        GroupMessageEvent,
        MessageEvent,
        MessageSegment,
    )

    def get_shortcut_handler(
        host: str,
        svr_type: ServerType,
    ) -> Callable[..., Awaitable[NoReturn]]:
        async def shortcut_handler(matcher: Matcher):
            img = await draw(host, svr_type)
            await matcher.finish(MessageSegment.image(img))

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

except ImportError:
    logger.warning("无法导入 OneBot V11 适配器，已跳过注册快捷指令")
