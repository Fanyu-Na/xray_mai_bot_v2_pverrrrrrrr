# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw,ImageFont
from src.libraries.maimai.completion_status_table.utils import get_abstract_cover_path,get_nomal_cover_path
from src.libraries.maimai.maimaidx_music import total_list
from src.libraries.data_handle.abstract_db_handle import abstract
from src.libraries.GLOBAL_CONSTANT import VERSION_MAP,DELETED_MUSIC,VERSION_DF_MAP,MAIPLATE_FILE_ID_MAP,TRADITIONAL2SIMPLIFIED
from src.libraries.GLOBAL_PATH import FONT_PATH,NEW_COMPLETION_STATUS_TABLE_PATH,COMPLETION_STATUS_TABLE_PATH,PLATE_PATH,ICON_PATH
from src.libraries.data_handle.userdata_handle import userdata
from pathlib import Path
import requests
def calculate(num,i):
    if num % i == 0:
        return num // i
    else:
        return num // i + 1
    
def get_music_info(finishs,id:int,level:int):
    result = finishs['verlist']
    for item in result:
        if item['id'] == id and item['level_index'] == level:
            return {'fc':item['fc'],'fs':item['fs'],'achievements':item['achievements']}
    return {}

    
def query_user_plate_data(versions,user_id:str):
    version_list = total_list.by_version_for_plate(versions)
    payload = {'qq':user_id,'version':versions}
    r = requests.post("https://www.diving-fish.com/api/maimaidxprober/query/plate", json=payload)
    finishs = r.json()
    version_song_info = {}
    for song in version_list:
        version_song_info[song.id] = {}
        for index ,level in enumerate(song['level']):
            version_song_info[song.id][index] = get_music_info(finishs,int(song.id),index)
    return version_song_info

def generate_music_data(version:str,is_abstract:bool):
    result_list = total_list.by_versions_for_cn(VERSION_MAP[version])
    default_song_list = {"15":[],"14+":[],"14":[],"13+":[],"13":[],"12+":[],"12":[],"11+":[],"11":[],"10+":[],"10":[],"9+":[],"9":[],"8+":[],"8":[],"7+":[],"7":[],"6":[],"5":[],"4":[],"3":[],"2":[],"1":[]}

    for song_info in result_list:
        if int(song_info.id) in DELETED_MUSIC:
            continue
        if int(song_info.id) > 99999:
            continue
        level= song_info.level[3]
        default_song_list[level].append(song_info.id)
        if version in ['舞霸']:
            if len(song_info.level) == 5:
                level= song_info.level[4]
                default_song_list[level].append(song_info.id)
    music_data_hight = 42
    for music_list in default_song_list.values():

        item = len(music_list)
        if item > 0:
            music_data_hight = music_data_hight+38
            music_data_hight = music_data_hight+(127*calculate(item,10))

    music_data_hight = music_data_hight-38
    music_data_img = Image.new("RGBA",(1420,music_data_hight),(255,255,255,255))

    ix = 216
    iy = 42

    if is_abstract:
        abstract_cover_file_map = abstract.get_abstract_file_name_all()


    for item in default_song_list.items():
        if item[1]:
            count = 0
            rcount = 0

            level_log_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/level/{item[0]}.png").convert('RGBA')
            music_data_img.paste(level_log_img,(40,iy),level_log_img)
            for song in range(0,len(default_song_list[item[0]])):
                id = default_song_list[item[0]][song]

                music_box = Image.new("RGBA",(113,125),(255,255,255,0))

                if is_abstract:
                    cover_path = get_abstract_cover_path(int(id),abstract_cover_file_map)
                else:
                    cover_path = get_nomal_cover_path(int(id))
                cover = Image.open(cover_path).convert('RGBA')
                cover = cover.resize((95, 95), Image.ANTIALIAS)
                music_box.paste(cover, (9, 8), cover)

                music_bg = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/song/框.png").convert('RGBA')
                music_box.paste(music_bg, (0, 0), music_bg)
                musicImageDraw = ImageDraw.Draw(music_box)
                tempFont = ImageFont.truetype(FONT_PATH + "/GlowSansSC-Normal-Bold.otf", 10, encoding='utf-8')
                fx,fy = tempFont.getsize(str(id))
                musicImageDraw.text((92 - (fx/2), 113 - (fy/2)), str(id), font=tempFont, fill="white")
                music_data_img.paste(music_box,(ix,iy),music_box)


                count = count + 1
                rcount = rcount + 1
                ix = ix + 113
                if count == 10 and len(default_song_list[item[0]])!= rcount:
                    ix = 216
                    iy = iy+127
                    count = 0
            iy = iy + 127+38
            ix = 216
    return music_data_img

def generate_full_version(version:str,is_abstract:bool):
    music_data_img = generate_music_data(version,is_abstract)
    music_data_img_hight = music_data_img.height
    full_version_hight = 107+700+music_data_img_hight+63+141+57+73
    full_version_img = Image.new("RGBA",(1600,full_version_hight),(255,255,255,0))
    if Path(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/background/有模糊/{version}.png").exists():
        bg_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/background/有模糊/{version}.png").convert('RGBA')
        full_version_img.paste(bg_img,(0,0),bg_img)
    else:
        return None
    top_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/top.png").convert('RGBA')
    full_version_img.paste(top_img,(90,107),top_img)
    full_version_img.paste(music_data_img,(90,107+700),music_data_img.split()[3])
    foot_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/foot.png").convert('RGBA')
    full_version_img.paste(foot_img,(90,107+700+music_data_img_hight),foot_img.split()[3])
    credits_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/Credits.png").convert('RGBA')
    full_version_img.paste(credits_img,(0,107+700+music_data_img_hight+63+57),credits_img.split()[3])

    text_bg = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/text/background.png").convert('RGBA')
    full_version_img.paste(text_bg,(143,402),text_bg.split()[3])

    progress_bg = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/progress/background.png").convert('RGBA')
    full_version_img.paste(progress_bg,(589,402),progress_bg.split()[3])
    if is_abstract:
        full_version_img.save(f"{COMPLETION_STATUS_TABLE_PATH}/new_pcst_base_img_abstract/{version}.png")
    else:
        full_version_img.save(f"{COMPLETION_STATUS_TABLE_PATH}/new_pcst_base_img_normal/{version}.png")
    return full_version_img

def check_completion_conditions(plate_mode,music_data):
    if not music_data:
        return False
    if plate_mode == '将':
        return music_data['achievements'] >= 100
    
    elif plate_mode == '极':
        return music_data['fc'] in ['fc','ap','fcp','app']

    elif plate_mode == '神':
        return music_data['fc'] in ['ap','app']

    elif plate_mode == '舞舞':
        return music_data['fs'] in ['fsd','fsdp']

def generate_user_music_data(version:str,plate_mode,uid:str):
    result_list = total_list.by_versions_for_cn(VERSION_MAP[version])
    version_song_info = query_user_plate_data(VERSION_DF_MAP[version],uid)
    default_song_list = {"15":[],"14+":[],"14":[],"13+":[],"13":[],"12+":[],"12":[],"11+":[],"11":[],"10+":[],"10":[],"9+":[],"9":[],"8+":[],"8":[],"7+":[],"7":[],"6":[],"5":[],"4":[],"3":[],"2":[],"1":[]}

    for song_info in result_list:
        if int(song_info.id) in DELETED_MUSIC:
            continue
        if int(song_info.id) > 99999:
            continue
        level= song_info.level[3]
        default_song_list[level].append(song_info.id)
        if version in ['舞霸']:
            if len(song_info.level) == 5:
                level= song_info.level[4]
                default_song_list[level].append(song_info.id)
    music_data_hight = 42
    for music_list in default_song_list.values():

        item = len(music_list)
        if item > 0:
            music_data_hight = music_data_hight+38
            music_data_hight = music_data_hight+(127*calculate(item,10))

    music_data_hight = music_data_hight-38
    music_data_img = Image.new("RGBA",(1420,music_data_hight),(255,255,255,0))

    ix = 216
    iy = 42

    basic_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/song/C_Basic.png").convert('RGBA')
    advanced_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/song/C_Advanced.png").convert('RGBA')
    expert_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/song/C_Expert.png").convert('RGBA')
    master_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/song/C_Master.png").convert('RGBA')

    fullcombo_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/song/极.png").convert('RGBA')
    sss_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/song/将.png").convert('RGBA')
    allpefect_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/song/神.png").convert('RGBA')
    fdx_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/song/舞.png").convert('RGBA')
    confirm_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/song/确认.png").convert('RGBA')

    diff_music_data = {
        "total":0,
        "basic":0,
        "advanced":0,
        "expert":0,
        "master":0,
    }

    difficulty_num = 0

    plate_mode_img_list = {
        "极":fullcombo_img,
        "将":sss_img,
        "神":allpefect_img,
        "舞舞":fdx_img
    }

    diff_img_list = {
        0:basic_img,
        1:advanced_img,
        2:expert_img,
        3:master_img
    }




    for item in default_song_list.items():
        if item[1]:
            count = 0
            rcount = 0

            level_log_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/level/{item[0]}.png").convert('RGBA')
            music_data_img.paste(level_log_img,(40,iy),level_log_img)
            for song in range(0,len(default_song_list[item[0]])):
                id = default_song_list[item[0]][song]

                music_box = Image.new("RGBA",(113,125),(255,255,255,0))
                diff_list = ['basic','advanced','expert','master']

                diff_music_data['total'] = diff_music_data['total']+1

                diff_all_completion = True
                for level_index in [0,1,2,3]:
                    check_result = check_completion_conditions(plate_mode,version_song_info.get(str(id),{}).get(level_index,{}))
                    if check_result:
                        diff_music_data[diff_list[level_index]] = diff_music_data[diff_list[level_index]]+1
                        completion_img = diff_img_list[level_index]
                        music_box.paste(completion_img,(0,0),completion_img)
                    else:
                        diff_all_completion = False
                
                if diff_all_completion:
                    plate_completion_img = plate_mode_img_list[plate_mode]
                    music_box.paste(plate_completion_img,(0,0),plate_completion_img)
                else:
                    if check_completion_conditions(plate_mode,version_song_info.get(str(id),{}).get(3,{})):
                        plate_completion_img = plate_mode_img_list[plate_mode]
                        music_box.paste(plate_completion_img,(0,0),plate_completion_img)
                        # music_box.paste(confirm_img,(0,0),confirm_img)
                    else:
                        if total_list.by_id(str(id)).ds[3] >= 13.7:
                            difficulty_num = difficulty_num+1

                music_data_img.paste(music_box,(ix,iy),music_box)
                count = count + 1
                rcount = rcount + 1
                ix = ix + 113
                if count == 10 and len(default_song_list[item[0]])!= rcount:
                    ix = 216
                    iy = iy+127
                    count = 0
            iy = iy + 127+38
            ix = 216
    # p = "版本牌子完成表-抽象封面" if is_abstract else "版本牌子完成表-标准封面"
    # music_data_img.save(f"{COMPLETION_STATUS_TABLE_PATH}/test/{version}.png")
    # none_bg.show()

    return music_data_img,diff_music_data,difficulty_num

def tran_plate_name(plate_name:str):
    for k,v in TRADITIONAL2SIMPLIFIED.items():
        plate_name = plate_name.replace(k,v)
    return plate_name

def generate_user_data(version:str,plate_mode:str,is_abstract:bool,userConfig,uid):
    try:
        if is_abstract:
            base_bg_path = f"/new_pcst_base_img_abstract/{version}.png"
        else:
            base_bg_path = f"/new_pcst_base_img_normal/{version}.png"
        base_img = Image.open(COMPLETION_STATUS_TABLE_PATH + base_bg_path).convert('RGBA')
    except:
        base_img = generate_full_version(version,is_abstract)

    # 姓名框
    plate_name = tran_plate_name(version+plate_mode)
    try:
        plate_id = MAIPLATE_FILE_ID_MAP[plate_name]
        plateImage = Image.open(PLATE_PATH + f"/UI_Plate_{plate_id}.png").convert('RGBA')
    except:
        return f"错误的文件:{plate_name}"
    plateImage = plateImage.resize((1314,212))

    base_img.paste(plateImage,(143,161),plateImage.split()[3])
    # 头像
    iconImage = Image.open(ICON_PATH + f'/UI_Icon_{userConfig.get("icon","000011")}.png').convert('RGBA')
    iconImage = iconImage.resize((198,198))
    base_img.paste(iconImage,(150,168),iconImage.split()[3])

    user_music_data_img,diff_music_data,difficulty_num = generate_user_music_data(version,plate_mode,uid)
    base_img.paste(user_music_data_img,(90,107+700),user_music_data_img.split()[3])

    # text
    lst = list(diff_music_data.values())
    
    if all(x == lst[0] for x in lst):
        text_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/text/已完成.png").convert('RGBA')
        base_img.paste(text_img,(143,402),text_img.split()[3])
    else:
        text_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/text/未完成.png").convert('RGBA')
        textImageDraw = ImageDraw.Draw(text_img)

        # residue_master
        residue_master = str(difficulty_num)
        if len(residue_master) == 3:
            tempFont = ImageFont.truetype(FONT_PATH + "/江城圆体 700W.ttf", 45, encoding='utf-8')
        else:
            tempFont = ImageFont.truetype(FONT_PATH + "/江城圆体 700W.ttf", 53, encoding='utf-8')
        fx,fy = tempFont.getsize(residue_master)
        textImageDraw.text((265 - (fx/2), 97 - (fy/2)), residue_master, font=tempFont, fill=(255,170,198))

        residue_music = sum(list(diff_music_data.values())[0]-count for count in diff_music_data.values())
        single_play_count = calculate(residue_music,3)
        double_play_count = calculate(residue_music,4)

        tempFont = ImageFont.truetype(FONT_PATH + "/江城圆体 700W.ttf", 43, encoding='utf-8')
        fx,fy = tempFont.getsize(str(single_play_count))
        textImageDraw.text((372 - (fx/2), 153- (fy/2)), str(single_play_count), font=tempFont, fill=(255,170,198))
        fx,fy = tempFont.getsize(str(double_play_count))
        textImageDraw.text((280 - (fx/2), 206 - (fy/2)), str(double_play_count), font=tempFont, fill=(255,170,198))

        if plate_mode != "舞舞":
            hour = (double_play_count*12) // 60
            min = (double_play_count*12) % 60
        else:
            hour = (double_play_count*16) // 60
            min = (double_play_count*16) % 60
        fx,fy = tempFont.getsize(str(hour))
        textImageDraw.text((193   - (fx/2), 258 - (fy/2)), str(hour), font=tempFont, fill=(255,170,198))
        fx,fy = tempFont.getsize(str(min))
        textImageDraw.text((328   - (fx/2), 258 - (fy/2)), str(min), font=tempFont, fill=(255,170,198))
        base_img.paste(text_img,(143,402),text_img.split()[3])


    # 进度条
    all_progress = generate_all_progress(diff_music_data['total']*4,sum([item[1] for item in diff_music_data.items() if item[0] in ['basic','advanced','expert','master']]))
    base_img.paste(all_progress,(602,402),all_progress)
    far_map = {
        0:(603,526-13),
        1:(1028,526-13),
        2:(603,635-13),
        3:(1028,635-13),
    }
    for index,diff in enumerate(['basic','advanced','expert','master']):
        far_progress = generate_progress(diff_music_data['total'],diff_music_data[diff],index)
        base_img.paste(far_progress,far_map[index],far_progress)

    # base_img.show()
    base_img = base_img.convert("RGB")
    return base_img

    



def generate_progress(total:int,num:int,diff):
    diff_list = ["Fra_Basic","Fra_Advanced","Fra_Expert","Fra_Master"]
    progress_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/progress/{diff_list[diff]}.png").convert('RGBA')
    completion_rate = (total-num)/total
    p_w = 393
    un_completion_width = int(p_w*completion_rate)
    full_version_img = Image.new("RGBA",(un_completion_width,78),(11,13,25,255))
    progress_img.paste(full_version_img,(404-un_completion_width,24),full_version_img.split()[3])
    if completion_rate != 0:
        radius_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/progress/radius.png").convert('RGBA')
        progress_img.paste(radius_img,(404-un_completion_width-3,24),radius_img.split()[3])

        fra_count_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/progress/Fra_Count.png").convert('RGBA')
        progress_img.paste(fra_count_img,(0,0),fra_count_img.split()[3])
        progressImageDraw = ImageDraw.Draw(progress_img)
        tempFont = ImageFont.truetype(FONT_PATH + "/FOT-RaglanPunchStd-UB.otf", 32, encoding='utf-8')
        p = str(int((num/total)*100))
        fx,fy = tempFont.getsize(str(p)+"%")
        progressImageDraw.text((126 - (fx/2), 62 - (fy/2)), str(p)+"%", font=tempFont, fill="white")

        tempFont = ImageFont.truetype(FONT_PATH + "/FOT-RaglanPunchStd-UB.otf", 25, encoding='utf-8')
        fx,fy = tempFont.getsize(str(num))
        progressImageDraw.text((213 - (fx/2), 63 - (fy/2)), str(num), font=tempFont, fill="white")
        fx,fy = tempFont.getsize(str(total))
        progressImageDraw.text((289 - (fx/2), 63 - (fy/2)), str(total), font=tempFont, fill="white")
    else:
        fra_clear_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/progress/Fra_Clear.png").convert('RGBA')
        progress_img.paste(fra_clear_img,(0,0),fra_clear_img.split()[3])
    return progress_img

def generate_all_progress(total:int,num:int):
    progress_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/progress/All_Backpack.png").convert('RGBA')
    completion_rate = (total-num)/total
    p_w = 818
    un_completion_width = int(p_w*completion_rate)
    full_version_img = Image.new("RGBA",(un_completion_width,78),(11,13,25,255))
    progress_img.paste(full_version_img,(829-un_completion_width,24),full_version_img.split()[3])
    if completion_rate != 0:
        radius_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/progress/radius.png").convert('RGBA')
        progress_img.paste(radius_img,(829-un_completion_width-3,24),radius_img.split()[3])

        all_count_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/progress/All_Count.png").convert('RGBA')
        progress_img.paste(all_count_img,(0,0),all_count_img.split()[3])
        progressImageDraw = ImageDraw.Draw(progress_img)
        tempFont = ImageFont.truetype(FONT_PATH + "/FOT-RaglanPunchStd-UB.otf", 28, encoding='utf-8')
        p = str(int((num/total)*100))
        fx,fy = tempFont.getsize(str(p)+"%")
        progressImageDraw.text((598 - (fx/2), 62 - (fy/2)), str(p)+"%", font=tempFont, fill="white")

        tempFont = ImageFont.truetype(FONT_PATH + "/FOT-RaglanPunchStd-UB.otf", 25, encoding='utf-8')
        fx,fy = tempFont.getsize(str(num))
        progressImageDraw.text((685 - (fx/2), 63 - (fy/2)), str(num), font=tempFont, fill="white")
        fx,fy = tempFont.getsize(str(total))
        progressImageDraw.text((761 - (fx/2), 63 - (fy/2)), str(total), font=tempFont, fill="white")
    else:
        all_clear_img = Image.open(f"{NEW_COMPLETION_STATUS_TABLE_PATH}/progress/All_Clear.png").convert('RGBA')
        progress_img.paste(all_clear_img,(0,0),all_clear_img.split()[3])

    return progress_img





# userConfig = userdata.getUserData("381268035")
# print(userConfig)
# icon = userConfig.get('icon','000011')


# for version in VERSION_DF_MAP.keys():
#     if version in "霸舞双":
#         continue

# generate_user_data("晓","将",False,userConfig)

# generate_user_data