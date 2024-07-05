from src.libraries.GLOBAL_PATH import HELP_PATH
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Message, GroupMessageEvent,Bot
from nonebot.params import CommandArg

bot_help = on_command('help',aliases={'帮助','菜单','功能'},priority=20)
bot_ping = on_command("ping",priority=20)


@bot_ping.handle()
async def _(event: GroupMessageEvent):
    await bot_ping.send(f'Pong!')

@bot_help.handle()
async def _(event: GroupMessageEvent):
    with open(HELP_PATH, mode="rb") as f:
        data = f.read()
    await bot_help.send([MessageSegment.image(data)])