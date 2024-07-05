import random
import pymongo
from src.libraries.GLOBAL_CONSTANT import MONGO_HOST,MONGO_DATABASE,MONGO_PASSWORD,MONGO_PORT,MONGO_USERNAME,MONGO_DB
class Abstract(object):
    def __init__(self):
        username = MONGO_USERNAME
        password = MONGO_PASSWORD
        host = MONGO_HOST
        port = MONGO_PORT
        database_name = MONGO_DATABASE
        connection_string = f'mongodb://{username}:{password}@{host}:{port}/{database_name}'
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[MONGO_DB]
        self.abstract_collection = self.db['abstract']
        self.counters_collection = self.db['counters']

    def get_abstract_id_list(self):
        search_data =  self.abstract_collection.find()
        music_list = [int(i['music_id']) for i in search_data]
        return music_list
    
    def get_abstract_file_name(self, music_id):
        music_id = str(music_id)
        if int(music_id) in self.get_abstract_id_list():
            music_abstract_data = self.abstract_collection.find_one(
                {"music_id": music_id})
            if music_abstract_data:
                rdr = random.choice(music_abstract_data['abstract_data'])
                return rdr["file_name"], rdr["nickname"]
            else:
                return f"{str(music_id)}_1", "Xray Art Team"
        else:
            return f"{str(music_id)}", "抽象画未收录"


    def get_abstract_data_by_id(self, music_id: str):
        doc = self.abstract_collection.find_one({"music_id": music_id})
        if doc:
            abstract_data = doc['abstract_data']
            if abstract_data:
                return abstract_data
            else:
                return [{
                    "user_id": 1919810,
                    "nickname": "Xray Art Team",
                    "file_name": f"{str(music_id)}_1"
                }]
        else:
            return []

    def get_abstract_data(self):
        ams = self.get_abstract_id_list()
        abstract_data = list(self.abstract_collection.find())
        ad = {"abstract": abstract_data, "ams": ams}
        return ad

    def get_abstract_file_name_all(self):
        music_abstract_data = self.abstract_collection.find({})

        file_name_map = {}
        for item in music_abstract_data:
            music_id = item['music_id']
            rdr = random.choice(item['abstract_data'])
            file_name_map[music_id] = rdr["file_name"]

        return file_name_map
abstract = Abstract()
