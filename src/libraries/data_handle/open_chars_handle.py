import pymongo
from src.plugins.xray_plugins_open_chars.utils import generate_game_data
from src.libraries.GLOBAL_CONSTANT import MONGO_HOST,MONGO_DATABASE,MONGO_PASSWORD,MONGO_PORT,MONGO_USERNAME

class OpenChars(object):
    def __init__(self):
        username = MONGO_USERNAME
        password = MONGO_PASSWORD
        host = MONGO_HOST
        port = MONGO_PORT
        database_name = MONGO_DATABASE
        connection_string = f'mongodb://{username}:{password}@{host}:{port}/{database_name}'
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client['xray-mai-bot']
        self.collection = self.db['open_chars']

    def start(self,group_id:int,arg:str):
        game_data = self.collection.find_one({"_id":group_id})
        if game_data:
            return True,game_data
        else:
            game_data = generate_game_data(arg)
            game_data['_id'] = group_id
            self.collection.insert_one(game_data)
            return False,game_data

    def game_over(self,group_id:int):
        self.collection.delete_one({"_id":group_id})

    def open_char(self,group_id:int,chars:str):
        game_data = self.collection.find_one({"_id":group_id})
        if game_data:
            if chars.lower() in game_data['open_chars']:
                return False,{}
            else:
                game_data['open_chars'].append(chars.lower())
                return True,game_data
        else:
            return None,None
    
    def get_game_data(self,group_id:int):
        game_data = self.collection.find_one({"_id":group_id})
        if game_data:
            return game_data
        else:
            return None
    
    def update_game_data(self,group_id:int,game_data):
        self.collection.update_one({"_id":group_id},{"$set":game_data})

    
openchars = OpenChars()