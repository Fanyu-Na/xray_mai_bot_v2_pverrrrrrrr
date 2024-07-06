from PIL import Image,ImageFont,ImageDraw
import os
from src.libraries.data_handle.abstract_db_handle import abstract
from src.libraries.GLOBAL_PATH import FORTUNE_PATH,FONT_PATH,NORMAL_COVER_PATH
from src.libraries.maimai.utils import get_abstract_cover_path_by_file_id

def _getCharWidth(o) -> int:
    widths = [
        (126, 1), (159, 0), (687, 1), (710, 0), (711, 1), (727,
                                                            0), (733, 1), (879, 0), (1154, 1), (1161, 0),
        (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369,
                                                        1), (8426, 0), (9000, 1), (9002, 2), (11021, 1),
        (12350, 2), (12351, 1), (12438, 2), (12442,
                                                0), (19893, 2), (19967, 1), (55203, 2), (63743, 1),
        (64106, 2), (65039, 1), (65059, 0), (65131,
                                                2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
        (120831, 1), (262141, 2), (1114109, 1),
    ]
    if o == 0xe or o == 0xf:
        return 0
    for num, wid in widths:
        if o <= num:
            return wid
    return 1

def _coloumWidth(s: str):
    res = 0
    for ch in s:
        res += _getCharWidth(ord(ch))
    return res

def _changeColumnWidth(s: str, len: int) -> str:
    res = 0
    sList = []
    for ch in s:
        res += _getCharWidth(ord(ch))
        if res <= len:
            sList.append(ch)
    return ''.join(sList)

def makeFortune(year:str,month:str,day:str,week:str,lucky:str,should,noshould,music):
    fortune = Image.new('RGB',(1080,1248),(255,255,255))


    if int(music.id) in abstract.get_abstract_id_list():
        file_name,nickname = abstract.get_abstract_file_name(str(music.id))
        file_path = get_abstract_cover_path_by_file_id(file_name)
        cover = Image.open(file_path)
    else:
        if os.path.exists(f'{NORMAL_COVER_PATH}/{(music.id)}.png'):
            cover = Image.open(f'{NORMAL_COVER_PATH}/{(music.id)}.png')
        else:
            cover = Image.open(f'{NORMAL_COVER_PATH}/{(str(int(music.id)-10000))}.png')
    # cover = Image.open('388.png')
    cover = cover.resize((366,366))
    fortune.paste(cover,(548,827))
    Bg = Image.open(f'{FORTUNE_PATH}/背景.png').convert('RGBA')
    fortune.paste(Bg,(0,0),Bg.split()[3])
    draw = ImageDraw.Draw(fortune)
    fontstyle = ImageFont.truetype(f'{FONT_PATH}/隶书.TTF',48)
    draw.text((329,188),week,(224,88,76),fontstyle)
    fontstyle = ImageFont.truetype(f'{FONT_PATH}/华文行楷.TTF',48)
    draw.text((63,136),f'{year}年{str(int(month))}月',(224,88,76),fontstyle)
    fontstyle = ImageFont.truetype(f'{FONT_PATH}/华文行楷.TTF',111)
    if len(day) == 1:
        draw.text((128,211),day,(224,88,76),fontstyle)
    else:
        draw.text((113,211),day,(224,88,76),fontstyle)
    fontstyle = ImageFont.truetype(f'{FONT_PATH}/华文行楷.TTF',85)
    if len(lucky) == 1:
        draw.text((425,416),lucky,(232,225,206),fontstyle)
    else:
        draw.text((405,416),lucky,(232,225,206),fontstyle)
    fontstyle = ImageFont.truetype(f'{FONT_PATH}/华文行楷.TTF',42)

    if len(should) == 1:
        draw.text((72,706),should[0],(224,88,76),fontstyle)
    else:
        draw.text((72,706),should[0],(224,88,76),fontstyle)
        draw.text((72,756),should[1],(224,88,76),fontstyle)

    if len(noshould) == 1:
        draw.text((72,1011),noshould[0],(224,88,76),fontstyle)
    else:
        draw.text((72,1011),noshould[0],(224,88,76),fontstyle)
        draw.text((72,1061),noshould[1],(224,88,76),fontstyle)

    fontstyle = ImageFont.truetype(f'{FONT_PATH}/男朋友字体.ttf',36)
    title= music.title
    if _coloumWidth(title) > 18:
        title = _changeColumnWidth(title, 17) + '...'
    art = music.artist
    if _coloumWidth(art) > 17:
        art = _changeColumnWidth(art, 16) + '...'
    level = ''
    for d in music.level:
        level += str(d) + '/'
    level = level[:-1]
    ds = ''
    for d in music.ds:
        ds += str(d) + '/'
    ds = ds[:-1]
    draw.text((548,496),f'ID:{str(music.id)}\n标题:{title}\n艺术家:{art}\nBPM:{str(music.bpm)}\n分类：{str(music.genre)}\n等级：{level}\n定数：{ds}',(224,88,76),fontstyle)
    # fortune.show()
    return fortune

def generate_fortune(year:str,month:str,day:str,week:str,lucky:str,should,noshould,music):
    fortune_img = makeFortune(year,month,day,week,lucky,should,noshould,music)
    return fortune_img