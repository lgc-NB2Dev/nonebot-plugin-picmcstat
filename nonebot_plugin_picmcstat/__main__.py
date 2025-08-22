from typing import NoReturn

from nonebot import logger, on_command, on_regex
from nonebot.adapters import Event as BaseEvent, Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot_plugin_alconna.uniseg import UniMessage

from .config import ShortcutType, config
from .draw import ServerType, draw
from mcstatus import BedrockServer, JavaServer
from .util import resolve_ip

try:
    from nonebot.adapters.onebot.v11 import GroupMessageEvent as OB11GroupMessageEvent
except ImportError:
    OB11GroupMessageEvent = None


async def finish_with_query(ip: str, svr_type: ServerType) -> NoReturn:
    try:
        ret = await draw(ip, svr_type)
    except Exception:
        msg = UniMessage("出现未知错误，请检查后台输出")
    else:
        msg = UniMessage.image(raw=ret)
    await msg.send(reply_to=config.mcstat_reply_target)
    raise FinishedException


motd_matcher = on_command(
    "motd",
    aliases={"!motd", "！motd"},
    priority=97,
)
motdpe_matcher = on_command(
    "motdpe",
    aliases={"motdbe", "!motdpe", "！motdpe", "!motdbe", "！motdbe"},
    priority=98,
    state={"svr_type": "be"},
)
motdje_matcher = on_command(
    "motdje",
    aliases={"!motdje", "！motdje"},
    priority=99,
    state={"svr_type": "je"},
)


@motdje_matcher.handle()
@motdpe_matcher.handle()
async def _(state: T_State, arg_msg: Message = CommandArg()):
    arg = arg_msg.extract_plain_text().strip()
    svr_type: ServerType = state["svr_type"]
    await finish_with_query(arg, svr_type)


@motd_matcher.handle()
async def _(arg_msg: Message = CommandArg()):
    arg = arg_msg.extract_plain_text().strip()
    if not arg:
        await finish_with_query("", "je")

    try:
        host, port = await resolve_ip(arg, srv=True)
        svr = JavaServer(host, port)
        await svr.async_status()
        await finish_with_query(arg, "je")
    except FinishedException:
        raise
    except Exception:
        try:
            host, port = await resolve_ip(arg)
            svr = BedrockServer(host, port)
            await svr.async_status()
            await finish_with_query(arg, "be")
        except FinishedException:
            raise
        except Exception:
            await UniMessage("查询失败，无法连接服务器，请尝试使用其他命令获取详细信息").send(
                reply_to=config.mcstat_reply_target
            )
            await finish_with_query("", "je") //返回help_msg图片
            raise FinishedException


def append_shortcut_handler(shortcut: ShortcutType):
    async def rule(event: BaseEvent):  # type: ignore[override]
        if not OB11GroupMessageEvent:
            logger.warning("快捷指令群号白名单仅可在 OneBot V11 适配器下使用")
        elif (wl := shortcut.whitelist) and isinstance(event, OB11GroupMessageEvent):
            return event.group_id in wl
        return True

    async def handler():
        await finish_with_query(shortcut.host, shortcut.type)

    on_regex(shortcut.regex, rule=rule, priority=99).append_handler(handler)


def startup():
    if s := config.mcstat_shortcuts:
        for v in s:
            append_shortcut_handler(v)


startup()
