from src.libraries.maimai.player_music_score.generate_utils import get_user_music_score,line_break,split_text_to_lines
from PIL import Image,ImageFont,ImageDraw
from src.libraries.maimai.maimaidx_music import total_list
from src.libraries.maimai.utils import get_cover_path
from src.libraries.GLOBAL_CONSTANT import VERSION_LOGO_MAP
from src.libraries.execution_time import timing_decorator,timing_decorator_async
from src.libraries.GLOBAL_PATH import PLAYER_MUSIC_SCORE_PATH,FONT_PATH


class PlayerMusicScore():

    def __init__(self,music_id:int,player_music_score,is_abstract:bool) -> None:
        self.music_id = music_id
        self.music_info = total_list.by_id(str(music_id))
        self.player_music_score = player_music_score
        self.is_abstract = is_abstract

        self.baseImg = Image.new("RGBA", (1700, 1800), (0, 0, 0, 0))
        self.baseImgDraw = ImageDraw.Draw(self.baseImg)

        self.pic_dir = PLAYER_MUSIC_SCORE_PATH
        self.font_path = f'{FONT_PATH}/GlowSansSC-Normal-Bold.otf'
        self.title_font_path = f'{FONT_PATH}/SourceHanSans_35.otf'

    def getRankIcon(self,achievements:str):
        achievements = float(achievements)
        if achievements >= 100.5:
            return 'sssp.png'
        elif achievements >= 100:
            return 'sss.png'
        elif achievements >= 99.5:
            return 'ssp.png'
        elif achievements >= 99:
            return 'ss.png'
        elif achievements >= 98:
            return 'sp.png'
        elif achievements >= 97:
            return 's.png'
        elif achievements >= 94:
            return 'aaa.png'
        elif achievements >= 90:
            return 'aa.png'
        elif achievements >= 80:
            return 'a.png'
        elif achievements >= 75:
            return 'bbb.png'
        elif achievements >= 70:
            return 'bb.png'
        elif achievements >= 60:
            return 'b.png'
        elif achievements >= 50:
            return 'c.png'
        else:
            return 'd.png'
        
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
        
    @timing_decorator
    def draw(self):
        cover_path = get_cover_path(self.music_id,self.is_abstract)
        musicCoverImg = Image.open(cover_path).convert('RGBA')
        musicCoverImg = musicCoverImg.resize((494,494))
        self.baseImg.paste(musicCoverImg,(191,172),musicCoverImg.split()[3])


        backageImg = Image.open(f"{self.pic_dir}/background.png").convert('RGBA')
        self.baseImg.paste(backageImg,(0,0),backageImg.split()[3])

        # 添加曲师
        tempFont = ImageFont.truetype(self.font_path, 43, encoding='utf-8')
        artist = self.music_info.artist
        if self._coloumWidth(artist) > 38:
            artist = self._changeColumnWidth(artist, 34) + '...'
        self.baseImgDraw.text((729,180), artist , "white" , tempFont)

        # Title 
        tempFont = ImageFont.truetype(self.title_font_path, 60, encoding='utf-8')
        title = split_text_to_lines(self.music_info.title,800,tempFont)
        # title = line_break(self.music_info.title,26,4)
        self.baseImgDraw.text((727,246), title , "white" , tempFont)

        # music_id bpm 分类 版本
        tempFont = ImageFont.truetype(self.font_path, 45, encoding='utf-8')

        text_width, text_height = tempFont.getsize(self.music_info.id)
        self.baseImgDraw.text(((810-text_width/2),(610-text_height/2)), self.music_info.id , "white" , tempFont)

        text_width, text_height = tempFont.getsize(str(self.music_info.bpm))
        self.baseImgDraw.text(((953-text_width/2),(610-text_height/2)), str(self.music_info.bpm) , "white" , tempFont)

        if self.music_info.genre in ["niconico & VOCALOID","niconicoボーカロイド","ゲームバラエティ"]:
            tempFont = ImageFont.truetype(self.font_path, 30, encoding='utf-8')
            text_width, text_height = tempFont.getsize(self.music_info.genre)
            self.baseImgDraw.text(((1194-text_width/2),(613-text_height/2)), self.music_info.genre , "white" , tempFont)
        else:
            text_width, text_height = tempFont.getsize(self.music_info.genre)
            self.baseImgDraw.text(((1194-text_width/2),(614-text_height/2)), self.music_info.genre , "white" , tempFont)

        # 类型
        TypeIconImg = Image.open(f"{self.pic_dir}/类型/{self.music_info.type}.png").convert('RGBA')
        self.baseImg.paste(TypeIconImg,(1393,597),TypeIconImg.split()[3])

        # logo
        if self.music_info.cn_version in VERSION_LOGO_MAP:
            VersionLogoImg = Image.open(f"{self.pic_dir}/版本牌/UI_CMN_TabTitle_MaimaiTitle_Ver{VERSION_LOGO_MAP.get(self.music_info.cn_version)}.png").convert('RGBA')
            text_width, text_height = VersionLogoImg.size
            self.baseImg.paste(VersionLogoImg,(250-int(text_width/2),150-int(text_height/2)),VersionLogoImg.split()[3])



        if 4 not in self.player_music_score:
            maskImg = Image.open(f"{self.pic_dir}/MASK/mask_2.png").convert('RGBA')
            self.baseImg.paste(maskImg,(191,751+158*4),maskImg.split()[3])

        score_box_y_map = {
            0:751,
            1:751+158*1,
            2:751+158*2,
            3:751+158*3,
            4:751+158*4
        }
        for k,v in self.player_music_score.items():
            if not v:
                maskImg = Image.open(f"{self.pic_dir}/MASK/mask_1.png").convert('RGBA')
                self.baseImg.paste(maskImg,(191,score_box_y_map.get(k)),maskImg.split()[3])
            else:
                baseBoxImg = Image.new("RGBA", (1321, 126), (0, 0, 0, 0))

                if v['fc']:
                    fcIconImg = Image.open(f"{self.pic_dir}/PlayBonus/{str(v['fc']).upper()}.png").convert('RGBA')
                    baseBoxImg.paste(fcIconImg,(0,0),fcIconImg.split()[3])

                if v['fs']:
                    if v['fs'].upper() != 'SYNC':
                        fsIconImg = Image.open(f"{self.pic_dir}/PlayBonus/{str(v['fs']).upper()}.png").convert('RGBA')
                        baseBoxImg.paste(fsIconImg,(0,0),fsIconImg.split()[3])

                rankIconImg = Image.open(f"{self.pic_dir}/RANK/{str(v['rate']).upper()}.png").convert('RGBA')
                baseBoxImg.paste(rankIconImg,(0,2),rankIconImg.split()[3])

                start_mun = v['dxScore'] / (sum(self.music_info.charts[k]['notes'])*3) *100
                star_index = self._get_dxscore_type(start_mun)
                if star_index != "0":
                    MusicdxStarIcon = Image.open(f"{self.pic_dir}/星级/Star_{star_index}.png").convert('RGBA')
                    baseBoxImg.paste(MusicdxStarIcon,(0,0),MusicdxStarIcon.split()[3])

                baseBoxImgDraw = ImageDraw.Draw(baseBoxImg)

                achievements = "%.4f" % v['achievements']
                tempFont = ImageFont.truetype(self.font_path, 62, encoding='utf-8')
                text_width, text_height = tempFont.getsize(achievements)
                baseBoxImgDraw.text((643-int(text_width/2),52-int(text_height/2)),  achievements, "black" , tempFont)

                # 单曲rat+ds
                content = str(self.music_info.ds[k]) + '→' + str(v['ra'])
                tempFont = ImageFont.truetype(self.font_path, 30, encoding='utf-8')
                text_width, text_height = tempFont.getsize(content)
                baseBoxImgDraw.text((1205-int(text_width/2),32-int(text_height/2)),  content, "black" , tempFont)

                # dx分
                content = str(v['dxScore']) + '/' + str((sum(self.music_info.charts[k]['notes'])*3))
                tempFont = ImageFont.truetype(self.font_path, 30, encoding='utf-8')
                text_width, text_height = tempFont.getsize(content)
                baseBoxImgDraw.text((1205-int(text_width/2),86-int(text_height/2)),  content, "black" , tempFont)


                self.baseImg.paste(baseBoxImg,(191,score_box_y_map.get(k)),baseBoxImg.split()[3])



        return self.baseImg

@timing_decorator_async
async def generate_info(music_id:int,user_id:str,is_abstract:bool):
    player_music_score = await get_user_music_score(music_id,qq=user_id)
    if player_music_score != 400:
        player_music_score_img = PlayerMusicScore(music_id=music_id,player_music_score=player_music_score,is_abstract=is_abstract).draw()
        return True,player_music_score_img
    else:
        return False,None