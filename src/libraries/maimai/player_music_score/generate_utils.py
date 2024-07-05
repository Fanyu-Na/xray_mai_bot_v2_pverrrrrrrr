import aiohttp
import requests
from src.libraries.maimai.maimaidx_music import total_list
from src.libraries.execution_time import timing_decorator_async
from src.libraries.GLOBAL_CONSTANT import DEVELOPER_TOKEN

def line_break(line,line_char_count:int,table_width:int):
    ret = ''
    width = 0
    for c in line:
        if len(c.encode('utf8')) == 3:  # 中文
            if line_char_count == width + 1:  # 剩余位置不够一个汉字
                width = 2
                ret += '\n' + c
            else: # 中文宽度加2，注意换行边界
                width += 2
                ret += c
        else:
            if c == '\t':
                space_c = table_width - width % table_width  # 已有长度对TABLE_WIDTH取余
                ret += ' ' * space_c
                width += space_c
            elif c == '\n':
                width = 0
                ret += c
            else:
                width += 1
                ret += c
        if width >= line_char_count:
            ret += '\n'
            width = 0
    if ret.endswith('\n'):
        return ret
    return ret + '\n'

# 辅助函数：分割文本以适应最大宽度  
def split_text_to_lines(text, max_width, font):  
    lines = []  
    current_line = ""  
    for char in text:  
        # 检查当前行的宽度加上新字符的宽度是否超过最大宽度  
        text_width, text_height = font.getsize(current_line + char)
        if text_width <= max_width:  
            current_line += char  
        else:  
            # 如果超过最大宽度，则将当前行添加到列表中，并开始新行  
            lines.append(current_line)  
            current_line = char  
    # 添加最后一行（如果有的话）  
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)

async def get_user_all_records(music_id:str,qq:str = None,username:str = None):
    payload = get_request_payload(qq=qq,username=username)
    if payload == 400:
        return 40
    payload['music_id'] = [music_id]
    headers = {
       "developer-token": DEVELOPER_TOKEN
    } 
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/dev/player/record", json=payload,headers=headers) as resp:
        request_json = await resp.json()
        return resp.status,request_json

def get_request_payload(qq:str = None,username:str = None):
    if qq is None and username is None:
        return 400
    else:
        if qq:
            payload = {"qq":qq}
        else:
            payload = {"username":username}
        return payload

@timing_decorator_async
async def get_user_music_score(music_id:int,qq:str = None,username:str = None):
    status_code,user_all_records = await get_user_all_records(str(music_id),qq=qq,username=username)
    if status_code!= 400:
        if str(music_id) in user_all_records:
        # filtered_data = [item for item in user_all_records['records'] if item['song_id'] == music_id]
            music_data = total_list.by_id(str(music_id))
            player_music_score = {index:{} for index,ds in enumerate(music_data.level)}
            # print(player_music_score)
            for item in user_all_records[str(music_id)]:
                player_music_score[item['level_index']] = item
            return player_music_score
        else:
            music_data = total_list.by_id(str(music_id))
            if len(music_data.level) < 4:
                player_music_score = {0:{},1:{},2:{},3:{}}
            else:
                player_music_score = {index:{} for index,ds in enumerate(music_data.level)}
            return player_music_score
    else:
        return 400
