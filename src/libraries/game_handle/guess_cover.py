from pathlib import Path
from os import path
from re import T
import peewee as pw
from typing import List
import datetime

db_path = Path().absolute() / "data" / "maimai" / "guess_cover.db"
db_path.parent.mkdir(exist_ok=True, parents=True)
db = pw.SqliteDatabase(db_path)

class Group_User(pw.Model):
    Group_id = pw.TextField()
    User_id = pw.TextField()
    guess_count = pw.IntegerField()
    # 地点id 时间 人数 姓名
    primary_key = pw.CompositeKey(
        "Group_id",
        "User_id"
    )
    class Meta:
        database = db

class Guess_data(pw.Model):
    User_id = pw.TextField()
    Guess_date = pw.DateField()
    guess_count = pw.IntegerField()
    class Meta:
        database = db


if not path.exists(db_path):
    db.connect()
    db.create_tables([Group_User,Guess_data])
    db.close()

def user_Add_Count(group_id:str,user_id:str,count:int):
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    user_data:List[Group_User] =Group_User.select().where(Group_User.Group_id == group_id,Group_User.User_id ==user_id)
    if user_data:
        Group_User.update(guess_count = Group_User.guess_count+count).where(Group_User.User_id ==user_id , Group_User.Group_id == group_id).execute()
    else:
        Group_User.insert(Group_id = group_id,User_id=user_id,guess_count=count).execute()
    guess_user_data:List[Guess_data] =Guess_data.select().where(Guess_data.User_id ==user_id,Guess_data.Guess_date == date_str)
    if guess_user_data:
        Guess_data.update(guess_count = Guess_data.guess_count+count).where(Guess_data.User_id ==user_id,Guess_data.Guess_date == date_str).execute()
    else:
        Guess_data.insert(User_id=user_id,guess_count=count,Guess_date=date_str).execute()

def get_group_top5(group_id:str):
    return Group_User.select().where(Group_User.Group_id == group_id).order_by(Group_User.guess_count.desc())

def get_group_last(group_id:str):
    return Group_User.select().where(Group_User.Group_id == group_id).order_by(Group_User.guess_count.asc())

def get_all_top5():
    return Group_User.select(Group_User.User_id,pw.fn.SUM(Group_User.guess_count).alias("guess_count_temp")).group_by(Group_User.User_id).order_by(pw.fn.SUM(Group_User.guess_count).alias("guess_count_temp").desc())

def get_day_top5():
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    return Guess_data.select(Guess_data.User_id,Guess_data.guess_count).where(Guess_data.Guess_date==date_str).order_by(Guess_data.guess_count.desc())

def execute_sql(sql:str):
    conn = db._connect()
    cur = conn.cursor()
    cur.execute(sql)
    if 'select' in sql:
        result = cur.fetchall()
        msg = '查询结果如下'
        for item in result:
            msg += '\n'+str(item)
        return msg
    else:
        return '执行完毕'