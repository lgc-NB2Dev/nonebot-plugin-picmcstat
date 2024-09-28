import base64
import socket
from asyncio.exceptions import TimeoutError
from functools import partial
from io import BytesIO
from typing import Any, List, Optional, Sequence, Tuple, Union, cast
from typing_extensions import TypeAlias

from mcstatus import BedrockServer, JavaServer
from mcstatus.bedrock_status import BedrockStatusResponse
from mcstatus.motd import Motd
from mcstatus.status_response import JavaStatusResponse
from nonebot import get_driver
from nonebot.log import logger
from PIL.Image import Resampling
from pil_utils import BuildImage, Text2Image
from pil_utils.types import ColorType

from .config import config
from .const import CODE_COLOR, GAME_MODE_MAP, STROKE_COLOR, ServerType
from .res import DEFAULT_ICON_RES, DIRT_RES, GRASS_RES
from .util import (
    BBCodeTransformer,
    chunks,
    format_mod_list,
    get_latency_color,
    resolve_ip,
    trim_motd,
)

MARGIN = 32
MIN_WIDTH = 512
TITLE_FONT_SIZE = 8 * 5
EXTRA_FONT_SIZE = 8 * 4
EXTRA_STROKE_WIDTH = 2
STROKE_RATIO = 0.0625
EXTRA_SPACING = 12
LIST_GAP = 32

JE_HEADER = "[MCJE服务器信息]"
BE_HEADER = "[MCBE服务器信息]"
SUCCESS_TITLE = "请求成功"

ImageType: TypeAlias = Union[BuildImage, Text2Image, "ImageGrid"]


def ex_default_style(text: str, color_code: str = "", **kwargs) -> Text2Image:
    default_kwargs = {
        "fontsize": EXTRA_FONT_SIZE,
        "fill": CODE_COLOR[color_code or "f"],
        "fontname": config.mcstat_font,
        "stroke_ratio": STROKE_RATIO,
        "stroke_fill": STROKE_COLOR[color_code or "f"],
        "spacing": EXTRA_SPACING,
    }
    default_kwargs.update(kwargs)
    return Text2Image.from_bbcode_text(text, **default_kwargs)


def calc_offset(*pos: Tuple[int, int]) -> Tuple[int, int]:
    return (sum(x[0] for x in pos), sum(x[1] for x in pos))


def draw_image_type_on(bg: BuildImage, it: ImageType, pos: Tuple[int, int]):
    if isinstance(it, ImageGrid):
        it.draw_on(bg, pos)
    elif isinstance(it, Text2Image):
        it.draw_on_image(bg.image, pos)
    else:
        bg.paste(it, pos, alpha=True)


class ImageLine:
    def __init__(
        self,
        left: Union[ImageType, str],
        right: Union[ImageType, str, None] = None,
        gap: int = 0,
    ):
        self.left = ex_default_style(left) if isinstance(left, str) else left
        self.right = (
            (ex_default_style(right) if isinstance(right, str) else right)
            if right
            else None
        )
        self.gap = gap

    @property
    def width(self) -> int:
        rw = self.right.width if self.right else 0
        return self.left.width + self.gap + rw

    @property
    def height(self) -> int:
        return max(self.left.height, (self.right.height if self.right else 0))

    @property
    def size(self) -> Tuple[int, int]:
        return self.width, self.height


class ImageGrid(List[ImageLine]):
    def __init__(
        self,
        *lines: ImageLine,
        spacing: int = 6,
        gap: Optional[int] = None,
        align_items: bool = True,
    ):
        if gap is not None:
            lines = tuple(ImageLine(x.left, x.right, gap=gap) for x in lines)
        super().__init__(lines)
        self.spacing = spacing
        self.align_items = align_items

    @classmethod
    def from_list(cls, li: Sequence[Union[ImageType, str]], **kwargs) -> "ImageGrid":
        return cls(
            *(ImageLine(*cast(Tuple[Any, Any], x)) for x in chunks(li, 2)),
            **kwargs,
        )

    @property
    def width(self) -> int:
        return (
            (
                max(x.left.width for x in self)
                + max((x.right.width + x.gap if x.right else 0) for x in self)
            )
            if self.align_items
            else max(x.width for x in self)
        )

    @property
    def height(self) -> int:
        return sum(x.height for x in self) + self.spacing * (len(self) - 1)

    @property
    def size(self) -> Tuple[int, int]:
        return self.width, self.height

    def append_line(self, *args, **kwargs):
        self.append(ImageLine(*args, **kwargs))

    def draw_on(self, bg: BuildImage, offset_pos: Tuple[int, int]) -> None:
        max_lw = max(x.left.width for x in self) if self.align_items else None
        y_offset = 0
        for line in self:
            draw_image_type_on(
                bg,
                line.left,
                calc_offset(offset_pos, (0, y_offset)),
            )
            if line.right:
                draw_image_type_on(
                    bg,
                    line.right,
                    calc_offset(
                        offset_pos,
                        ((max_lw or line.left.width) + line.gap, y_offset),
                    ),
                )
            y_offset += line.height + self.spacing

    def to_image(
        self,
        background: Optional[ColorType] = None,
        padding: int = 2,
    ) -> BuildImage:
        bg = BuildImage.new(
            "RGBA",
            calc_offset(self.size, (padding * 2, padding * 2)),
            background or (0, 0, 0, 0),
        )
        self.draw_on(bg, (padding, padding))
        return bg


def get_header_by_svr_type(svr_type: ServerType) -> str:
    return JE_HEADER if svr_type == "je" else BE_HEADER


def draw_bg(width: int, height: int) -> BuildImage:
    size = DIRT_RES.width
    bg = BuildImage.new("RGBA", (width, height))

    for hi in range(0, height, size):
        for wi in range(0, width, size):
            bg.paste(DIRT_RES if hi else GRASS_RES, (wi, hi))

    return bg


def build_img(
    header1: str,
    header2: str,
    icon: Optional[BuildImage] = None,
    extra: Optional[Union[ImageType, str]] = None,
) -> BytesIO:
    if not icon:
        icon = DEFAULT_ICON_RES
    if isinstance(extra, str):
        extra = ex_default_style(extra)

    header_text_color = CODE_COLOR["f"]
    header_stroke_color = STROKE_COLOR["f"]

    header_height = 128
    half_header_height = int(header_height / 2)

    bg_width = extra.width + MARGIN * 2 if extra else MIN_WIDTH
    bg_height = header_height + MARGIN * 2
    if bg_width < MIN_WIDTH:
        bg_width = MIN_WIDTH
    if extra:
        bg_height += extra.height + int(MARGIN / 2)
    bg = draw_bg(bg_width, bg_height)

    if icon.size != (header_height, header_height):
        icon = icon.resize_height(
            header_height,
            inside=False,
            resample=Resampling.NEAREST,
        )
    bg.paste(icon, (MARGIN, MARGIN), alpha=True)

    bg.draw_text(
        (
            header_height + MARGIN + MARGIN / 2,
            MARGIN - 4,
            bg_width - MARGIN,
            half_header_height + MARGIN + 4,
        ),
        header1,
        halign="left",
        fill=header_text_color,
        max_fontsize=TITLE_FONT_SIZE,
        fontname=config.mcstat_font,
        stroke_ratio=STROKE_RATIO,
        stroke_fill=header_stroke_color,
    )
    bg.draw_text(
        (
            header_height + MARGIN + MARGIN / 2,
            half_header_height + MARGIN - 4,
            bg_width - MARGIN,
            header_height + MARGIN + 4,
        ),
        header2,
        halign="left",
        fill=header_text_color,
        max_fontsize=TITLE_FONT_SIZE,
        fontname=config.mcstat_font,
        stroke_ratio=STROKE_RATIO,
        stroke_fill=header_stroke_color,
    )

    if extra:
        draw_image_type_on(
            bg,
            extra,
            (MARGIN, int(header_height + MARGIN + MARGIN / 2)),
        )

    return bg.convert("RGB").save("jpeg")


def draw_help(svr_type: ServerType) -> BytesIO:
    cmd_prefix_li = list(get_driver().config.command_start)
    prefix = cmd_prefix_li[0] if cmd_prefix_li else ""

    extra_txt = f"查询Java版服务器: {prefix}motd <服务器IP>\n查询基岩版服务器: {prefix}motdpe <服务器IP>"
    return build_img(get_header_by_svr_type(svr_type), "使用帮助", extra=extra_txt)


def draw_java(res: JavaStatusResponse, addr: str) -> BytesIO:
    transformer = BBCodeTransformer(bedrock=res.motd.bedrock)
    motd = transformer.transform(trim_motd(res.motd.parsed))
    online_percent = (
        "{:.2f}".format(res.players.online / res.players.max * 100)
        if res.players.max
        else "?.??"
    )

    mod_svr_type: Optional[str] = None
    mod_list: Optional[List[str]] = None
    if mod_info := res.raw.get("modinfo"):
        if tmp := mod_info.get("type"):
            mod_svr_type = tmp
        if tmp := mod_info.get("modList"):
            mod_list = format_mod_list(tmp)

    l_style = partial(ex_default_style, color_code="7")
    grid = ImageGrid(align_items=False)
    grid.append_line(motd)
    if config.mcstat_show_addr:
        grid.append_line(l_style("测试地址: "), addr)
    grid.append_line(l_style("服务端名: "), res.version.name)
    if mod_svr_type:
        grid.append_line(l_style("Mod 端类型: "), mod_svr_type)
    grid.append_line(l_style("协议版本: "), str(res.version.protocol))
    grid.append_line(
        l_style("当前人数: "),
        f"{res.players.online}/{res.players.max} ({online_percent}%)",
    )
    if mod_list:
        grid.append_line(l_style("Mod 总数: "), str(len(mod_list)))
    grid.append_line(
        l_style("聊天签名: "),
        "必需" if res.enforces_secure_chat else "无需",
    )
    if config.mcstat_show_delay:
        grid.append_line(
            l_style("测试延迟: "),
            ex_default_style(f"{res.latency:.2f}ms", get_latency_color(res.latency)),
        )
    if mod_list and config.mcstat_show_mods:
        grid.append_line(
            l_style("Mod 列表: "),
            ImageGrid.from_list(mod_list, gap=LIST_GAP),
        )
    if res.players.sample:
        grid.append_line(
            l_style("玩家列表: "),
            ImageGrid.from_list(
                [
                    transformer.transform(Motd.parse(x.name).parsed)
                    for x in res.players.sample
                ],
                gap=LIST_GAP,
            ),
        )

    icon = (
        BuildImage.open(BytesIO(base64.b64decode(res.icon.split(",")[-1])))
        if res.icon
        else None
    )
    return build_img(JE_HEADER, SUCCESS_TITLE, icon=icon, extra=grid)


def draw_bedrock(res: BedrockStatusResponse, addr: str) -> BytesIO:
    transformer = BBCodeTransformer(bedrock=res.motd.bedrock)
    motd = transformer.transform(trim_motd(res.motd.parsed))
    online_percent = (
        "{:.2f}".format(int(res.players_online) / int(res.players_max) * 100)
        if res.players_max
        else "?.??"
    )

    l_style = partial(ex_default_style, color_code="7")
    grid = ImageGrid(align_items=False)
    grid.append_line(motd)
    if config.mcstat_show_addr:
        grid.append_line(l_style("测试地址: "), addr)
    grid.append_line(l_style("协议版本: "), str(res.version.protocol))
    grid.append_line(l_style("游戏版本: "), res.version.version)
    grid.append_line(
        l_style("当前人数: "),
        f"{res.players.online}/{res.players.max} ({online_percent}%)",
    )
    if res.map:
        grid.append_line(l_style("存档名称: "), res.map)
    if res.gamemode:
        grid.append_line(
            l_style("游戏模式: "),
            GAME_MODE_MAP.get(res.gamemode, res.gamemode),
        )
    if config.mcstat_show_delay:
        grid.append_line(
            l_style("测试延迟: "),
            ex_default_style(f"{res.latency:.2f}ms", get_latency_color(res.latency)),
        )

    return build_img(BE_HEADER, SUCCESS_TITLE, extra=grid)


def draw_error(e: Exception, svr_type: ServerType) -> BytesIO:
    extra = ""
    if isinstance(e, TimeoutError):
        reason = "请求超时"
    elif isinstance(e, socket.gaierror):
        reason = "域名解析失败"
        extra = str(e)
    else:
        reason = "出错了！"
        extra = f"{e.__class__.__name__}: {e}"
    extra_img = ex_default_style(extra).wrap(MIN_WIDTH - MARGIN * 2) if extra else None
    return build_img(get_header_by_svr_type(svr_type), reason, extra=extra_img)


def draw_resp(
    resp: Union[JavaStatusResponse, BedrockStatusResponse],
    addr: str,
) -> BytesIO:
    if isinstance(resp, JavaStatusResponse):
        return draw_java(resp, addr)
    return draw_bedrock(resp, addr)


async def draw(ip: str, svr_type: ServerType) -> BytesIO:
    try:
        if not ip:
            return draw_help(svr_type)

        is_java = svr_type == "je"
        host, port = await resolve_ip(ip, is_java)

        svr = JavaServer(host, port) if is_java else BedrockServer(host, port)
        kw = {"version": config.mcstat_java_protocol_version} if is_java else {}
        if config.mcstat_query_twice:
            await svr.async_status(**kw)  # 第一次延迟通常不准
        resp = await svr.async_status(**kw)
        return draw_resp(resp, ip)

    except Exception as e:
        logger.exception("获取服务器状态/画服务器状态图出错")
        try:
            return draw_error(e, svr_type)
        except Exception:
            logger.exception("画异常状态图失败")
            raise
