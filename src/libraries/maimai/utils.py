from src.libraries.data_handle.abstract_db_handle import abstract
from pathlib import Path
from src.libraries.GLOBAL_PATH import ABSTRACT_COVER_PATH,NORMAL_COVER_PATH,ABSTRACT_DOWNLOAD_URL
import requests


def download_image(url, save_path):  
    try:  
        # 发送HTTP GET请求  
        response = requests.get(url)  
        # 确保请求成功  
        response.raise_for_status()  
          
        # 将图片内容写入到本地文件  
        with open(save_path, 'wb') as file:  
            file.write(response.content)  
          
        print(f"图片已保存到 {save_path}")  
    except requests.RequestException as e:  
        print(e)  



def check_file_and_save_img(file_name):
    file_path = Path(ABSTRACT_COVER_PATH + f'/{str(file_name)}.png')
    if not file_path.exists():
        url = ABSTRACT_DOWNLOAD_URL + f'/{file_name}.png'
        download_image(url,file_path)
    else:
        return '存在'

def get_abstract_cover_path_by_file_id(file_name):
    CoverPath = ABSTRACT_COVER_PATH + f'/{file_name}.png'
    check_file_and_save_img(file_name)
    return CoverPath


def get_cover_path(song_id,is_abstract:bool):
    id = int(song_id)
    if is_abstract:
        file_name,nickname = abstract.get_abstract_file_name(id)
        if nickname != "抽象画未收录":
            CoverPath = ABSTRACT_COVER_PATH + f'/{file_name}.png'
            check_file_and_save_img(file_name)
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