from src.libraries.image_handle.image import split_text_to_lines
from PIL import Image,ImageFont,ImageDraw
from src.libraries.maimai.maimaidx_music import total_list
from src.libraries.maimai.utils import get_cover_path
from src.libraries.GLOBAL_CONSTANT import VERSION_LOGO_MAP
from src.libraries.execution_time import timing_decorator
from .utils import truncate_text,decimalPoints
from src.libraries.data_handle.abstract_db_handle import abstract
from src.libraries.GLOBAL_PATH import MAIMAI_MUSIC_DATA,FONT_PATH
from src.libraries.maimai.utils import get_abstract_cover_path_by_file_id
class MaiMusicData():
    def __init__(self,music_id:int,is_abstract:bool) -> None:
        self.music_id = music_id 
        self.music_info = total_list.by_id(str(music_id))
        self.is_abstract = is_abstract

        self.baseImg = Image.new("RGBA", (1700, 2000), (0, 0, 0, 0))
        self.baseImgDraw = ImageDraw.Draw(self.baseImg)

        
    @timing_decorator
    def draw(self):
        if self.is_abstract:
            abstract_data = abstract.get_abstract_id_list()
            if int(self.music_id) in abstract_data:
                file_name,nickname = abstract.get_abstract_file_name(str(self.music_id))
                filename = file_name
                self.abstract_artist = nickname
                musicCoverImg = Image.open(get_abstract_cover_path_by_file_id(file_name)).convert('RGBA')
            else:
                self.abstract_artist = "抽象画未收录"
                musicCoverImg = Image.open(get_cover_path(self.music_id,False)).convert('RGBA')
        else:
            self.abstract_artist = "-"
            musicCoverImg = Image.open(get_cover_path(self.music_id,False)).convert('RGBA')
        musicCoverImg = musicCoverImg.resize((494,494))
        self.baseImg.paste(musicCoverImg,(191,172),musicCoverImg.split()[3])


        backageImg = Image.open(f"{MAIMAI_MUSIC_DATA}/background.png").convert('RGBA')
        self.baseImg.paste(backageImg,(0,0),backageImg.split()[3])

        # 添加曲师
        tempFont = ImageFont.truetype(f"{FONT_PATH}/GlowSansSC-Normal-Bold.otf", 43, encoding='utf-8')
        artist = truncate_text(self.music_info.artist, tempFont, 800)
        self.baseImgDraw.text((729,180), artist , "white" , tempFont)

        # Title 
        tempFont = ImageFont.truetype(f'{FONT_PATH}/SourceHanSans_35.otf', 60, encoding='utf-8')
        title = split_text_to_lines(self.music_info.title,800,tempFont)
        self.baseImgDraw.text((727,246), title , "white" , tempFont)

        # music_id bpm 分类 版本
        tempFont = ImageFont.truetype(f"{FONT_PATH}/GlowSansSC-Normal-Bold.otf", 45, encoding='utf-8')

        text_width, text_height = tempFont.getsize(self.music_info.id)
        self.baseImgDraw.text(((810-text_width/2),(610-text_height/2)), self.music_info.id , "white" , tempFont)

        text_width, text_height = tempFont.getsize(str(self.music_info.bpm))
        self.baseImgDraw.text(((953-text_width/2),(610-text_height/2)), str(self.music_info.bpm) , "white" , tempFont)

        if self.music_info.genre in ["niconico & VOCALOID","niconicoボーカロイド","ゲームバラエティ"]:
            tempFont = ImageFont.truetype(f"{FONT_PATH}/GlowSansSC-Normal-Bold.otf", 30, encoding='utf-8')
            text_width, text_height = tempFont.getsize(self.music_info.genre)
            self.baseImgDraw.text(((1194-text_width/2),(613-text_height/2)), self.music_info.genre , "white" , tempFont)
        else:
            text_width, text_height = tempFont.getsize(self.music_info.genre)
            self.baseImgDraw.text(((1194-text_width/2),(614-text_height/2)), self.music_info.genre , "white" , tempFont)

        # 类型
        TypeIconImg = Image.open(f"{MAIMAI_MUSIC_DATA}/类型/{self.music_info.type}.png").convert('RGBA')
        self.baseImg.paste(TypeIconImg,(1393,597),TypeIconImg.split()[3])

        # logo
        if self.music_info.cn_version in VERSION_LOGO_MAP:
            VersionLogoImg = Image.open(f"{MAIMAI_MUSIC_DATA}/版本牌/UI_CMN_TabTitle_MaimaiTitle_Ver{VERSION_LOGO_MAP.get(self.music_info.cn_version)}.png").convert('RGBA')
            text_width, text_height = VersionLogoImg.size
            self.baseImg.paste(VersionLogoImg,(250-int(text_width/2),150-int(text_height/2)),VersionLogoImg.split()[3])

        if len(self.music_info.ds) > 4:
            charterBg= Image.open(f"{MAIMAI_MUSIC_DATA}/Charter_2.png").convert('RGBA')
            charter_map = [(),(),(247,27),(247,107),(247,187)]
        else:
            charterBg= Image.open(f"{MAIMAI_MUSIC_DATA}/Charter_1.png").convert('RGBA')
            charter_map = [(),(),(250,47),(250,165)]
        charterDraw = ImageDraw.Draw(charterBg)
        tempFont = ImageFont.truetype(f"{FONT_PATH}/GlowSansSC-Normal-Bold.otf", 40, encoding='utf-8')
        for index,chart in enumerate(self.music_info.charts):
            if charter_map[index]:
                chart_charter = str(chart['charter'])
                chart_charter = truncate_text(chart_charter, tempFont, 550)
                charterDraw.text(charter_map[index], chart_charter , "black" , tempFont)
        self.baseImg.paste(charterBg,(181,1429),charterBg.split()[3])

        versionBg= Image.open(f"{MAIMAI_MUSIC_DATA}/Ver.png").convert('RGBA')
        versionDraw = ImageDraw.Draw(versionBg)
        tempFont = ImageFont.truetype(f"{FONT_PATH}/GlowSansSC-Normal-Bold.otf", 40, encoding='utf-8')
        version = truncate_text(self.music_info.ez_version, tempFont, 420)
        fontSizeX,fontSizeY = tempFont.getsize(version)
        versionDraw.text((257-int(fontSizeX/2),70), version , "black" , tempFont)
        abstract_artist = truncate_text(self.abstract_artist, tempFont, 420)
        fontSizeX,fontSizeY = tempFont.getsize(abstract_artist)
        versionDraw.text((257-int(fontSizeX/2),187), abstract_artist , "black" , tempFont)
        self.baseImg.paste(versionBg,(1005,1429),versionBg.split()[3])
     
        if len(self.music_info.ds) > 4:
            TapDataBg = Image.open(f"{MAIMAI_MUSIC_DATA}/Total_2-1.png").convert('RGBA')
            ReMasterIcon = Image.open(f"{MAIMAI_MUSIC_DATA}/Total_2-2.png").convert('RGBA')
            TapDataBg.paste(ReMasterIcon,(0,0),ReMasterIcon.split()[3])
            TapDataDraw = ImageDraw.Draw(TapDataBg)
            for index,chart in enumerate(self.music_info.charts):
                ds = self.music_info.ds[index]
                tempFont = ImageFont.truetype(f"{FONT_PATH}/RoGSanSrfStd-Bd.otf", 50, encoding='utf-8')
                ds = decimalPoints(ds,1)
                fontSizeX,fontSizeY = tempFont.getsize(ds)
                TapDataDraw.text((350+(202*index) - int(fontSizeX/2),100 - int(fontSizeY/2)), ds , "white" , tempFont)
                notes = list(chart['notes'])
                total_notes = sum(notes)

                if len(notes) == 4:
                    notes.insert(len(notes)-1, '-')
                notes.insert(0, total_notes)

                for note_index,note_count in enumerate(notes):
                    tempFont = ImageFont.truetype(f"{FONT_PATH}/RoGSanSrfStd-Bd.otf", 48, encoding='utf-8')
                    note_count = str(note_count)
                    fontSizeX,fontSizeY = tempFont.getsize(note_count)
                    TapDataDraw.text((350+(202*index) - int(fontSizeX/2),162+(88*note_index) ), note_count , "black" , tempFont)
            self.baseImg.paste(TapDataBg,(206,729),TapDataBg.split()[3])
        else:
            TapDataBg = Image.open(f"{MAIMAI_MUSIC_DATA}/Total_1.png").convert('RGBA')
            TapDataDraw = ImageDraw.Draw(TapDataBg)
            for index,chart in enumerate(self.music_info.charts):
                ds = self.music_info.ds[index]
                tempFont = ImageFont.truetype(f"{FONT_PATH}/RoGSanSrfStd-Bd.otf", 50, encoding='utf-8')
                ds = decimalPoints(ds,1)
                fontSizeX,fontSizeY = tempFont.getsize(ds)
                TapDataDraw.text((350+(202*index) - int(fontSizeX/2),100 - int(fontSizeY/2)), ds , "white" , tempFont)
                notes = list(chart['notes'])
                total_notes = sum(notes)

                if len(notes) == 4:
                    notes.insert(len(notes)-1, '-')
                notes.insert(0, total_notes)

                for note_index,note_count in enumerate(notes):
                    tempFont = ImageFont.truetype(f"{FONT_PATH}/RoGSanSrfStd-Bd.otf", 48, encoding='utf-8')
                    note_count = str(note_count)
                    fontSizeX,fontSizeY = tempFont.getsize(note_count)
                    TapDataDraw.text((350+(202*index) - int(fontSizeX/2),162+(88*note_index) ), note_count , "black" , tempFont)
            self.baseImg.paste(TapDataBg,(307,729),TapDataBg.split()[3])
        return self.baseImg


