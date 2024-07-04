# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw,ImageFont
from .utils import get_abstract_cover_path,get_nomal_cover_path
from src.libraries.maimai.maimaidx_music import total_list
from src.libraries.data_handle.abstract_db_handle import abstract
from src.libraries.GLOBAL_CONSTANT import VERSION_MAP,DELETED_MUSIC
from src.libraries.GLOBAL_PATH import FONT_PATH,COMPLETION_STATUS_TABLE_PATH
def calculate(num):
    if num % 10 == 0:
        return num // 10
    else:
        return num // 10 + 1

def generate_version_image(version:str,is_abstract:bool):
    result_list = total_list.by_versions_for_cn(VERSION_MAP[version])
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

    h = 180

    for song_info in result_list:
        if int(song_info.id) in DELETED_MUSIC:
            continue
        level= song_info.level[3]
        default_song_list[level].append(song_info.id)

    for music_list in default_song_list.values():
        item = len(music_list)
        if item > 0:
            h = h+ (85*calculate(item))
    none_bg = Image.new("RGBA",(1000,h+100),(255,255,255,0))
    bg_img = Image.open(f"{COMPLETION_STATUS_TABLE_PATH}/版本完成表背景/{version}.png").convert('RGBA')
    img = bg_img
    if version in ["祭","祝"]:
        none_bg.paste(bg_img,(0,0),bg_img)
        img = none_bg

    draw = ImageDraw.Draw(img)

    ix = 130
    iy = 120

    if is_abstract:
        abstract_cover_file_map = abstract.get_abstract_file_name_all()

    fontstyle = ImageFont.truetype(f'{FONT_PATH}/SourceHanSans_17.ttf',40)

    for item in default_song_list.items():
        if item[1]:
            count = 0
            rcount = 0
            content = str(item[0])
            # 计算文本的尺寸
            x0,yo = fontstyle.getsize(content)
            # 绘制文本描边
            outline_color = "black"
            draw.text((60-(x0/2)-1, iy-1), content, font=fontstyle, fill=outline_color)  # 左上
            draw.text((60-(x0/2)+1, iy-1), content, font=fontstyle, fill=outline_color)  # 右上
            draw.text((60-(x0/2)-1, iy+1), content, font=fontstyle, fill=outline_color)  # 左下
            draw.text((60-(x0/2)+1, iy+1), content, font=fontstyle, fill=outline_color)  # 右下
            # 绘制文本
            text_color = "white"
            draw.text((60-(x0/2), iy), content, font=fontstyle, fill=text_color)

            for song in range(0,len(default_song_list[item[0]])):
                id = default_song_list[item[0]][song]

                if is_abstract:
                    cover_path = get_abstract_cover_path(int(id),abstract_cover_file_map)
                else:
                    cover_path = get_nomal_cover_path(int(id))
                cover = Image.open(cover_path).convert('RGBA')

                cover = cover.resize((70, 70), Image.ANTIALIAS)
                img.paste(cover, (ix, iy), cover)

                count = count + 1
                rcount = rcount + 1
                ix = ix + 80
                if count == 10 and len(default_song_list[item[0]])!= rcount:
                    ix = 130
                    iy = iy+85
                    count = 0
            iy = iy + 100
            ix = 130
    p = "版本牌子完成表-抽象封面" if is_abstract else "版本牌子完成表-标准封面"
    img.save(f"{COMPLETION_STATUS_TABLE_PATH}/{p}/{version}.png")

    return True