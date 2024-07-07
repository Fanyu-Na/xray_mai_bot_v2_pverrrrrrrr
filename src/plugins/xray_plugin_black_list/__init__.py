from src.libraries.GLOBAL_CONSTANT import BOT_DATA_STAFF
from src.libraries.GLOBAL_RULE import check_is_bot_data_staff
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message ,MessageEvent,GroupMessageEvent,Bot
from nonebot.plugin import on_command
from nonebot.params import CommandArg
from src.libraries.data_handle.black_list_handle import admin
from nonebot.log import logger
import contextlib
from typing import Dict, Any
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from src.plugins.xray_plugins_log import c_logger


add_group_white = on_command('开启群', rule=check_is_bot_data_staff(),priority=3)
delete_group_white = on_command('关闭群', rule=check_is_bot_data_staff(),priority=3)
add_user_black = on_command('拉黑', rule=check_is_bot_data_staff(),priority=3)
delete_user_black = on_command('解黑', rule=check_is_bot_data_staff(),priority=3)

def execut_event_message(event:MessageEvent):
    data = event.message
    msglist = []
    for item in data:
        if item.type == 'text':
            msg = item.data['text']
            msglist.append(msg)
        else:
            msglist.append(f"【{item.type}】")
    msg = ''.join(msglist)
    log_data = {"type":"message_event"}
    if isinstance(event,GroupMessageEvent):
        log_data["group_id"] = event.group_id
    log_data['user_id'] = event.user_id
    log_data['content'] = msg
    c_logger.debug(log_data)
    
@Bot.on_calling_api
async def __(bot: Bot, api: str, data: Dict[str, Any]):
    with contextlib.suppress(Exception):
        if api not in ['send_msg', 'send_message']:
            return
        msglist = []
        for item in data['message']:
            if item.type == 'text':
                msg = item.data['text']
                msglist.append(msg)
            else:
                msglist.append(f"【{item.type}】")
        msg = ''.join(msglist)
        c_logger.info({
                "type":"send_message",
                "bot_id":bot.self_id,
                "user_id":data['user_id'],
                "group_id":data['group_id'],
                "content":msg
            })

# 取消注释开启黑白名单

# @event_preprocessor
# def blacklist_processor(event: MessageEvent):
#     is_block = 0
#     if isinstance(event,GroupMessageEvent):
#         if event.group_id in admin.get_groupid():
#             is_block = 0
#         else:
#             is_block = 1
#     if event.user_id in admin.get_userid():
#         is_block = 1
#     if event.user_id in BOT_DATA_STAFF:
#         is_block = 0

#     if is_block:
#         logger.success(f'拒绝开启会话')
#         raise IgnoredException('黑名单会话')
#     else:
#         execut_event_message(event)
#         return

@add_group_white.handle()
async def __(event: MessageEvent, args:Message=CommandArg()):
    groupid = int(str(args).strip())
    await add_group_white.send(admin.add_group(groupid))

@delete_group_white.handle()
async def __(event: MessageEvent, args:Message=CommandArg()):
    groupid = int(str(args).strip())
    await delete_group_white.send(admin.del_group(groupid))

@add_user_black.handle()
async def __(event: MessageEvent, args:Message=CommandArg()):
    userid = int(str(args).strip())
    await add_user_black.send(admin.add_user(userid))

@delete_user_black.handle()
async def __(event: MessageEvent, args:Message=CommandArg()):
    userid = int(str(args).strip())
    await add_user_black.send(admin.del_user(userid))