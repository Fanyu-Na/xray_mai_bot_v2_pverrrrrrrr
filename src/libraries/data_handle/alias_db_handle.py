import pymongo
import time
from datetime import datetime,timedelta
from src.libraries.maimai.maimaidx_music import total_list
import re
from src.libraries.GLOBAL_CONSTANT import MONGO_HOST,MONGO_DATABASE,MONGO_PASSWORD,MONGO_PORT,MONGO_USERNAME

class Alias(object):
    def __init__(self):
        username = MONGO_USERNAME
        password = MONGO_PASSWORD
        host = MONGO_HOST
        port = MONGO_PORT
        database_name = MONGO_DATABASE
        connection_string = f'mongodb://{username}:{password}@{host}:{port}/{database_name}'
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client['xray-mai-bot']
        self.alias_collection = self.db['alias']
        self.alias_examine_collection = self.db['alias_examine']
        self.counters_collection = self.db['counters']

    def queryMusicByAlias(self,alias: str):
        if list(set(list(alias))) == ['.']:
            return []
        escaped_alias = re.escape(alias)
        search_result = list(self.alias_collection.find(
            {"alias":{'$regex': f'^{escaped_alias}$', '$options': 'i'},"enable":True},
            {"_id":0,"music_id":1}))
        music_ids = [m['music_id'] for m in search_result]
        return music_ids

    def SearchAlias(self,music_id:str):
        alias_data = self.alias_collection.find_one({"music_id":music_id})
        return list(set(alias_data['alias']))


alias = Alias()
