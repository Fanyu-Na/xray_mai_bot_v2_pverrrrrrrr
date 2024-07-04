
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Message, GroupMessageEvent,Bot
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from src.libraries.data_handle.alias_db_handle import alias
from src.libraries.maimai.maimaidx_music import total_list
import asyncio
import nonebot
from src.libraries.GLOBAL_CONSTANT import BOT_DATA_STAFF,INITIAL_MACHINE,INITIAL_GROUP
from nonebot_plugin_imageutils import Text2Image
import io

application_alias = on_command('添加别名', priority=20)
@application_alias.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    args = str(args).strip().split(' ', 1)
    if len(args) == 2:
        music = total_list.by_id(args[0])
        if not music:
            await application_alias.send(f"未找到id为{args[0]}的歌曲")
        else:
            if event.user_id in BOT_DATA_STAFF:
                await application_alias.finish(
                    alias.adminAddAlias(str(event.user_id), str(event.group_id), args[0], args[1], music.title))
            msg, cid = alias.addalias(str(event.user_id), str(event.group_id), args[0], args[1], music.title)
            await application_alias.send(msg)
            if cid:
                bot = nonebot.get_bots()[str(INITIAL_MACHINE)]
                application_alias_message = f'{cid}-{str(args[0])}.{music.title}-{str(args[1])}-申请别名'
                await asyncio.sleep(2)
                await bot.send_group_msg(group_id=INITIAL_GROUP, message=application_alias_message)

delete_alias = on_command('删除别名', priority=20)
@delete_alias.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    args = str(args).strip().split(' ',1)
    if event.user_id in BOT_DATA_STAFF:
        await delete_alias.finish(alias.removeAlias(args[0], args[1]))
    else:
        await delete_alias.finish('权限不足')

agree_alias = on_command('投票', priority=20)
@agree_alias.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    cid = str(args).strip()
    result_r, re = alias.agreeAlias(cid, str(event.user_id))
    if not re:
        await agree_alias.finish(result_r)
    else:
        await agree_alias.send('投票成功。')

alias_examine_result = on_command('别名投票列表', aliases={'投票列表'}, priority=20)
@alias_examine_result.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    str2img = alias.getUnPassAlias()
    if str2img == '暂无':
        await alias_examine_result.finish('别名投票列表暂无')
    else:
        try:
            ima = Text2Image.from_text(str2img, 50).to_image(bg_color="white")
            imgByteArr = io.BytesIO()
            ima.save(imgByteArr, format="PNG")
        except ValueError:
            await alias_examine_result.finish("nmmd,检测到傻逼emjio表情符号,请联系管理员删除。")
        await alias_examine_result.send(MessageSegment.image(imgByteArr))

stepon_alias = on_command('踩', priority=20)
@stepon_alias.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    cid = str(args).strip()
    if event.user_id in BOT_DATA_STAFF:
        if alias.steponAlias(cid):
            await stepon_alias.send('已踩')

pass_alias = on_command('过', priority=20)

@pass_alias.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    cid = str(args).strip()
    if event.user_id in BOT_DATA_STAFF:
        result_r = alias.passAlias(cid)
        if result_r:
            await pass_alias.send('过')
            # todo 别名申请添加botID 用于通知别名申请通过
            # alias_name = result_r['alias']
            # sendMsg = [MessageSegment.at(result_r['user_id']),
            #            MessageSegment.text(f'你的{cid}号别名({alias_name})已添加成功')]
            # await asyncio.sleep(3)
            # sendbot = nonebot.get_bots()['3651135753']
            # try:
            #     await sendbot.send_group_msg(group_id=result_r['group_id'], message=sendMsg)
            # except:
            #     sendbot = nonebot.get_bots()['1719025274']
            #     await sendbot.send_group_msg(group_id=result_r['group_id'], message=sendMsg)

search_alias_examine = on_command('查别名申请', priority=20)
@search_alias_examine.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    cid = str(args).strip()
    if event.user_id in BOT_DATA_STAFF:
        result_r = alias.getAliasExamine(cid)
        if result_r:
            msg = f'添加用户ID:{result_r["user_id"]}\n申请群ID:{result_r["group_id"]}\n申请内容:{result_r["music_id"]}-{result_r["alias"]}\n同意情况:{",".join(result_r["agreeList"])}\n申请时间:{result_r["create_dt"]}'
            await search_alias_examine.send(msg)