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
    

    def getNextCount(self,counter_id:str):
        ret = self.counters_collection.find_and_modify({"_id":counter_id},{"$inc": {"seq": 1}})
        return int(ret['seq'])


    def addalias(self,user_id:str,group_id: str,music_id: str,alias: str,songTitle: str):
        if music_id in self.queryMusicByAlias(alias):
            return "该别名已经存在", 0

        if list(self.alias_examine_collection.find({"music_id":music_id,"alias":alias})):
            return '该别名已经存在', 0

        uncount = self.alias_examine_collection.count_documents({"$expr": {"$lt": [{"$size": "$agreeList"}, 3]}})
        if uncount >= 35:
            return '目前投票列表未完成别名申请过多,建议使用<投票列表>给你心仪的别名投票,带未完成别名申请少于35条后再进行添加,或联系管理员添加别名', 0
        
        cid = f'a{self.getNextCount("examin")}'
        now_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now_time_ts = int(time.time())
        self.alias_examine_collection.insert_one({"_id":cid,'user_id':user_id,'create_dt':now_time_str,'create_ts':now_time_ts,'group_id':group_id,'music_id':music_id,'alias':alias,'agreeList':[]})
        return f'为歌曲{songTitle}添加的{alias}别名以加入审核列表中\n获得3名玩家的票数后将添加别名成功\n你的别名号为{cid}\n玩家可使用<投票{cid}>为此别名投票',cid



    def agreeAlias(self,cid:str,user_id:str):
        examine_data = self.alias_examine_collection.find_one({"_id":cid})
        if examine_data:
            if len(examine_data['agreeList']) >= 3:
                return f'{cid}已获得3票,请勿重复投票', 0
            if user_id in examine_data['agreeList']:
                return '请勿重复投票', 0

            update_result = self.alias_examine_collection.update_one({"_id":cid},{"$addToSet":{"agreeList":user_id}})
            if update_result.modified_count == 1:
                examine_data = self.alias_examine_collection.find_one({"_id":cid})
                if len(examine_data['agreeList']) >= 3:
                    existing_document = self.alias_collection.find_one({"music_id": examine_data["music_id"]})
                    if not existing_document:
                        self.alias_collection.insert_one({"music_id": examine_data["music_id"],"enable":True, "alias": [examine_data["alias"]]})
                    self.alias_collection.update_one(
                        {"music_id": examine_data["music_id"]},
                        {"$addToSet": {"alias": examine_data["alias"]}}
                    )
                    return examine_data, 1
                return '投票成功',0
            
    def adminAddAlias(self,user_id:str,group_id: str,music_id: str,alias: str,songTitle: str):

        cid = f'a{self.getNextCount("examin")}'
        # print(cid)
        now_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now_time_ts = int(time.time())
        self.alias_examine_collection.insert_one(
            {
                "_id":cid,
                'user_id':user_id,
                'create_dt':now_time_str,
                'create_ts':now_time_ts,
                'group_id':group_id,
                'music_id':music_id,
                'alias':alias,
                'agreeList':["管理员","管理员","管理员"]
            }
        )
        existing_document = self.alias_collection.find_one({"music_id": music_id})
        if not existing_document:
            self.alias_collection.insert_one({"music_id": music_id,"enable":True, "alias": [alias]})
        update_result = self.alias_collection.update_one(
            {"music_id": music_id},
            {"$addToSet": {"alias": alias}}
        )
        if update_result.modified_count:
            return '添加成功'
        else:
            return '重复添加'
    

    def getUnPassAlias(self):
        str2img = '当前票数未超过三次的别名列表如下:'
        three_days_ago = int((datetime.now() - timedelta(days=3)).timestamp())
        # 删除超时的记录
        update_result = self.alias_examine_collection.update_many(
            {
                "create_ts":{'$lt': three_days_ago},
                "$expr": {  
                    "$lt": [{"$size": "$agreeList"}, 3]  
                }  
            },
            {  
                "$push": {  
                    "agreeList": {  
                        "$each": ["别名处理","申请时间","超时"] 
                    }  
                }  
            } 
        )

        remove_count = update_result.modified_count
        examine_data = list(self.alias_examine_collection.find({"$expr": {"$lt": [{"$size": "$agreeList"}, 3]}}))
        for examine in examine_data:
            cid = examine['_id']
            music_id = examine['music_id']
            alias = examine['alias']
            title = total_list.by_id(music_id).title
            count = len(examine['agreeList'])
            str2img += f'\n{cid}-{music_id}.{title}-{alias}-{count}票'
        if len(examine_data) > 0:
            str2img += '\n玩家可使用<投票 别名号>为你赞同的别名投票,本次显示投票列表已删除超过三日未完成的别名申请'+str(remove_count)+'条'
            return str2img
        else:
            return "暂无"
        
    def removeAlias(self,music_id:str,alias:str):
        update_result = self.alias_collection.update_one(
            {
                "music_id":music_id,
                "alias":alias
            },
            {
                "$pull": {
                    "alias": alias
                }
            }

        )
        if update_result.modified_count:
            return '删除成功'
        else:
            return '未找到此别名'
        

    def SearchAlias(self,music_id:str):
        alias_data = self.alias_collection.find_one({"music_id":music_id})
        return list(set(alias_data['alias']))
        
    def steponAlias(self,cid:str):
        update_result = self.alias_examine_collection.update_one(
            {
                "_id": cid
            },
            {  
                "$push": {  
                    "agreeList": {  
                        "$each": ["别名处理", "管理员", "踩"]  
                    }  
                }  
            } 
        )
        return update_result.modified_count


    def passAlias(self,cid:str):
        update_result = self.alias_examine_collection.update_one(
            {
                "_id": cid
            },
            {  
                "$push": {  
                    "agreeList": {  
                        "$each": ["别名处理","管理员","通过"]
                    }  
                }  
            } 
        )
        if update_result.modified_count:
            examine_data = self.alias_examine_collection.find_one({"_id":cid})
            existing_document = self.alias_collection.find_one({"music_id": examine_data["music_id"]})
            if not existing_document:
                self.alias_collection.insert_one({"music_id": examine_data["music_id"],"enable":True, "alias": [examine_data["alias"]]})
            self.alias_collection.update_one(
                {"music_id": examine_data["music_id"]},
                {"$addToSet": {"alias": examine_data["alias"]}}
            )
            return examine_data
        else:
            return 0
        
    def getAliasExamine(self,cid:str):
        examine_data = self.alias_examine_collection.find_one({"_id":cid})
        if examine_data:
            return examine_data
        else:
            return {}


alias = Alias()
