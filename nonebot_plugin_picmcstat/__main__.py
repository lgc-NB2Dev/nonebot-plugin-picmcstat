from nonebot import on_command, require
from nonebot.internal.adapter import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

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
