import time
import re
import asyncio
from nonebot import on_command, on_regex, on_message, on_shell_command, require
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageEvent, MessageSegment, Bot
from nonebot.params import CommandArg, ShellCommandArgs, RawCommand, EventMessage
from nonebot.rule import Namespace, ArgumentParser
from nonebot.log import logger
from src.libraries.data_handle.abstract_db_handle import abstract
from src.libraries.maimai.maimaidx_music import *
from src.libraries.image_handle.image import *
from src.libraries.data_handle.userdata_handle import userdata
from src.libraries.maimai.maimai_play_best50.maimai_play_best50_new import generate_best_50 as nb
from src.libraries.maimai.maimai_play_best50.maimai_play_best50_old_design import generate_best_50 as ob
from src.libraries.maimai.maimai_play_best50.utils import filter_map
from src.libraries.data_handle.alias_db_handle import alias
from src.libraries.maimai.maimai_fortune.utils import gen_fortune
from src.libraries.maimai.player_music_score.player_music_score import generate_info
from src.libraries.maimai.completion_status_table.new_pcst_base_img import generate_user_data
from src.libraries.maimai.completion_status_table.user_level_completion_status_table import generate_user_level_cst
from .utils import inner_level_q,music_image,query_PANDORA_PARADOXXX_score_content,get_maidx_location,read_location_json,query_user_version_plate_schedule_result,query_user_top_result
from src.libraries.GLOBAL_PATH import RANK_TABLE_PATH,COMPLETION_STATUS_TABLE_PATH,MAIMAIDX_PATH,COLLECTIBLES_PATH
from src.libraries.GLOBAL_CONSTANT import VERSION_DF_MAP
from src.libraries.maimai.near_maimai import getCityName,get_send_result


search_music_abstract_parser = ArgumentParser()
search_music_abstract_parser.add_argument("music_id")
search_music_abstract_parser.add_argument("-n", "--normal", action='store_false')


query_ds = on_command('查定数', priority=20)
random_choice_music = on_regex(r"^[来整搞弄]个(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?", priority=20)
what_maimai = on_regex(r".*mai.*什么", priority=20)

@query_ds.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    level = str(args).strip().split(" ")
    if len(level) > 2 or len(level) == 0:
        await query_ds.finish("Xray检测到您格式输入错误啦！！命令格式为\n定数查歌 <定数>\n定数查歌 <定数下限> <定数上限>")
    if len(level) == 1:
        result_set = inner_level_q(float(level[0]))
    else:
        result_set = inner_level_q(float(level[0]), float(level[1]))
    if len(result_set) > 50:
        await query_ds.finish("找到超过50条数据(")
    s = ""
    for elem in result_set:
        s += f"{elem[0]}. {elem[1]} {elem[3]} {elem[4]}({elem[2]})\n"
    await query_ds.finish(s.strip())

@random_choice_music.handle()
async def _(event: GroupMessageEvent):
    regex = "[来整搞弄随]个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)"
    res = re.match(regex, str(event.get_message()).lower())
    try:
        if res.groups()[0] == "dx":
            tp = ["DX"]
        elif res.groups()[0] == "sd" or res.groups()[0] == "标准":
            tp = ["SD"]
        else:
            tp = ["SD", "DX"]
        level = res.groups()[2]
        if res.groups()[1] == "":
            music_data = total_list.filter(level=level, type=tp)
        else:
            music_data = total_list.filter(
                level=level, diff=['绿黄红紫白'.index(res.groups()[1])], type=tp)
        userConfig = userdata.getUserData(event.get_user_id())
        is_abstract = userConfig.get("is_abstract",True)
        await random_choice_music.send(music_image(music_data.random(), is_abstract))
    except Exception as e:
        await random_choice_music.finish("Xray出错啦,估计是指令错了,请检查语法！")

@what_maimai.handle()
async def _(event: GroupMessageEvent):
    userConfig = userdata.getUserData(event.get_user_id())
    is_abstract = userConfig.get("is_abstract",True)
    await what_maimai.finish(music_image(total_list.random(), is_abstract))


search_music_by_title = on_command("S ", aliases={'s ', 'Search '}, priority=20)
@search_music_by_title.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    name = str(args)
    if name == "":
        await search_music_by_title.finish("不懂就问,你让我查什么???")
    res = total_list.filter(title_search=name)
    if not res:
        await search_music_by_title.finish('未找到歌曲')
    filter_result = []
    for music in res:
        ds = ''
        for d in music['ds']:
            ds += str(d) + '/'
        filter_result.append(f"{music['id']}. {music['title']}-{ds[:-1]}\n")
    await search_music_by_title.send(filter_result)

search_music_by_id = on_shell_command("id", parser=search_music_abstract_parser, priority=20)
@search_music_by_id.handle()
async def _(event: GroupMessageEvent, foo: Namespace = ShellCommandArgs()):
    music_id = str(foo.music_id).strip()
    print(music_id)
    music = total_list.by_id(music_id)
    userConfig = userdata.getUserData(event.get_user_id())
    is_abstract = userConfig.get("is_abstract",foo.normal)
    if music:
        await search_music_by_id.send(music_image(music, is_abstract))
    else:
        await search_music_by_id.send("Xray未找到该乐曲~")

search_music_by_id_for_text = on_regex(r"^([绿黄红紫白]?)msong ([0-9]+)", priority=20)
@search_music_by_id_for_text.handle()
async def _(event: GroupMessageEvent, message: Message = EventMessage()):
    regex = "([绿黄红紫白]?)msong ([0-9]+)"
    groups = re.match(regex, str(message)).groups()
    level_labels = ['绿', '黄', '红', '紫', '白']
    if groups[0] != "":
        try:
            level_index = level_labels.index(groups[0])
            level_name = ['Basic', 'Advanced', 'Expert', 'Master', 'Re: MASTER']
            name = groups[1]
            music = total_list.by_id(name)
            chart = music['charts'][level_index]
            ds = music['ds'][level_index]
            level = music['level'][level_index]
            file_name, nickname = abstract.get_abstract_file_name(music.id)
            print(file_name,nickname)
            file = f"https://download.fanyu.site/abstract/{file_name}.png"
            if len(chart['notes']) == 4:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
BREAK: {chart['notes'][3]}
谱师: {chart['charter']}
抽象画作者:{nickname}'''
            else:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
TOUCH: {chart['notes'][3]}
BREAK: {chart['notes'][4]}
谱师: {chart['charter']}
抽象画作者:{nickname}'''
            await search_music_by_id_for_text.send(Message([
                MessageSegment("text", {"text": f"{music['id']}. {music['title']}\n"}),
                MessageSegment.image(file),
                MessageSegment("text", {"text": msg})
            ]))
        except Exception:
            await search_music_by_id_for_text.send("未找到该谱面")
    else:
        name = groups[1]
        music = total_list.by_id(name)
        try:
            file_name, nickname = abstract.get_abstract_file_name(music.id)
            file = f"https://download.fanyu.site/abstract/{file_name}.png"
            await search_music_by_id_for_text.send(Message([
                MessageSegment("text", {
                    "text": f"{music['id']}. {music['title']}\n"
                }),
                MessageSegment.image(file)
                ,
                MessageSegment("text", {
                    "text": f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['cn_from']}\n难度: {'/'.join(music['level'])}\n抽象画作者:{nickname}"
                })
            ]))
        except Exception:
            await search_music_by_id_for_text.send("未找到该乐曲")

today_maimai = on_command('今日舞萌', priority=20)
@today_maimai.handle()
async def _(event: GroupMessageEvent):
    await today_maimai.finish('咦,你是不是来错地方了,试试\'抽签\'获取今日运势吧')


mai_fortune = on_command('抽签', priority=3)
@mai_fortune.handle()
async def _(event: GroupMessageEvent):
    img = gen_fortune(event)
    await mai_fortune.send([MessageSegment.reply(event.message_id),
                     MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}")])
    
search_music_by_alias = on_regex(r".+是什么歌", priority=20)
@search_music_by_alias.handle()
async def _(event: GroupMessageEvent):
    regex = "(.+)是什么歌"
    name = re.match(regex, str(event.get_message())).groups()[0].strip()
    result_set = alias.queryMusicByAlias(name)
    userConfig = userdata.getUserData(event.get_user_id())
    is_abstract = userConfig.get("is_abstract",True)
    if len(result_set) == 1:
        if result_set[0] == "未找到":
            await search_music_by_alias.finish("此歌曲国服已经删除。")
        if result_set[0] == "834":
            PANDORA_PARADOXXX_score_content = query_PANDORA_PARADOXXX_score_content(str(event.user_id))
            if PANDORA_PARADOXXX_score_content:
                await search_music_by_alias.finish(PANDORA_PARADOXXX_score_content)
        music = total_list.by_id(result_set[0])
        await search_music_by_alias.finish(music_image(music, is_abstract))
    elif len(result_set) == 0:
        res = total_list.filter(title_search=name)
        if len(res) == 1:
            music = total_list.by_id(res[0].id)
            await search_music_by_alias.finish(music_image(music, is_abstract))
        if not res:
            await search_music_by_alias.finish(
                f"没有找到名为{name}的歌曲，可以使用<添加别名 歌曲id 别名>申请添加别名,获得玩家三票同意将添加成功")
        filter_result = []
        for music in res:
            ds = ''
            for d in music['ds']:
                ds += str(d) + '/'
            filter_result.append(f"{music['id']}. {music['title']}-{ds[:-1]}\n")
        await search_music_by_alias.finish(filter_result)
    else:
        s = ''
        for result in result_set:
            if result == "未找到":
                continue
            try:
                music = total_list.by_id(result)
                s += '\n' + music.id + '.' + music.title
            except:
                continue
        await search_music_by_alias.finish(f"看,是不是这些：{s}")

search_alias_by_id = on_command('查看别名', priority=20)
@search_alias_by_id.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    music = total_list.by_id(str(args).strip())
    if music:
        aliasnames = alias.SearchAlias(str(args).strip())
        if aliasnames:
            s = f'{music.id}.{music.title}的别名有'
            for name in aliasnames:
                s += f'\n{name}'
            await search_alias_by_id.send(s)
        else:
            await search_alias_by_id.send(f'{music.id}.{music.title}暂无别名')
    else:
        await search_alias_by_id.send(f'未找到此歌曲')


maimai_score_line = on_command('分数线', priority=20)
@maimai_score_line.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    r = "([绿黄红紫白])(id)?([0-9]+)"
    argv = str(args).strip().split(" ")
    if len(argv) == 1 and argv[0] == '帮助':
        s = '''此功能为查找某首歌分数线设计。
命令格式：分数线 <难度+歌曲id> <分数线>
例如：分数线 紫799 100
命令将返回分数线允许的 TAP GREAT 容错以及 BREAK 50落等价的 TAP GREAT 数。
以下为 TAP GREAT 的对应表：
GREAT/GOOD/MISS
TAP\t1/2.5/5
HOLD\t2/5/10
SLIDE\t3/7.5/15
TOUCH\t1/2.5/5
BREAK\t5/12.5/25(外加200落)'''
        await maimai_score_line.send(Message([{
            "type": "image",
            "data": {
                "file": f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"
            }
        }]))
    elif len(argv) == 2:
        try:
            grp = re.match(r, argv[0]).groups()
            level_labels = ['绿', '黄', '红', '紫', '白']
            level_labels2 = ['Basic', 'Advanced',
                             'Expert', 'Master', 'Re:MASTER']
            level_index = level_labels.index(grp[0])
            chart_id = grp[2]
            line = float(argv[1])
            music = total_list.by_id(chart_id)
            chart: Dict[Any] = music['charts'][level_index]
            tap = int(chart['notes'][0])
            slide = int(chart['notes'][2])
            hold = int(chart['notes'][1])
            touch = int(chart['notes'][3]) if len(chart['notes']) == 5 else 0
            brk = int(chart['notes'][-1])
            total_score = 500 * tap + slide * 1500 + hold * 1000 + touch * 500 + brk * 2500
            break_bonus = 0.01 / brk
            break_50_reduce = total_score * break_bonus / 4
            reduce = 101 - line
            if reduce <= 0 or reduce >= 101:
                raise ValueError
            await maimai_score_line.send(f'''{music['title']} {level_labels2[level_index]}
分数线 {line}% 允许的最多 TAP GREAT 数量为 {(total_score * reduce / 10000):.2f}(每个-{10000 / total_score:.4f}%),
BREAK 50落(一共{brk}个)等价于 {(break_50_reduce / 100):.3f} 个 TAP GREAT(-{break_50_reduce / total_score * 100:.4f}%)''')
        except Exception:
            await maimai_score_line.send("Xray检测到格式错误,输入“分数线 帮助”以查看帮助信息")


mai_best_50_pic = on_regex(r"(.*?)b?50( \S+|$)", priority=20)
@mai_best_50_pic.handle()
async def _(event: GroupMessageEvent, message: Message = EventMessage()):
    start = time.perf_counter()
    regex = "(.*?)b?50( \S+|$)"
    if re.match(regex, str(message)):
        filter_mode,username = re.match(regex, str(message)).groups()
        if filter_mode != '':
            key_list = list(filter_map.keys())
            key_list.append("sp")
            if filter_mode not in key_list:
                regex = r'(\d+)(\+)?'
                match = re.match(regex, filter_mode)
                if not match:
                    if len(filter_mode) <= 4:
                        await mai_best_50_pic.finish(f'Xray Bot暂时不支持{filter_mode}Best50查询')
                    else:
                        await mai_best_50_pic.finish()
        else:
            filter_mode = None
    if username == "":
        payload = {'qq': str(event.user_id), 'b50': 1}
        mode = 2
    else:
        payload = {'username': username.strip(), 'b50': 1}
        mode = 1
    username = username if username else ""

    userConfig = userdata.getUserData(event.get_user_id())
    is_abstract = userConfig.get("is_abstract",True)
    best50_style = userConfig.get("style_index","1")



    if best50_style in ["1","3"]:
        img, success, ratingS = await nb(payload,is_abstract,userConfig,best50_style,filter_mode)
    elif best50_style == "2":
        img, success, ratingS = await ob(payload,is_abstract,userConfig,best50_style,filter_mode)

    end = time.perf_counter()
    runTime = end - start
    if success == 400:
        if mode == 2:
            await mai_best_50_pic.send(
                f"☠你没有绑定查分器哩.....\n或者在使用该指令时添加你的查分器用户名!!!\n例:Xray b50 xray")
        else:
            await mai_best_50_pic.send(f"Xray没有查找到当前用户名,请检查用户名是否正确")
    elif success == 403:
        await mai_best_50_pic.send("人家不让俺查,你要查什么嘛，哼！\nps:看置顶 or 精华 or 公告")
    else:
        if ratingS == 0:
            await mai_best_50_pic.finish('Xray查到你还没有上传成绩呢,请先上传成绩再来~')

        best50_message_list = [MessageSegment.reply(event.message_id),
                                MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"),
                                MessageSegment.text(f"本次b50生成时间:{runTime:.2f}秒")]
        


        if userConfig.get("style_index","None") == "None":
            best50_message_list.append(MessageSegment.text(f"\nps:可使用【设置主题 主题ID】指令,切换Best50主题样式。\nps:可用主题ID有【1】、【2】、【3】。"))
        if userConfig.get("is_abstract","None") == "None":
            best50_message_list.append(MessageSegment.text(f"\nps:可使用【开启\关闭抽象画】指令，设置全局抽象画配置。"))

        best50_message_list.append(MessageSegment.text(f"\nps:自定义Best50样式，可使用以下指令。"))
        best50_message_list.append(MessageSegment.text(f"\nps:可使用【设置头像/姓名框/背景 收藏品ID】指令，收藏品ID可以使用【查看收藏品】指令查询。"))


        await mai_best_50_pic.send(best50_message_list)
        if username == "" and event.user_id in [381268035, 3434334409]:
            await mai_best_50_pic.finish(f'卧槽,是我爹😍')
        if ratingS >= 16000:
            await mai_best_50_pic.finish(f'卧槽,大爹😍')
        if username.lower() == 'xray':
            await mai_best_50_pic.finish('卧槽,我是大爹😋')

find_address = on_regex(r"(.*)(在哪|哪里)有[m|M]ai打", priority=20)
@find_address.handle()
async def _(event: GroupMessageEvent):
    regex = "(.*)(在哪|哪里)有[m|M]ai打"
    name = re.findall(regex, str(event.get_message()))
    if name:
        city = name[0][0]
        if city in ['日本', '立本', '霓虹', '霓虹国', '美国']:
            await find_address.finish(f'你查个锤子的{city}')
        maidx_location = await get_maidx_location()
        total_location = 0
        query_location_result = '结果如下:\n'
        for i in maidx_location:
            if city in i['address']:
                query_location_result += '店名:' + i['arcadeName'] + '\n'
                query_location_result += '地址:' + i['address'] + '\n'
                query_location_result += '台数:' + str(i['machineCount']) + '\n\n'
                total_location = total_location + 1
        query_location_result += '数据仅供参考('
        if total_location > 0:
            query_location_result = query_location_result.lstrip()
            await find_address.send(
                [MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(query_location_result)), encoding='utf-8')}")])
        else:
            await find_address.send('没得Mai打,快找朱总(要是发现你们查一些很离谱的地方,我就,我就....')

find_new_address = on_command('哪里有新Mai', aliases={'哪里有新mai', '哪里新开业'}, priority=20)
@find_new_address.handle()
async def _(event: MessageEvent):
    new_location = await get_maidx_location()
    old_location = read_location_json()

    new_address = []
    old_address = []

    for i in new_location:
        new_address.append(i['placeId'])
    for j in old_location:
        old_address.append(j['placeId'])

    new_open_location = list(set(new_address) - set(old_address))
    if len(new_open_location) == 0:
        await find_new_address.finish('还没有新机,不要着急,朱总马上安排了')
    query_location_result = '结果如下:\n'
    for i in new_location:
        if i['placeId'] in new_open_location:
            query_location_result += '店名:' + i['arcadeName'] + '\n'
            query_location_result += '地址:' + i['address'] + '\n'
            query_location_result += '台数:' + str(i['machineCount']) + '\n\n'
    query_location_result += '月末请联系作者更新最新数据('
    query_location_result = query_location_result.lstrip()
    await find_new_address.send(
        [MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(query_location_result)), encoding='utf-8')}")])

view_collectibles = on_command('查看收藏品', priority=20)
@view_collectibles.handle()
async def _(event: GroupMessageEvent):
    file_list = ["nameplate","frame","icon"]
    image_message_list = []
    for filename in file_list:
        with open(f"{COLLECTIBLES_PATH}/{filename}.png", mode="rb") as f:
            data = f.read()
        image_message_list.append(MessageSegment.image(data))
    await view_collectibles.send(image_message_list)
    await view_collectibles.send('自定义抽象姓名框:http://download.fanyu.site/plate/')

# todo 重构获得未完成抽象画代码 解决更新抽象画后不同步问题
get_unfinished_abstract = on_command('来张没画的', priority=20)
@get_unfinished_abstract.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    try:
        tp = ["SD", "DX"]
        level = str(args)
        if level == '':
            await get_unfinished_abstract.send(music_image(unfinish_list.random(), True))
        else:
            music_data = unfinish_list.filter(level=level, type=tp)
            await get_unfinished_abstract.send(music_image(music_data.random(), True))
    except Exception as e:
        print(e)
        await get_unfinished_abstract.finish("抽象画已经制霸了......")

user_version_plate_schedule = on_regex('.(将|极|神|舞舞|者)进度', priority=20)

@user_version_plate_schedule.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    regex = "(.)(将|极|神|舞舞|者)进度"
    reresult = re.match(regex, str(event.get_message()))
    if reresult:
        groups = reresult.groups()
        ver = groups[0]
        if ver in VERSION_DF_MAP.keys():
            sdmsg = query_user_version_plate_schedule_result(ver, str(event.user_id), groups[1], groups[0])
            await user_version_plate_schedule.send(sdmsg)
        else:
            await user_version_plate_schedule.finish(f'未找到{groups[0]}代')
    else:
        await user_version_plate_schedule.send('格式错误')



user_player_info = on_command("info", priority=20)

@user_player_info.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    user_id = str(event.user_id)
    song_id = str(args).strip()
    userConfig = userdata.getUserData(event.get_user_id())
    is_abstract = userConfig.get("is_abstract",True)
    songinfo = total_list.by_id(song_id)
    if not songinfo:
        songinfo = total_list.by_title(song_id)
    if not songinfo:
        result_set = alias.queryMusicByAlias(song_id)
        if len(result_set) == 1:
            songinfo = total_list.by_id(result_set[0])
            song_id = result_set[0]
        elif len(result_set) > 1:
            await user_player_info.finish(f"关键字检索到多个{song_id},查询歌曲后使用歌曲ID\nps:{song_id}是什么歌")
        else:
            songinfo = 0
    if songinfo:
        song_id= songinfo.id
        isDone, img = await generate_info(int(song_id), user_id, is_abstract)
        if isDone:
            await user_player_info.send([MessageSegment.reply(event.message_id),
                                    MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}")])
        else:
            await user_player_info.finish('未找到ID' + song_id)
    else:
        await user_player_info.finish('未找到ID' + song_id)

user_top_power_df = on_command('我有多菜', priority=20)
@user_top_power_df.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    arg = str(args).strip()
    if arg == '':
        msg = await query_user_top_result(str(event.user_id), 'qq')
    else:
        msg = await query_user_top_result(arg, 'username')
    try:
        await user_top_power_df.send(msg)
    except:
        await user_top_power_df.send(
            [MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(msg)), encoding='utf-8')}")])

# user_version_plate_completion_status_table = on_regex('.(将|极|神|舞舞)完成表', priority=20)
# @user_version_plate_completion_status_table.handle()
# async def _(bot: Bot, event: GroupMessageEvent):
#     regex = "(.)(将|极|神|舞舞)完成表"
#     reresult = re.match(regex, str(event.get_message()))
#     if reresult:
#         groups = reresult.groups()
#         ver = groups[0]
#         if ver in VERSION_DF_MAP.keys():
#             userConfig = userdata.getUserData(event.get_user_id())
#             is_abstract = userConfig.get("is_abstract",True)
#             Img = generate_user_version_plate_cst(ver, groups[1], str(event.user_id),is_abstract)
#             await user_version_plate_completion_status_table.send([MessageSegment.reply(event.message_id), MessageSegment.image(
#                 f"base64://{str(image_to_base64(Img), encoding='utf-8')}")])
#         else:
#             await user_version_plate_completion_status_table.finish(f'未找到{groups[0]}代')
#     else:
#         await user_version_plate_completion_status_table.send('格式错误')

new_user_version_plate_completion_status_table = on_regex('.(将|极|神|舞舞)新?完成表', priority=20)
@new_user_version_plate_completion_status_table.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    regex = "(.)(将|极|神|舞舞)新?完成表"
    reresult = re.match(regex, str(event.get_message()))
    if reresult:
        groups = reresult.groups()
        ver = groups[0]
        if ver in '舞霸':
            await new_user_version_plate_completion_status_table.send('霸者、舞系完成表暂不支持')
        else:
            if ver in VERSION_DF_MAP.keys():
                userConfig = userdata.getUserData(event.get_user_id())
                is_abstract = userConfig.get("is_abstract",True)
                Img = generate_user_data(ver, groups[1],is_abstract,userConfig,str(event.user_id))
                if isinstance(Img,str):
                    await new_user_version_plate_completion_status_table.finish(Img)
                else:
                    await new_user_version_plate_completion_status_table.send([MessageSegment.reply(event.message_id), MessageSegment.image(
                        f"base64://{str(image_to_base64(Img), encoding='utf-8')}")])
            else:
                await new_user_version_plate_completion_status_table.finish(f'未找到{groups[0]}代')
    else:
        await new_user_version_plate_completion_status_table.send('格式错误')

user_level_completion_status_table = on_regex(r'^([0-9]+\+?)完成表', priority=20)
@user_level_completion_status_table.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    regex = r'^([0-9]+\+?)完成表'
    reresult = re.match(regex, str(event.get_message()))
    if reresult:
        level = reresult.groups()[0]
        userConfig = userdata.getUserData(event.get_user_id())
        is_abstract = userConfig.get("is_abstract",True)
        Img = generate_user_level_cst(level, str(event.user_id),is_abstract)
        await user_level_completion_status_table.send([MessageSegment.reply(event.message_id),
                                    MessageSegment.image(f"base64://{str(image_to_base64(Img), encoding='utf-8')}")])
    else:
        await user_level_completion_status_table.send('格式错误')

rank_table = on_command('段位表', priority=20)
@rank_table.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    arg = str(args).strip()
    if arg == "":
        await rank_table.send(
            "现在可获取的段位表有：\n1. 段位认定 舞萌DX2024\n2. 真段位认定 舞萌DX2024\n3. 随机段位认定 舞萌DX2024")
    elif arg in ["1", "2", "3"]:
        userConfig = userdata.getUserData(event.get_user_id())
        is_abstract = userConfig.get("is_abstract",True)
        if arg in '12':
            if is_abstract:
                with open(f"{RANK_TABLE_PATH}/SDGBq1.40_course_{arg}.png", mode="rb") as f:
                    data = f.read()
            else:
                with open(f"{RANK_TABLE_PATH}/SDGBq1.40_normal_course_{arg}.jpg", mode="rb") as f:
                    data = f.read()
        await rank_table.send([MessageSegment.image(data)])
    else:
        await rank_table.send("段位表参数错误")
        
level_table = on_regex(r'^([0-9]+\+?)定数表', priority=20)
@level_table.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    regex = r'^([0-9]+\+?)定数表'
    reresult = re.match(regex, str(event.get_message()))
    if reresult:
        level = reresult.groups()[0]
        userConfig = userdata.getUserData(event.get_user_id())
        is_abstract = userConfig.get("is_abstract",True)
        tabel_mode = "难度完成表-抽象封面" if is_abstract else "难度完成表-标准封面"
        imgpath = f"{COMPLETION_STATUS_TABLE_PATH}/{tabel_mode}/{level}.png"
        if os.path.exists(imgpath):
            with open(imgpath, mode="rb") as f:
                img_data = f.read()
            await level_table.send([MessageSegment.reply(event.message_id), MessageSegment.image(img_data)])
        else:
            await level_table.send('Xray目前只支持7-15级的定数表捏')
    else:
        await level_table.send('格式错误')


plate_condition = on_regex(r'^牌子条件$',priority=20)
@plate_condition.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    with open(f"{MAIMAIDX_PATH}/plate_condition.png", mode="rb") as f:
        data = f.read()
    await plate_condition.send([MessageSegment.image(data)])

Nearby_Dx = on_command('附近mai', priority=20)
@Nearby_Dx.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    logger.success("用户使用附近mai")


@Nearby_Dx.got(prompt='请发送当前位置(使用QQ位置)', key="address")
async def _(bot: Bot, event: GroupMessageEvent):
    # 正则获取当前用户经纬度信息和地理位置
    Nearby_Dx.block = True
    for msg in event.message:
        if msg.type == "json":
            data = json.loads(msg.data['data'])['meta']['Location.Search']
            lat = data.get("lat", 0)
            lng = data.get("lng", 0)
            if lat or lng:
                break
    if lat:
        await Nearby_Dx.send('稍等,高达地图正在全力搜索！！！')
        try:
            await bot.delete_msg(message_id=event.message_id)
        except:
            await Nearby_Dx.send('Xray好像没有权限撤回你的消息呢,记得撤回自己的位置呢。')

        result = await getCityName(lng, lat)
        if not result:
            await Nearby_Dx.finish('😥好惨 没有找到')
        SendList, BY_SendList = await get_send_result(result)
        try:
            await bot.send_group_forward_msg(group_id=event.group_id, messages=SendList)
        except:
            await bot.send_group_forward_msg(group_id=event.group_id, messages=BY_SendList)
    else:
        await Nearby_Dx.finish('消息格式异常')