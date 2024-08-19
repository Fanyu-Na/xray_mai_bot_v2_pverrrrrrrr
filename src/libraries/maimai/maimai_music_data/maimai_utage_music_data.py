"""
This module let you draw the UTAGE music data image.
"""
import json
import re

from PIL import Image, ImageFont, ImageDraw

from src.libraries.GLOBAL_PATH import UTAGE_MAIMAI_MUSIC_DATA, FONT_PATH, ABSTRACT_COVER_PATH
from src.libraries.data_handle.abstract_db_handle import abstract
from src.libraries.execution_time import timing_decorator
from src.libraries.maimai.maimai_music_data.utils import truncate_text
from src.libraries.maimai.maimaidx_music import total_list
from src.libraries.maimai.utils import get_cover_path


class MaiUtageMusicData:
    """
    Draw UTAGE music data image.
    """

    def __init__(self, music_id: int, is_abstract: bool) -> None:
        self.abstract_artist = ""
        self.music_id = music_id
        self.music_info = total_list.by_id(str(music_id))
        self.is_abstract = is_abstract
        self.base_img = Image.new("RGBA", (1700, 2000), (0, 0, 0, 0))
        self.base_img_draw = ImageDraw.Draw(self.base_img)
        self.utg_music_data = self.get_utg_music_data()

    def get_utg_music_data(self):
        """
        Get UTAGE music data.
        """
        path = UTAGE_MAIMAI_MUSIC_DATA + "/utg_song_data.json"
        with open(path, 'r', encoding="utf-8") as file:
            jp_obj = json.load(file)
        music_data = jp_obj.get(str(self.music_id), {})
        print(music_data)
        return music_data

    @timing_decorator
    def draw(self):
        """
        Main function to draw the image.
        For UTAGE.
        """
        self.draw_cover()
        self.draw_bg()
        self.draw_artist()
        self.draw_title()
        self.draw_utage_type()
        self.draw_music_id()
        self.draw_bpm()
        self.draw_type()
        self.draw_comment()
        self.draw_charter()
        self.draw_version()
        self.draw_abstract_artist()
        self.draw_referrals_num()
        self.draw_buddy()
        return self.base_img

    def draw_charter(self):
        """
        draw the charter
        """
        level_icon_image = (
            Image.open(
                f"{UTAGE_MAIMAI_MUSIC_DATA}/levels/"
                f"{str(self.utg_music_data['level'][0]).replace('?', '')}.png"
            )
            .convert('RGBA')
        )
        if len(self.utg_music_data['charts']) > 1:
            charter_bg = Image.open(
                f"{UTAGE_MAIMAI_MUSIC_DATA}/Charter_2.png"
            ).convert('RGBA')
            start_y = 246
            charter_bg.paste(
                level_icon_image,
                (181, 118 - 49),
                level_icon_image
            )
        else:
            charter_bg = Image.open(
                f"{UTAGE_MAIMAI_MUSIC_DATA}/Charter_1.png"
            ).convert('RGBA')
            start_y = 295
            charter_bg.paste(
                level_icon_image,
                (181, 118),
                level_icon_image
            )
        charter_draw = ImageDraw.Draw(charter_bg)
        for data_chart in self.utg_music_data['charts']:
            chart_notes = list(data_chart['notes'])

            font = get_font("FOT-RaglanPunchStd-UB.otf", 53)
            _, _, text_width, text_height = font.getbbox(str(sum(chart_notes)))
            charter_draw.text(
                (482 - text_width / 2, start_y - text_height / 2),
                str(sum(chart_notes)),
                "white",
                font
            )

            font = get_font("FOT-RaglanPunchStd-UB.otf", 45)
            for index, chart in enumerate(chart_notes):
                note = str(chart)
                _, _, text_width, text_height = font.getbbox(note)
                charter_draw.text(
                    (672 + (190 * index) - text_width / 2, start_y - text_height / 2),
                    note,
                    "white",
                    font
                )

            start_y += 105
        self.base_img.paste(
            charter_bg,
            (0, 919),
            charter_bg
        )

    def draw_referrals_num(self):
        """
        draw the referrals num
        """
        font = get_font("FOT-RaglanPunchStd-UB.otf", 75)
        referrals_num = self.utg_music_data.get('referrals_num')
        # single player
        if referrals_num['mode'] == 'normal':
            referrals_num_img = Image.open(
                f"{UTAGE_MAIMAI_MUSIC_DATA}/referrals_num/normal.png"
            ).convert('RGBA')
            self.base_img.paste(
                referrals_num_img,
                (1002, 1404),
                referrals_num_img.split()[3]
            )
            player = str(referrals_num['player'][0])
            _, _, text_width, text_height = font.getbbox(player)

            # single player draw
            self.base_img_draw.text(
                (1002 + 383 - text_width / 2, 1399 + 99 - text_height / 2),
                player,
                "white",
                font
            )

        # two player
        elif referrals_num['mode'] == 'buddy_normal':
            referrals_num_img = Image.open(
                f"{UTAGE_MAIMAI_MUSIC_DATA}/referrals_num/buddy_normal.png").convert('RGBA')
            self.base_img.paste(
                referrals_num_img,
                (1002, 1404),
                referrals_num_img.split()[3]
            )
            player_left = str(referrals_num['player'][0])
            player_right = str(referrals_num['player'][1])
            _, _, text_width, text_height = font.getbbox(player_left)

            # player left draw
            self.base_img_draw.text(
                (1002 + 289 - text_width / 2, 1399 + 99 - text_height / 2),
                player_left,
                "white",
                font
            )

            _, _, text_width, text_height = font.getbbox(player_right)

            # player right draw
            self.base_img_draw.text(
                (1002 + 494 - text_width / 2, 1399 + 99 - text_height / 2),
                player_right,
                "white",
                font
            )

        # three player
        elif referrals_num['mode'] == 'buddy_clamp':
            referrals_num_img = Image.open(
                f"{UTAGE_MAIMAI_MUSIC_DATA}/referrals_num/buddy_clamp.png"
            ).convert('RGBA')
            self.base_img.paste(
                referrals_num_img,
                (1002, 1404),
                referrals_num_img.split()[3]
            )
            player_left = str(referrals_num['player'][0])
            player_mid = str(referrals_num['player'][1])
            player_right = str(referrals_num['player'][2])
            _, _, text_width, text_height = font.getbbox(player_left)
            self.base_img_draw.text(
                (1002 + 255 - text_width / 2, 1399 + 99 - text_height / 2),
                player_left,
                "white",
                font
            )
            _, _, text_width, text_height = font.getbbox(player_mid)
            self.base_img_draw.text(
                (1002 + 389 - text_width / 2, 1399 + 99 - text_height / 2),
                player_mid,
                "white",
                font
            )
            _, _, text_width, text_height = font.getbbox(player_right)
            self.base_img_draw.text(
                (1002 + 525 - text_width / 2, 1399 + 99 - text_height / 2),
                player_right,
                "white",
                font
            )

    def draw_abstract_artist(self):
        """
        draw the abstract artist
        """
        abstract_artist = self.abstract_artist
        font = get_font("GlowSansSC-Normal-ExtraBold.otf", 47)
        _, _, text_width, text_height = font.getbbox(abstract_artist)
        self.base_img_draw.text(
            (
                676 - text_width / 2,
                1463 + 104 * 2 - text_height / 2
            ),
            abstract_artist,
            "white",
            font
        )

    def draw_version(self):
        """
        draw the version
        """
        font = get_font("GlowSansSC-Normal-ExtraBold.otf", 47)
        jp_ver = self.utg_music_data.get('jp_update')
        cn_ver = self.utg_music_data.get('cn_update')
        _, _, text_width, text_height = font.getbbox(jp_ver)
        self.base_img_draw.text(
            (676 - text_width / 2, 1463 - text_height / 2),
            jp_ver,
            "white",
            font
        )
        _, _, text_width, text_height = font.getbbox(cn_ver)
        self.base_img_draw.text(
            (
                676 - text_width / 2,
                1463 + 104 - text_height / 2
            ),
            cn_ver,
            "white",
            font
        )
        return font

    def draw_comment(self):
        """
        Draw music comment.
        """
        font = get_font("GlowSansSC-Normal-Bold.otf", 40)
        comment = self.utg_music_data.get('comment', 'LET PLAY')
        _, _, text_width, text_height = font.getbbox(comment)
        self.base_img_draw.text(
            (850 - text_width / 2, 840 - text_height / 2),
            comment,
            "white",
            font
        )

    def draw_type(self):
        """
        Draw chart type
        """
        type_img = Image.open(
            f"{UTAGE_MAIMAI_MUSIC_DATA}/others/type_{self.utg_music_data['type'].lower()}.png"
        ).convert('RGBA')
        self.base_img.paste(
            type_img,
            (0, 0),
            type_img.split()[3]
        )

    def draw_bpm(self):
        """
        Draw music BPM.
        """
        font = get_font("GlowSansSC-Normal-Bold.otf", 42)
        _, _, text_width, text_height = font.getbbox(str(self.music_info.bpm))
        self.base_img_draw.text(
            (987 - text_width / 2, 629 - text_height / 2),
            str(self.music_info.bpm),
            "white",
            font
        )

    def draw_music_id(self):
        """
        Draw music ID.
        """
        font = get_font("GlowSansSC-Normal-Bold.otf", 42)
        _, _, text_width, text_height = font.getbbox(self.music_info.id)
        self.base_img_draw.text(
            (815 - text_width / 2, 629 - text_height / 2),
            self.music_info.id,
            "white",
            font
        )

    def draw_utage_type(self):
        """
        Draw utage type.
        """
        font = get_font("M Plus 5.ttf", 46)
        matches = re.findall(r'\[(\w+|\W+)]', self.music_info.title.title())
        utage_type = truncate_text(
            matches[0] if matches else [''],
            font,
            800
        )
        _, _, text_width, text_height = font.getbbox(utage_type)
        self.base_img_draw.text(
            (876 - text_width / 2, 447 - text_height / 2),
            utage_type,
            "white",
            font
        )

    def draw_title(self):
        """
        Draw music title.
        """
        font = get_font("SourceHanSans_35.otf", 60)
        title = truncate_text(
            self.music_info.title,
            font,
            800
        )
        self.base_img_draw.text(
            (727, 246),
            title,
            "white",
            font
        )

    def draw_artist(self):
        """
        Draw music artist.
        """
        font = get_font("GlowSansSC-Normal-Bold.otf", 43)
        artist = truncate_text(
            self.music_info.artist,
            font,
            800
        )
        self.base_img_draw.text(
            (729, 180),
            artist,
            "white",
            font
        )

    def draw_cover(self):
        """
        Copy music cover image.
        """
        if self.is_abstract:
            abstract_data = abstract.get_abstract_id_list()
            if int(self.music_id) in abstract_data:
                file_name, nickname = abstract.get_abstract_file_name(str(self.music_id))
                filename = file_name
                self.abstract_artist = nickname
                music_cover_img = Image.open(
                    f'{ABSTRACT_COVER_PATH}/{filename}.png'
                ).convert('RGBA')
            else:
                self.abstract_artist = "抽象画未收录"
                music_cover_img = Image.open(
                    get_cover_path(self.music_id, False)
                ).convert('RGBA')
        else:
            self.abstract_artist = "-"
            music_cover_img = Image.open(
                get_cover_path(self.music_id, False)
            ).convert('RGBA')
        music_cover_img = music_cover_img.resize((494, 494))
        self.base_img.paste(
            music_cover_img,
            (191, 172),
            music_cover_img.split()[3]
        )

    def draw_bg(self):
        """
        Copy background image.
        """
        background_img = Image.open(
            f"{UTAGE_MAIMAI_MUSIC_DATA}/background.png"
        ).convert('RGBA')
        self.base_img.paste(
            background_img,
            (0, 0),
            background_img.split()[3]
        )

    def draw_buddy(self):
        """
        Draw buddy icon.
        """
        if self.utg_music_data['referrals_num']['mode'] == 'buddy_normal' or \
                self.utg_music_data['referrals_num']['mode'] == 'buddy_clamp':
            buddy_img = Image.open(
                f"{UTAGE_MAIMAI_MUSIC_DATA}/others/buddy.png"
            ).convert('RGBA')
            self.base_img.paste(
                buddy_img,
                (0, 0),
                buddy_img.split()[3]
            )


def get_font(font_name: str, font_size: int):
    """
    Get font.
    """
    return ImageFont.truetype(
        f"{FONT_PATH}/{font_name}",
        font_size,
        encoding='utf-8'
    )
