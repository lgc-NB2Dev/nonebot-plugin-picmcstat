import socket
from asyncio.exceptions import TimeoutError
from io import BytesIO
from typing import Literal, Union

from mcstatus import BedrockServer, JavaServer
from mcstatus.bedrock_status import BedrockStatusResponse
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_imageutils import BuildImage, Text2Image

from .const import CODE_COLOR, GAME_MODE_MAP, STROKE_COLOR
from .res import DEFAULT_ICON_RES, DIRT_RES, GRASS_RES
from .util import format_code_to_bbcode, get_latency_color

MARGIN = 32
DEFAULT_WIDTH = 640
FONT_NAME = "unifont"
TITLE_FONT_SIZE = 8 * 5
EXTRA_FONT_SIZE = 8 * 4
EXTRA_STROKE_WIDTH = 2
STROKE_RATIO = 0.0625
EXTRA_SPACING = 12

JE_HEADER = "[MCJE服务器信息]"
BE_HEADER = "[MCBE服务器信息]"


def draw_bg(width: int, height: int) -> BuildImage:
    size = DIRT_RES.width
    bg = BuildImage.new("RGBA", (width, height))

    for hi in range(0, height, size):
        for wi in range(0, width, size):
            bg.paste(DIRT_RES if hi else GRASS_RES, (wi, hi))

    return bg


def build_img(
    icon: BuildImage,
    header1: str,
    header2: str,
    extra: Text2Image = None,
) -> BytesIO:
    HEADER_TEXT_COLOR = CODE_COLOR["f"]
    HEADER_STROKE_COLOR = STROKE_COLOR["f"]

    HEADER_HEIGHT = 128
    HALF_HEADER_HEIGHT = int(HEADER_HEIGHT / 2)

    BG_WIDTH = extra.width + MARGIN * 2 if extra else DEFAULT_WIDTH
    BG_HEIGHT = HEADER_HEIGHT + MARGIN * 2
    if extra:
        BG_HEIGHT += extra.height + int(MARGIN / 2)
    bg = draw_bg(BG_WIDTH, BG_HEIGHT)

    if icon.size != (HEADER_HEIGHT, HEADER_HEIGHT):
        icon = icon.resize_height(HEADER_HEIGHT, inside=False)
    bg.paste(icon, (MARGIN, MARGIN), alpha=True)

    bg.draw_text(
        (
            HEADER_HEIGHT + MARGIN + MARGIN / 2,
            MARGIN,
            BG_WIDTH - MARGIN,
            HALF_HEADER_HEIGHT + MARGIN,
        ),
        header1,
        halign="left",
        fill=HEADER_TEXT_COLOR,
        max_fontsize=TITLE_FONT_SIZE,
        fontname=FONT_NAME,
        stroke_ratio=STROKE_RATIO,
        stroke_fill=HEADER_STROKE_COLOR,
    )
    bg.draw_text(
        (
            HEADER_HEIGHT + MARGIN + MARGIN / 2,
            HALF_HEADER_HEIGHT + MARGIN,
            BG_WIDTH - MARGIN,
            HEADER_HEIGHT + MARGIN,
        ),
        header2,
        halign="left",
        fill=HEADER_TEXT_COLOR,
        max_fontsize=TITLE_FONT_SIZE,
        fontname=FONT_NAME,
        stroke_ratio=STROKE_RATIO,
        stroke_fill=HEADER_STROKE_COLOR,
    )

    if extra:
        extra.draw_on_image(
            bg.image,
            (MARGIN, int(HEADER_HEIGHT + MARGIN + MARGIN / 2)),
        )

    # bg.image.show()
    with open("test.png", "wb") as f:
        bg.image.save(f)
    return bg.convert("RGB").save("PNG")


def draw_java(res) -> BytesIO:
    pass


def draw_bedrock(res: BedrockStatusResponse) -> BytesIO:
    map_name = f"§7存档名称：§f{res.map}§r\n" if res.map else ""
    game_mode = (
        f"§7游戏模式：§f{GAME_MODE_MAP.get(res.gamemode, res.gamemode)}\n"
        if res.gamemode
        else ""
    )
    online_percent = round(int(res.players_online) / int(res.players_max) * 100, 2)

    extra_txt = (
        f"{res.motd}§r\n"
        f"§7协议版本：§f{res.version.protocol}\n"
        f"§7游戏版本：§f{res.version.version}\n"
        f"§7在线人数：§f{res.players_online}/{res.players_max} ({online_percent}%)\n"
        f"{map_name}"
        f"{game_mode}"
        f"§7测试延迟：§{get_latency_color(res.latency)}{res.latency:.2f}ms"
    )

    extra = Text2Image.from_bbcode_text(
        format_code_to_bbcode(extra_txt),
        EXTRA_FONT_SIZE,
        fill=CODE_COLOR["f"],
        fontname=FONT_NAME,
        stroke_ratio=STROKE_RATIO,
        stroke_fill=STROKE_COLOR["f"],
        spacing=EXTRA_SPACING,
    )
    return build_img(DEFAULT_ICON_RES, BE_HEADER, "请求成功", extra)


def draw_error(e: Exception, svr_type: str) -> BytesIO:
    extra = ""
    if isinstance(e, TimeoutError):
        reason = "请求超时"
    elif isinstance(e, socket.gaierror):
        reason = "域名解析失败"
        extra = str(e)
    else:
        reason = "出错了！"
        extra = repr(e)

    if extra:
        extra = Text2Image.from_text(
            extra,
            EXTRA_FONT_SIZE,
            fill=CODE_COLOR["f"],
            fontname=FONT_NAME,
            stroke_width=EXTRA_STROKE_WIDTH,
            stroke_fill=STROKE_COLOR["f"],
        ).wrap(DEFAULT_WIDTH - MARGIN * 2)

    return build_img(
        DEFAULT_ICON_RES, JE_HEADER if svr_type == "je" else BE_HEADER, reason, extra
    )


async def draw(ip: str, svr_type: Literal["je", "be"]) -> Union[MessageSegment, str]:
    if svr_type not in ("je", "be"):
        raise ValueError("Server type must be `je` or `be`")

    try:
        if svr_type == "je":
            return MessageSegment.image(
                draw_java(await (await JavaServer.async_lookup(ip)).async_query())
            )
        else:  # be
            return MessageSegment.image(
                draw_bedrock(await BedrockServer.lookup(ip).async_status())
            )
    except Exception as e:
        logger.exception("获取服务器状态/画服务器状态图出错")
        try:
            return MessageSegment.image(draw_error(e, svr_type))
        except:
            logger.exception("画异常状态图失败")
            return "出现未知错误，请检查后台输出"
