from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require

require("nonebot_plugin_alconna")

from . import __main__ as __main__  # noqa: E402
from .config import ConfigClass  # noqa: E402

__version__ = "0.7.2"
__plugin_meta__ = PluginMetadata(
    name="PicMCStat",
    description="将一个 Minecraft 服务器的 MOTD 信息绘制为一张图片",
    usage="使用 motd 指令查看使用帮助",
    homepage="https://github.com/lgc-NB2Dev/nonebot-plugin-picmcstat",
    type="application",
    config=ConfigClass,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={"License": "MIT", "Author": "LgCookie"},
)
