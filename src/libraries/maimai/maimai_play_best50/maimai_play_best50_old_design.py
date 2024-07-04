# Author: xyb, Diving_Fish
import asyncio,requests
import os,io
import math
from typing import Optional, Dict, List, Tuple
import random
from PIL import Image, ImageDraw, ImageFont
from src.libraries.maimai.maimaidx_music import total_list
from src.libraries.maimai.utils import get_cover_path
import asyncio
from pathlib import Path
import time
import aiohttp
from src.libraries.maimai.maimai_play_best50.maimai_recommend import Recommend
from src.libraries.GLOBAL_CONSTANT import MAIPLATE_FILE_ID_MAP
from src.libraries.maimai.maimai_play_best50.utils import get_best_50_data,get_user_all_records,filter_all_perfect_records,filter_best_35_records,filter_all_records,BestList,ChartInfo
import traceback
from src.libraries.GLOBAL_PATH import OLD_BEST_50_PATH,FRAME_PATH,PLATE_PATH,FONT_PATH,ICON_PATH

# scoreRank = 'D C B BB BBB A AA AAA S S+ SS SS+ SSS SSS+'.split(' ')
# combo = ' FC FC+ AP AP+'.split(' ')
# diffs = 'Basic Advanced Expert Master Re:Master'.split(' ')
# whatscore = 'd c b bb bbb a aa aaa s s+ ss ss+ sss sss+'.split(' ')



comb = ' fc fcp ap app'.split(' ')
isfs = ' fs fsp fsd fsdp'.split(' ')
level_index = 'BSC ADV EXP MST MST_Re'.split(' ')
rankPic = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')



class DrawBest(object):
    def __init__(self,is_abstract:bool,nickName:str,best35Rating,best15Rating,sdBest:BestList, dxBest:BestList,userConfig,best50_style_index:str):
        self.pic_dir = f'{OLD_BEST_50_PATH}/'
        self.frame_dir = f"{FRAME_PATH}/"
        self.plate_dir = f"{PLATE_PATH}/"
        self.icon_dir = f'{ICON_PATH}/'
        self.font_dir = f'{FONT_PATH}/'
        self.baseImg = Image.new("RGBA", (1920, 1700), (0, 0, 0, 0))
        self.is_abstract = is_abstract
        self.best35Rating = best35Rating
        self.best15Rating = best15Rating
        self.playerRating = best35Rating + best15Rating
        self.sdBest = sdBest
        self.dxBest = dxBest
        self.userConfig = userConfig
        self.userName = self._stringQ2B(nickName)



    def _Q2B(self, uchar):
        """单个字符 全角转半角"""
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xfee0
        if inside_code < 0x0020 or inside_code > 0x7e: # 转完之后不是半角字符返回原来的字符
            return uchar
        return chr(inside_code)

    def _stringQ2B(self, ustring):
        """把字符串全角转半角"""
        return "".join([self._Q2B(uchar) for uchar in ustring])


    def _get_dxscore_type(self,dxscorepen):
        if dxscorepen <= 90:
            return "star-1.png"
        elif dxscorepen <= 93:
            return "star-2.png"
        elif dxscorepen <= 95:
            return "star-3.png"        
        elif dxscorepen <= 97:
            return "star-4.png"        
        else:
            return "star-5.png"
        
    def _getCharWidth(self, o) -> int:
        widths = [
            (126, 1), (159, 0), (687, 1), (710, 0), (711, 1), (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
            (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1), (8426, 0), (9000, 1), (9002, 2), (11021, 1),
            (12350, 2), (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1), (55203, 2), (63743, 1),
            (64106, 2), (65039, 1), (65059, 0), (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
            (120831, 1), (262141, 2), (1114109, 1),
        ]
        if o == 0xe or o == 0xf:
            return 0
        for num, wid in widths:
            if o <= num:
                return wid
        return 1
        
    def _coloumWidth(self, s:str):
        res = 0
        for ch in s:
            res += self._getCharWidth(ord(ch))
        return res

    def _changeColumnWidth(self, s:str, len:int) -> str:
        res = 0
        sList = []
        for ch in s:
            res += self._getCharWidth(ord(ch))
            if res <= len:
                sList.append(ch)
        return ''.join(sList)
    
    
    def _findRaPic(self) -> str:
        num = '10'
        if self.playerRating >= 15000:
            num = '10'
        elif self.playerRating >= 14000:
            num = '09'
        elif self.playerRating >= 13000:
            num = '08'
        elif self.playerRating >= 12000:
            num = '07'
        elif self.playerRating >= 10000:
            num = '06'
        elif self.playerRating >= 7000:
            num = '05'
        elif self.playerRating >= 4000:
            num = '04'
        elif self.playerRating >= 2000:
            num = '03'
        elif self.playerRating >= 1000:
            num = '02'
        else:
            num = '01'
        return f'UI_CMN_DXRating_S_{num}.png'
    
    def _resizePic(self, img:Image.Image, time:float):
        return img.resize((int(img.size[0] * time), int(img.size[1] * time)))

    def _drawRating(self, ratingBaseImg:Image.Image):
        COLOUMS_RATING = [105, 122, 140, 158, 175]
        theRa = int(self.playerRating)
        i = 4
        while theRa:
            digit = theRa % 10
            theRa = theRa // 10
            digitImg = Image.open(self.pic_dir + f"Rating/UI_NUM_Drating_{digit}.png").convert('RGBA')
            digitImg = self._resizePic(digitImg, 0.6)
            ratingBaseImg.paste(digitImg, (COLOUMS_RATING[i], 12), mask=digitImg.split()[3])
            i = i - 1
        return ratingBaseImg

    def drawGenerateUserInfo(self):
        logoImage = Image.open(self.pic_dir + 'Logo.png').convert('RGBA')
        logoImage = logoImage.resize((432,208))
        self.baseImg.paste(logoImage,(-19,0), logoImage.split()[3])

        # 姓名框
        plate_id = str(self.userConfig.get('plate','000011'))
        if "custom_plate" in plate_id:
            plate_id = plate_id.split('custom_plate')[1]
            plateImage = Image.open(self.plate_dir + f"custom/UI_Plate_{plate_id}.png").convert('RGBA')
        else:
            plateImage = Image.open(self.plate_dir + f"UI_Plate_{plate_id}.png").convert('RGBA')
        
        plateImage = plateImage.resize((942, 152))
        self.baseImg.paste(plateImage,(390,36),plateImage)


        # 头像
        IconImg = Image.open(self.icon_dir + f"UI_Icon_{self.userConfig.get('icon','000011')}.png").convert('RGBA')
        IconImg = IconImg.resize((124, 124))
        self.baseImg.paste(IconImg,(405,49),IconImg.split()[3])

        # Rating
        RankLogo = Image.open(self.pic_dir + f"Rating/{self._findRaPic()}").convert('RGBA')
        RankLogo = RankLogo.resize((212, 40))
        RankLogo = self._drawRating(RankLogo)
        self.baseImg.paste(RankLogo, (546, 49),RankLogo)

        # 名字
        namebackgroundImg = Image.open(self.pic_dir + '姓名背景.png').convert('RGBA')
        namebackgroundImg = namebackgroundImg.resize((320, 50))
        DXLogoImg = Image.open(self.pic_dir + 'UI_CMN_Name_DX.png').convert('RGBA')
        DXLogoImg = DXLogoImg.resize((36, 26))
        namebackgroundImg.paste(DXLogoImg,(270,8),DXLogoImg)
        namePlateDraw = ImageDraw.Draw(namebackgroundImg)
        tempFont = ImageFont.truetype(f'{self.font_dir}msyh.ttc', 27, encoding='unic')
        namePlateDraw.text((15, 2), ' '.join(list(self.userName)), 'black', tempFont)
        self.baseImg.paste(namebackgroundImg, (543, 93),namebackgroundImg)

        # 称号
        TitleBgImg = Image.open(self.pic_dir + 'UI_CMN_Shougou_Rainbow.png').convert('RGBA')
        TitleBgImg = TitleBgImg.resize((313,29))
        TitleBgImgDraw = ImageDraw.Draw(TitleBgImg)

        tempFont = ImageFont.truetype(f'{self.font_dir}adobe_simhei.otf', 17, encoding='utf-8')
        playCountInfo = f'MaiMai DX Rating'
        TitleBgImgW, TitleBgImgH = TitleBgImg.size
        playCountInfoW, playCountInfoH = TitleBgImgDraw.textsize(playCountInfo, tempFont)
        textPos = ((TitleBgImgW - playCountInfoW - tempFont.getoffset(playCountInfo)[0]) / 2, 5)
        TitleBgImgDraw.text((textPos[0] - 1, textPos[1]), playCountInfo, 'black', tempFont)
        TitleBgImgDraw.text((textPos[0] + 1, textPos[1]), playCountInfo, 'black', tempFont)
        TitleBgImgDraw.text((textPos[0], textPos[1] - 1), playCountInfo, 'black', tempFont)
        TitleBgImgDraw.text((textPos[0], textPos[1] + 1), playCountInfo, 'black', tempFont)
        TitleBgImgDraw.text((textPos[0] - 1, textPos[1] - 1), playCountInfo, 'black', tempFont)
        TitleBgImgDraw.text((textPos[0] + 1, textPos[1] - 1), playCountInfo, 'black', tempFont)
        TitleBgImgDraw.text((textPos[0] - 1, textPos[1] + 1), playCountInfo, 'black', tempFont)
        TitleBgImgDraw.text((textPos[0] + 1, textPos[1] + 1), playCountInfo, 'black', tempFont)
        TitleBgImgDraw.text(textPos, playCountInfo, 'white', tempFont)
        TitleBgImg = self._resizePic(TitleBgImg, 1.05)
        self.baseImg.paste(TitleBgImg,(546,145),TitleBgImg)





    def drawMusicBox(self,musicChartInfo:ChartInfo):
        # 判断使用什么难度的成绩背景
        MusicBoxImage = Image.open(self.pic_dir + f'box/XP_UI_MSS_MBase_{level_index[musicChartInfo.diff]}.png').convert('RGBA')
        MusicBoxImage = self._resizePic(MusicBoxImage, 0.25)

        CoverPath = get_cover_path(musicChartInfo.idNum,self.is_abstract)

        CoverImage = Image.open(CoverPath).convert('RGBA')
        CoverImage = CoverImage.resize((86, 86))
        MusicBoxImage.paste(CoverImage, (16, 14), CoverImage.split()[3])


        # DX/标准
        MusicTypeLogoPath = self.pic_dir + f'UI_UPE_Infoicon_StandardMode.png'
        if musicChartInfo.tp == "DX":
            MusicTypeLogoPath = self.pic_dir + f'UI_UPE_Infoicon_DeluxeMode.png'
        MusicTypeLogoImg = Image.open(MusicTypeLogoPath).convert('RGBA')
        MusicTypeLogoImg = self._resizePic(MusicTypeLogoImg, 0.4)
        MusicBoxImage.paste(MusicTypeLogoImg, (14, 100), MusicTypeLogoImg.split()[3])

        MusicBoxImageDraw = ImageDraw.Draw(MusicBoxImage)

        # Title
        font = ImageFont.truetype(self.font_dir + "adobe_simhei.otf", 18, encoding='utf-8')
        title = musicChartInfo.title
        if self._coloumWidth(title) > 16:
            title = self._changeColumnWidth(title, 14) + '...'
        MusicBoxImageDraw.text((119, 12), title, 'white', font)
        # 歌曲ID
        font = ImageFont.truetype(self.font_dir + "adobe_simhei.otf", 14, encoding='utf-8')
        song_id = musicChartInfo.idNum
        MusicBoxImageDraw.text((120, 31), f'id: {song_id}', 'white', font)


        # 星星
        start_mun = musicChartInfo.dxscore / (sum(total_list.by_id(str(musicChartInfo.idNum)).charts[musicChartInfo.diff]['notes'])*3) *100
        start_path = self.pic_dir + 'start/' +self._get_dxscore_type(start_mun)
        musicDxStartIcon = Image.open(start_path).convert('RGBA')
        musicDxStartIcon = self._resizePic(musicDxStartIcon, 0.9)
        MusicBoxImage.paste(musicDxStartIcon, (225, 64), musicDxStartIcon.split()[3])

        # 成绩图标
        rankImg = Image.open(self.pic_dir + f'Rank/UI_TTR_Rank_{rankPic[musicChartInfo.scoreId]}.png').convert('RGBA')
        rankImg = self._resizePic(rankImg, 0.35)
        MusicBoxImage.paste(rankImg, (220, 32), rankImg.split()[3])

        # FC/AP图标
        if musicChartInfo.comboId:
            playBoundIconImg = Image.open(self.pic_dir + f'PlayBounds/{comb[musicChartInfo.comboId]}.png').convert('RGBA')
        else:
            playBoundIconImg = Image.open(self.pic_dir + f'PlayBounds/fc_dummy.png').convert('RGBA')
        playBoundIconImg = self._resizePic(playBoundIconImg, 0.4)
        # 横向位置和竖直位置
        MusicBoxImage.paste(playBoundIconImg, (210, 86), playBoundIconImg.split()[3])

        # FSD/FS图标
        if musicChartInfo.fs:
            playBoundIconImg = Image.open(self.pic_dir + f'PlayBounds/{isfs[musicChartInfo.fs]}.png').convert('RGBA')
        else:
            playBoundIconImg = Image.open(self.pic_dir + f'PlayBounds/fs_dummy.png').convert('RGBA')
        playBoundIconImg = self._resizePic(playBoundIconImg, 0.4)
        # 横向位置和竖直位置
        MusicBoxImage.paste(playBoundIconImg, (252, 86), playBoundIconImg.split()[3])

        # Base 完成率 Ra
        font = ImageFont.truetype(self.font_dir + "adobe_simhei.otf", 28, encoding='utf-8')
        # 完成度
        MusicBoxImageDraw.text((118, 47), f"{str(format(musicChartInfo.achievement, '.4f'))[0:-5]}", '#fadf62', font)

        font = ImageFont.truetype(self.font_dir + "adobe_simhei.otf", 16, encoding='utf-8')

        # 小数部分
        index = str(musicChartInfo.achievement).split('.')[0]
        achievement_f = "0" if len(str(musicChartInfo.achievement).split('.')) != 2 else str(musicChartInfo.achievement).split('.')[1]
        if int(index) < 100:
            MusicBoxImageDraw.text((150, 57), '. '+achievement_f, '#fadf62', font)
        else:
            MusicBoxImageDraw.text((167, 57), '. '+achievement_f, '#fadf62', font)

        # 下方
        font = ImageFont.truetype(self.font_dir + "adobe_simhei.otf", 11, encoding='utf-8')

        # Base -> Rating
        MusicBoxImageDraw.text((125, 85), f"定数\n{format(musicChartInfo.ds, '.1f')}", '#000000', font)

        font = ImageFont.truetype(self.font_dir + "adobe_simhei.otf", 20, encoding='utf-8')

        MusicBoxImageDraw.text((151, 85), f'>', '#000000', font)
        MusicBoxImageDraw.text((164, 86), f'{musicChartInfo.ra}', '#000000', font)

        MusicBoxImage = self._resizePic(MusicBoxImage,1.2)
        return MusicBoxImage

        


    def draw(self):
        backGroundImg = Image.open(self.pic_dir + "background.png")
        self.baseImg.paste(backGroundImg,(0,0),backGroundImg.split()[3])

        # 生成用户信息
        self.drawGenerateUserInfo()

        for index,ci in enumerate(self.sdBest):
            i = index // 5  #  需要多少行
            j = index % 5    # 一行有几个
            MusicBoxImg = self.drawMusicBox(ci)
            self.baseImg.paste(MusicBoxImg, (35 + 370 * j, 220 + 140 * i), MusicBoxImg.split()[3])


        for index,ci in enumerate(self.dxBest):
            i = index // 5  #  需要多少行
            j = index % 5    # 一行有几个
            MusicBoxImg = self.drawMusicBox(ci)
            self.baseImg.paste(MusicBoxImg,(35 + 370 * j, 1240 + 140 * i),MusicBoxImg.split()[3])
        return self.baseImg




def computeRa(ds: float, achievement:float) -> int:
    if achievement >= 50 and achievement < 60:
        baseRa = 6.0
    elif achievement < 70:
        baseRa = 7.0
    elif achievement < 75:
        baseRa = 7.5
    elif achievement < 80:
        baseRa = 8.5
    elif achievement < 90:
        baseRa = 9.5
    elif achievement < 94:
        baseRa = 10.5
    elif achievement < 97:
        baseRa = 12.5
    elif achievement < 98:
        baseRa = 12.7
    elif achievement < 99:
        baseRa = 13.0
    elif achievement < 99.5:
        baseRa = 13.2
    elif achievement < 100:
        baseRa = 13.5
    elif achievement < 100.5:
        baseRa = 14.0
    else:
        baseRa = 5.0

    return math.floor(ds * (min(100.5, achievement) / 100) * baseRa)

async def generate_ap50(payload: Dict,is_abstract:bool,userConfig,best50_style:str):
    payload = payload
    status,request_json = await get_user_all_records(payload)
    if status == 400:
            return None, 400, 0
    records = request_json['records']
    b35_ap_records,b15_ap_records = filter_all_perfect_records(records)
    b35_ap_records = b35_ap_records[:35]
    b15_ap_records = b15_ap_records[:15]
    sd_best = BestList(35)
    dx_best = BestList(15)
    for c in b35_ap_records:
        sd_best.push(ChartInfo.from_json(c))
    for c in b15_ap_records:
        dx_best.push(ChartInfo.from_json(c))
    nickName = request_json['nickname']
    if b35_ap_records or b15_ap_records:
        best35Rating = sum([item['ra'] for item in b35_ap_records])
        best15Rating = sum([item['ra'] for item in b15_ap_records])
        rating = best35Rating+best15Rating
        plate_id = userConfig.get('plate',"")
        if plate_id == "":
            df_plate = request_json['plate']
            if df_plate:
                userConfig['plate'] = MAIPLATE_FILE_ID_MAP.get(df_plate,"000011")
            else:
                userConfig['plate'] = "000011"
        pic = DrawBest(is_abstract,nickName,best15Rating,best35Rating,sd_best, dx_best,userConfig,best50_style).draw()
        return pic, 0, rating
    else:
        return None, 0, 0    
    
async def generate_best_35(payload: Dict,is_abstract:bool,userConfig,best50_style:str):
    payload = payload
    status,request_json = await get_user_all_records(payload)
    if status == 400:
            return None, 400, 0
    records = request_json['records']
    b35_ap_records,b15_ap_records = filter_best_35_records(records)
    b35_ap_records = b35_ap_records[:35]
    b15_ap_records = b15_ap_records[:15]
    sd_best = BestList(35)
    dx_best = BestList(15)
    for c in b35_ap_records:
        sd_best.push(ChartInfo.from_json(c))
    for c in b15_ap_records:
        dx_best.push(ChartInfo.from_json(c))
    nickName = request_json['nickname']
    if b35_ap_records or b15_ap_records:
        best35Rating = sum([item['ra'] for item in b35_ap_records])
        best15Rating = sum([item['ra'] for item in b15_ap_records])
        rating = best35Rating+best15Rating
        plate_id = userConfig.get('plate',"")
        if plate_id == "":
            df_plate = request_json['plate']
            if df_plate:
                userConfig['plate'] = MAIPLATE_FILE_ID_MAP.get(df_plate,"000011")
            else:
                userConfig['plate'] = "000011"
        pic = DrawBest(is_abstract,nickName,best15Rating,best35Rating,sd_best, dx_best,userConfig,best50_style).draw()
        return pic, 0, rating
    else:
        return None, 0, 0 
    
async def generate_best_50(payload: Dict,is_abstract:bool,userConfig,best50_style:str,mode:str):
    status,request_json,best35_records,best15_records,best35_BestList,best15_BestList = await get_best_50_data(payload,mode)
    if status == 400:
        return None, 400, 0
    if status == 403:
        return None, 403, 0
    if best35_records or best15_records:
        best35Rating = sum([item['ra'] for item in best35_records])
        best15Rating = sum([item['ra'] for item in best15_records])
        rating = best35Rating+best15Rating
        nickName = request_json['nickname']
        plate_id = userConfig.get('plate',"")
        if plate_id == "":
            df_plate = request_json['plate']
            if df_plate:
                userConfig['plate'] = MAIPLATE_FILE_ID_MAP.get(df_plate,"000011")
            else:
                userConfig['plate'] = "000011"
        pic = DrawBest(is_abstract,nickName,best15Rating,best35Rating,best35_BestList, best15_BestList,userConfig,best50_style).draw()

        return pic, 0, rating
    else:
        return None, 0, 0
     
async def generate_b50(payload: Dict,is_abstract:bool,userConfig,best50_style:str):
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400, 0
        if resp.status == 403:
            return None, 403, 0
        sd_best = BestList(35)
        dx_best = BestList(15)
        obj = await resp.json()
        dx: List[Dict] = obj["charts"]["dx"]
        sd: List[Dict] = obj["charts"]["sd"]
        rating = int(str(obj["rating"]))
        for c in sd:
            sd_best.push(ChartInfo.from_json(c))
        for c in dx:
            dx_best.push(ChartInfo.from_json(c))
        nickName = obj['nickname']
        if rating > 0:
            best35Rating = sum([item['ra'] for item in obj["charts"]["sd"]])
            best15Rating = sum([item['ra'] for item in obj["charts"]["dx"]])
            plate_id = userConfig.get('plate',"")
            if plate_id == "":
                df_plate = obj['plate']
                if df_plate:
                    userConfig['plate'] = MAIPLATE_FILE_ID_MAP.get(df_plate,"000011")
                else:
                    userConfig['plate'] = "000011"

            pic = DrawBest(is_abstract,nickName,best15Rating,best35Rating,sd_best, dx_best,userConfig,best50_style).draw()
            return pic, 0, rating
        else:
            return None, 0, 0
    
async def generate_all_best50(payload: Dict,is_abstract:bool,userConfig,best50_style:str):
    payload = payload
    status,request_json = await get_user_all_records(payload)
    if status == 400:
            return None, 400, 0
    records = request_json['records']
    b35_ap_records,b15_ap_records = filter_all_records(records)
    b35_ap_records = b35_ap_records[:50]
    b15_ap_records = b15_ap_records[:15]
    sd_best = BestList(50)
    dx_best = BestList(15)
    for c in b35_ap_records:
        sd_best.push(ChartInfo.from_json(c))
    for c in b15_ap_records:
        dx_best.push(ChartInfo.from_json(c))
    nickName = request_json['nickname']
    if b35_ap_records or b15_ap_records:
        best35Rating = sum([item['ra'] for item in b35_ap_records])
        best15Rating = sum([item['ra'] for item in b15_ap_records])
        rating = best35Rating+best15Rating
        plate_id = userConfig.get('plate',"")
        if plate_id == "":
            df_plate = request_json['plate']
            if df_plate:
                userConfig['plate'] = MAIPLATE_FILE_ID_MAP.get(df_plate,"000011")
            else:
                userConfig['plate'] = "000011"
        pic = DrawBest(is_abstract,nickName,best15Rating,best35Rating,sd_best, dx_best,userConfig,best50_style).draw()
        return pic, 0, rating
    else:
        return None, 0, 0  