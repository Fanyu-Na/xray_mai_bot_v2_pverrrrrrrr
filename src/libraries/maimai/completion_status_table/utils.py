from pathlib import Path
import requests
from PIL import Image
from io import BytesIO
from src.libraries.GLOBAL_PATH import NORMAL_COVER_PATH,ABSTRACT_COVER_PATH

def get_nomal_cover_path(music_id):
    cover_path = Path(f"{NORMAL_COVER_PATH}/{music_id}.png")
    if cover_path.exists():
        return cover_path
    else:
        music_id = int(int(music_id)-10000)
        cover_path = Path(f"{NORMAL_COVER_PATH}/{music_id}.png")
        if cover_path.exists():
            return cover_path
        else:
            music_id = int(int(music_id)+20000)
            cover_path = Path(f"{NORMAL_COVER_PATH}/{music_id}.png")
            if cover_path.exists():
                return cover_path
            else:
                raise Exception('未找到封面',music_id)
            
            
def open_image_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 404:
            return -1
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content)).convert('RGBA')
        return image
    except Exception as e:
        print(f"Error: {e}")
        return None
            
def get_abstract_cover_path(music_id,abstract_cover_file_map):
    cover_path = abstract_cover_file_map.get(str(music_id),f"{str(music_id)}_1")

    img_path = Path(f"{ABSTRACT_COVER_PATH}/{cover_path}.png")
    if img_path.exists():
        return img_path
    else:
        return get_nomal_cover_path(int(music_id))