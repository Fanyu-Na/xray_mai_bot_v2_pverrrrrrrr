from nonebot import get_driver
from nonebot.plugin import PluginMetadata

from . import common

global_config = get_driver().config


__plugin_meta__ = PluginMetadata(
    name="MaiMaiDx更新完成表",
    description="MaiMaiDx更新完成表",
    usage="",
    type="application",
    config=None,
    supported_adapters={"~onebot.v11"}
)