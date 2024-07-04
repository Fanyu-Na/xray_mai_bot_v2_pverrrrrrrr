from nonebot import on_command,on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message,MessageSegment,Bot
from nonebot.params import CommandArg
from src.libraries.data_handle.alias_db_handle import alias
from src.libraries.maimai.maimaidx_music import total_list
from nonebot.typing import T_State
from nonebot.adapters.onebot.utils import rich_unescape
from src.libraries.data_handle.open_chars_handle import openchars
from src.plugins.xray_plugins_log import c_logger
from .utils import generate_message_state,check_music_id,generate_success_state,check_title,check_music_id,generate_success_state

start_open_chars = on_command('dlx猜歌',priority=20)
open_chars = on_command('开',priority=20)
all_message_handle = on_message(priority=18,block=False)
pass_game = on_command('跳过猜歌',priority=20)

@start_open_chars.handle()
async def _(bot: Bot, event: GroupMessageEvent, args:Message=CommandArg()):
    arg = str(args).strip()
    group_id = event.group_id
    is_exist,game_data = openchars.start(group_id,arg)
    if is_exist:
        await start_open_chars.send("游戏进行中，请不要再次开始噢~")
    else:
        await start_open_chars.send("准备开始猜歌游戏~\n输入“开（字母）”开出字母\n输入“跳过猜歌”跳过\n输入“结束猜歌”结束\n直接发送别名或id即可猜歌")
        is_game_over,game_state,char_all_open,game_data = generate_message_state(game_data)
        c_logger.debug(game_data)
        # openchars.update_game_data(group_id,game_data)
        await start_open_chars.send(game_state)
        # if is_game_over:
        #     openchars.game_over(group_id)
        #     await start_open_chars.send('全部答对啦，恭喜各位🎉\n本轮猜歌已结束，可发送“dlx猜歌”再次游玩')

@open_chars.handle()   
async def _(event: GroupMessageEvent, args:Message=CommandArg()):
    char = rich_unescape(str(args).strip())
    group_id = event.group_id
    print(char,len(char))
    if len(char) != 1:
        await open_chars.finish()
    
    is_start,game_data = openchars.open_char(group_id,char)
    if is_start is not None:
        if is_start:
            is_game_over,game_state,char_all_open,game_data = generate_message_state(game_data)
            openchars.update_game_data(group_id,game_data)

            if char_all_open:
                await open_chars.send(char_all_open)
            await open_chars.send(game_state)
            if is_game_over:
                openchars.game_over(group_id)
                await open_chars.send('全部答对啦，恭喜各位🎉\n本轮猜歌已结束，可发送“dlx猜歌”再次游玩')
        else:
            await open_chars.send([MessageSegment.reply(event.message_id),MessageSegment.text("该字母已经开过了噢，换一个字母吧~")])
    else:
        await open_chars.send('游戏还未开启')


@all_message_handle.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    msg_content = str(event.get_message())
    group_id = event.group_id
    game_data = openchars.get_game_data(group_id)
    if game_data:
        try:
            songinfo = total_list.by_id(msg_content)
            if songinfo:
                music_ids = [int(songinfo.id)]
            elif not songinfo:
                music_ids = alias.queryMusicByAlias(msg_content)
        except:
            music_ids = None
    
        if not music_ids:
            guess_success,game_data = check_title(game_data,msg_content)
            if guess_success:
                await all_message_handle.send(guess_success)
                is_game_over,game_state,char_all_open,game_data = generate_message_state(game_data)
                if is_game_over:
                    openchars.game_over(group_id)
                    await start_open_chars.send('全部答对啦，恭喜各位🎉\n本轮猜歌已结束，可发送“dlx猜歌”再次游玩')
                else:
                    openchars.update_game_data(group_id,game_data)
                await start_open_chars.send(game_state)
        else:
            guess_success,game_data = check_music_id(game_data,music_ids)
            print(game_data)
            if guess_success:
                await all_message_handle.send(guess_success)
                is_game_over,game_state,char_all_open,game_data = generate_message_state(game_data)
                if is_game_over:
                    openchars.game_over(group_id)
                    await start_open_chars.send('全部答对啦，恭喜各位🎉\n本轮猜歌已结束，可发送“dlx猜歌”再次游玩')
                else:
                    openchars.update_game_data(group_id,game_data)
                await start_open_chars.send(game_state)

@pass_game.handle()   
async def _(event: GroupMessageEvent):
    group_id = event.group_id
    game_data = openchars.get_game_data(group_id)
    if game_data:
        openchars.game_over(group_id)
        await pass_game.send(generate_success_state(game_data))
        await pass_game.send("本次猜歌跳过，准备开始下一轮~")
