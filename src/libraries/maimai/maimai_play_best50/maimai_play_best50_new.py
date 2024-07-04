# Author: Ekzykes
from typing import Dict, List
from PIL import Image, ImageDraw, ImageFont
from src.libraries.maimai.maimaidx_music import total_list
from src.libraries.maimai.utils import get_cover_path
import asyncio
import aiohttp
from src.libraries.maimai.maimai_play_best50.maimai_recommend import Recommend
from src.libraries.GLOBAL_CONSTANT import MAIPLATE_FILE_ID_MAP
from src.libraries.maimai.maimai_play_best50.utils import get_best_50_data,get_user_all_records,filter_all_perfect_records,filter_best_35_records,filter_all_records,BestList,ChartInfo
import traceback


from src.libraries.GLOBAL_PATH import NORMAL_BEST_50_PATH,ABSTRACT_BEST_50_PATH,FRAME_PATH,PLATE_PATH,FONT_PATH,ICON_PATH

class DrawBest(object):
    def __init__(self,is_abstract:bool,nickName:str,best35Rating,best15Rating,sdBest:BestList, dxBest:BestList,userConfig,best50_style_index:str):
        self.pic_dir = f'{NORMAL_BEST_50_PATH}/' if best50_style_index == "1" else f'{ABSTRACT_BEST_50_PATH}/'
        self.frame_dir = f"{FRAME_PATH}/"
        self.plate_dir = f"{PLATE_PATH}/"
        self.font_dir = f'{FONT_PATH}/'
        self.icon_dir = f'{ICON_PATH}/'
        self.baseImg = Image.new("RGBA", (1700, 2350), (0, 0, 0, 0))
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


    def findRaPic(self) -> str:
        num = '10'
        if self.playerRating >= 15000:
            num = '15000'
        elif self.playerRating >= 14500:
            num = '14000'
        elif self.playerRating >= 14000:
            num = '14000'
        elif self.playerRating >= 13000:
            num = '13000'
        elif self.playerRating >= 12000:
            num = '12000'
        elif self.playerRating >= 10000:
            num = '10000'
        elif self.playerRating >= 8000:
            num = '8000'
        elif self.playerRating >= 6000:
            num = '6000'
        elif self.playerRating >= 4000:
            num = '4000'
        elif self.playerRating >= 2000:
            num = '2000'
        else:
            num = '0'
        return num


    
    def _get_dxscore_type(self,dxscorepen):
        if dxscorepen <= 85:
            return "0"
        elif dxscorepen <= 90:
            return "1"
        elif dxscorepen <= 93:
            return "2"
        elif dxscorepen <= 95:
            return "3"        
        elif dxscorepen <= 97:
            return "4"        
        else:
            return "5"
        
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


    def drawGenerateUserInfo(self):
        plate_id = str(self.userConfig.get('plate','000011'))
        if "custom_plate" in plate_id:
            plate_id = plate_id.split('custom_plate')[1]
            plateImage = Image.open(self.plate_dir + f"custom/UI_Plate_{plate_id}.png").convert('RGBA')
        else:
            plateImage = Image.open(self.plate_dir + f"UI_Plate_{plate_id}.png").convert('RGBA')
        plateImage = plateImage.resize((1103,178))

        # 头像
        IconImg = Image.open(self.icon_dir + f"UI_Icon_{self.userConfig.get('icon','000011')}.png").convert('RGBA')
        IconImg = IconImg.resize((148,148))
        plateImage.paste(IconImg,(47-32,42-27),IconImg.split()[3])


        # 分数框
        ratingBoxImg = Image.open(self.pic_dir + f"姓名框/RAT框/{self.findRaPic()}.png").convert('RGBA')
        ratingBoxImg = ratingBoxImg.resize((264,49))
        plateImage.paste(ratingBoxImg,(203-32,37-27),ratingBoxImg.split()[3])

        # 昵称
        userNameBoxImg = Image.open(self.pic_dir + "姓名框/usernamebox.png").convert('RGBA')
        userNameBoxImg = userNameBoxImg.resize((362,67))
        plateImage.paste(userNameBoxImg,(203-32,90-27),userNameBoxImg.split()[3])



        plateImageDraw = ImageDraw.Draw(plateImage)
        tempFont = ImageFont.truetype(self.font_dir + "江城圆体 500W.ttf", 35, encoding='utf-8')
    
        plateImageDraw.text((222-30, 58+22), " ".join(list(self.userName)), 'black', tempFont)
        # plateImage.paste(Name, (543, 93),Name)


        # 称号
        titleBoxImg = Image.open(self.pic_dir + "姓名框/称号/15000.png").convert('RGBA')
        titleBoxImg = titleBoxImg.resize((361,34))
        plateImage.paste(titleBoxImg,(203-32,161-27),titleBoxImg.split()[3])
        tempFont = ImageFont.truetype(self.font_dir + "RoGSanSrfStd-Bd.otf", 20, encoding='utf-8')
        content = f"旧版本{self.best15Rating}+新版本{self.best35Rating}"
        # 计算文本的尺寸
        text_width, text_height = tempFont.getsize(content)
        # 绘制文本描边
        outline_color = "black"
        plateImageDraw.text((350 - (text_width/2)-1, 150 - (text_height/2)-1), content, font=tempFont, fill=outline_color)  # 左上
        plateImageDraw.text((350 - (text_width/2)+1, 150 - (text_height/2)-1), content, font=tempFont, fill=outline_color)  # 右上
        plateImageDraw.text((350 - (text_width/2)-1, 150 - (text_height/2)+1), content, font=tempFont, fill=outline_color)  # 左下
        plateImageDraw.text((350 - (text_width/2)+1, 150 - (text_height/2)+1), content, font=tempFont, fill=outline_color)  # 右下
        # 绘制文本
        text_color = "white"
        plateImageDraw.text((350 - (text_width/2), 150 - (text_height/2)), content, font=tempFont, fill=text_color)


        # rating
        reverseRating = str(self.playerRating)[::-1]
        tempFont = ImageFont.truetype(self.font_dir + "江城圆体 500W.ttf", 30, encoding='utf-8')
        ratingColor = (248,232,122)
        startX = 381
        for v in reverseRating:
            plateImageDraw.text((startX, 19), v , ratingColor, tempFont)
            startX = startX - 21
            
        return plateImage



    def drawRecommendedlevelDecimal(self):
        recommendedlevelDecimalImg = Image.open(self.pic_dir + "推荐定数/推荐定数.png").convert('RGBA')

        recommendedlevelDecimalDraw = ImageDraw.Draw(recommendedlevelDecimalImg)

        if len(self.sdBest):
            best35Max = max([item.ra for item in self.sdBest])
            best35Min = min([item.ra for item in self.sdBest])
        else:
            best35Max = 0
            best35Min = 0
        if len(self.dxBest):
            best15Max = max([item.ra for item in self.dxBest])
            best15Min = min([item.ra for item in self.dxBest])
        else:
            best15Max = 0
            best15Min = 0

        self.best35Recommended = {
                "recommended":Recommend((best35Max + best35Min) // 2).getRatingRecommendData(),
                "min":Recommend(best35Min).getRatingRecommendData()
            }
        self.best15Recommended = {
                "recommended":Recommend((best15Max + best15Min) // 2).getRatingRecommendData(),
                "min":Recommend(best15Min).getRatingRecommendData()
            }
        
        self.best35Startcoordinate = {"x":243+17,"y":368-249+23}
        tempFont = ImageFont.truetype(self.font_dir + "RoGSanSrfStd-Bd.otf", 37, encoding='utf-8')
        self.recommendedlevelDecimalColor = (203, 41, 98)
        for k in self.best35Recommended:
            for v in self.best35Recommended[k].values():
                if v == -1:
                    seatImg = Image.open(self.pic_dir + "推荐定数/占位.png").convert('RGBA')
                    recommendedlevelDecimalImg.paste(seatImg,(self.best35Startcoordinate['x']-74,self.best35Startcoordinate['y']-28),seatImg.split()[3])
                else:
                    font_x,font_y = tempFont.getsize(str(v))
                    recommendedlevelDecimalDraw.text((self.best35Startcoordinate['x'] - (font_x/2), self.best35Startcoordinate['y'] - (font_y/2)), str(v), self.recommendedlevelDecimalColor, tempFont)
                self.best35Startcoordinate['x'] = self.best35Startcoordinate['x'] + 158
            self.best35Startcoordinate['x'] = 243+17
            self.best35Startcoordinate['y'] = self.best35Startcoordinate['y'] + 57


        self.best15Startcoordinate = {"x":243+17,"y":504-249+24}

        for k in self.best15Recommended:
            for v in self.best15Recommended[k].values():
                if v == -1:
                    seatImg = Image.open(self.pic_dir + "推荐定数/占位.png").convert('RGBA')
                    recommendedlevelDecimalImg.paste(seatImg,(self.best15Startcoordinate['x']-74,self.best15Startcoordinate['y']-28),seatImg.split()[3])
                else:
                    font_x,font_y = tempFont.getsize(str(v))
                    recommendedlevelDecimalDraw.text((self.best15Startcoordinate['x'] - (font_x/2), self.best15Startcoordinate['y'] - (font_y/2)), str(v), self.recommendedlevelDecimalColor, tempFont)
                self.best15Startcoordinate['x'] = self.best15Startcoordinate['x'] + 158
            self.best15Startcoordinate['x'] = 243+17
            self.best15Startcoordinate['y'] = self.best15Startcoordinate['y'] + 57

        return recommendedlevelDecimalImg



    def drawMusicBox(self,musicChartInfo:ChartInfo,Bestindex:int):
        baseMusicBoxImg = Image.new("RGBA", (324, 140), (0, 0, 0, 0))

        baseMusicBoxDraw = ImageDraw.Draw(baseMusicBoxImg)


        musicBoxImg = Image.open(self.pic_dir + f"BOX/歌曲卡片/{musicChartInfo.diff}.png" ).convert('RGBA')

        coverPath = get_cover_path(musicChartInfo.idNum,self.is_abstract)
        musicCoverImg = Image.open(coverPath).convert('RGBA')
        musicCoverImg = musicCoverImg.resize((100,100))
        baseMusicBoxImg.paste(musicCoverImg,(17,15),musicCoverImg.split()[3])

        baseMusicBoxImg.paste(musicBoxImg,(0,0),musicBoxImg.split()[3])

        # 谱面模式
        MusicTypeIcon = Image.open(self.pic_dir + ("BOX/版本/DX.png" if musicChartInfo.tp == "DX" else "BOX/版本/ST.png") ).convert('RGBA')
        baseMusicBoxImg.paste(MusicTypeIcon,(0,0),MusicTypeIcon.split()[3])

        # Title
        tempFont = ImageFont.truetype(self.font_dir + "江城圆体 600W.ttf", 20, encoding='utf-8')

        title = musicChartInfo.title
        if self._coloumWidth(title) > 16:
            title = self._changeColumnWidth(title, 14) + '...'
        baseMusicBoxDraw.text((137,7), title , "white" , tempFont)

        # Rank
        MusicRankIcon = Image.open(self.pic_dir + f"BOX/RANK/{musicChartInfo.scoreId}.png" ).convert('RGBA')
        baseMusicBoxImg.paste(MusicRankIcon,(135,31),MusicRankIcon.split()[3])

        # combo
        MusicComboIcon = Image.open(self.pic_dir + f"BOX/特殊标识/combo{musicChartInfo.comboId}.png" ).convert('RGBA')
        baseMusicBoxImg.paste(MusicComboIcon,(218,31),MusicComboIcon.split()[3])

        # sync
        MusicSyncIcon = Image.open(self.pic_dir + f"BOX/特殊标识/fs{musicChartInfo.fs}.png" ).convert('RGBA')
        baseMusicBoxImg.paste(MusicSyncIcon,(259,31),MusicSyncIcon.split()[3])

        # 完成率
        tempFont = ImageFont.truetype(self.font_dir + "M Plus 6.ttf", 30, encoding='utf-8')
        baseMusicBoxDraw.text((136,60), "%.4f" % musicChartInfo.achievement + "%" , "white" , tempFont)

        # TOP
        tempFont = ImageFont.truetype(self.font_dir + "江城圆体 600W.ttf", 18, encoding='utf-8')
        baseMusicBoxDraw.text((134,104), f"#{Bestindex}" , "black" , tempFont)

        # dx+rating
        baseMusicBoxDraw.text((177,104), f"{musicChartInfo.ds}→{musicChartInfo.ra}" , "black" , tempFont)

        # dxStar
        start_mun = musicChartInfo.dxscore / (sum(total_list.by_id(str(musicChartInfo.idNum)).charts[musicChartInfo.diff]['notes'])*3) *100
        star_index = self._get_dxscore_type(start_mun)
        if star_index != "0":
            MusicdxStarIcon = Image.open(self.pic_dir + f"星级/{star_index}.png" ).convert('RGBA')
            baseMusicBoxImg.paste(MusicdxStarIcon,(292,102),MusicdxStarIcon.split()[3])


        # musicId
        # text_color = (0, 0, 0)
        # text_opacity = 50  # 0 表示完全透明，255 表示完全不透明
        # text_color_with_opacity = text_color + (text_opacity,)
        # # baseMusicBoxImg = baseMusicBoxImg.rotate(90, expand=True)
        # # baseMusicBoxImg.show()
        # tempFont = ImageFont.truetype(self.font_dir + "江城圆体 600W.ttf", 25, encoding='utf-8')

        # font_x,font_y = tempFont.getsize(musicChartInfo.idNum)
        # baseMusicBoxDraw.text((310 - (font_x), 15 - (font_y/2)), musicChartInfo.idNum, (57,61,105), tempFont)
        

        return baseMusicBoxImg


    def draw(self):
        frameImg = Image.open(self.frame_dir + f"UI_Frame_{self.userConfig.get('frame','200502')}.png" ).convert('RGBA')
        frameImg = frameImg.resize((1700,711))

        self.baseImg.paste(frameImg,(0,0),frameImg.split()[3])

        backGroundImg = Image.open(self.pic_dir + "background.png")
        self.baseImg.paste(backGroundImg,(0,0),backGroundImg.split()[3])

        plateImage = self.drawGenerateUserInfo()
        self.baseImg.paste(plateImage,(32,27),plateImage.split()[3])

        recommendedlevelDecimalImg = self.drawRecommendedlevelDecimal()
        self.baseImg.paste(recommendedlevelDecimalImg,(23,249),recommendedlevelDecimalImg.split()[3])

        for index,ci in enumerate(self.sdBest):
            i = index // 5  #  需要多少行
            j = index % 5    # 一行有几个
            MusicBoxImg = self.drawMusicBox(ci,index+1)
            self.baseImg.paste(MusicBoxImg,(18 + ((324+10) * j),721 + ((140+10) * i)),MusicBoxImg.split()[3])

        for index,ci in enumerate(self.dxBest):
            # ci = self.dxBest[index]
            i = index // 5  #  需要多少行
            j = index % 5    # 一行有几个
            MusicBoxImg = self.drawMusicBox(ci,index+1)
            self.baseImg.paste(MusicBoxImg,(18 + ((324+10) * j),1883 + ((140+10) * i)),MusicBoxImg.split()[3])

        return self.baseImg
    
async def generate_best_50(payload: Dict,is_abstract:bool,userConfig,best50_style:str,mode:str):
    status,request_json,best35_records,best15_records,best35_BestList,best15_BestList = await get_best_50_data(payload,mode)
    if status == 400:
        return None, 400, 0
    if status == 403:
        return None, 403, 0
    nickName = request_json['nickname']
    if best35_records or best15_records:
        best35Rating = sum([item['ra'] for item in best35_records])
        best15Rating = sum([item['ra'] for item in best15_records])
        rating = best35Rating+best15Rating
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
        best15Rating = sum([item['ra'] for item in dx_best])
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