from typing import List, Optional, TypedDict

from nonebot import get_driver
from pydantic import BaseModel

from .const import ServerType


class ShortcutType(TypedDict):
    regex: str
    host: str
    type: ServerType


class ConfigClass(BaseModel):
    mcstat_shortcuts: Optional[List[ShortcutType]] = []


config = ConfigClass.parse_obj(get_driver().config)
