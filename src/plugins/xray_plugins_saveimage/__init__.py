import string
import random
import httpx
import aiofiles
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg
from nonebot.typing import T_State
from typing import Optional
from nonebot.log import logger
from pathlib import Path
from src.libraries.data_handle.abstract_db_handle import abstract
from io import BytesIO
from PIL import Image
from src.libraries.GLOBAL_PATH import DRAGON_PATH,CUSTOM_PLATE_PATH,ABSTRACT_COVER_PATH
from src.libraries.GLOBAL_CONSTANT import SAVE_IMAGE

save_plate = on_command('添加姓名框', priority=20)
save_along = on_command('添加龙图', priority=20)
save_abstract = on_command('添加抽象画', priority=20)

@save_plate.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    arg = str(args).strip()
    if arg:
        state['platename'] = arg

@save_plate.got("platename", prompt="姓名框叫啥名???(私自上传官方姓名框直接飞机票处理)")
async def _(event: GroupMessageEvent, state: T_State):
    platename = state['platename']
    plate_path = Path(f"{CUSTOM_PLATE_PATH}/UI_Plate_{platename}.png")
    if plate_path.exists():
        await save_plate.finish(f"自定义姓名【{platename}】已经存在。")

@save_plate.got("img", prompt="请发送姓名框图片")
async def _(event: GroupMessageEvent, state: T_State):
    platename = str(state["platename"])
    result = await save_plate_img(state["img"], platename)
    await save_plate.send(result)

@save_along.handle()
async def _(event: GroupMessageEvent, state: T_State):
    if event.group_id not in SAVE_IMAGE:
        await save_along.finish('权限不足')

@save_along.got("img", prompt="请发送龙图")
async def _(event: GroupMessageEvent, state: T_State):
    data = string.ascii_letters + string.digits
    filename = "".join(random.sample(data, random.randint(5, 8)))
    result = await save_along_img(state["img"], filename)  # 保存回答中的图片
    await save_along.send(result)

@save_abstract.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if event.group_id not in SAVE_IMAGE:
        await save_abstract.finish('权限不足')
    arg = str(args).strip()
    if arg:
        state['songid'] = arg

@save_abstract.got("songid", prompt="请输入要需要添加的抽象画歌曲ID,如有DX和标准两个铺面请添加两次")
async def _(event: GroupMessageEvent, state: T_State):
    music_id = str(state['songid']).strip()
    is_int = True
    try:
        temp = int(music_id)
    except:
        is_int = False
    if not is_int:
        await save_abstract.finish(f"添加失败:【{music_id}】不是正确的歌曲ID。")

@save_abstract.got("img", prompt="请发送抽象画图片")
async def _(event: GroupMessageEvent, state: T_State):
    songid = str(state["songid"])
    file_name = f"{songid}_{abstract.getNextCount(songid)}"
    result = await save_abstract_img(state["img"], file_name)

    if result == '添加成功,太好康了，你就是干这个的料。':  # 保存回答中的图片
        file_name = abstract.add_abstract(songid, event.user_id, event.sender.nickname,file_name)
    await save_abstract.send(result)

async def save_plate_img(msg: Message, file_name:str):
    custom_plate_path = Path(f"{CUSTOM_PLATE_PATH}/").absolute()
    for msg_seg in msg:
        if msg_seg.type == "image":
            plate_file_name = f"UI_Plate_{file_name}.png"

            file_path = custom_plate_path / plate_file_name
            url = msg_seg.data.get("url", "")
            if not url:
                continue
            data = await get_img(url)
            if not data:
                continue
            result = await check_plate_img(data, file_path)
            return result
    return "添加失败:消息内容中未检索到图片内容。"

async def save_along_img(msg: Message, file_name:str):
    along_path = Path(f"{DRAGON_PATH}/").absolute()
    for msg_seg in msg:
        if msg_seg.type == "image":
            along_file_name = file_name

            file_path = along_path / along_file_name
            url = msg_seg.data.get("url", "")
            if not url:
                continue
            data = await get_img(url)
            if not data:
                continue
            result = await save_img(data, file_path)
            return result
    return "添加失败:消息内容中未检索到图片内容。"

async def save_abstract_img(msg: Message, file_name:str):
    abstract_cover_path = Path(f"{ABSTRACT_COVER_PATH}/").absolute()
    for msg_seg in msg:
        if msg_seg.type == "image":
            abstract_cover_file_name = f"{file_name}.png"

            file_path = abstract_cover_path / abstract_cover_file_name
            url = msg_seg.data.get("url", "")
            if not url:
                continue
            data = await get_img(url)
            if not data:
                continue
            result = await check_abstract_img(data, file_path)
            return result
    return "添加失败:消息内容中未检索到图片内容。"
     
async def check_plate_img(img: bytes, filepath: Path):
    image_bytes = BytesIO(img)
    image = Image.open(image_bytes)
    width, height = image.size
    if (width != 720) and (height != 116):
        return "添加失败:自定义姓名框尺寸为720X116。"
    else:
        try:
            async with aiofiles.open(str(filepath.absolute()), "wb") as f:
                await f.write(img)
            return "添加成功,太好康了，你就是干这个的料。"
        except:
            return "添加失败:图片保存失败，请重试。"
        
async def check_abstract_img(img: bytes, filepath: Path):
    image_bytes = BytesIO(img)
    image = Image.open(image_bytes)
    width, height = image.size
    if abs(width-height) >= 3:
        return "添加失败:请使用1:1的图片规格。"
    else:
        try:
            async with aiofiles.open(str(filepath.absolute()), "wb") as f:
                await f.write(img)
            return "添加成功,太好康了，你就是干这个的料。"
        except:
            return "添加失败:图片保存失败，请重试。"

async def save_img(img: bytes, filepath: Path):
    try:
        async with aiofiles.open(str(filepath.absolute()), "wb") as f:
            await f.write(img)
        return "添加成功。"
    except:
        return "添加失败:图片保存失败，请重试。"

async def get_img(url: str) -> Optional[bytes]:
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.53",
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            return resp.content
    except:
        logger.warning(f"图片下载失败：{url}")
        return None