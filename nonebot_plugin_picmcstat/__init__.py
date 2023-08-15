from nonebot.plugin import PluginMetadata

from . import __main__ as __main__
from .config import ConfigClass

__version__ = "0.3.5"
__plugin_meta__ = PluginMetadata(
    name="PicMCStat",
    description="将一个 Minecraft 服务器的 MOTD 信息绘制为一张图片",
    usage="使用 motd 指令查看使用帮助",
    homepage="https://github.com/lgc-NB2Dev/nonebot-plugin-picmcstat",
    type="application",
    config=ConfigClass,
    supported_adapters={"~onebot.v11"},
    extra={"License": "MIT", "Author": "student_2333"},
)
