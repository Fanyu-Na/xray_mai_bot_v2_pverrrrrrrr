from nonebot import on_message,on_shell_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message,MessageSegment,Bot
from nonebot.params import ShellCommandArgs
from nonebot.rule import Rule
import random
from nonebot.typing import T_State
import asyncio
import datetime
from src.libraries.data_handle.alias_db_handle import alias
from src.libraries.data_handle.abstract_db_handle import abstract
from src.libraries.maimai.maimaidx_music import obj,total_list
from typing import Dict
from src.libraries.image_handle.image import *
from PIL import Image, ImageFilter
from nonebot.rule import Namespace, ArgumentParser
from src.libraries.maimai.utils import get_abstract_cover_path_by_file_id

hot_music_ids = []
music_ids = abstract.get_abstract_id_list()
for item in music_ids:
    hot_music_ids.append(str(item))


my_data = list(filter(lambda x: x['id'] in hot_music_ids, obj))

guess_music_dict = {}

def check_Admin():
    async def _checker(event: GroupMessageEvent) -> bool:
        if event.user_id in [381268035,3434334409]:
            return True
        else:
            return False
    return Rule(_checker)

def Get_Cut_Img(file_name,mode) -> None:
        IMG_data = get_abstract_cover_path_by_file_id(file_name)
        img = Image.open(IMG_data).convert("RGBA")
        if mode:
            img = img.resize((400,400))
            img = img.filter(random.choice([ImageFilter.CONTOUR(),ImageFilter.GaussianBlur(7)]))
        else:
            img = img.resize((300,300))
        w, h = img.size
        w2, h2 = int(w / 3), int(h / 3)
        l, u = random.randrange(0, int(2 * w / 3)), random.randrange(0, int(2 * h / 3))
        img = img.crop((l, u, l+w2, u+h2))
        b64image = image_to_base64(img)
        return b64image

async def guess_music_loop(bot: Bot, event: GroupMessageEvent, state: T_State,mode:0):
    # print(my_data)
    music: Dict = random.choice(my_data)
    file_name,nickname = abstract.get_abstract_file_name(str(music['id']))

    b64image = Get_Cut_Img(file_name,mode)
    last_time = (datetime.datetime.now() + datetime.timedelta(seconds= +30)).strftime('%Y-%m-%d %H:%M:%S')

    guess_music_dict[event.group_id] = {"music":music,"end_time":last_time,"is_end":0,"mode":mode,"file_name":file_name}
    asyncio.create_task(bot.send(event, Message([
        MessageSegment.text("这首歌封面的一部分是："),
        MessageSegment.image("base64://" + str(b64image, encoding="utf-8")),
        MessageSegment.text("答案将在 30 秒后揭晓")
    ])))
    asyncio.create_task(give_answer(bot, event, state))
    return

async def give_answer(bot: Bot, event: GroupMessageEvent, state: T_State):
    for item in range(30):
        await asyncio.sleep(1)
        if not guess_music_dict.get(event.group_id,0):
            return
    music = guess_music_dict[event.group_id]['music']
    file_name = guess_music_dict[event.group_id]['file_name']
    IMG_data = get_abstract_cover_path_by_file_id(file_name)
    with open(IMG_data, mode="rb") as f:
        data = f.read()
    asyncio.create_task(bot.send(event, Message([MessageSegment.text("答案是：" + f"{music['id']}. {music['title']}\n"),MessageSegment.image(data)])))
    guess_music_dict.pop(event.group_id)

search_location_parser = ArgumentParser()
search_location_parser.add_argument("-hd", default=False, action='store_true')


guess_music = on_shell_command('猜曲绘', priority=10,parser=search_location_parser)

@guess_music.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State,foo: Namespace = ShellCommandArgs()):
    group_id = event.group_id
    if not guess_music_dict.get(group_id,0):
        asyncio.create_task(guess_music_loop(bot, event, state,foo.hd))
    else:
        await guess_music.send("当前已有正在进行的猜曲绘")

guess_music_solve = on_message(priority=8, block=False)
@guess_music_solve.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    if guess_music_dict.get(event.group_id,0):
        ans = str(event.get_message())
        music = guess_music_dict[event.group_id]["music"]
        ermnade = False
        name = str(event.get_message()).strip().lower()
        result_set = alias.queryMusicByAlias(name)

        if len(result_set) == 1:
            music_result = total_list.by_id(result_set[0])
            if music['id'] == music_result.id:
                ermnade = True
        elif len(result_set) == 0:
            ermnade = False
        else:
            for result in result_set:
                music_result = total_list.by_id(result)
                if music['id'] == music_result.id:
                    ermnade = True
                    break
        if str(event.message) == "开挂" and event.user_id in [381268035]:
            cheat = 1
        else:
            cheat = 0

        if str(event.message) == "跳过":
            await guess_music_solve.send([MessageSegment.text("你们真TM菜😶‍🌫️")])
            mode = guess_music_dict[event.group_id]['mode']

            music = guess_music_dict[event.group_id]['music']
            file_name = guess_music_dict[event.group_id]['file_name']
            IMG_data = get_abstract_cover_path_by_file_id(file_name)
            guess_music_dict.pop(event.group_id)

            with open(IMG_data, mode="rb") as f:
                data = f.read()
            await guess_music_solve.send([MessageSegment.text("答案是：" + f"{music['id']}. {music['title']}\n"),MessageSegment.image(data)])


        if cheat or ermnade or ans == music['id'] or (ans.lower() == music['title'].lower()) or (len(ans) >= 5 and ans.lower() in music['title'].lower()):
            mode = guess_music_dict[event.group_id]['mode']
            file_name = guess_music_dict[event.group_id]['file_name']
            guess_music_dict.pop(event.group_id)
            with open(get_abstract_cover_path_by_file_id(file_name), mode="rb") as f:
                data = f.read()
            await guess_music_solve.send(Message([
                MessageSegment.reply(event.message_id),
                MessageSegment.text("猜对了，答案是：" + f"{music['id']}. {music['title']}\n"),
                MessageSegment.image(data)
            ]))
            group_id = event.group_id
            if not guess_music_dict.get(group_id,0):
                # group_Data = guess_music_dict.get(group_id,0)
                asyncio.create_task(guess_music_loop(bot, event, state,mode))
    else:
        return
    

