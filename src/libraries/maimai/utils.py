from src.libraries.data_handle.abstract_db_handle import abstract
from pathlib import Path
from src.libraries.GLOBAL_PATH import ABSTRACT_COVER_PATH,NORMAL_COVER_PATH

def get_cover_path(song_id,is_abstract:bool):
    id = int(song_id)
    if is_abstract:
        file_name,nickname = abstract.get_abstract_file_name(id)
        if nickname != "抽象画未收录":
            CoverPath = ABSTRACT_COVER_PATH + f'/{file_name}.png'
        else:
            CoverPath = f'{NORMAL_COVER_PATH}/{id}.png'
    else:
        CoverPath = f'{NORMAL_COVER_PATH}/{id}.png'

    if Path(CoverPath).exists():
        return CoverPath
    else:
        if Path(NORMAL_COVER_PATH + f'/{id-10000}.png').exists():
            return NORMAL_COVER_PATH + f'/{id-10000}.png'
        if Path(NORMAL_COVER_PATH + f'/{id+10000}.png').exists():
            return NORMAL_COVER_PATH + f'/{id+10000}.png'
        if Path(NORMAL_COVER_PATH + f'/{id-100000}.png').exists():
            return NORMAL_COVER_PATH + f'/{id-100000}.png'
        if Path(NORMAL_COVER_PATH + f'/{id-110000}.png').exists():
            return NORMAL_COVER_PATH + f'/{id-110000}.png'
        return f'{ABSTRACT_COVER_PATH}/1000.jpg'