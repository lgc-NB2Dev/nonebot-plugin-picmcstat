import random
import re
import string
from collections.abc import Iterator, Sequence
from typing import Optional, TypeVar, Union, cast

import dns.asyncresolver
import dns.name
import dns.rdatatype as rd
from dns.rdtypes.IN.SRV import SRV as SRVRecordAnswer  # noqa: N811
from mcstatus.motd.components import (
    Formatting,
    MinecraftColor,
    ParsedMotdComponent,
    WebColor,
)
from mcstatus.motd.transformers import PlainTransformer
from nonebot import logger

from .config import config
from .const import (
    ENUM_CODE_COLOR,
    ENUM_CODE_COLOR_BEDROCK,
    ENUM_STROKE_COLOR,
    ENUM_STROKE_COLOR_BEDROCK,
    ENUM_STYLE_BBCODE,
    FORMAT_CODE_REGEX,
    OBFUSCATED_PLACEHOLDER_REGEX,
    STROKE_COLOR,
)

RANDOM_CHAR_TEMPLATE = f"{string.ascii_letters}{string.digits}!§$%&?#"
WHITESPACE_EXCLUDE_NEWLINE = string.whitespace.replace("\n", "")
DNS_RESOLVER = dns.asyncresolver.Resolver()
DNS_RESOLVER.nameservers = [*DNS_RESOLVER.nameservers, "1.1.1.1", "1.0.0.1"]

T = TypeVar("T")


def get_latency_color(delay: float) -> str:
    if delay <= 50:
        return "a"
    if delay <= 100:
        return "e"
    if delay <= 200:
        return "6"
    return "c"


def random_char(length: int) -> str:
    return "".join(random.choices(RANDOM_CHAR_TEMPLATE, k=length))


def replace_format_code(txt: str, new_str: str = "") -> str:
    return re.sub(FORMAT_CODE_REGEX, new_str, txt)


def format_mod_list(li: list[Union[dict, str]]) -> list[str]:
    def mapping_func(it: Union[dict, str]) -> Optional[str]:
        if isinstance(it, str):
            return it
        if isinstance(it, dict) and (name := it.get("modid")):
            version = it.get("version")
            return f"{name}-{version}" if version else name
        return None

    return sorted((x for x in map(mapping_func, li) if x), key=lambda x: x.lower())


async def resolve_host(
    host: str,
    data_types: Optional[list[rd.RdataType]] = None,
) -> Optional[str]:
    data_types = data_types or [rd.CNAME, rd.AAAA, rd.A]
    for rd_type in data_types:
        try:
            resp = (await DNS_RESOLVER.resolve(host, rd_type)).response
            name = resp.answer[0][0].to_text()  # type: ignore
        except Exception as e:
            logger.debug(
                f"Failed to resolve {rd_type.name} record for {host}: "
                f"{e.__class__.__name__}: {e}",
            )
        else:
            logger.debug(f"Resolved {rd_type.name} record for {host}: {name}")
            if rd_type is rd.CNAME:
                return await resolve_host(name)
            return name
    return None


async def resolve_srv(host: str) -> tuple[str, int]:
    host = "_minecraft._tcp." + host
    resp = await DNS_RESOLVER.resolve(host, rd.SRV)
    answer = cast(SRVRecordAnswer, resp[0])
    return str(answer.target), int(answer.port)


async def resolve_ip(ip: str, srv: bool = False) -> tuple[str, Optional[int]]:
    if ":" in ip:
        host, port = ip.split(":", maxsplit=1)
    else:
        host = ip
        port = None

    if (not port) and srv:
        try:
            host, port = await resolve_srv(host)
        except Exception as e:
            logger.debug(
                f"Failed to resolve SRV record for {host}: "
                f"{e.__class__.__name__}: {e}",
            )
        logger.debug(f"Resolved SRV record for {ip}: {host}:{port}")

    return (
        (await resolve_host(host) if config.mcstat_resolve_dns else None) or host,
        int(port) if port else None,
    )


def chunks(lst: Sequence[T], n: int) -> Iterator[Sequence[T]]:
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


# shit code
def trim_motd(motd: list[ParsedMotdComponent]) -> list[ParsedMotdComponent]:
    modified_motd: list[ParsedMotdComponent] = []

    in_content = False
    for comp in motd:
        if not isinstance(comp, str):
            modified_motd.append(comp)
            continue
        if not comp:
            continue

        if not in_content:
            if comp[0] in WHITESPACE_EXCLUDE_NEWLINE:
                comp = comp.lstrip(WHITESPACE_EXCLUDE_NEWLINE)
            if not comp:
                continue

        if not comp[0].isspace():
            in_content = True

        if "\n" not in comp:
            modified_motd.append(comp)
            continue

        # new line
        last, *inner = comp.split("\n")
        last = last.rstrip()
        if not inner:
            modified_motd.append(f"{last}\n")
            in_content = False
            continue

        for i in range(len(modified_motd) - 1, -1, -1):
            it = modified_motd[i]
            if not (isinstance(it, str) and it):
                continue
            if it[-1] in WHITESPACE_EXCLUDE_NEWLINE:
                modified_motd[i] = it = it.rstrip(WHITESPACE_EXCLUDE_NEWLINE)
            if it:
                break

        new = inner[-1].lstrip()
        inner = (x.strip() for x in inner[:-1])
        modified_motd.append("\n".join((last, *inner, new)))
        in_content = bool(new)

    return [x for x in modified_motd if x]


def split_motd_lines(motd: Sequence[ParsedMotdComponent]):
    lines: list[list[ParsedMotdComponent]] = []

    current_line: list[ParsedMotdComponent] = []
    using_color: Union[MinecraftColor, WebColor, None] = None
    using_formats: list[Formatting] = []

    for comp in motd:
        if isinstance(comp, str) and "\n" in comp:
            # not fully tested, lazy to do
            str_lines = comp.split("\n")

            last_line = ""
            if len(str_lines) > 1:
                last_line = str_lines[-1]
                str_lines = str_lines[:-1]

            for line in str_lines:
                if line:
                    current_line.append(line)
                current_line.append(Formatting.RESET)
                lines.append(current_line)

                current_line = []
                if using_color:
                    current_line.append(using_color)
                if using_formats:
                    current_line.extend(using_formats)

            if last_line:
                current_line.append(last_line)

            continue

        if isinstance(comp, (MinecraftColor, WebColor)):
            using_color = comp

        elif isinstance(comp, Formatting):
            if comp is Formatting.RESET:
                using_color = None
                using_formats = []
            else:
                using_formats.append(comp)

        current_line.append(comp)

    if current_line:
        lines.append(current_line)

    return lines


class BBCodeTransformer(PlainTransformer):
    def __init__(self, *, bedrock: bool = False) -> None:
        self.bedrock = bedrock
        self.on_reset = []

    def transform(self, motd_components: Sequence[ParsedMotdComponent]) -> str:
        self.on_reset = []
        return super().transform(motd_components)

    def _format_output(self, results: list[str]) -> str:
        text = super()._format_output(results) + "".join(reversed(self.on_reset))
        return re.sub(
            OBFUSCATED_PLACEHOLDER_REGEX,
            lambda m: (random_char(len(i)) if (i := m.group("inner")) else ""),
            text,
        )

    def _handle_minecraft_color(self, element: MinecraftColor, /) -> str:
        stroke_map = ENUM_STROKE_COLOR_BEDROCK if self.bedrock else ENUM_STROKE_COLOR
        color_map = ENUM_CODE_COLOR_BEDROCK if self.bedrock else ENUM_CODE_COLOR
        self.on_reset.append("[/color][/stroke]")
        return f"[stroke={stroke_map[element]}][color={color_map[element]}]"

    def _handle_web_color(self, element: WebColor, /) -> str:
        self.on_reset.append("[/color][/stroke]")
        return f"[stroke={STROKE_COLOR['f']}][color={element.hex}]"

    def _handle_formatting(self, element: Formatting, /) -> str:
        if element is Formatting.RESET:
            to_return = "".join(self.on_reset)
            self.on_reset = []
            return to_return
        start, end = ENUM_STYLE_BBCODE[element]
        self.on_reset.append(end)
        return start
