from src.libraries.maimai.maimaidx_music import total_list
import requests
from PIL import Image, ImageDraw
from src.libraries.GLOBAL_CONSTANT import VERSION_MAP,VERSION_DF_MAP,DELETED_MUSIC
from src.libraries.GLOBAL_PATH import COMPLETION_STATUS_TABLE_PATH

def get_music_info(finishs,id:int,level:int):
    result = finishs['verlist']
    for item in result:
        if item['id'] == id and item['level_index'] == level:
            return {'fc':item['fc'],'fs':item['fs'],'achievements':item['achievements']}
    return {}


def query_user_plate_data(versions,user_id:str):
    version_list = total_list.by_version_for_plate(versions)
    payload = {'qq':user_id,'version':versions}
    r = requests.post("https://www.diving-fish.com/api/maimaidxprober/query/plate", json=payload)
    finishs = r.json()
    version_song_info = {}
    for song in version_list:
        version_song_info[song.id] = {}
        for index ,level in enumerate(song['level']):
            version_song_info[song.id][index] = get_music_info(finishs,int(song.id),index)
    return version_song_info

def generate_user_version_plate_cst(version:str,mode:str,QQ:str,is_abstract):
    result_list = total_list.by_versions_for_cn(VERSION_MAP[version])
    version_song_info = query_user_plate_data(VERSION_DF_MAP[version],QQ)
    default_song_list = {
        "15":[],
        "14+":[],
        "14":[],
        "13+":[],
        "13":[],
        "12+":[],
        "12":[],
        "11+":[],
        "11":[],
        "10+":[],
        "10":[],
        "9+":[],
        "9":[],
        "8+":[],
        "8":[],
        "7+":[],
        "7":[],
        "6":[],
        "5":[],
        "4":[],
        "3":[],
        "2":[],
        "1":[],
    }
    for song_info in result_list:
        if int(song_info.id) in DELETED_MUSIC:
            continue
        level= song_info.level[3]
        default_song_list[level].append(song_info.id)
    p = "版本牌子完成表-抽象封面" if is_abstract else "版本牌子完成表-标准封面"
    img = Image.open(f"{COMPLETION_STATUS_TABLE_PATH}/{p}/{version}.png").convert('RGBA')
    ji = Image.open(f"{COMPLETION_STATUS_TABLE_PATH}/极.png").convert('RGBA')
    jiang = Image.open(f"{COMPLETION_STATUS_TABLE_PATH}/将.png").convert('RGBA')
    shen = Image.open(f"{COMPLETION_STATUS_TABLE_PATH}/神.png").convert('RGBA')
    wu = Image.open(f"{COMPLETION_STATUS_TABLE_PATH}/舞舞.png").convert('RGBA')
    ix = 130
    iy = 120
    for item in default_song_list.items():
        if item[1]:
            count = 0
            rcount = 0
            for song in range(0,len(default_song_list[item[0]])):
                id = default_song_list[item[0]][song]

                if version_song_info[id][3]:
                    if mode == '将' and version_song_info[id][3]['achievements'] >= 100:
                        if version_song_info[id][3]['fc'] in ['ap','app']:
                            img.paste(shen, (ix, iy), shen)
                        else:
                            img.paste(jiang, (ix, iy), jiang)
                    elif mode == '极' and version_song_info[id][3]['fc'] in ['fc','ap','fcp','app']:
                        if version_song_info[id][3]['fc'] in ['ap','app']:
                            img.paste(shen, (ix, iy), shen)
                        else:
                            img.paste(ji, (ix, iy), ji)
                    elif mode == '神'and version_song_info[id][3]['fc'] in ['ap','app']:
                        img.paste(shen, (ix, iy), shen)
                    elif mode == '舞舞' and version_song_info[id][3]['fs'] in ['fsd','fsdp']:
                        img.paste(wu, (ix, iy), wu)
                    else:
                        pass
                count = count + 1
                rcount = rcount + 1
                ix = ix + 80
                if count == 10 and len(default_song_list[item[0]])!= rcount:
                    ix = 130
                    iy = iy+85
                    count = 0
            iy = iy + 100
            ix = 130
    return img