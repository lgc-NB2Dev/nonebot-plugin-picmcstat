import asyncio

from nonebot_plugin_picmcstat.draw import draw


async def main():
    await draw("asia.easecation.net", "be")


asyncio.run(main())
