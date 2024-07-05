import pymongo
from src.libraries.GLOBAL_CONSTANT import MONGO_HOST,MONGO_DATABASE,MONGO_PASSWORD,MONGO_PORT,MONGO_USERNAME


class UserData(object):
    def __init__(self):
        username = MONGO_USERNAME
        password = MONGO_PASSWORD
        host = MONGO_HOST
        port = MONGO_PORT
        database_name = MONGO_DATABASE
        connection_string = f'mongodb://{username}:{password}@{host}:{port}/{database_name}'
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client['xray-mai-bot']
        self.userdata_collection = self.db['xray_user_data']

    def getUserData(self,user_id:str):
        user_data = self.userdata_collection.find_one({"_id":user_id})
        if user_data:
            print(user_data)
            return user_data
        else:
            return {}
        
    def setUserConfig(self,user_id:str,group_id:int,arg_name:str,value):
        try:
            data = {arg_name: value}
            existing_data = self.userdata_collection.find_one({'_id': user_id})
            if existing_data:
                data['create_group'] = existing_data.get("group",group_id)
                self.userdata_collection.update_one({'_id': user_id}, {'$set': data})
            else:
                data['_id'] = user_id
                data['create_group'] = group_id
                self.userdata_collection.insert_one(data)
            return True
        except:
            return False

userdata = UserData()
