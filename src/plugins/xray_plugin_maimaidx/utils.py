from src.libraries.maimai.maimaidx_music import total_list,Music
from src.libraries.image_handle.image import image_to_base64
from nonebot.adapters.onebot.v11 import MessageSegment
from src.libraries.maimai.maimai_music_data.maimai_music_data import MaiMusicData
import requests
import aiohttp
import json
from src.libraries.GLOBAL_PATH import MAIDX_LOCATION_PATH
from src.libraries.GLOBAL_CONSTANT import VERSION_MAP,VERSION_DF_MAP
import operator

def inner_level_q(ds1, ds2=None):
    result_set = []
    diff_label = ['Bas', 'Adv', 'Exp', 'Mst', 'ReM']
    if ds2 is not None:
        music_data = total_list.filter(ds=(ds1, ds2))
    else:
        music_data = total_list.filter(ds=ds1)
    for music in music_data:
        for i in music.diff:
            result_set.append(
                (music['id'], music['title'], music['ds'][i], diff_label[i], music['level'][i]))
    return result_set


def music_image(music: Music, is_abstract: bool):
    musicDataImg = MaiMusicData(music.id, is_abstract).draw()
    return [MessageSegment.image(f"base64://{str(image_to_base64(musicDataImg), encoding='utf-8')}")]

def query_PANDORA_PARADOXXX_score_content(qq):
    payload = {'qq': qq, 'version': ["maimai FiNALE"]}
    r = requests.post("https://www.diving-fish.com/api/maimaidxprober/query/plate", json=payload)
    verlist = r.json()
    song_Info_list = {}
    for item in verlist['verlist']:
        if item['id'] == 834:
            song_Info_list[item['level_index']] = item
    bas_ach = song_Info_list.get(0, {'achievements': -1}).get('achievements', -1)
    adv_ach = song_Info_list.get(1, {'achievements': -1}).get('achievements', -1)
    ex_ach = song_Info_list.get(2, {'achievements': -1}).get('achievements', -1)
    mas_ach = song_Info_list.get(3, {'achievements': -1}).get('achievements', -1)
    remas_ach = song_Info_list.get(4, {'achievements': -1}).get('achievements', -1)
    msg = '你好\n'

    if bas_ach == -1:
        msg += f'你的绿潘成绩:未游玩\n'
    else:
        msg += f'你的绿潘成绩是:{bas_ach}\n'

    if adv_ach == -1:
        msg += f'你的黄潘成绩:未游玩\n'
    else:
        msg += f'你的黄潘成绩是:{adv_ach}\n'

    if ex_ach == -1:
        msg += f'你的红潘成绩:未游玩\n'
    else:
        msg += f'你的红潘成绩是:{ex_ach}\n'

    if mas_ach == -1:
        msg += f'你的紫潘成绩:未游玩\n'
    else:
        msg += f'你的紫潘成绩是:{mas_ach}\n'

    if remas_ach == -1:
        msg += f'你的白潘成绩:未游玩\n'
    else:
        msg += f'你的白潘成绩是:{remas_ach}\n'
    if len(msg) > 5:
        return msg
    else:
        return 0

async def get_maidx_location():
    async with aiohttp.request('GET', 'http://wc.wahlap.net/maidx/rest/location') as resp:
        AddressData = await resp.json()
        return AddressData
    
def read_location_json():
    data = open(MAIDX_LOCATION_PATH, encoding='utf-8')
    strJson = json.load(data)
    return strJson


def findsong_byid(id,index,list):
    for item in list:
        if item["id"] == id and item['level_index'] == index:
            return item
    return None

def query_user_version_plate_schedule_result(version, qq: str, plateType: str, vername: str):
    version_list = total_list.by_versions_for_cn(VERSION_MAP[version])
    version_id_list = []
    for song in version_list:
        version_id_list.append(int(song['id']))

    payload = {'qq': qq, 'version': VERSION_DF_MAP[version]}
    r = requests.post("https://www.diving-fish.com/api/maimaidxprober/query/plate", json=payload)
    finishs = r.json()
    unfinishList = {0: [], 1: [], 2: [], 3: [], 4: []}

    for song in version_list:
        songid = int(song['id'])
        for index in range(len(song['level'])):
            song_result = findsong_byid(songid, index, finishs['verlist'])
            if song_result:
                if plateType == '将':
                    if song_result['achievements'] < 100:
                        unfinishList[index].append(song_result)
                elif plateType == '极':
                    if song_result['fc'] not in ['fc', 'ap', 'fcp', 'app']:
                        unfinishList[index].append(song_result)
                elif plateType == '神':
                    if song_result['fc'] not in ['ap', 'app']:
                        unfinishList[index].append(song_result)
                elif plateType == '舞舞':
                    if song_result['fs'] not in ['fsd', 'fsdp']:
                        unfinishList[index].append(song_result)
                elif plateType == '者':
                    if song_result['achievements'] < 80:
                        unfinishList[index].append(song_result)
            else:
                unfinishList[index].append(song)

    # 高难度铺面
    HardSong = ''
    for item in unfinishList[3]:
        if item.get('achievements', -1) >= 0:
            # print(item['level'],1,type(item['level']))
            if item['level'] in ['13+', '14', '14+', '15']:
                socre = str(item['achievements'])
                HardSong += '    ' + str(item['id']) + '.' + item['title'] + '(' + item['level'] + ')   ' + socre + '\n'
        else:
            # print(item['level'],2)
            if item['level'][3] in ['13+', '14', '14+', '15']:
                socre = '未游玩'
                HardSong += ' ' + str(item['id']) + '.' + item['title'] + '(' + item['level'][3] + ')   ' + socre + '\n'
    if vername in ['舞', '霸']:
        for item in unfinishList[4]:
            if item.get('achievements', -1) >= 0:
                # print(item['level'],1,type(item['level']))
                if item['level'] in ['13+', '14', '14+', '15']:
                    socre = str(item['achievements'])
                    HardSong += '    ' + str(item['id']) + '.' + item['title'] + '(' + item[
                        'level'] + ')   ' + socre + '\n'
            else:
                # print(item['level'],2)
                if item['level'][3] in ['13+', '14', '14+', '15']:
                    socre = '未游玩'
                    HardSong += ' ' + str(item['id']) + '.' + item['title'] + '(' + item['level'][
                        3] + ')   ' + socre + '\n'
    t = vername + plateType
    SendMsg = f'你的{t}剩余进度如下：\n'
    unfinishSongCount = len(unfinishList[0]) + len(unfinishList[1]) + len(unfinishList[2]) + len(
        unfinishList[3]) if vername not in ['舞', '者'] else len(unfinishList[0]) + len(unfinishList[1]) + len(
        unfinishList[2]) + len(unfinishList[3]) + len(unfinishList[4])
    unfinishGCount = len(unfinishList[0])
    unfinishYCount = len(unfinishList[1])
    unfinishRCount = len(unfinishList[2])
    unfinishPCount = len(unfinishList[3])
    unfinishREPCount = len(unfinishList[4])
    if unfinishSongCount == 0:
        return f'您的{t}进度已经全部完成!!!\n'
    if unfinishGCount == 0:
        SendMsg += 'Basic难度已经全部完成\n'
    else:
        SendMsg += f'Basic剩余{str(unfinishGCount)}首\n'
    if unfinishYCount == 0:
        SendMsg += 'Advanced难度已经全部完成\n'
    else:
        SendMsg += f'Advanced剩余{str(unfinishYCount)}首\n'
    if unfinishRCount == 0:
        SendMsg += 'Expert难度已经全部完成\n'
    else:
        SendMsg += f'Expert剩余{str(unfinishRCount)}首\n'
    if unfinishPCount == 0:
        SendMsg += f'Master难度已经全部完成\n你已经{t}确认了!!!!\n'
    else:
        SendMsg += f'Master剩余{str(unfinishPCount)}首\n'
    if vername in ['舞', '霸']:
        if unfinishREPCount == 0:
            SendMsg += f'Re_Master难度已经全部完成\n你已经{t}确认了!!!!\n'
        else:
            SendMsg += f'Re_Master剩余{str(unfinishREPCount)}首\n'
    SendMsg += f'总共剩余{str(unfinishSongCount)}首\n'
    # print(unfinishRCount,unfinishPCount)
    if (unfinishRCount != 0 or unfinishPCount != 0) and vername not in ["舞", "霸"]:
        # print('Join')
        SendMsg += '未完成高难度谱面还剩下\n'
        SendMsg += HardSong[0:-1]
    lxzt = (unfinishSongCount // 4) + 1 if unfinishSongCount % 4 != 0 else unfinishSongCount // 4
    dszt = (unfinishSongCount // 3) + 1 if unfinishSongCount % 3 != 0 else unfinishSongCount // 3
    if plateType == "舞舞":
        SendMsg += f'\n单刷需要{str(dszt)}批西'
    else:
        SendMsg += f'\n贫瘠状态下需要{str(lxzt)}批西,单刷需要{str(dszt)}批西'
    SendMsg += '\n加油嗷！！！'
    return SendMsg


async def getUsername(payload):
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player",
                               json=payload) as resp:
        if resp.status == 400:
            return 400
        elif resp.status == 403:
            return 403
        elif resp.status == 200:
            best_info_Dict = await resp.json()
            username = str(best_info_Dict['username'])
            return username
        else:
            return -1
        
async def getLowMsg(username: str, mode: int):
    async with aiohttp.request("get", 'https://www.diving-fish.com/api/maimaidxprober/rating_ranking') as resp:
        ranking_Dict = await resp.json()
        count = len(ranking_Dict)
        sum = 0
        top = -1
        ra = 0
        ranking_Dict = sorted(ranking_Dict, key=operator.itemgetter('ra'), reverse=True)
        if mode == 1:
            for index, item in enumerate(ranking_Dict):
                if str(item['username']).lower() == username:
                    top = index + 1
                    ra = item['ra']
                sum += item['ra']
        else:
            for index, item in enumerate(ranking_Dict):
                if item['username'] == username:
                    top = index + 1
                    ra = item['ra']
                sum += item['ra']
        if top == -1:
            return f'未找到{username},可能设置隐私。'
        avg = f'{sum / count:.4f}'
        topp = f'{((count - top) / count):.2%}'
        msg = f'{username}的底分为{ra}\nRating排名在{top}\n平均rating为{avg}\n你已经超越了{topp}的玩家。'
        return msg


async def query_user_top_result(userOrQq: str, mode: str):
    if mode == 'qq':
        payload = {'qq': userOrQq}
        username = await getUsername(payload)
        if username not in [400, 403, -1]:
            # print(username)
            return await getLowMsg(username, 0)
        elif username == 400:
            return '未找到此QQ'
        elif username == 403:
            return '此ID不允许查询'
        else:
            return '未知错误'
    else:
        return await getLowMsg(userOrQq.lower(), 1)