import json
from pathlib import Path
from typing import Dict
from nonebot.log import logger
from src.libraries.GLOBAL_PATH import DATA_ADMIN_PATH
class Admin(object):
    def __init__(self):
        self.data_dir = Path(DATA_ADMIN_PATH).absolute()
        self.admin_path = self.data_dir / "admin.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data: Dict[str, Dict[str, Dict[str, list]]] = {}
        self.__load()

    def __load(self):
        if self.admin_path.exists() and self.admin_path.is_file():
            with self.admin_path.open("r", encoding="utf-8") as f:
                data: dict = json.load(f)
            self.data = data
            logger.success("读取词库位于 " + str(self.admin_path))
        else:
            self.data = {"group_id":[],"user_id":[]}
            self.__save()
            logger.success("创建词库位于 " + str(self.admin_path))

    def __save(self):
        with self.admin_path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def get_groupid(self):
        return self.data.get('group_id',[])

    def get_userid(self):
        return self.data.get('user_id',[])
    
    def get_along_black(self):
        return self.data.get('along_black',[])

    def add_group(self,group_id:int):
        if group_id in self.data['group_id']:
            return f'{str(group_id)}已开启,请勿重复开启'
        else:
            self.data['group_id'].append(group_id)
            self.__save()
            return f'{str(group_id)}开启成功'

    def del_group(self,group_id:int):
        if group_id in self.data['group_id']:
            self.data['group_id'].remove(group_id)
            self.__save()
            return f'{str(group_id)}关闭成功'
        else:
            return f'{str(group_id)}未开启,无法关闭群'

    def add_user(self,user_id:int):
        if user_id in self.data['user_id']:
            return f'{str(user_id)}已拉黑,请勿重复拉黑'
        else:
            self.data['user_id'].append(user_id)
            self.__save()
            return f'{str(user_id)}拉黑成功'

    def del_user(self,user_id:int):
        if user_id in self.data['user_id']:
            self.data['user_id'].remove(user_id)
            self.__save()
            return f'{str(user_id)}解除黑名单成功'
        else:
            return f'{str(user_id)}未拉黑,无法解除黑名单'

    def add_along_black(self,group_id:int):
        if group_id in self.data['along_black']:
            return f'{str(group_id)}已关闭龙图模式,请勿重复关闭'
        else:
            self.data['along_black'].append(group_id)
            self.__save()
            return f'{str(group_id)}关闭龙图模式成功'
        
    def del_along_black(self,group_id:int):
        if group_id in self.data['along_black']:
            self.data['along_black'].remove(group_id)
            self.__save()
            return f'{str(group_id)}恢复龙图模式成功'
        else:
            return f'{str(group_id)}未关闭,无法开启龙图模式'
admin = Admin()
