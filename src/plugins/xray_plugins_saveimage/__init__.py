import string
import random
import httpx
import aiofiles
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.typing import T_State
from typing import Optional
from nonebot.log import logger
from pathlib import Path
from src.libraries.GLOBAL_PATH import DRAGON_PATH
from src.libraries.GLOBAL_CONSTANT import SAVE_IMAGE

save_along = on_command('添加龙图', priority=20)


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