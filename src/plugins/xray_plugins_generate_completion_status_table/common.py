import nonebot
from nonebot import on_shell_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent,Bot,Message
from nonebot.params import CommandArg,ShellCommandArgs
from nonebot.log import logger
from src.libraries.GLOBAL_CONSTANT import VERSION_MAP
from nonebot.rule import ArgumentParser,Namespace
from src.libraries.maimai.completion_status_table.new_pcst_base_img import generate_full_version
from src.libraries.GLOBAL_RULE import check_is_bot_admin



nomal_switch_parser = ArgumentParser()
nomal_switch_parser.add_argument("version", metavar="version")
nomal_switch_parser.add_argument("-c", "--abstract", action='store_true')

generate_version_images = on_shell_command("更新版本完成表",rule=check_is_bot_admin, parser=nomal_switch_parser, priority=20)
@generate_version_images.handle()
async def _(bot: Bot, event: GroupMessageEvent,  foo: Namespace = ShellCommandArgs()):
    if str(foo.version) in VERSION_MAP.keys():
        # try:
        mode = "抽象" if foo.abstract else "正常"

        base_img = generate_full_version(foo.version,foo.abstract)
        if base_img is not None:
            await generate_version_images.send(f"{str(foo.version)}更新成功-{mode}")
        else:
            await generate_version_images.send(f"{str(foo.version)}更新失败-{mode},未找到版本:{str(foo.version)}")


        # if generate_version_image(foo.version,foo.abstract):
        #     await generate_version_images.send(f"{str(foo.version)}更新成功-{mode}")
        # else:
        #     await generate_version_images.send(f"{str(foo.version)}更新失败-{mode}")
    # except Exception as e:
        #     await generate_version_images.finish(str(e))
    else:
        await generate_version_images.finish("未找到版本"+str(foo.version))

