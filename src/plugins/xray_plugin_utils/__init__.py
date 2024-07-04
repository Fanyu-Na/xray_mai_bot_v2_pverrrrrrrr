from src.libraries.GLOBAL_CONSTANT import BOT_STAFF,USER_POKE_MESSAGE
from src.libraries.GLOBAL_PATH import DRAGON_PATH,REWARD_QR_PATH,HELP_PATH
from src.libraries.data_handle.black_list_handle import admin
from nonebot import on_command,on_regex,on_notice
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Event, MessageSegment, Message, GroupMessageEvent,Bot
from nonebot.permission import SUPERUSER
import nonebot
from nonebot.params import CommandArg
from nonebot.adapters.onebot.utils import rich_unescape
import asyncio
import os
import random
import re
import time
import httpx

LAST_MSG = {}
LAST_REPEAT_MSG = {}
REPEAT_COUNT = {}


now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
staff_speak_time = {"time":now_time}



async def _group_poke(bot: Bot, event: Event) -> bool:
    value = (event.notice_type == "notify" and event.sub_type == "poke" and event.target_id == int(bot.self_id))
    return value

modify_group_card = on_command('修改群名片', permission=SUPERUSER,priority=20)
modify_group_title = on_command('设置群头衔',priority=20)

bot_help = on_command('help',aliases={'帮助','菜单','功能'},priority=20)
bot_ping = on_command("ping",priority=20)

# 戳一戳
user_poke = on_notice(rule=_group_poke, priority=10, block=True) 

long_yu_tao = on_command('来点龙图',aliases={'疯狂龙玉涛'},priority=20)
bot_selector = on_regex(r"(xray|Xray).+还是.+",priority=20)

send_update_notice = on_command('推送通知', priority=20)

@modify_group_card.handle()
async def _(bot: Bot, event: GroupMessageEvent, args:Message=CommandArg()):
    args = str(args).strip()
    Group_Num = event.group_id
    Bot_QQ = event.self_id
    await bot.set_group_card(group_id=Group_Num, user_id=Bot_QQ, card=args)
    await modify_group_card.finish('~已修改群名片为'+args+'哩')

@modify_group_title.handle()
async def _(bot: Bot, event: GroupMessageEvent, args:Message=CommandArg()):
    Group_Id = event.group_id
    User_Id = event.user_id
    Title = str(args).strip()
    if str == '':
      await bot.set_group_special_title(group_id=Group_Id,user_id=User_Id)
      await modify_group_title.send('设置成功捏~')
    else:
      await bot.set_group_special_title(group_id=Group_Id,user_id=User_Id,special_title=Title)
      await modify_group_title.send('设置成功捏~')

@bot_ping.handle()
async def _(bot:Bot, event: GroupMessageEvent, args:Message=CommandArg()):
    await bot_ping.send(f'Pong!')

@bot_help.handle()
async def _(event: GroupMessageEvent):
    with open(HELP_PATH, mode="rb") as f:
        data = f.read()
    await bot_help.send([MessageSegment.image(data)])

@user_poke.handle()
async def _(event: Event):
    ri = random.randint(1,20)
    if ri <= 7:
        await user_poke.send(random.choice(['靠,你打扰到我睡觉了,赔钱','我不要脸,给我打钱']))
        with open(REWARD_QR_PATH,mode="rb") as f:
            data = f.read()
        await user_poke.finish(MessageSegment.image(data))
    else:
        await user_poke.send(random.choice(USER_POKE_MESSAGE))

@long_yu_tao.handle()
async def _(event: GroupMessageEvent):
    fillname = random.choice(os.listdir(DRAGON_PATH))
    with open(f"{DRAGON_PATH}/{fillname}", mode="rb") as f:
        data = f.read()
    await long_yu_tao.finish(MessageSegment.image(data))

@bot_selector.handle()
async def _(event: GroupMessageEvent):
    r = "(xray|Xray)(.+还是.+)"
    args = re.match(r,str(event.get_message()))
    if args:
        if len(args.groups()) == 2:
            msg = args.groups()[1].strip()
            thingss = msg.split('还是')
            things = []
            for item in thingss:
                if not item == '':
                    things.append(item.replace("我","你"))
            if len(things) >= 2:
                v = random.choice(things)
                await bot_selector.finish(f'Xray Bot建议你选择{v}呢')



@send_update_notice.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if event.user_id not in BOT_STAFF:
        await send_update_notice.finish('权限不足')

@send_update_notice.got("msg_content", prompt="请输入要推送的通知内容。")
async def _(event: GroupMessageEvent, state: T_State):
    msg_content:Message = state['msg_content']
    message_content = []
    for msg in msg_content:
        if msg.type == 'text':
            message_content.append(MessageSegment.text(msg.data['text']))
        elif msg.type == 'image':
            image_url = rich_unescape(msg.data['file'])
            result = await get_img(image_url)
            message_content.append(MessageSegment.image(result))
    bots = nonebot.get_bots()
    await send_update_notice.send(f'开始推送通知。\n当前登录Bot:{",".join([bot for bot in bots.keys()])}\n推送内容如下。')
    await send_update_notice.send(message_content)
    for bot_id,bot in bots.items():
        try:
            group_data_list = await bot.get_group_list()
            await send_update_notice.send(f"{bot_id}开始推送通知。")
        except:
            await send_update_notice.send(f"{bot_id}获取群列表失败。")
            continue
        for group_data in group_data_list:
            
            try:
                if int(group_data['group_id']) in admin.get_groupid():
                    await bot.send_group_msg(group_id = group_data['group_id'],message = message_content)
                else:
                    continue
            except:
                await send_update_notice.send(f"{bot_id}推送群消息失败。")
                continue
            await send_update_notice.send(f"{bot_id}_{group_data['group_id']}_{group_data['group_name']}推送通知完毕,Sleep:30S")
            await asyncio.sleep(30)
    await send_update_notice.finish("全部Bot通知推送完毕。")
    
async def get_img(url):
    try:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.53",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            img_data = resp.content
        return img_data
    except:
        return None

