
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.params import CommandArg
from pathlib import Path
from nonebot.plugin import on_command
from src.libraries.data_handle.userdata_handle import userdata
from nonebot.log import logger
from src.libraries.GLOBAL_PATH import FRAME_PATH,PLATE_PATH,CUSTOM_PLATE_PATH,ICON_PATH

set_style = on_command("设置主题", priority=20)
set_abstract_on = on_command("开启抽象画", priority=20)
set_abstract_off = on_command("关闭抽象画", priority=20)
set_plate = on_command("设置姓名框", priority=20)
set_frame = on_command("设置背景板", priority=20,aliases={'设置背景'})
set_icon = on_command("设置头像", priority=20)
set_best30_mode = on_command("设置模式", priority=20)

def is_int(content:str):
    try:
        content = int(content)
        return True
    except:
        return False

@set_style.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    group_id = event.group_id
    user_id = event.get_user_id()
    style_arg = str(args).strip()
    if style_arg in ["1","2","3"]:
        if userdata.setUserConfig(user_id,group_id,"style_index",style_arg):
            await set_style.send("Best50主题设置成功。")
        else:
            await set_style.send("Best50主题设置出现错误,请联系Xray Bot管理员。")
    else:
        await set_style.send("主题样式目前只有【1】、【2】、【3】请检查主题ID正确。")

@set_abstract_on.handle()
async def _(event: GroupMessageEvent):
    group_id = event.group_id
    user_id = event.get_user_id()
    if userdata.setUserConfig(user_id,group_id,"is_abstract",True):
        await set_abstract_on.send("已开启抽象画模式。")
    else:
        await set_abstract_on.send("抽象画模式设置出现错误,请联系Xray Bot管理员。")

@set_abstract_off.handle()
async def _(event: GroupMessageEvent):
    group_id = event.group_id
    user_id = event.get_user_id()
    if userdata.setUserConfig(user_id,group_id,"is_abstract",False):
        await set_abstract_off.send("已关闭抽象画模式。")
    else:
        await set_abstract_off.send("抽象画模式设置出现错误,请联系Xray Bot管理员。")

@set_plate.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    user_id = event.get_user_id()
    plate_id = str(args).strip()
    group_id = event.group_id
    if plate_id == "":
        userdata.setUserConfig(user_id,group_id,"plate","")
        await set_plate.finish("姓名框清除成功。")

    plate_id = plate_id.zfill(6) if is_int(plate_id) else plate_id
    
    path = PLATE_PATH + f"/UI_Plate_{plate_id}.png"
    custom_plate_path = CUSTOM_PLATE_PATH + f"/UI_Plate_{plate_id}.png"
    File = Path(path)
    custom_file = Path(custom_plate_path)
    logger.success(path)
    logger.success(custom_plate_path)
    if File.exists() and File.is_file():
        if userdata.setUserConfig(user_id,group_id,"plate",plate_id):
            await set_plate.send("姓名框设置成功。")
        else:
            await set_plate.send("姓名框设置出现错误,请联系Xray Bot管理员。")
    elif custom_file.exists() and custom_file.is_file():
        if userdata.setUserConfig(user_id,group_id,"plate",f"custom_plate{plate_id}"):
            await set_plate.send("姓名框设置成功。")
        else:
            await set_plate.send("姓名框设置出现错误,请联系Xray Bot管理员。")
    else:
        await set_plate.send("姓名框ID错误,请检查ID后重新设置。")

@set_frame.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    user_id = event.get_user_id()
    frame_id = str(args).strip()
    group_id = event.group_id

    frame_id = frame_id.zfill(6)

    path = FRAME_PATH + f"/UI_Frame_{frame_id}.png"
    File = Path(path)
    if File.exists() and File.is_file():
        if userdata.setUserConfig(user_id,group_id,"frame",frame_id):
            await set_frame.send("背景设置成功。")
        else:
            await set_frame.send("背景设置出现错误,请联系Xray Bot管理员。")
    else:
        await set_frame.send("背景ID错误,请检查ID后重新设置。")

@set_icon.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    user_id = event.get_user_id()
    icon_id = str(args).strip()
    group_id = event.group_id

    icon_id = icon_id.zfill(6)


    path = ICON_PATH + f"/UI_Icon_{icon_id}.png"
    File = Path(path)
    if File.exists() and File.is_file():
        if userdata.setUserConfig(user_id,group_id,'icon',icon_id):
            await set_icon.send("头像设置成功。")
        else:
            await set_icon.send("头像设置出现错误,请联系Xray Bot管理员。")
    else:
        await set_icon.send("头像ID错误,请检查ID后重新设置。")

        
@set_best30_mode.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    group_id = event.group_id
    user_id = event.get_user_id()
    style_arg = str(args).strip()
    if style_arg in ["水鱼","落雪"]:
        if userdata.setUserConfig(user_id,group_id,"best30_mode",style_arg):
            await set_best30_mode.send("Best30模式设置成功。")
        else:
            await set_best30_mode.send("Best30模式设置出现错误,请联系Xray Bot管理员。")
    else:
        await set_best30_mode.send("Best30模式样式目前只有【落雪】、【水鱼】请检查主题ID正确。")
