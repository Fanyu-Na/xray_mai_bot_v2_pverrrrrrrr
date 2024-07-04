import json
import random
from typing import Dict, List, Optional, Union, Tuple, Any
from copy import deepcopy
from src.libraries.GLOBAL_CONSTANT import VERSION_EZ_MAP,DELETED_MUSIC
from src.libraries.GLOBAL_PATH import DATA_MAIMAI_PATH,CHN_MUSIC_DATA_URL
from src.libraries.data_handle.abstract_db_handle import abstract
import requests


def cross(checker: List[Any], elem: Optional[Union[Any, List[Any]]], diff):
    ret = False
    diff_ret = []
    if not elem or elem is Ellipsis:
        return True, diff
    if isinstance(elem, List):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if __e in elem:
                diff_ret.append(_j)
                ret = True
    elif isinstance(elem, Tuple):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem[0] <= __e <= elem[1]:
                diff_ret.append(_j)
                ret = True
    else:
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem == __e:
                return True, [_j]
    return ret, diff_ret


def in_or_equal(checker: Any, elem: Optional[Union[Any, List[Any]]]):
    if elem is Ellipsis:
        return True
    if isinstance(elem, List):
        return checker in elem
    elif isinstance(elem, Tuple):
        return elem[0] <= checker <= elem[1]
    else:
        return checker == elem


class Chart(Dict):
    tap: Optional[int] = None
    slide: Optional[int] = None
    hold: Optional[int] = None
    touch: Optional[int] = None
    brk: Optional[int] = None
    charter: Optional[int] = None

    def __getattribute__(self, item):
        if item == 'tap':
            return self['notes'][0]
        elif item == 'hold':
            return self['notes'][1]
        elif item == 'slide':
            return self['notes'][2]
        elif item == 'touch':
            return self['notes'][3] if len(self['notes']) == 5 else 0
        elif item == 'brk':
            return self['notes'][-1]
        elif item == 'charter':
            return self['charter']
        return super().__getattribute__(item)


class Music(Dict):
    id: Optional[str] = None
    title: Optional[str] = None
    ds: Optional[List[float]] = None
    level: Optional[List[str]] = None
    genre: Optional[str] = None
    type: Optional[str] = None
    bpm: Optional[float] = None
    version: Optional[str] = None
    charts: Optional[Chart] = None
    release_date: Optional[str] = None
    artist: Optional[str] = None
    cn_version : Optional[str] = None
    ez_version : Optional[str] = None

    diff: List[int] = []

    def __getattribute__(self, item):
        if item in {'genre', 'artist', 'release_date', 'bpm', 'version','cn_version','ez_version'}:
            if item == 'version':
                return self['basic_info']['from']
            if item == 'cn_version':
                return self['basic_info']['cn_from']
            if item == 'ez_version':
                return self['basic_info']['ez_from']
            return self['basic_info'][item]
        elif item in self:
            return self[item]
        return super().__getattribute__(item)



class MusicList(List[Music]):
    def by_version_for_plate(self,music_version) -> Optional[Music]:
        musiclist = []
        for music in self:
            if int(music.id) in DELETED_MUSIC:
                continue
            if music.version in music_version:
                musiclist.append(music)
        return musiclist
    
    def by_versions_for_cn(self,music_version) -> Optional[Music]:
        musiclist = []
        for music in self:
            if int(music.id) in DELETED_MUSIC:
                continue
            if music.cn_version in music_version:
                musiclist.append(music)
        return musiclist
    
    def by_id(self, music_id: str) -> Optional[Music]:
        for music in self:
            if music.id == music_id:
                return music
        return None

    def by_title(self, music_title: str) -> Optional[Music]:
        for music in self:
            if music.title == music_title:
                return music
        return None

    def by_version(self,music_version: str) -> Optional[Music]:

        for music in self:
            # print(music.version)
            if music.version == music_version:
                return music
        return None


    def get_version_music(self,music_version: str):
        new_list = MusicList()
        for music in self:
            # print(music_version,music_version)
            if music.version == music_version:
                new_list.append(music)
        return new_list
    
    def get_othversion_music(self,music_version: str):
        new_list = MusicList()
        for music in self:
            # print(music_version,music_version)
            if music.version != music_version:
                new_list.append(music)
        return new_list

    def random(self):
        return random.choice(self)
    
    def random_no_eng(self):
        while True:
            music = random.choice(self)
            need_continue = False
            for c in music.title:
                if c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    need_continue = True
                    break
            if need_continue:continue
            break
        return music
        
    def level_unfinish_filter(self,level):
        new_list = MusicList()
        for music in self:
            # print(music.level)
            if level in music.level:
                new_list.append(music)
        return new_list

    def filter(self,
               *,
               level: Optional[Union[str, List[str]]] = ...,
               ds: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
               title_search: Optional[str] = ...,
               genre: Optional[Union[str, List[str]]] = ...,
               bpm: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
               type: Optional[Union[str, List[str]]] = ...,
               diff: List[int] = ...,
               ):
        new_list = MusicList()
        for music in self:
            diff2 = diff
            music = deepcopy(music)
            ret, diff2 = cross(music.level, level, diff2)
            if not ret:
                continue
            ret, diff2 = cross(music.ds, ds, diff2)
            if not ret:
                continue
            if not in_or_equal(music.genre, genre):
                continue
            if not in_or_equal(music.type, type):
                continue
            if not in_or_equal(music.bpm, bpm):
                continue
            if title_search is not Ellipsis and title_search.lower() not in music.title.lower():
                continue
            # if not music.version == ver:
            #     continue
            music.diff = diff2
            new_list.append(music)
        return new_list



obj = requests.get(CHN_MUSIC_DATA_URL).json()

for item in obj:
    if item['basic_info']['from'] == "maimai でらっくす":
        item['basic_info']['cn_from'] = "舞萌DX"
    elif item['basic_info']['from'] == "maimai でらっくす Splash":
        item['basic_info']['cn_from'] = "舞萌DX 2021"
    elif item['basic_info']['from'] == "maimai でらっくす UNiVERSE":
        item['basic_info']['cn_from'] = "舞萌DX 2022"
    elif item['basic_info']['from'] == "maimai でらっくす FESTiVAL":
        item['basic_info']['cn_from'] = "舞萌DX 2023"
    elif item['basic_info']['from'] == "maimai でらっくす BUDDiES":
        item['basic_info']['cn_from'] = "舞萌DX 2024"
    else:
        item['basic_info']['cn_from'] = item['basic_info']['from']

    if item['basic_info']['cn_from'] == 'maimai':
        item['basic_info']['ez_from'] = 'maimai'
    else:
        ez_ver = str(item['basic_info']['cn_from']).replace("maimai ","")
        item['basic_info']['ez_from'] = f"{ez_ver}({VERSION_EZ_MAP.get(ez_ver,ez_ver)})"
    
    

    if item['basic_info']['genre'] in ['舞萌','maimai']:
        item['basic_info']['genre'] = '舞萌痴'
    if item['basic_info']['genre'] in ['POPSアニメ','流行&动漫']:
        item['basic_info']['genre'] = '现充&二次元'
    if item['basic_info']['genre'] in ['音击&中二节奏','オンゲキCHUNITHM']:
        item['basic_info']['genre'] = '幼击&除你祖母'
    if item['basic_info']['genre'] in ['niconico & VOCALOID','niconicoボーカロイド']:
        item['basic_info']['genre'] = '术&力&口'
    if item['basic_info']['genre'] in ['東方Project','东方Project']:
        item['basic_info']['genre'] = '车万Project'
    if item['basic_info']['genre'] in ['其他游戏','ゲームバラエティ']:
        item['basic_info']['genre'] = '骑她游嘻'
    



total_list: MusicList = MusicList(obj)

for __i in range(len(total_list)):
    total_list[__i] = Music(total_list[__i])
    for __j in range(len(total_list[__i].charts)):
        total_list[__i].charts[__j] = Chart(total_list[__i].charts[__j])


demolist = abstract.get_abstract_id_list()
unfinishobj = []
for item in obj:
    try:
        if int(item['id']) not in demolist:
            unfinishobj.append(item)
    except:
        pass

unfinish_list: MusicList = MusicList(unfinishobj)
for __i in range(len(unfinish_list)):
    unfinish_list[__i] = Music(unfinish_list[__i])
    for __j in range(len(unfinish_list[__i].charts)):
        unfinish_list[__i].charts[__j] = Chart(unfinish_list[__i].charts[__j])