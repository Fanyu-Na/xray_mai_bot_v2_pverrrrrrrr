from nonebot.adapters.onebot.v11 import GroupRequestEvent,Bot,RequestEvent
from nonebot.plugin import on_request
from src.libraries.data_handle.alias_db_handle import alias
from src.libraries.maimai.maimaidx_music import total_list
from src.libraries.GLOBAL_CONSTANT import BOT_DATA_ADMINISTRATOR,AUTO_ACCEPT_GROUP_REQUEST

group_request = on_request()

@group_request.handle()
async def _(bot: Bot, event: RequestEvent):
    if isinstance(event,GroupRequestEvent):
        if event.group_id in AUTO_ACCEPT_GROUP_REQUEST:
            oname = event.comment.split('答案：')[1]
            result_set = alias.queryMusicByAlias(oname)
            if len(oname) >=6 :
                res = total_list.filter(title_search=oname)
            else:
                res = []
            if result_set or res:
                await bot.set_group_add_request(flag=event.flag,sub_type='add',approve=True)
            else:
                await group_request.finish()
                
    if event.sub_type == "invite":
        if event.user_id in BOT_DATA_ADMINISTRATOR:
            await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=True)