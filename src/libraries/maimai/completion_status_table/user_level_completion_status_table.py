import requests
from PIL import Image, ImageDraw
import json
import requests
from typing import Dict, List, Optional
from src.libraries.GLOBAL_CONSTANT import ALL_VERSION_LIST
from src.libraries.GLOBAL_PATH import COMPLETION_STATUS_TABLE_PATH

def make_level_ds_jsonfile():
    with open(f"{COMPLETION_STATUS_TABLE_PATH}/level_ds_list.json", 'r', encoding='utf-8') as fw:
        level_ds_list = json.load(fw)

    return level_ds_list

level_ds_list = make_level_ds_jsonfile()

def makeImg(level_str,level_ds_list:Dict,is_abstract):
    sssp = Image.open(f"{COMPLETION_STATUS_TABLE_PATH}/sssp.png").convert('RGBA')
    sss = Image.open(f"{COMPLETION_STATUS_TABLE_PATH}/sss.png").convert('RGBA')
    ssp = Image.open(f"{COMPLETION_STATUS_TABLE_PATH}/ssp.png").convert('RGBA')
    ss = Image.open(f"{COMPLETION_STATUS_TABLE_PATH}/ss.png").convert('RGBA')
    sp = Image.open(f"{COMPLETION_STATUS_TABLE_PATH}/sp.png").convert('RGBA')
    s = Image.open(f"{COMPLETION_STATUS_TABLE_PATH}/s.png").convert('RGBA')
    tabel_mode = "难度完成表-抽象封面" if is_abstract else "难度完成表-标准封面"
    img = Image.open(f"{COMPLETION_STATUS_TABLE_PATH}/{tabel_mode}/{level_str}.png").convert('RGBA')

    ix = 150
    iy = 180

    for ds in level_ds_list: # 不同定数有多少首歌
        count = 0
        rcount = 0
        for music in level_ds_list[ds]:
            
            if not music.get('achievements',0):
                music['achievements'] = 0
            if music['achievements']>= 100.5:
                img.paste(sssp, (ix, iy), sssp)
            elif music['achievements']>= 100:
                img.paste(sss, (ix, iy), sss)
            elif music['achievements']>= 99.5:
                img.paste(ssp, (ix, iy), ssp)
            elif music['achievements']>= 99:
                img.paste(ss, (ix, iy), ss)
            elif music['achievements']>= 98:
                img.paste(sp, (ix, iy), sp)
            elif music['achievements']>= 97:
                img.paste(s, (ix, iy), s)

            count = count + 1
            rcount = rcount + 1
            ix = ix + 80
            # print(len(level_ds_list[ds]),rcount)
            if count == 15 and len(level_ds_list[ds]) != rcount:
                ix = 150
                iy = iy+85
                count = 0
        iy = iy + 100
        ix = 150
    return img
    # print(level_str)
    # img.save(f"level_finish/{level_str}.png")


def query_user_plate_data(QQ:str):
    payload = {'qq':QQ,'version':ALL_VERSION_LIST}
    r = requests.post("https://www.diving-fish.com/api/maimaidxprober/query/plate", json=payload)
    finishs = r.json()
    return finishs['verlist']

def generate_user_level_cst(level:str,QQ:str,is_abstract):
    user_music_data = query_user_plate_data(QQ)
    temp_level_ds_list = make_level_ds_jsonfile()
    level_music = temp_level_ds_list[level]
    for ds in level_music:
        for music in level_music[ds]:
            # print(music)
            for user_data in user_music_data:
                if str(user_data['id']) == music['song_id'] and user_data['level_index'] == music['level_index']:
                    music['achievements'] = user_data['achievements']
    return makeImg(level,level_music,is_abstract)
