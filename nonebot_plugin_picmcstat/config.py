from typing import List, Optional

from nonebot import get_plugin_config
from pydantic import BaseModel, Field

from .const import ServerType


class ShortcutType(BaseModel):
    regex: str
    host: str
    type: ServerType  # noqa: A003
    whitelist: Optional[List[int]] = []


class ConfigClass(BaseModel):
    mcstat_font: str = "unifont"
    mcstat_show_addr: bool = False
    mcstat_show_delay: bool = True
    mcstat_show_mods: bool = False
    mcstat_reply_target: bool = True
    mcstat_shortcuts: List[ShortcutType] = Field(default_factory=list)
    mcstat_resolve_dns: bool = True
    mcstat_query_twice: bool = True
    mcstat_java_protocol_version: int = 767


config = get_plugin_config(ConfigClass)
