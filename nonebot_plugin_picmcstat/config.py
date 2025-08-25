from typing import Any

from cookit.pyd import field_validator, model_with_alias_generator
from nonebot import get_plugin_config
from pydantic import BaseModel, Field

from .const import ServerType


class ShortcutType(BaseModel):
    regex: str
    host: str
    type: ServerType  # noqa: A003
    whitelist: list[int] | None = []


@model_with_alias_generator(lambda x: f"mcstat_{x}")
class ConfigClass(BaseModel):
    font: list[str] = ["Minecraft Seven", "unifont"]
    show_addr: bool = False
    show_delay: bool = True
    show_mods: bool = False
    reply_target: bool = True
    shortcuts: list[ShortcutType] = Field(default_factory=list)
    resolve_dns: bool = True
    query_twice: bool = True
    java_protocol_version: int = 772
    enable_auto_detect: bool = True

    @field_validator("font", mode="before")
    def transform_to_list(cls, v: Any):  # noqa: N805
        return v if isinstance(v, list) else [v]


config = get_plugin_config(ConfigClass)
