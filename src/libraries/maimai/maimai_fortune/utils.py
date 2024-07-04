import datetime
import time
from src.libraries.maimai.maimaidx_music import *
from src.libraries.image_handle.image import *
from src.libraries.GLOBAL_CONSTANT import FORTUNE_LIST
from .maimai_fortune import generate_fortune


def gen_fortune(event):
    qq = str(event.user_id)
    qq = int(qq.replace('0', ''))
    DayTime = time.strftime("%m%d", time.localtime())
    h = qq * int(DayTime)
    rp = h % 100
    wm_value = []
    year = time.strftime("%Y", time.localtime())
    month = time.strftime("%m", time.localtime())
    day = time.strftime("%d", time.localtime())
    for i in range(11):
        wm_value.append(h & 3)
        h >>= 2
    s = f"🌈{DayTime}:幸运值🌟：{rp}！\n"
    should_list = []
    noshould_list = []
    for i in range(11):
        if wm_value[i] == 3:
            should_list.append(FORTUNE_LIST[i][0])
        elif wm_value[i] == 0:
            noshould_list.append(FORTUNE_LIST[i][0])
    week_list = ["星\n期\n一", "星\n期\n二", "星\n期\n三", "星\n期\n四", "星\n期\n五", "星\n期\n六", "星\n期\n日"]

    should = []
    noshould = []

    itemstr = ''
    index = 0
    for item in should_list:
        itemstr += item + ','
        index += 1
        if index == 3:
            index = 0
            should.append(itemstr[:-1])
            itemstr = ''

    if itemstr:
        should.append(itemstr[:-1])
        itemstr = ''
        index = 0

    if len(should) > 2:
        should = should[:2]
    elif len(should) == 0:
        should = ['无']

    for item in noshould_list:
        itemstr += item + ','
        index += 1
        if index == 3:
            index = 0
            noshould.append(itemstr[:-1])
            itemstr = ''

    if itemstr:
        noshould.append(itemstr[:-1])
        itemstr = ''
        index = 0

    if len(noshould) > 2:
        noshould = noshould[:2]
    elif len(noshould) == 0:
        noshould = ['无']

    week = week_list[datetime.datetime.today().weekday()]
    music = total_list[h % len(total_list)]
    img = generate_fortune(year, month, day, week, str(rp), should, noshould, music)
    return img