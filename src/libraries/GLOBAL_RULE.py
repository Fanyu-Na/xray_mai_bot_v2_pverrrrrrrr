
from src.libraries.GLOBAL_CONSTANT import BOT_DATA_STAFF,BOT_DATA_ADMINISTRATOR
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.rule import Rule

def check_is_bot_data_staff():
    async def _checker(event: GroupMessageEvent) -> bool:
        if event.user_id in BOT_DATA_STAFF:
            return True
        else:
            return False
    return Rule(_checker)

async def check_is_bot_admin(event: GroupMessageEvent) -> bool:
    return event.user_id in BOT_DATA_ADMINISTRATOR