import aiohttp
import nonebot
from src.libraries.maimai.maimaidx_music import total_list
from typing import Dict, List
import re
from src.libraries.GLOBAL_CONSTANT import NOW_VERSION
# config = nonebot.get_driver().config
# DEVELOPER_TOKEN = config.developer_token
# config = nonebot.get_driver().config
DEVELOPER_TOKEN = "FVXMqKTE51fWsR42gSdNrume9IkwGHYn"

scoreRank = 'D C B BB BBB A AA AAA S S+ SS SS+ SSS SSS+'.split(' ')
combo = ' FC FC+ AP AP+'.split(' ')
diffs = 'Basic Advanced Expert Master Re:Master'.split(' ')
comb = ' fc fcp ap app'.split(' ')
isfs = ' fs fsp fsd fsdp'.split(' ')
whatscore = 'd c b bb bbb a aa aaa s s+ ss ss+ sss sss+'.split(' ')


class ChartInfo(object):
    def __init__(self, idNum: str, diff: int, tp: str, achievement: float, ra: int, comboId: int, scoreId: int,
                 title: str, ds: float, lv: str, fs: int, dxscore: int):
        self.idNum = idNum
        self.diff = diff
        self.tp = tp
        self.achievement = achievement
        self.dxscore = dxscore
        if achievement >= 100.5:
          self.ra = int(ds * 22.4 * 100.5 / 100)
        elif achievement >= 100:
          self.ra = int(ds * 21.6 * achievement / 100)
        elif achievement >= 99.5:
          self.ra = int(ds * 21.1 * achievement / 100)
        elif achievement >= 99:
          self.ra = int(ds * 20.8 * achievement / 100)
        elif achievement >= 98:
          self.ra = int(ds * 20.3 * achievement / 100)
        elif achievement >= 97:
          self.ra = int(ds * 20 * achievement / 100)
        elif achievement >= 94:
          self.ra = int(ds * 16.8 * achievement / 100)
        elif achievement >= 90:
          self.ra = int(ds * 15.2 * achievement / 100)
        elif achievement >= 80:
          self.ra = int(ds * 13.6 * achievement / 100)
        elif achievement >= 75:
          self.ra = int(ds * 12.0 * achievement / 100)
        elif achievement >= 70:
          self.ra = int(ds * 11.2 * achievement / 100)
        elif achievement >= 60:
          self.ra = int(ds * 9.6 * achievement / 100)
        elif achievement >= 50:
          self.ra = int(ds * 8 * achievement / 100)
        else:
          self.ra = 0
        self.comboId = comboId
        self.scoreId = scoreId
        self.title = title
        self.ds = ds
        self.lv = lv
        self.fs = fs

    def __str__(self):
        return '%-50s' % f'{self.title} [{self.tp}]' + f'{self.ds}\t{diffs[self.diff]}\t{self.ra}'

    def __eq__(self, other):
        return self.ra == other.ra

    def __lt__(self, other):
        return self.ra < other.ra

    @classmethod
    def sp_from_json(cls, data):
        rate = ['d', 'c', 'b', 'bb', 'bbb', 'a', 'aa',
            'aaa', 's', 'sp', 'ss', 'ssp', 'sss', 'sssp']
        ri = rate.index(data["rate"])
        fc = ['', 'fc', 'fcp', 'ap', 'app']
        fi = fc.index(data["fc"])
        fs = ['', 'fs', 'fsp', 'fsd', 'fsdp']
        fsi = fs.index(data['fs'])
        # idNum=total_list.by_title(data["title"]).id,

        return cls(
            idNum=data['song_id'],
            title=data["title"],
            diff=data["level_index"],
            ra=data["ra"],
            ds=data["ds"],
            comboId=fi,
            scoreId=ri,
            lv=data["level"],
            achievement=data["achievements"],
            tp=data["type"],
            fs=fsi,
            dxscore=data["dxScore"]
        )

    @classmethod
    def from_json(cls, data):
        rate = ['d', 'c', 'b', 'bb', 'bbb', 'a', 'aa',
            'aaa', 's', 'sp', 'ss', 'ssp', 'sss', 'sssp']
        ri = rate.index(data["rate"])
        fc = ['', 'fc', 'fcp', 'ap', 'app']
        fi = fc.index(data["fc"])
        fs = ['', 'fs', 'fsp', 'fsd', 'fsdp']
        try:
          fsi = fs.index(data['fs'])
        except:
          fsi = 0
        # idNum=total_list.by_title(data["title"]).id,

        return cls(
            idNum=str(data['song_id']),
            title=data["title"],
            diff=data["level_index"],
            ra=data["ra"],
            ds=data["ds"],
            comboId=fi,
            scoreId=ri,
            lv=data["level"],
            achievement=data["achievements"],
            tp=data["type"],
            fs=fsi,
            dxscore=data["dxScore"]
        )


class BestList(object):

    def __init__(self, size: int):
        self.data = []
        self.size = size

    def push(self, elem: ChartInfo):
        if len(self.data) >= self.size and elem < self.data[-1]:
            return
        self.data.append(elem)
        self.data.sort()
        self.data.reverse()
        while (len(self.data) > self.size):
            del self.data[-1]

    def pop(self):
        del self.data[-1]

    def __str__(self):
        return '[\n\t' + ', \n\t'.join([str(ci) for ci in self.data]) + '\n]'

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


def filter_all_perfect_records(records):
    b15_all_perfect_records = []
    b35_all_perfect_records = []
    for item in records:
      if item['fc'] in ['ap', 'app']:
        if total_list.by_id(str(item['song_id'])).cn_version == NOW_VERSION:
            b15_all_perfect_records.append(item)
        else:
            b35_all_perfect_records.append(item)

    b35_sorted_data = sorted(b35_all_perfect_records,
                             key=lambda x: x['ra'], reverse=True)
    b15_sorted_data = sorted(b15_all_perfect_records,
                             key=lambda x: x['ra'], reverse=True)
    return b35_sorted_data[:35], b15_sorted_data[:15]


def filter_full_combo_records(records):
    b15_full_combo_records = []
    b35_full_combo_records = []
    for item in records:
      if item['fc'] in ['fc', 'fcp','ap', 'app']:
        if total_list.by_id(str(item['song_id'])).cn_version == NOW_VERSION:
            b15_full_combo_records.append(item)
        else:
            b35_full_combo_records.append(item)

    b35_sorted_data = sorted(b35_full_combo_records,
                             key=lambda x: x['ra'], reverse=True)
    b15_sorted_data = sorted(b15_full_combo_records,
                             key=lambda x: x['ra'], reverse=True)
    return b35_sorted_data[:35], b15_sorted_data[:15]


def filter_full_combo_plus_records(records):
    b15_full_combo_records = []
    b35_full_combo_records = []
    for item in records:
      if item['fc'] in ['fcp','ap', 'app']:
        if total_list.by_id(str(item['song_id'])).cn_version == NOW_VERSION:
            b15_full_combo_records.append(item)
        else:
            b35_full_combo_records.append(item)

    b35_sorted_data = sorted(b35_full_combo_records,
                             key=lambda x: x['ra'], reverse=True)
    b15_sorted_data = sorted(b15_full_combo_records,
                             key=lambda x: x['ra'], reverse=True)
    return b35_sorted_data[:35], b15_sorted_data[:15]



def filter_best_35_records(records):
    b15_all_perfect_records = []
    b35_all_perfect_records = []
    for item in records:
      achievement = item['achievements']
      ds = total_list.by_id(str(item['song_id'])).ds[item['level_index']]
      if achievement >= 100.5:
        ra = int(ds * 22.4 * 100.5 / 100)
      elif achievement >= 100:
        ra = int(ds * 21.6 * achievement / 100)
      elif achievement >= 99.5:
        ra = int(ds * 21.1 * achievement / 100)
      elif achievement >= 99:
        ra = int(ds * 20.8 * achievement / 100)
      elif achievement >= 98:
        ra = int(ds * 20.3 * achievement / 100)
      elif achievement >= 97:
        ra = int(ds * 20 * achievement / 100)
      elif achievement >= 94:
        ra = int(ds * 16.8 * achievement / 100)
      elif achievement >= 90:
        ra = int(ds * 15.2 * achievement / 100)
      elif achievement >= 80:
        ra = int(ds * 13.6 * achievement / 100)
      elif achievement >= 75:
        ra = int(ds * 12.0 * achievement / 100)
      elif achievement >= 70:
        ra = int(ds * 11.2 * achievement / 100)
      elif achievement >= 60:
        ra = int(ds * 9.6 * achievement / 100)
      elif achievement >= 50:
        ra = int(ds * 8 * achievement / 100)
      else:
        ra = 0
      item['ra'] = ra
      item['ds'] = ds
      b35_all_perfect_records.append(item)

    b35_sorted_data = sorted(b35_all_perfect_records,
                             key=lambda x: x['ra'], reverse=True)
    b15_sorted_data = sorted(b15_all_perfect_records,
                             key=lambda x: x['ra'], reverse=True)
    return b35_sorted_data[:35], b15_sorted_data[:15]


def filter_all_records(records):
    all_records = []
    for item in records:
      all_records.append(item)

    all_sorted_data = sorted(all_records, key=lambda x: x['ra'], reverse=True)
    return all_sorted_data[:50], []

def filter_level_best_35_records(records,_level):
    b15_records = []
    b35_records = []
    for item in records:
      music_info = total_list.by_id(str(item['song_id']))
      if music_info.level[item['level_index']]==_level:
        if music_info.cn_version == NOW_VERSION:
          b15_records.append(item)
        else:
          b35_records.append(item)

    b35_sorted_data = sorted(b35_records,
                             key=lambda x: x['ra'], reverse=True)
    b15_sorted_data = sorted(b15_records,
                             key=lambda x: x['ra'], reverse=True)
    return b35_sorted_data[:35], b15_sorted_data[:15]


def filter_c_best_35_records(records):
    b15_records = []
    b35_records = []
    for item in records:
      achievement = item['achievements']

      if 96.9800 < achievement < 97 or 98.9800 < achievement < 99 or 99.4800 < achievement < 99.5 or 99.9800 < achievement < 100 or 100.4800 < achievement < 100.5:
        music_info = total_list.by_id(str(item['song_id']))
        if music_info.cn_version == NOW_VERSION:
          b15_records.append(item)
        else:
          b35_records.append(item)

    b35_sorted_data = sorted(b35_records,
                             key=lambda x: x['ra'], reverse=True)
    b15_sorted_data = sorted(b15_records,
                             key=lambda x: x['ra'], reverse=True)
    return b35_sorted_data[:35], b15_sorted_data[:15]

def filter_m_best_35_records(records):
    b15_records = []
    b35_records = []
    for item in records:
      achievement = item['achievements']

      if 100 <= achievement <= 100.0100 or 100.5 <= achievement <= 100.5100:
        music_info = total_list.by_id(str(item['song_id']))
        if music_info.cn_version == NOW_VERSION:
          b15_records.append(item)
        else:
          b35_records.append(item)

    b35_sorted_data = sorted(b35_records,
                             key=lambda x: x['ra'], reverse=True)
    b15_sorted_data = sorted(b15_records,
                             key=lambda x: x['ra'], reverse=True)
    return b35_sorted_data[:35], b15_sorted_data[:15]

async def get_user_all_records(payload):
    headers = {
       "developer-token": DEVELOPER_TOKEN
    }
    async with aiohttp.request("GET", "https://www.diving-fish.com/api/maimaidxprober/dev/player/records", params=payload, headers=headers) as resp:
        request_json = await resp.json()
        return resp.status, request_json
    
filter_map = {
  "all":filter_all_records,
  "a":filter_all_records,
  "2024":filter_best_35_records,
  "ap":filter_all_perfect_records,
  "fc":filter_full_combo_records,
  "fc+":filter_full_combo_plus_records,
  "寸":filter_c_best_35_records,
  "c":filter_c_best_35_records,
  "名刀":filter_m_best_35_records
}

async def get_best_50_data(payload, filter_mode):
  if filter_mode is None:
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
      obj = await resp.json()
      if resp.status == 400:
          return resp.status, obj, None, None, None, None
      if resp.status == 403:
          return resp.status, obj, None, None, None, None
      sd_best = BestList(35)
      dx_best = BestList(15)
      dx: List[Dict] = obj["charts"]["dx"]
      sd: List[Dict] = obj["charts"]["sd"]
      for c in sd:
          sd_best.push(ChartInfo.from_json(c))
      for c in dx:
          dx_best.push(ChartInfo.from_json(c))
      return resp.status, obj, sd, dx, sd_best, dx_best
  else:
    status,request_json = await get_user_all_records(payload)
    if status == 400:
      return status,request_json, None, None, None, None
    records = request_json['records']

    regex = r'(\d+)(\+)?'
    match = re.match(regex, filter_mode)
    if match:
      level,is_plus = match.groups()
      if 1 <= int(level) <= 15:
        if is_plus =="+":
           level = level+"+"
        best35_record,best15_records = filter_level_best_35_records(records,level)
      else:
        filter_fun = filter_map[filter_mode]
        best35_record,best15_records = filter_fun(records)
    else:
      filter_fun = filter_map[filter_mode]
      best35_record,best15_records = filter_fun(records)
    sd_best = BestList(50)
    dx_best = BestList(50)
    for c in best35_record:
        sd_best.push(ChartInfo.from_json(c))
    for c in best15_records:
        dx_best.push(ChartInfo.from_json(c))
    return status,request_json, best35_record, best15_records, sd_best, dx_best